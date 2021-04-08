from PymoNNto.NetworkCore.Network import *
import numpy as np
import matplotlib.pylab as plt
from collections import Counter
import scipy.sparse as sp


class Reconstruct_Analyze_Label_Network():
    def __init__(self, network):
        self.network = network


    def get_network_responses(self, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = 2, pattern_repeat=1, shuffle=True, combinations=False):

        activators={}
        for ng in self.network.NeuronGroups:
            ng.learning=False
            for be in ng.behaviour.values():
                if isinstance(be, NeuronActivator) and not isinstance(be, NeuronManualActivator):
                    activators[be] = be.active
                    be.active = False


        man_act = None

        for be in target_activation_neurons.behaviour.values():
            if isinstance(be, NeuronManualActivator):
                man_act = be

        if man_act is None:
            man_act=self.network.add_behaviours_to_neuron_group([NeuronManualActivator()], target_activation_neurons)[0]

        if target_recording_neuron_groups is None:
            target_recording_neuron_groups = self.network.NeuronGroups

        activity_trace = []
        pattern_ids = []

        pattern_steps = []

        pgp=pattern_group.patterns
        if len(pattern_group.patterns) == 0:
            pgp=[pattern_group.get_pattern() for _ in range(100)]

        for _ in range(pattern_repeat):

            for i in range(len(pgp)):

                if combinations:
                    for i2 in range(len(pgp)):
                        pattern_steps.append([i, i2])
                else:
                    pattern_steps.append([i])

        if shuffle:
            random.shuffle(pattern_steps)

        pattern_steps += [-1 for _ in range(max_gamma_cycles_for_pattern)]

        for i in pattern_steps:
            if i != -1:
                id=''
                for p in i:
                    pattern = pgp[p]
                    man_act.activate(pattern)
                    id+='{}'.format(pattern)

                pattern_ids.append(id)
            #else:
            #    pattern_ids.append('[]')

            self.network.simulate_iteration()

            activation_step = []
            for neuron_group in target_recording_neuron_groups:
                activation_step.append(neuron_group.activity.copy())#.output_activity_history[0].copy())
            activity_trace.append(np.array(activation_step).flatten())


        for ng in self.network.NeuronGroups:
            ng.learning = True

        for be in activators:
            be.active = activators[be]

        return np.array(activity_trace), np.array(pattern_ids)


    def get_random_network_responses(self, iterations, neuron_groups=None, PatternGroups=None):
        activity_trace = []
        pattern_ids = []

        if neuron_groups is None:
            neuron_groups = self.network.NeuronGroups

        for ng in neuron_groups: ng.learning = False
        for pg in PatternGroups:
            pg.individual_possibility = 0.0
            pg.group_possibility = 1.0
        #LGN_PC_Neurons[TRENNeuronActivator].TNAPatterns[0].individual_possibility = 0.0
        #LGN_PC_Neurons[TRENNeuronActivator].TNAPatterns[0].group_possibility = 1.0

        for i in range(iterations):
            self.network.simulate_iteration()

            activation_step = []
            for neuron_group in neuron_groups:
                activation_step.append(neuron_group.activity.copy())#.output_activity_history[0].copy())
            activity_trace.append(np.array(activation_step).flatten())

            if PatternGroups is not None:
                pattern_step = ""
                for patter_group in PatternGroups:
                    pattern_step += "{}".format(patter_group.current_pattern_index)
                pattern_ids.append(pattern_step)

        for ng in neuron_groups: ng.learning = True
        #for pg in PatternGroups:
        #    pg.individual_possibility = 0.0
        #    pg.group_possibility = 1.0

        return np.array(activity_trace), np.array(pattern_ids)


    def single_reconstruction(self, dest_group, synapse_weight_attribute_name, reconstruction_steps, individual_norm=False, print_status=False):
        timestep_reconstructions = []

        for step in range(reconstruction_steps):
            if print_status:
                print('reconstruction', step)

            for neurons in self.network.NeuronGroups:
                neurons.reconstruction_act_temp *= 0

            for syn in self.network.SynapseGroups:
                if hasattr(syn, synapse_weight_attribute_name):
                    syn.src.reconstruction_act_temp += np.dot(getattr(syn, synapse_weight_attribute_name).transpose(),
                                                              syn.dst.reconstruction_act)  # [][syn.dst.mask]

            for neurons in self.network.NeuronGroups:
                neurons.reconstruction_act = neurons.reconstruction_act_temp.copy()  # +=

            timestep_reconstructions.append(dest_group.reconstruction_act.copy())

        timestep_reconstructions = np.array(timestep_reconstructions)
        if individual_norm:
            timestep_reconstructions /= np.max(timestep_reconstructions)

        return timestep_reconstructions


    def get_network_activity_reconstruction(self, dest_group, synapse_weight_attribute_name, recostruction_steps, individual_norm=False, print_status=False, active_groups=None):

        for neurons in self.network.NeuronGroups:
            neurons.reconstruction_act = neurons.output_activity_history[0].copy()
            if active_groups is not None and not neurons in active_groups:
                neurons.reconstruction_act *= 0
            neurons.reconstruction_act_temp = np.zeros(neurons.size)

        return self.single_reconstruction(dest_group, synapse_weight_attribute_name, recostruction_steps, individual_norm, print_status=False)


    def get_reconstruction(self, source_group, source_group_neuron_indexes, dest_group, synapse_weight_attribute_name, recostruction_steps, individual_norm=False, print_status=False, single_timestep=True):

        if source_group_neuron_indexes is None:
            source_group_neuron_indexes = list(range(source_group.size))

        for neurons in self.network.NeuronGroups:
            neurons.reconstruction_act = np.zeros(neurons.size)
            neurons.reconstruction_act_temp = np.zeros(neurons.size)

        result = []

        for neuron_index in source_group_neuron_indexes:
            if print_status:
                print('neuron', neuron_index, 'reconstruction')

            for neurons in self.network.NeuronGroups:
                neurons.reconstruction_act *= 0

            source_group.reconstruction_act[neuron_index] = 1

            timestep_reconstructions = self.single_reconstruction(dest_group, synapse_weight_attribute_name, recostruction_steps, individual_norm, print_status=False)

            if single_timestep:
                result.append(np.sum(timestep_reconstructions, axis=0))
            else:
                result.append(timestep_reconstructions)

        result = np.array(result)

        #if individual_norm:#todo test
        #    result = result / np.max(result, axis=1)[:, None]

        return np.array(result)

    def contains_with_gap(self, string, substring, gapchar='|'):
        result = 0
        text = []
        for s in range(len(string) - len(substring)):
            match = True
            for ss in range(len(substring)):
                if string[s + ss] != substring[ss] and (substring[ss] != gapchar):
                    match = False
            if match:
                result += 1
                if len(substring)>1:#exclude default characters
                    text.append(string[s - 5:s + len(substring) + 5])
        #print(set(text))
        return result, np.unique(text)#list(set(text))






    def ng_list(self, ng_list_or_name):
        if ng_list_or_name is None:
            return []
        elif type(ng_list_or_name)==list:
            return ng_list_or_name
        elif ng_list_or_name=='all':
            return self.network.NeuronGroups
        else:
            return self.network.getNG(ng_list_or_name)



    def zero_recon(self):
        for ng in self.network.NeuronGroups:
            ng.recon = ng.get_neuron_vec()


    #propagation variables:
    #- ng.recon             (needs to be set before call)
    #- ng.recon_temp        (temporal var)
    #- ng.layer_recon       (optional)
    #- ng.temporal_recon    (optional)

    #weight_attribute_name  name of synapse attribute
    #recon_steps            (steps of recon)

    #propagation_mode:
        # forward
        # backward

    #compute_layers: Bool   (written into ng.layer)
    #clip_min               (min recon values)
    #clip_max               (max recon values)

    #accumulation_mode:
        # addititve         recon+=new_recon
        # first_touch       recon=new_recon if recon==0
        # forget            recon=new_recon

    #synapse_filter:
        # 'all'             all
        # 'biggest'         biggest
        # [float]           syn >= max_syn*[float]

    #temporal_recon_groups  (optional)
        #[]                 disabled
        #[ng1,ng2,...]      temporal recon for ng1 and ng2

    #layer_compute_groups  (optional)
        #[]                 disabled
        #[ng1,ng2,...]      layer computation for ng1 and ng2

    #todo inhibitory and excitatory synapses
    #todo activation function (default:f(x)=x)



    def propagation(self, weight_attribute_name,  recon_steps, propagation_mode='forward', accumulation_mode='addititve', synapse_filter='all', clip_min=None, clip_max=None, temporal_recon_groups=[], layer_compute_groups=[], exponent=None, normalize=None, filter_weakest_percent=None):

        for ng in self.ng_list(layer_compute_groups):
            ng.layer_recon = ng.get_neuron_vec()+np.inf

        for ng in self.ng_list(temporal_recon_groups):
            ng.temporal_recon = []

        for step in range(recon_steps):

            for ng in self.network.NeuronGroups:
                ng.recon_temp = ng.get_neuron_vec()


            if propagation_mode == 'simulation':#todo implement
                for ng in self.network.NeuronGroups:#feed in
                    ng.activity = ng.recon.copy()
                self.network.learning_off()
                self.network.simulate_iteration()#simulate
                self.network.learning_on()
                for ng in self.network.NeuronGroups:#read out
                    ng.recon_temp = ng.activity
            else:
                for syn in self.network.SynapseGroups:
                    if hasattr(syn, weight_attribute_name) and 'GLU' in syn.tags:

                        w = getattr(syn, weight_attribute_name)
                        if type(w) == sp.csc.csc_matrix:
                            w = np.array(w.todense())

                        if synapse_filter == 'all':
                            w_mul = True
                        if synapse_filter == 'biggest':
                            # w_mul=w==w.max(axis=1)
                            w_mul = np.equal(w, np.tile(w.max(axis=1), (w.shape[1], 1)).transpose())  # better way!!!
                        if type(synapse_filter) == float:
                            # w_mul = w >= (w.max(axis=1)*synapse_filter)
                            w_mul = np.greater(w, np.tile(w.max(axis=1) * synapse_filter, (w.shape[1], 1)))

                        if propagation_mode == 'backward':
                            syn.src.recon_temp += (w * w_mul).transpose().dot(syn.dst.recon)  # disabled???

                        if propagation_mode == 'forward':
                            syn.dst.recon_temp += (w * w_mul).dot(syn.src.recon)  # disabled???

            if exponent is not None:
                syn.dst.recon_temp = np.power(syn.dst.recon_temp, exponent)

            if filter_weakest_percent is not None:
                recon_min = np.min(syn.dst.recon_temp)
                recon_max = np.max(syn.dst.recon_temp)
                syn.dst.recon_temp *= syn.dst.recon_temp>=(recon_min+(recon_max-recon_min)/100.0*filter_weakest_percent)

            if normalize is not None:
                s=np.sum(np.abs(syn.dst.recon_temp))
                if s>0:
                    syn.dst.recon_temp/=s




            for ng in self.ng_list(layer_compute_groups):
                ng.layer_recon[(ng.recon_temp != 0) * (ng.layer_recon == np.inf)] = step + 1

            for ng in self.network.NeuronGroups:

                if accumulation_mode == 'additive':
                    ng.recon += ng.recon_temp#.copy()??? not neccessary because of ng.get_neuron_vec() ?

                if accumulation_mode == 'first_touch':
                    ng.recon += ng.recon_temp*(ng.recon==0)

                if accumulation_mode == 'forget':
                    ng.recon = ng.recon_temp

                if clip_min is not None or clip_max is not None:
                    ng.recon = np.clip(ng.recon, clip_min, clip_max)



            for ng in self.ng_list(temporal_recon_groups):
                ng.temporal_recon.append(ng.recon.copy())





    #dict([(char,source.char_index_to_one_hot()) for char in range(source.A)])
    def label_and_group_neurons(self, label_ng, label_vectors, weight_attribute_name, steps):

        for ng in self.network.NeuronGroups:
            ng.class_label = []
            ng.temporal_layer = ng.get_neuron_vec()+np.inf


        for label_vec in label_vectors:
            self.zero_recon()
            label_ng.recon = label_vec.copy()

            label_ng.temporal_layer[label_vec != 0] = 0 #set first layer

            self.propagation(recon_steps=steps, propagation_mode='forward', accumulation_mode='first_touch', synapse_filter='biggest', clip_min=None, clip_max=None, temporal_recon_groups=[], layer_compute_groups='all', weight_attribute_name=weight_attribute_name)

            for ng in self.network.NeuronGroups:
                ng.class_label.append(ng.recon.copy())
                ng.temporal_layer = np.minimum(ng.temporal_layer, ng.layer_recon)

        for ng in self.network.NeuronGroups:
            ng.class_label = np.argmax(np.array(ng.class_label), axis=0)


    def synapse_iterate(self, func, x_attribute_name, y_attribute_name, weight_attribute_name, groups='all', weight_limit=1, include_fist_layer=False, n_biggest=None):

        #inf!!!

        for syn in self.network.SynapseGroups:
            if syn.src in self.ng_list(groups) and syn.dst in self.ng_list(groups):

                sg_indx = self.ng_list(groups).index(syn.src)
                dg_indx = self.ng_list(groups).index(syn.dst)

                #if group_shift:
                #    d_ng_y = self.ng_list(groups).index(syn.dst) * ng.size#* h * max_class_label * group_shift
                #    s_ng_y = self.ng_list(groups).index(syn.src) * ng.size#* h * max_class_label * group_shift
                #else:
                #    d_ng_y = 0
                #    s_ng_y = 0

                W = getattr(syn, weight_attribute_name)
                if type(W) == sp.csc.csc_matrix:
                    W = np.array(W.todense())
                w_global_max = np.max(W)

                src_x = getattr(syn.src, x_attribute_name)
                src_y = getattr(syn.src, y_attribute_name)
                dst_x = getattr(syn.dst, x_attribute_name)
                dst_y = getattr(syn.dst, y_attribute_name)
                for d in range(syn.dst.size):
                    print('\r', d, '/', syn.dst.size, end='')
                    wmax = np.max(W[d])
                    sorted_w = W[d].copy()
                    sorted_w.sort()
                    if wmax != 0:
                        for s in range(syn.src.size):
                            w = W[d, s]
                            if w != 0 and (dst_x[d] != 0 or include_fist_layer) and (weight_limit is None or w >= wmax * weight_limit) and (n_biggest is None or w==sorted_w[-n_biggest]):# and w >= wmax * weight_limit:# and w==wmax:# and w > wmax * 0.3333: #and w==wmax
                                func(s, src_x[s], src_y[s], d, dst_x[d], dst_y[d], w, sorted_w, w_global_max, sg_indx, dg_indx)



    #def multiple_timescale_layer_adjustment(self, groups='all'):

    #    for ng in self.ng_list(groups):

    #        if

    #def label

    def visualize_label_and_group_neurons(self, x_attribute_name, y_attribute_name, weight_attribute_name, groups='all', weight_limit=0.3333, group_shift=0, source=None, include_fist_layer=False, n_biggest=None, return_graph=False):
        max_layers = int(np.max([np.max(ng.temporal_layer[ng.temporal_layer!=np.inf]) for ng in self.ng_list(groups)]))
        max_class_label = int(np.max([np.max(ng.class_label) for ng in self.ng_list(groups)]))

        for ng in self.ng_list(groups):
            ng.i = np.arange(ng.size)

        h = np.sum([ng.size for ng in self.ng_list(groups)])

        #plt.xlim(left=-1)
        plt.axhline(0, color='gray')
        for char in range(max_class_label+1):#*len(self.ng_list(groups))
            plt.axhline(h * (char + 1), color='gray')
            if source is not None:
                c = ''# source.corpus[0:100000].count(source.index_to_symbol(char))
                plt.text(max_layers, h * char + 25, '\'{}\'{}'.format(source.index_to_char(char), c))

        result_neurons = []
        result_synapses = []

        #draw synapses
        def loop_func(s, sx, sy, d, dx, dy, w, sorted_w, w_global_max, sg_indx, dg_indx):
            if sx != np.inf and dx != np.inf:
                w_norm = w / w_global_max  # wmax
                if sy == dy:
                    color = [0, 1, 0, w_norm]
                else:

                    if sx < dx:  # forward =>black
                        color = [0, 0, 0, w_norm]
                    else:  # backward or sideways =>red
                        color = [1, 0, 0, w_norm]
                        # color[2] = 1
                        # color[3] = w_norm# * 0.1

                if return_graph:
                    result_synapses.append([s, d])
                else:
                    plt.plot([dx, sx], [d + h * dy + dg_indx, s + h * sy + sg_indx], '-k', color=color)

        self.synapse_iterate(loop_func, x_attribute_name=x_attribute_name, y_attribute_name=y_attribute_name, weight_attribute_name=weight_attribute_name, groups=groups, weight_limit=weight_limit, include_fist_layer=include_fist_layer, n_biggest=n_biggest)

        #draw_neurons
        for ng in self.ng_list(groups):#todo group neuron_groups or filter
            ng_y = self.ng_list(groups).index(ng) * ng.size#* h * max_class_label * group_shift
            x_positions = getattr(ng, x_attribute_name)
            y_positions = getattr(ng, y_attribute_name)
            for x in np.unique(x_positions):#range(max_layers+1)
                ng_color = 'black'
                if hasattr(ng, 'color'):
                    ng_color = ng.color

                lmask = x_positions == x
                if x==np.inf:
                    ng_color = 'red'
                    x=-1
                if return_graph:
                    for i,l in enumerate(lmask):
                        if l:
                            result_neurons.append([x, np.arange(ng.size)[i] + h * y_positions[i]+ ng_y])
                else:
                    plt.plot(np.ones(np.sum(lmask)) * x, np.arange(ng.size)[lmask] + h * y_positions[lmask]+ ng_y, 'ok', ms=3, color=ng_color)


        if return_graph:
            return result_neurons, result_synapses
        else:
            plt.show()

    def get_neuron_positions(self, ng, x_attribute_name, y_attribute_name, y_scale=1.0):
        x_positions = np.array(getattr(ng, x_attribute_name))
        y_positions = np.array(getattr(ng, y_attribute_name))
        size=len(x_positions)
        return np.array(list(zip(x_positions+np.random.rand(size)*0.5-0.25, y_positions+np.random.rand(size)*0.5-0.25)))#(np.arange(ng.size)+np.arange(ng.size)*y_positions)*y_scale



    def get_all_buffer_length_distribution(self, groups):
        max_class_label = int(np.max([np.max(ng.class_label) for ng in self.ng_list(groups)]))
        max_temporal_layer = int(np.max([np.max(ng.temporal_layer[ng.temporal_layer!=np.inf]) for ng in self.ng_list(groups)]))

        max_label_buffers = []
        label_buffer_length_distribution=[]
        for label in range(max_class_label):

            buffer_elements=[]
            for ng in [self.network.NeuronGroups[0]]:
                buffer_elements+=list(ng.temporal_layer[(ng.class_label==label) * (ng.temporal_layer!=np.inf)])

            max_buffer_length=np.max(buffer_elements)

            max_label_buffers.append(max_buffer_length)

            buffer_length_distribution=[]
            for l in range(max_temporal_layer+1):#range(int(max_buffer_length+1)):
                occurences=buffer_elements.count(l)
                buffer_length_distribution.append(occurences)

            label_buffer_length_distribution.append(buffer_length_distribution)

        average_max=np.average(max_label_buffers)
        return max_label_buffers, label_buffer_length_distribution, average_max


    def get_synapse_transition_dict(self, source, x_attribute_name, y_attribute_name, weight_attribute_name, groups='all', weight_limit=0.3333, include_fist_layer=False, n_biggest=None):

        #forward_same = 0
        #forward_different = 0
        #backward = 0
        transitions = {}

        def inc(key):
            if not key in transitions:
                transitions[key] = 1
            else:
                transitions[key] += 1

        def loop_func(s, sx, sy, d, dx, dy, w, sorted_w, w_global_max, sg_indx, dg_indx):
            #if sy == dy:
            #    inc('forward_same')
            #else:
            #    inc('forward_different')
            #if sx >= dx:
            #    inc('backward')'

            ss = source.index_to_char(int(sy))
            ds = source.index_to_char(int(dy))

            key = 'UNKNOWN'

            if dx != np.inf and sx != np.inf:

                dist = int(dx - sx)

                if dist > 1:
                    key = ss + ''.join(['-' for _ in range(dist - 2)]) + ds

                if dist <= 0:
                    key = ss + ''.join(['|' for _ in range(-dist)]) + ds

                if ss == ds:  # buffer
                    if dist > 0:
                        key = ss  # dist does not matter
            # if len(key) == 2:
            #    print(key)
            inc(key)

        self.synapse_iterate(loop_func, x_attribute_name=x_attribute_name, y_attribute_name=y_attribute_name, weight_attribute_name=weight_attribute_name, groups=groups, weight_limit=weight_limit, include_fist_layer=include_fist_layer, n_biggest=n_biggest)
        return transitions

    def get_transition_frequencies(self, transitions, source):
        frequency_dict = {}
        occurence_dict = {}
        filtered_transitions = {}
        for key in transitions:
            found, occurences = self.contains_with_gap(source.corpus, key, gapchar='|')
            frequency_dict[key] = found
            occurence_dict[key] = occurences
            if found > 0:
                filtered_transitions[key] = transitions[key]

        return frequency_dict, occurence_dict, filtered_transitions


    def plot_trend_line(self, x, y):
        plt.plot(x, np.poly1d(np.polyfit(x, y, 1))(x))

        fit = np.polyfit(x, y, 1, cov=True)  # linear

        unc = np.sqrt(np.diag(fit[1]))

        slope = fit[0][0]
        intercept = fit[0][1]
        slopes = np.linspace(slope - unc[0], slope + unc[0], 20)  # take 20 slopes in unc range
        intercepts = np.linspace(intercept - unc[1], intercept + unc[1], 20)  # take 20 intercepts in unc range

        line_array = []
        for i in range(len(slopes)):
            line_array.append(x * slopes[i] + intercepts[i])
        line_array = np.array(line_array)
        lower_edge = np.min(line_array, axis=0)
        upper_edge = np.max(line_array, axis=0)

        # slopes = np.linspace(slope - unc[0], slope + unc[0], 20)  # take 20 slopes in unc range
        # intercepts = np.linspace(intercept - unc[1], intercept + unc[1], 20)
        plt.fill_between(x, lower_edge, upper_edge, color='gray', alpha=0.4)


    def plot_transition_frequencies(self, transitions, frequencies, plot_single=False, plot_multiple=True, show_labels=True):

        txt = []
        x = []
        y = []
        for key in transitions:
            if key != 'UNKNOWN' and ((plot_single and len(key)==1) or (plot_multiple and len(key)>1)):
                txt.append(key)
                x.append(transitions[key])
                y.append(frequencies[key])
        plt.scatter(x, y)

        if show_labels:
            for txt,xv,yv in zip(txt,x,y):
                plt.annotate(txt.replace(' ','_'), (xv, yv))

        return np.array(x).astype(def_dtype), np.array(y).astype(def_dtype)

    def get_transition_classes(self, transitions, frequencies):

        buffer = 0
        useful = 0
        useless = 0

        for key in transitions:
            if len(key) == 1:
                buffer += transitions[key]
            elif frequencies[key]>0:
                useful += transitions[key]
            else:
                useless += transitions[key]
            #unknown automatically counted to useless

        return {'BUFFER': buffer, 'USEFUL': useful, 'USELESS': useless}

        # print('useful:', useful_conn, 'forward_same', forward_same, 'forward_different', forward_different, 'backward', backward)

    def plot_bars(self, transitions):
        key_l = []
        value_l = []
        for key, value in sorted(transitions.items(), key=lambda item: item[1]):
            key_l.append(key)
            value_l.append(value)

        rects = plt.bar(np.arange(len(key_l)) * 10 - 4, value_l, width=8)
        for rect, label in zip(rects, key_l):
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height, label.replace(' ', '_'), ha='center', va='bottom')
