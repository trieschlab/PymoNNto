from PymoNNto import *




def get_unique_non_partitioned_Groups(groups):
    temp = {}
    result = []
    for g in groups:
        key = ','.join(g.tags)
        if key not in temp:
            temp[key] = [g]
            result.append(g)
        else:
            temp[key].append(g)
    return result


#########################################
####Partitioned
#########################################

def get_partitioned_synapse_matrix(neurons, synapse_tag, synapse_var, return_first=True):
    results = {}
    shapes = {}
    for s in neurons.synapses(afferent, synapse_tag):
        base_src = s.src.group_without_subGroup()
        base_dst = s.dst.group_without_subGroup()
        key = ','.join(s.tags)
        if not key in results:
            results[key] = np.zeros((base_dst.size, base_src.size))
            shapes[key] = (base_src.height, base_src.width)
        try:
            syn_mat = eval('s.' + synapse_var)
            if type(syn_mat) is not bool:
                w = s.ignore_transpose_mode(syn_mat)
            else:
                w = syn_mat
            if base_src == s.src and base_dst == s.dst:
                results[key] += w  # .copy()
            else:
                mat_mask = s.dst.mask[:, None] * s.src.mask[None, :]
                results[key][mat_mask] += np.array(w).flatten()  # np.array required if syn_mat is bool (enabled)
        except:
            print(synapse_var, "cannot be evaluated")

    if return_first:
        return list(results.values())[0]
    else:
        return results

def set_partitioned_synapse_matrix(neurons, synapse_tag, synapse_var, mat):#warning! synapse_tag has to be unique and only used by partition synapses
    for s in neurons.synapses(afferent, synapse_tag):
        try:
            mask = s.dst.mask[:, None] * s.src.mask[None, :]
            setattr(s, synapse_var, mat[mask].reshape(s.matrix_dim()))
        except:
            print(synapse_var, "cannot be set")


def SingleNeuron_attached_SubSGs(neuron_group, synapse_tag, neuron_id):
    result = []
    for s in neuron_group.synapses(afferent, synapse_tag):
        if neuron_id in s.dst.id:
            result.append(s)
    return result

def get_single_neuron_combined_partition_matrix(neurons, synapse_tag, synapse_var, neuron_id, return_first=True):
    results = []
    for s in SingleNeuron_attached_SubSGs(neurons, synapse_tag, neuron_id):
        base_src = s.src.group_without_subGroup()
        mat = np.zeros(base_src.depth*base_src.height*base_src.width)
        indx = np.where(s.dst.id == neuron_id)[0]
        if hasattr(s, synapse_var):
            mat[s.src.mask] = eval('s.' + synapse_var)[indx].flatten()
        results.append(mat.reshape((base_src.depth*base_src.height, base_src.width)))

    if return_first:
        return results[0]
    else:
        return results

#def set_partitioned_single_neuron_weights(neurons, synapse_tag, synapse_var, neuron_id, vec):
#    for s in SingleNeuron_attached_SubSGs(neurons, synapse_tag, id):
#        base_src = s.src.group_without_subGroup()
#        mat = np.zeros(base_src.height*base_src.width)
#        mat[s.src.mask] = eval('s.' + synapse_var).flatten()
#        results.append(mat.reshape((base_src.height, base_src.width)))

#        try:
#            mask = s.dst.mask[:, None] * s.src.mask[None, :]
#            setattr(s, synapse_var, mat[mask].reshape(s.matrix_dim()))
#        except:
#            print(synapse_var, "cannot be set")


#def get_partitioned_matrix(neuron, synapse_tag, synapse_var):
#    return list(get_combined_syn_mats(neuron.synapses(afferent, synapse_tag), None, synapse_var).values())[0]

#def set_partitioned_matrix(neuron, synapse_tag, synapse_var, mat):



#########################################
####Old
#########################################


def get_combined_syn_mats(synapses, neuron_id=None, attr='W'):
    results = {}
    shapes = {}
    for s in synapses:
        base_src = s.src.group_without_subGroup()
        base_dst = s.dst.group_without_subGroup()
        key = ','.join(s.tags)
        if not key in results:
            results[key] = np.zeros((base_dst.size, base_src.size))
            shapes[key] = (base_src.height, base_src.width)
        try:
            syn_mat = eval('s.' + attr)
            if type(syn_mat) is not bool:
                w = s.ignore_transpose_mode(syn_mat)
            else:
                w = syn_mat
            if base_src == s.src and base_dst == s.dst:
                results[key] += w # .copy()
            else:
                mat_mask = s.dst.mask[:, None] * s.src.mask[None, :]
                results[key][mat_mask] += np.array(w).flatten()  # np.array required if syn_mat is bool (enabled)
        except:
            print(attr, "cannot be evaluated")

    if neuron_id is not None:
        for key in results:
            results[key] = results[key][neuron_id].reshape(shapes[key])

    return results

