from PymoNNto import *
from PymoNNto.Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *

def compute_temporal_reconstruction(network, single_neuron_group=None, single_neuron_id=None, recon_group_tag='recon'):
    RALN = Reconstruct_Analyze_Label_Network(network)
    RALN.zero_recon()
    if single_neuron_id is not None and single_neuron_group is not None:
        single_neuron_group.recon[single_neuron_id] = 1
    else:
        for ng in network.NeuronGroups:
            ng.recon = ng.output.copy()
    RALN.propagation('W', 10, 'backward', 'forget', 'all', temporal_recon_groups=network[recon_group_tag], exponent=4, normalize=True, filter_weakest_percent=40.0)  # forget

    for ng in network[recon_group_tag]:
        baseline = ng.Input_Weights.transpose().dot(ng.temporal_recon[-1])
        if np.sum(baseline)!=0:
            baseline = baseline / np.sum(baseline)
        else:
            baseline = 0

        if single_neuron_id is not None and single_neuron_group is not None and ng == single_neuron_group:  # clicked group?
            temp = ng.vector()
            temp[single_neuron_id] = 1.0
            ng.temporal_recon.insert(0, temp)
        else:
            ng.temporal_recon.append(ng.vector())


        res = []

        for r in ng.temporal_recon:
            char_vec = ng.Input_Weights.transpose().dot(r)
            s = np.sum(char_vec)
            if s > 0:
                char_vec = char_vec / s
                res.insert(0, char_vec - baseline)
                #text = generator.index_to_char(np.argmax(char_vec)) + text
            else:
                res.insert(0, np.zeros(ng.Input_Weights.shape[1]))
                #text = '#' + text

        #text = list(text)
        #start = text[0]
        #for i, c in enumerate(text):
        #    if text[i] == start:
        #        text[i] = '#'
        #    else:
        #        break
        #text = ''.join(text)

        return res

def generate_text_from_recon_mat(recon_mat, generator):
    text = ''
    for char_vec in recon_mat:
        s = np.max(char_vec)-np.min(char_vec)#np.sum(char_vec)
        if s>0:
            text = text + generator.index_to_char(np.argmax(char_vec))
        else:
            text = text + '#'

    text = list(text)
    start = text[0]
    for i, c in enumerate(text):
        if text[i] == start:
            text[i] = '#'
        else:
            break
    text = ''.join(text)
    return text.replace(' ','_')