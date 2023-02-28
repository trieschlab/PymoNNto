from PymoNNto.NetworkCore.Behaviour import *

class Normalization(Behaviour):

    def set_variables(self, neurons):
        self.syn_type = self.parameter('syn_type', 'GLUTAMATE', neurons)
        self.norm_factor = self.parameter('norm_factor', 1.0, neurons)
        neurons.temp_weight_sum = neurons.vector()

    def new_iteration(self, neurons):

        neurons.temp_weight_sum *= 0.0

        for s in neurons.afferent_synapses[self.syn_type]:
            s.dst.temp_weight_sum += np.sum(np.abs(s.W), axis=1)

        neurons.temp_weight_sum /= self.norm_factor

        for s in neurons.afferent_synapses[self.syn_type]:
            s.W = s.W / (s.dst.temp_weight_sum[:, None] + (s.dst.temp_weight_sum[:, None] == 0))