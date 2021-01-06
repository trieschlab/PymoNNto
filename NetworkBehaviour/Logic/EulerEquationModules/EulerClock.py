from SORNSim.NetworkCore.Behaviour import *
import numpy as np
from sympy import symbols
from sympy.physics.units import *


class ClockModule(Behaviour):

    def set_variables(self, neuron_or_network):
        self.add_tag('Clock')

        #convert_to(seconds / tau, seconds)

        neuron_or_network.clock_step_size = float(convert_to(eval(self.get_init_attr('step', '1*ms')), seconds)/second) #in ms (*ms)
        self.clock_step_size=neuron_or_network.clock_step_size
        print(neuron_or_network.clock_step_size)
        neuron_or_network.t = 0.0

    def new_iteration(self, neuron_or_network):
        neuron_or_network.t += neuron_or_network.clock_step_size

    def time_to_iterations(self, time_str):
        iterations = int(convert_to(eval(time_str + '/seconds'), seconds)/self.clock_step_size)
        print(iterations)
        return iterations
