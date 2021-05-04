from PymoNNto import *
import os
import sys

#def get_gene_string(gene):  # same implementation as interface_function get_gene_id
#    id = ''
#    for key, value in gene.items():
#        id += '#' + key + '$' + str(value)
#    return id + '#'

def execute_local_file(slave_file, genome):
    for arg in sys.argv:  # remove old
        if 'genome=' in arg:
            sys.argv.remove(arg)
    sys.argv.append('genome=' + get_gene_id(genome))  # add new

    py_file = open(slave_file, "r")
    execution_string = py_file.read()
    exec(execution_string)
    py_file.close()

class Evolution_Device():#one device per thread

    def __init__(self, device_string, parent):
        self.device_string = device_string
        self.parent = parent
        self.current_gene = None

    def score_processing(self, genome):
        score = self.get_score(genome)

        if score is not None:
            genome['score'] = score
            self.new_score_event(genome)
        else:
            self.error_event(genome, 'loaded score is None/ not able to load score')

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

    def new_score_event(self, genome):
        if genome['gen'] == self.parent.Breed_And_Select.generation:  # part of current execution? still relevant?
            self.parent.new_score_event(genome)
        else:
            self.parent.error_event(genome, 'processed gene result from previous generation')

    def error_event(self, genome, message):
        if genome['gen'] == self.parent.Breed_And_Select.generation: #part of current execution? still relevant?
            self.parent.error_event(genome, message)
        else:
            self.parent.error_event(genome, message+' (from previous generation)')

    def get_score(self, genome):# override
        return