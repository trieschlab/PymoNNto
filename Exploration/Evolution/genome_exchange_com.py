from PymoNNto.Exploration.Evolution.communication import *
from PymoNNto.Exploration.Evolution.Evolution_Individual import *
import ast



class Genome_Exchanger_Socket(Socket_Listener):

    def __init__(self):
        super().__init__()
        self.individuals = []

    def get_new_individuals(self):
        if len(self.individuals)>0:
            return self.individuals.pop(0)
        return None

    def handle_message(self, data):
        lines = data.split("\r\n")
        if lines[0] == "insert":
            self.individuals = []
            valid = 0
            for l in lines[1:]:
                try:
                    genome = ast.literal_eval(l)
                    self.individuals.insert(0, Evolution_individual(genome))
                    valid += 1
                except:
                    print("received invalid genome", l)
            return str(valid) + " genomes inserted"
        return "no known command"