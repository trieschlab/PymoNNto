from PymoNNto.NetworkCore.Behaviour import *

class Homeostasis(Behaviour):

    def set_variables(self, neurons):
        target_act = self.parameter('target_voltage', 0.05, neurons)

        self.max_ta = self.parameter('max_ta', target_act, neurons)
        self.min_ta = self.parameter('min_ta', target_act, neurons)

        self.adj_strength = -self.parameter('eta_ip', 0.001, neurons)

        neurons.exhaustion = neurons.vector()



    def new_iteration(self, neurons):

        greater = ((neurons.voltage > self.max_ta) * -1).astype(neurons.def_dtype)
        smaller = ((neurons.voltage < self.min_ta) * 1).astype(neurons.def_dtype)

        greater *= neurons.voltage - self.max_ta
        smaller *= self.min_ta - neurons.voltage

        change = (greater + smaller) * self.adj_strength
        neurons.exhaustion += change

        neurons.voltage -= neurons.exhaustion