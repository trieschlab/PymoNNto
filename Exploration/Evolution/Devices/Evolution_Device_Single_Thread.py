from PymoNNto.Exploration.Evolution.Devices.Evolution_Device import *

class Evolution_Device_Single_Thread(Evolution_Device):

    def get_score(self, genome):
        sm = StorageManager(main_folder_name=genome['evo_name'], folder_name=get_gene_file(genome), add_new_when_exists=False)#, print_msg=False
        return sm.load_param('score', default=None)

    def main_loop_update(self):
        current_genome = self.parent.get_next_genome()

        if current_genome is not None:

            if os.path.isfile(self.parent.slave_file):
                execute_local_file(self.parent.slave_file, current_genome)
            else:
                print('file not found')

            self.score_processing(current_genome)

        else:
            print('no genes found to process')
