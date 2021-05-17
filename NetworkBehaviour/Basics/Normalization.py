from PymoNNto.NetworkCore.Behaviour import *
import numpy as np

class Synaptic_Normalization(Behaviour):

    def set_variables(self, neurons):
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)
        self.clip_max = self.get_init_attr('clip_max', None, neurons)
        neurons.weight_norm_factor = neurons.get_neuron_vec()+self.get_init_attr('norm_factor', 1.0, neurons)

    def new_iteration(self, neurons):
        normalize_synapse_attr('W', 'W', neurons.weight_norm_factor, neurons, self.syn_type)
        for s in neurons.afferent_synapses[self.syn_type]:
            s.W = np.clip(s.W, 0, self.clip_max)






def normalize_synapse_attr(src_attr, target_attr, target_value, neurons, synapse_type):
    neurons.temp_weight_sum = neurons.get_neuron_vec()

    for s in neurons.afferent_synapses[synapse_type]:
        s.dst.temp_weight_sum += np.sum(np.abs(getattr(s, src_attr)), axis=1)

    neurons.temp_weight_sum /= target_value

    for s in neurons.afferent_synapses[synapse_type]:
        setattr(s, target_attr, getattr(s, target_attr) / (s.dst.temp_weight_sum[:, None] + (s.dst.temp_weight_sum[:, None] == 0)))

