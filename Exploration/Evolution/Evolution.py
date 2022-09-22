from PymoNNto.Exploration.Evolution.Devices.Evolution_Device_Single_Thread import *
from PymoNNto.Exploration.Evolution.Devices.Evolution_Device_SSH import *
from PymoNNto.Exploration.Evolution.Breed_And_Selection_Module import *
from PymoNNto.Exploration.Evolution.UI_Single_Evolution_Monitor import *
from PymoNNto.Exploration.Evolution.genome_exchange_com import *
import os.path
import time
from PymoNNto.Exploration.Evolution.Evolution_Individual import *


class Evolution:

    def __init__(self, name, slave_file, individual_count=10, mutation=0.4, death_rate=0.5, devices={'single_thread':1}, constraints=[], start_genomes=[], inactive_genome_info={}, breed_and_select_module=Default_Breed_And_Select, additional_evo_params={}):

        self.Breed_And_Select = breed_and_select_module(self, death_rate=death_rate, mutation=mutation, individual_count=individual_count, constraints=constraints, additional_evo_params=additional_evo_params)

        self.genome_exchanger_socket = Genome_Exchanger_Socket()

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

        for key in ['generation', 'score', 'id']:
            for genome in self.start_genomes:
                if key in genome:
                    genome.pop(key)
                    print(key, 'removed form genomes')

        self.gene_keys = []
        if len(self.start_genomes) > 0:
            self.gene_keys = list(self.start_genomes[0].keys())

            individuals = []
            for genome in self.start_genomes:
                individuals.append(Evolution_individual(genome=genome))

            #for genome in self.start_genomes:
            #    if len(self.gene_keys) != len(genome):
            #        print('Error: start genomes do not have the same size')
            #    for gene in genome:
            #        if gene not in self.gene_keys:
            #            print('Error: start genomes have different gene keys')

            #    if not self.Breed_And_Select.is_valid_genome(genome):
            #        print('Error: start genome does not fulfill constraints', genome)

            self.scored_individuals = []
            self.running_individuals = []
            self.non_scored_individuals = self.Breed_And_Select.breed(individuals)

            for individual in self.non_scored_individuals:
                individual.id = self.get_individual_id()

            print('starting individuals:', self.non_scored_individuals)
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

    def get_individual_id(self):
        result = self.id_counter
        self.id_counter += 1
        return result

    def iteration(self):
        for device in self.devices:
            device.main_loop_update()
        #time.sleep(1.0)

    #def part_of_genome(self, small_genome, big_genome):
    #    result = True
    #    for key in small_genome:
    #        if key!='score' and key not in big_genome or small_genome[key] != big_genome[key]:
    #            result = False
    #    return result

    #def find(self, genome_list, genome):
    #    found = None
    #    for g in genome_list:
    #        if self.part_of_genome(g, genome):
    #            found = g
    #    return found

    def new_score_event(self, evo_id, score):
        found = find_individual(evo_id, self.running_individuals)
        if found is not None:
            found.score = score
            self.running_individuals.remove(found)
            self.scored_individuals.append(found)
            self.Breed_And_Select.update_population()
            if self.ui is not None:
                self.ui.update()
        else:
            self.error_event(evo_id, 'processed gene not found in running_individuals | running:' + str(self.running_individuals) + ' scored:' + str(self.scored_individuals))

    #def new_score_event(self, genome):#called by devices
    #    #found = self.find(self.running_individuals, genome)
    #    found = find_individual(genome['id'], self.running_individuals)
    #
    #    if found is not None:
    #        self.running_individuals.remove(found)
    #        found['score'] = genome['score']
    #        self.scored_individuals.append(found)
    #        self.Breed_And_Select.update_population()
    #        print('+', genome)#g
    #
    #        if self.ui is not None:
    #            self.ui.update()
    #
    #    else:
    #        self.error_event(genome, 'processed gene not found in running_individuals | running:' + str(self.running_individuals)+' scored:'+str(self.scored_individuals))

    def error_event(self, evo_id, message, terminate=False):#called by devices
        print('failed', message, 'id=', evo_id)

        if terminate:
            ssm= SimpleStorageManager(get_data_folder()+'/')
            ssm.save_str('error', message+" \r\nid="+str(evo_id))
            print(get_data_folder()+'error.txt write')
        else:
            found = find_individual(evo_id, self.running_individuals)

            if found is not None:
                self.running_individuals.remove(found)
                self.non_scored_individuals.append(found)
                print('move genome from running_individuals back to non_scored_individuals...')
            else:
                print('not able to find failed genome in running_individuals.')

    #def error_event(self, genome, message, terminate=False):#called by devices
    #    print('failed', message, genome)

    #    if terminate:
    #        ssm= SimpleStorageManager(get_data_folder()+'/')
    #        ssm.save_str('error', message+" \r\n"+str(genome))
    #        print(get_data_folder()+'error.txt write')
    #    else:
    #        found = find_individual(genome['id'], self.running_individuals)
    #        #found = None
    #        #for g in self.running_individuals:
    #        #    if self.part_of_genome(g, genome):
    #        #        found = g

    #        if found is not None:
    #            self.running_individuals.remove(found)
    #            self.non_scored_individuals.append(found)
    #            print('move genome from running_individuals back to non_scored_individuals...')
    #        else:
    #            print('not able to find failed genome in running_individuals. Maybe the genome was changed during processing')


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

                new_ind = self.genome_exchanger_socket.get_new_individuals()
                if new_ind is not None:
                    if new_ind.has_genes(self.gene_keys):
                        self.non_scored_individuals.append(new_ind)
                        print('socket gene insertion successful', new_ind)
                    else:
                        print('socket gene insertion failed', new_ind)


                for device in self.devices:
                    device.main_loop_update()
                time.sleep(0.01)

        for device in self.devices:
            device.stop()

    def load_state(self):
        population = []

        smg = StorageManagerGroup(self.name)

        smg.sort_by('generation')
        gens = smg.get_param_list('generation', remove_None=True)
        if len(gens)>0:
            last_full_gen = np.max(gens) - 1
            for sm in smg['generation==' + str(last_full_gen)]:
                individual = Evolution_individual(genome={})

                valid = True
                for gene in self.gene_keys:
                    individual.genome[gene] = sm.load_param(gene)
                    if individual.genome[gene] is None:
                        valid = False

                individual.score = sm.load_param('score')

                if individual.score is None:
                    valid = False

                if valid:
                    population.append(individual)
                else:
                    print('invalid individual!')

            ids = smg.get_param_list('id', remove_None=True)
            max_id = np.max(ids)
            self.id_counter = max_id + 1

            if len(population) != 0:
                self.scored_individuals = population
                self.running_individuals = []
                self.non_scored_individuals = []
                self.Breed_And_Select.generation = last_full_gen

            print('Continuing', self.name, 'at generation', last_full_gen, 'with genomes', self.scored_individuals)

        self.Breed_And_Select.update_population()

    def continue_evolution(self, ui=True):
        self.load_state()
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

    #def add_name_gen_id_inactive_to_genome(self, genome):
    #    #result = genome.copy()
    #    result['evo_name'] = self.name
    #    #result['generation'] = self.Breed_And_Select.generation
    #    #result['id'] = self.id_counter
    #    self.id_counter += 1
    #    #result.update(self.inactive_genome_info)
    #    return result

    def get_next_individual(self):
        result = None
        if len(self.non_scored_individuals) > 0:
            result = self.non_scored_individuals[0]
            self.non_scored_individuals.pop(0)
            self.running_individuals.append(result)

        #if result is not None:
        #    result = self.add_name_gen_id_inactive_to_genome(result)

        return result

    #add evo_name and static genome to pipeline!!!