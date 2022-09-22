from PymoNNto.Exploration.Evolution.Devices.Evolution_Device import *

class Evolution_Device_Single_Thread(Evolution_Device):

    def main_loop_update(self):
        current_individual = self.parent.get_next_individual()

        if current_individual is not None:

            #if os.path.isfile(self.parent.slave_file):
            #print('exec', current_individual.id)
            execute_local_file(self.parent.slave_file, self.parent.name , current_individual.id, self.parent.Breed_And_Select.generation, current_individual.genome, self.parent.inactive_genome_info)
            #else:
            #    print('file not found', self.parent.slave_file)

            self.score_processing(current_individual.id)

        else:
            print('no genes found to process')
