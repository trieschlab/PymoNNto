from PymoNNto import *

class refractory(Behavior):

    def initialize(self, neurons):
        neurons.refractory_counter = neurons.vector()
        self.decayfactor = self.parameter('decayfactor', 0.5, neurons)
        self.strengthfactor = self.parameter('strengthfactor', 1.0, neurons)

    def iteration(self, neurons):
        neurons.refractory_counter *= self.decayfactor
        neurons.refractory_counter += neurons.output

        neurons.activity -= neurons.refractory_counter * self.strengthfactor