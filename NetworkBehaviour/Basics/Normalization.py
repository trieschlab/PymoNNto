import numpy as np


def normalize_synapse_attr(src_attr, target_attr, target_value, neurons, synapse_type):
    neurons.temp_weight_sum = neurons.get_neuron_vec()

    for s in neurons.afferent_synapses[synapse_type]:
        s.dst.temp_weight_sum += np.sum(np.abs(getattr(s, src_attr)), axis=1)

    neurons.temp_weight_sum /= target_value

    # print(neurons.temp_weight_sum)

    for s in neurons.afferent_synapses[synapse_type]:
        setattr(s, target_attr,
                getattr(s, target_attr) / (s.dst.temp_weight_sum[:, None] + (s.dst.temp_weight_sum[:, None] == 0)))



def normalize_synapse_attr_sparse(self, src_attr, target_attr, target_value, neurons, synapse_type):

    neurons.temp_weight_sum = neurons.get_neuron_vec()

    for s in neurons.afferent_synapses[synapse_type]:
        if 'sparse' in s.tags:
            s.dst.temp_weight_sum += np.array(getattr(s, src_attr).sum(1)).flatten()
        else:
            s.dst.temp_weight_sum += np.sum(getattr(s, src_attr), axis=1)

    neurons.temp_weight_sum /= target_value

    for s in neurons.afferent_synapses[synapse_type]:
        if 'sparse' in s.tags:
            W = getattr(s, target_attr)
            W.data /= np.array(neurons.temp_weight_sum[W.indices]).reshape(W.data.shape)
        else:
            setattr(s, target_attr, getattr(s, target_attr) / (s.dst.temp_weight_sum[:, None]+(s.dst.temp_weight_sum[:, None]==0)))
