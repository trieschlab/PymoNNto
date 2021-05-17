import numpy as np

scipy.sparse

def normalize_synapse_attr_sparse(src_attr, target_attr, target_value, neurons, synapse_type):

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
