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




def normalize_synapse_attr_efferent(src_attr, target_attr, target_value, neurons, synapse_type):
    neurons.temp_weight_sum = neurons.get_neuron_vec()

    for s in neurons.efferent_synapses[synapse_type]:
        s.src.temp_weight_sum += np.sum(np.abs(getattr(s, target_attr)), axis=0)

    neurons.temp_weight_sum /= target_value

    for s in neurons.efferent_synapses[synapse_type]:
        setattr(s, src_attr, getattr(s, src_attr) / (s.src.temp_weight_sum + (s.src.temp_weight_sum == 0)))

'''
from PymoNNto import *

net = Network(tag='Network')

ng = NeuronGroup(tag='Neuron', net=net, behaviour={}, size=10)
sg = SynapseGroup(tag='GLU', src=ng, dst=ng, net=net, behaviour={})

net.initialize()

sg.W = sg.get_synapse_mat('random')

print(np.sum(sg.W,0))
print(np.sum(sg.W,1))

normalize_synapse_attr_efferent('W','W', 1, ng, 'GLU')
normalize_synapse_attr('W','W', 1, ng, 'GLU')

print(np.sum(sg.W,0))
print(np.sum(sg.W,1))

import matplotlib.pyplot as plt

plt.matshow(sg.W)
plt.show()
'''