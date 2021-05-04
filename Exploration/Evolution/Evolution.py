from Exploration.Evolution.Devices.Evolution_Device_Single_Thread import *
from Exploration.Evolution.Devices.Evolution_Device_SSH import *
from PymoNNto.Exploration.Evolution.Breed_And_Selection_Module import *
from PymoNNto.Exploration.Evolution.UI_Single_Evolution_Monitor import *
import os.path
import time


class Evolution:

    def __init__(self, name, slave_file, individual_count=10, mutation=0.4, death_rate=0.5, devices={'single_thread':1}, constraints=[], start_genomes=[], inactive_genome_info={}):

        self.Breed_And_Select = Default_Breed_And_Select(self, death_rate=death_rate, mutation=mutation, individual_count=individual_count, constraints=constraints)

        self.name = name

        self.slave_file = slave_file

        self.devices = []
        self.start_genomes = start_genomes
        self.inactive_genome_info = inactive_genome_info

        self.id_counter = 0

        if not os.path.isfile(slave_file):
            print('warning slave file not found')

        if start_genomes==[]:
            print('Error no genomes found')

        self.scored_individuals = []
        self.running_individuals = []

        self.gene_keys=[]
        if len(self.start_genomes) > 0:
            self.gene_keys = list(self.start_genomes[0].keys())
            for genome in self.start_genomes:
                if len(self.gene_keys) != len(genome):
                    print('Error: start genomes do not have the same size')
                for gene in genome:
                    if gene not in self.gene_keys:
                        print('Error: start genomes have different gene keys')

                if not self.Breed_And_Select.is_valid_genome(genome):
                    print('Error: start genome does not fulfill constraints', genome)

            self.non_scored_individuals = self.Breed_And_Select.breed(start_genomes)
            print(self.non_scored_individuals)
        else:
            print('Error no start genomes found')

        for device_string, number_of_threads in devices.items():
            self.add_devices(device_string, number_of_threads)

        if is_invalid_evo_name(name):
            print('Error: For savety reasons some names and characters are forbidden to avoid the accidental removal of files or folders')
            self.devices = {}

        for device in self.devices:
            device.initialize()

        self.ui = None

        return

    def iteration(self):
        for device in self.devices:
            device.main_loop_update()
        #time.sleep(1.0)

    def part_of_genome(self, small_genome, big_genome):
        result = True
        for key in small_genome:
            if key!='score' and key not in big_genome or small_genome[key] != big_genome[key]:
                result = False
        return result


    def new_score_event(self, genome):#called by devices
        found = None

        for g in self.running_individuals:
            if self.part_of_genome(g, genome):
                found = g

        if found is not None:
            self.running_individuals.remove(found)
            found['score'] = genome['score']
            self.scored_individuals.append(found)
            self.Breed_And_Select.update_population()
            print('+', genome)#g

            if self.ui is not None:
                self.ui.update()

        else:
            self.error_event(genome, 'processed gene not found in running_individuals | running:' + str(self.running_individuals)+' scored:'+str(self.scored_individuals))

    def error_event(self, genome, message):#called by devices
        print('failed', message, genome)

        found = None
        for g in self.running_individuals:
            if self.part_of_genome(g, genome):
                found = g

        if found is not None:
            self.running_individuals.remove(found)
            self.non_scored_individuals.append(found)
            print('move genome from running_individuals back to non_scored_individuals...')
        else:
            print('not able to find failed genome in running_individuals. Maybe the genome was changed during processing')


    def add_device(self, device_string):
        if device_string == 'single_thread':
            self.devices.append(Evolution_Device_Single_Thread(device_string, self))
        if device_string == 'multi_thread':
            self.devices.append(Evolution_Device_Multi_Thread(device_string, self))
        if 'ssh' in device_string:
            self.devices.append(Evolution_Device_SSH(device_string, self))

    def add_devices(self, device_string, number_of_threads):
        # move folder to remote device if needed
        for _ in range(number_of_threads):
            self.add_device(device_string)

        if len(self.devices) > 0:
            self.devices[-1].initialize_device_group()

    def _run_evo(self, ui=True):
        for device in self.devices:
            device.start()

        if ui:
            self.ui = UI_Single_Evolution_Monitor(self)
            self.ui.show()
        else:
            self.active = True
            while self.active:
                for device in self.devices:
                    device.main_loop_update()
                time.sleep(0.01)

        for device in self.devices:
            device.stop()

    def continue_evolution(self, ui=True):

        genomes = []

        smg = StorageManagerGroup(self.name)

        smg.sort_by('gen')
        gens = smg.get_param_list('gen', remove_None=True)
        last_full_gen = np.max(gens)-1
        for sm in smg['gen=='+str(last_full_gen)]:
            genome = {}
            try:
                valid=True
                for key in self.gene_keys:
                    genome[key] = sm.load_param(key)
                    if genome[key] is None:
                        valid = False
                genome['score'] = sm.load_param('score')
                if genome['score'] is not None and valid:
                    genomes.append(genome)
            except:
                print('failed to load gene from', sm.folder_name)

        if len(genomes)!=0:
            self.scored_individuals = genomes
            self.running_individuals = []
            self.non_scored_individuals = []
            self.Breed_And_Select.generation = last_full_gen

        print('Continuing', self.name, 'at generation', last_full_gen, 'with the following genomes:')
        print(self.scored_individuals)

        self.Breed_And_Select.update_population()

        self._run_evo(ui)

    def start(self, ui=True):
        folder = get_data_folder()+'/StorageManager/'+self.name
        if not os.path.isdir(folder):

            self._run_evo(ui)
            return True
        else:
            print('Warning:', folder, 'already exists. Remove folder or try continue_evolution() instead of start()')
            return False

    def stop(self):
        for device in self.devices:
            device.stop()

    def get_next_genome(self):
        result = None
        if len(self.non_scored_individuals) > 0:
            result = self.non_scored_individuals[0]
            self.non_scored_individuals.pop(0)
            self.running_individuals.append(result)

        #if result is None and len(self.running_individuals) > 0:
        #    result = self.running_individuals[0]

        if result is not None:
            result = result.copy()
            result['evo_name'] = self.name
            result['gen'] = self.Breed_And_Select.generation
            result['id'] = self.id_counter
            self.id_counter += 1
            result.update(self.inactive_genome_info)

        return result