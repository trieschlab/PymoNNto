from PymoNNto import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *
import os
import sys

#def get_gene_string(gene):  # same implementation as interface_function get_gene_id
#    id = ''
#    for key, value in gene.items():
#        id += '#' + key + '$' + str(value)
#    return id + '#'

#def execute_local_file(slave_file, genome):
#    for arg in sys.argv:  # remove old
#        if 'genome=' in arg:
#            sys.argv.remove(arg)
#    sys.argv.append('genome=' + get_gene_id(genome))  # add new

#    py_file = open(slave_file, "r")
#    execution_string = py_file.read()
#    exec(execution_string)
#    py_file.close()

class Evolution_Device():#one device per thread

    def __init__(self, device_string, parent):
        self.device_string = device_string
        self.parent = parent
        self.current_gene = None

    def score_processing(self, evo_id):
        score = self.get_score(self.parent.name, evo_id)

        if score is not None:
            self.parent.new_score_event(evo_id, score)
        else:
            self.parent.error_event(evo_id, 'not able to load score (score=None)', False)

    def initialize_device_group(self):# override / called before initialize but only once per thread group
        return

    def initialize(self):# override
        return

    def main_loop_update(self):# override
        return

    def start(self):# override
        return

    def stop(self):# override
        return

    #def new_score_event(self, id, score):
    #    if genome.generation == self.parent.Breed_And_Select.generation:  # part of current execution? still relevant?
    #        self.parent.new_score_event(id, score)
    #    else:
    #        self.parent.error_event(id, 'processed gene result from previous generation', False)

    #def error_event(self, genome, message):
    #    if genome.generation == self.parent.Breed_And_Select.generation: #part of current execution? still relevant?
    #        self.parent.error_event(genome, message, True)
    #    else:
    #        self.parent.error_event(genome, message+' (from previous generation)')

    def get_score(self, evo_name, evo_id):
        sm = StorageManager(main_folder_name=evo_name, folder_name=get_gene_file(evo_name, evo_id), add_new_when_exists=False, use_evolution_path=False, last=True)#, print_msg=False
        return float(sm.load_param('score', default=None))
