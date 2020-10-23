from NetworkBehaviour.Input.Activator import *


##########################################################################
#Helper functions
##########################################################################
def modular_activation_function(neurons):
    result = neurons.activity.copy()

    if hasattr(neurons, 'rnd_act_factor') and neurons.rnd_act_factor is not None:
        result += neurons.rnd_act_factor * np.random.rand(neurons.size)

    if hasattr(neurons, 'nox') and neurons.nox is not None:
        result -= neurons.nox

    if hasattr(neurons, 'refractory_counter_analog') and neurons.refractory_counter_analog is not None:
        result -= neurons.refractory_counter_analog

    if hasattr(neurons, 'TH') and neurons.TH is not None:
        result -= neurons.TH

    if hasattr(neurons, 'digital_output') and neurons.digital_output:
        result = (result >= 0.0).astype(np.float64)

    if hasattr(neurons, 'refractory_counter_digital') and neurons.refractory_counter_digital is not None:
        result *= (neurons.refractory_counter_digital < neurons.refractory_counter_threshold)

    return result

def last_cycle_step(neurons):
    return neurons.iteration % neurons.timescale == neurons.timescale-1

def first_cycle_step(neurons):
    return neurons.iteration % neurons.timescale == 0



##########################################################################
#Init synapses
##########################################################################
class SORN_init_afferent_synapses(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('init_afferent_synapses')

        #add synapsegroup.group_weighting attribute to change its weight compared to synapsegroups of same kind

        self.transmitter = self.get_init_attr('transmitter', None, neurons)

        density = self.get_init_attr('density', None, neurons)
        if type(density)==str and density[-1] == '%':
            density=float(density[:-1])/100

        density_mode = self.get_init_attr('density_mode', 'auto', neurons)

        self.distribution = self.get_init_attr('distribution', 'random_sample(dim)', neurons, do_not_diversify=True)

        if self.distribution is not None and ';plot' in self.distribution:
            import matplotlib.pyplot as plt
            self.distribution = self.distribution.replace(';plot', '')
            plt.hist(eval(self.distribution.replace(')', ',size=1000)')), bins=100)
            plt.show()

        partition_compensation = self.get_init_attr('partition_compensation', False, neurons)

        # np.random. ...
        #lognormal([mean, sigma, size])
        #normal([loc, scale, size])
        #random_sample(dim)
        #https://docs.scipy.org/doc/numpy-1.13.0/reference/routines.random.html


        if density == 'full':
            density_mode = 'full'
            density = 1

        if density_mode == 'auto':
            if np.min(density) < 1: #min because of array possibility
                density_mode = 'chance'
            else:
                density_mode = 'syn_count'


        if density_mode == 'full':
            density = 1
        elif density_mode == 'chance':
            density = density
        elif density_mode == 'syn_count':
            base_density = density#...
        elif density_mode == 'fixed_syn_count':
            density = -1
            #todo:implement (difficult with s.enabled...)
            #s.get_random_synapse_mat_fixed(syn_lamb)
        else:
            print('invalid density mode')

        self.group_weighting = self.get_init_attr('group_weighting', False, neurons)#each group can be weighted individually with a unique parameter (s.group_weighting)

        for s in neurons.afferent_synapses[self.transmitter]:
            if self.group_weighting == False:
                weighting = 1
            else:
                weighting = s.get_synapse_group_size_factor(s, self.transmitter)#todo test

            if partition_compensation:
                weighting *= s.src.group_without_subGroup().size/s.src.size

            if density_mode == 'syn_count':
               density = base_density/s.src.size

            if self.distribution is not None:
                s.W = s.get_random_synapse_mat(density=float(density*weighting), rnd_code=self.distribution)#density*weighting
            else:
                s.W = (s.get_synapse_mat()+1)*s.enabled #all same

            s.enabled *= (s.W > 0)

            s.slow_add=0
            s.fast_add=0

        self.normalize = self.get_init_attr('normalize', True, neurons)# can be number or bool
        if self.normalize is not None and self.normalize is not False:
            if self.normalize==True:
                self.normalize=1.0
            self.normalize_synapse_attr('W', 'W', self.normalize, neurons, self.transmitter)

        #for s in neurons.afferent_synapses[self.transmitter]:
        #    plt.hist(s.W.flatten()[s.W.flatten()>0],bins=100)
        #    plt.show()


    def new_iteration(self, neurons):
        return


class SORN_temporal_synapses(Behaviour):
    def set_variables(self, neurons):
        self.add_tag('temporal_synapses')

        self.syn_type = self.get_init_attr('syn_type', 1)
        self.shift_factor = self.get_init_attr('shift_factor', 0.1)
        self.shift_loss_factor = self.get_init_attr('shift_loss_factor', 0.5)

        for s in neurons.afferent_synapses[self.syn_type]:
            s.W_stable = s.W.copy()
            s.W_temp = s.get_synapse_mat()

        self.behaviour_norm_factor = self.get_init_attr('behaviour_norm_factor', 1.0, neurons)
        neurons.weight_norm_factor = neurons.get_neuron_vec()+self.get_init_attr('neuron_norm_factor', 1.0, neurons)

    def new_iteration(self, neurons):

        if last_cycle_step(neurons):
            for s in neurons.afferent_synapses[self.syn_type]:
                #s.W_temp += (s.get_synapse_mat()+0.15)*(s.get_random_synapse_mat()>0.99)
                s.W = s.W_stable + s.W_temp
                s.W[s.W < 0.0] = 0.0

            self.normalize_synapse_attr('W', 'W_temp', neurons.weight_norm_factor * self.behaviour_norm_factor, neurons, self.syn_type)
            self.normalize_synapse_attr('W', 'W_stable', neurons.weight_norm_factor * self.behaviour_norm_factor, neurons, self.syn_type)

            for s in neurons.afferent_synapses[self.syn_type]:
                shift = s.W_temp * self.shift_factor
                s.W_temp -= shift
                s.W_stable += shift*self.shift_loss_factor



class SORN_dopamine(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('temporal_synapses')

        self.temporal_synapse_tag = self.get_init_attr('temporal_synapse_tag', 'GLU')
        self.positive_dopamine_tag = self.get_init_attr('dopamine_tag', 'DOP+')
        self.negative_dopamine_tag = self.get_init_attr('dopamine_tag', 'DOP-')

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            if self.positive_dopamine_tag in neurons.afferent_synapses:
                positive_dopamine_level = np.mean([np.mean(s.src.output) for s in neurons.afferent_synapses[self.positive_dopamine_tag]])
                for s in neurons.afferent_synapses[self.temporal_synapse_tag]:
                    positive_w_shift = s.W_temp * positive_dopamine_level
                    s.W_temp -= positive_w_shift  # w_temp_gets_smaller (neccessary???)
                    s.W_stable += positive_w_shift #W_stable gets larger

            if self.negative_dopamine_tag in neurons.afferent_synapses:
                negative_dopamine_level = np.mean([np.mean(s.src.output) for s in neurons.afferent_synapses[self.negative_dopamine_tag]])
                for s in neurons.afferent_synapses[self.temporal_synapse_tag]:
                    negative_w_shift = s.W_temp * negative_dopamine_level
                    s.W_temp -= negative_w_shift  # w_temp_gets_smaller (neccessary???)
                    s.W_stable -= negative_w_shift #W_stable gets smaller



##########################################################################
#Init neurons
##########################################################################
class SORN_init_neuron_vars(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('init_neuron_vars')

        neurons.activity = neurons.get_neuron_vec()
        neurons.excitation = neurons.get_neuron_vec()
        neurons.inhibition = neurons.get_neuron_vec()
        neurons.input_act = neurons.get_neuron_vec()

        neurons.output = neurons.get_neuron_vec()

        #neurons.slow_act=neurons.get_neuron_vec()

        neurons.timescale = self.get_init_attr('timescale', 1)

    def new_iteration(self, neurons):
        if first_cycle_step(neurons):
            neurons.activity.fill(0)# *= 0
            neurons.excitation.fill(0)# *= 0
            neurons.inhibition.fill(0)# *= 0
            neurons.input_act.fill(0)# *= 0

            neurons.output_old=neurons.output.copy()

        #neurons.buffer_timescale_sum_dict={}

            #neurons.slow_act *= 0


##########################################################################
#NOX
##########################################################################
class SORN_NOX(Instant_Homeostasis):

    def partition_sum(self, neurons):
        neurons._temp_act_sum = neurons.get_neuron_vec()
        for s in neurons.afferent_synapses['GLU']:
            s.dst._temp_act_sum += np.mean(s.src.output)
        return neurons._temp_act_sum

    def set_variables(self, neurons):
        self.add_tag('NOX')
        super().set_variables(neurons)
        neurons.nox = neurons.get_neuron_vec()
        self.measurement_param = self.get_init_attr('mp', 'self.partition_sum(n)', None)#'np.mean(n.output_new)'
        self.adjustment_param = 'nox'
        self.measure_group_sum = True

        self.set_threshold(self.get_init_attr('h_dh', 0, neurons))#'same(IPTI, th)'
        self.adj_strength = -self.get_init_attr('eta_nox', 0.002, neurons)

        self.distance_sensitive=True

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.nox.fill(0)# *= 0
            super().new_iteration(neurons)


##########################################################################
#Basic activity transission class
##########################################################################
class SORN_signal_propagation_base(Behaviour):

    def set_variables(self, neurons):
        self.transmitter = self.get_init_attr('transmitter', None, neurons)
        self.strength = self.get_init_attr('strength', 1, neurons)  # 1 or -1

        if self.transmitter==None:
            print('warning no transmitter defined')
        #elif self.transmitter is not 'GLU' and self.transmitter is not 'GABA':
        #    print('warning unknown transmitter')

        if self.transmitter=='GLU' and self.strength<0:
            print('warning glutamate strength is inhibitory')

        if self.transmitter=='GABA' and self.strength>0:
            print('warning GABA strength is excitatory')

    def new_iteration(self, neurons):
        print('warning: signal_propagation_base has to be overwritten')


##########################################################################
#External Input
##########################################################################
class SORN_external_input(NeuronActivator):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.strength = self.get_init_attr('strength', 1.0, neurons)
        neurons.input = np.zeros(neurons.size)
        self.write_to = 'input'
        neurons.add_tag('text_input_group')
        #pre_syn = neurons.connected_NG_param_list('afferent_buffer_requirement', same_NG=True, search_behaviours=True)
        neurons.input_buffer = neurons.get_neuron_vec_buffer(neurons.timescale)#pre_syn[0][0]


    def new_iteration(self, neurons):
        super().new_iteration(neurons)

        neurons.input_buffer = neurons.buffer_roll(neurons.input_buffer, neurons.input)

        if last_cycle_step(neurons) and self.strength != 0:
            add = np.sum(neurons.input_buffer[neurons.timescale-1:neurons.timescale*2-1], axis=0)/neurons.timescale * self.strength#neurons.input * self.strength / neurons.timescale
            neurons.activity += add
            neurons.input.fill(0)# *= 0
            neurons.input_act += add


##########################################################################
#Slow(normal) transmission
##########################################################################
class SORN_slow_syn(SORN_signal_propagation_base):

    def afferent_buffer_requirement(self, neurons):
        return buffer_reqirement(length=1, variable='output', timescale=neurons.timescale)
        #return 1, neurons.timescale#, 0

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('slow_' + self.transmitter)
        self.sparse_optimization = self.get_init_attr('so', False, neurons)

        self.pre_syn_groups = []
        for s in neurons.afferent_synapses[self.transmitter]:
            if s.src.BaseNeuronGroup not in self.pre_syn_groups:
                self.pre_syn_groups.append(s.src.BaseNeuronGroup)


    def new_iteration(self, neurons):
        if last_cycle_step(neurons) and self.strength != 0:

            for s in neurons.afferent_synapses[self.transmitter]:

                #mask = True
                #if hasattr(s.src, 'temporal_shift_mask'):
                #    mask = s.src.temporal_shift_mask == (s.src.iteration % s.src.timescale)

                #*mask
                s.slow_add = s.W.dot(get_buffer(s.src, 'output', neurons.timescale, 0)[0]) * self.strength

                s.dst.activity += s.slow_add
                if self.strength > 0:
                    s.dst.excitation += s.slow_add
                else:
                    s.dst.inhibition += s.slow_add


##########################################################################
#Fast(same clock cycle) transmission
##########################################################################
class SORN_fast_syn(SORN_signal_propagation_base):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('fast_' + self.transmitter)
        self.sparse_optimization = self.get_init_attr('so', False, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons) and self.strength!=0:
            for s in neurons.afferent_synapses[self.transmitter]:
                #if self.sparse_optimization:
                #    s.fast_add = (np.sum(s.W[:, s.src.activation_function(s.src).astype(np.bool)], axis=1) * self.strength) / neurons.timescale
                #    #add = (np.sum(s.W.transpose()[s.src.output.astype(np.bool)], axis=0) * self.strength) / neurons.timescale
                #else:

                mask = True
                if hasattr(s.src, 'temporal_shift_mask'):
                    mask = s.src.temporal_shift_mask == (s.src.iteration % s.src.timescale)

                s.fast_add = s.W.dot(s.src.activation_function(s.src) * mask) * self.strength# / neurons.timescale

                s.dst.activity += s.fast_add
                if self.strength > 0:
                    s.dst.excitation += s.fast_add
                else:
                    s.dst.inhibition += s.fast_add


##########################################################################
#Generate output with activation fucntion
##########################################################################
class SORN_generate_output(Behaviour):#has to be executed AFTER intra, inter...behaviours

    def set_variables(self, neurons):
        self.add_tag('generate output')

        neurons.output = neurons.get_neuron_vec()

        neurons.digital_output = self.get_init_attr('digital_output', True, neurons)

        neurons.activation_function = self.get_init_attr('activation_function', modular_activation_function, neurons)
        if not callable(neurons.activation_function):
            neurons.activation_function = eval(neurons.activation_function)

        neurons.TH = neurons.get_neuron_vec()+self.get_init_attr('init_TH', 0.0, neurons)#neurons.get_random_neuron_vec()*0.5

        neurons.rnd_act_factor = self.get_init_attr('rnd_act_factor', None, neurons)  # sigma

        #neurons.get_buffer = get_buffer

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.output = neurons.activation_function(neurons)


##########################################################################
#Buffer allocation and output production
##########################################################################
class buffer_reqirement:
    def __init__(self, length=-1, variable='', timescale=1, offset=0):
        self.length = length
        self.variable = variable
        self.timescale = timescale
        self.offset = offset

def get_buffer(neurons, variable, timescale=1, offset=0):
    return neurons.mask_var(neurons.buffers[variable][timescale][offset])

class SORN_buffer_variables(Behaviour):#has to be executed AFTER intra, inter...behaviours

    def set_variables(self, neurons):
        n=neurons#for compile...
        self.add_tag('buffer')
        neurons.get_buffer = get_buffer#just for simpler access

        post_syn_req = neurons.connected_NG_param_list('afferent_buffer_requirement', syn_tag='All', efferent_NGs=True, search_behaviours=True)
        own_req = neurons.connected_NG_param_list('own_buffer_requirement', same_NG=True, search_behaviours=True)
        pre_syn_req = neurons.connected_NG_param_list('efferent_buffer_requirement', syn_tag='All', afferent_NGs=True, search_behaviours=True)
        all_requirments = post_syn_req+own_req+pre_syn_req

        variable_key = np.unique([vr.variable+'_'+str(vr.timescale)+'_'+str(vr.offset) for vr in all_requirments]) #remove timescale

        neurons.precompiled_vars = {}
        neurons.buffers = {}

        def add_buffer(variable, timescale, offset, length):#create dict(offset) in a dict(timescale) in a dict(variable)...
            #print(n.tags, variable, timescale, offset, length)

            if '.' in variable or '(' in variable:
                neurons.precompiled_vars[variable] = compile(variable, '<string>', 'eval')

            if variable not in neurons.buffers:
                neurons.buffers[variable] = {}
            if timescale not in neurons.buffers[variable]:
                neurons.buffers[variable][timescale] = {}

            current = None
            if offset in neurons.buffers[variable][timescale]:#buffer already exists:
                current=len(neurons.buffers[variable][timescale][offset])

            if current==None or length>current:
                neurons.buffers[variable][timescale][offset]=neurons.get_neuron_vec_buffer(length)

        for var_key in variable_key:
            split_key=var_key.split('_')
            variable = split_key[0]
            timescale = int(split_key[1])
            offset = int(split_key[2])
            max_req_length = np.max([vr.length for vr in all_requirments if vr.variable == variable and vr.timescale == timescale and vr.offset == offset])
            add_buffer(variable, 1, 0, timescale)#??????
            add_buffer(variable, timescale, offset, max_req_length)


        ####################################################

        if self.get_init_attr('random_temporal_output_shift', True) and neurons.timescale > 1:
            neurons.temporal_shift_mask = np.random.randint(neurons.timescale, size=neurons.size)


    def new_iteration(self, neurons):
        n = neurons  # for compile...

        for variable in neurons.buffers:
            for timescale in neurons.buffers[variable]:
                if timescale == 1:
                    if variable in neurons.precompiled_vars:
                        new = eval(variable)
                    else:
                        new = getattr(neurons, variable)
                    neurons.buffer_roll(neurons.buffers[variable][1][0], new)

        for variable in neurons.buffers:
            for timescale in neurons.buffers[variable]:
                if timescale > 1:
                    for offset in neurons.buffers[variable][timescale]:
                        if neurons.iteration % timescale == timescale - 1 - offset:
                            if timescale <= neurons.timescale:
                                new = neurons.buffers[variable][1][0][0]#previously saved value
                                if hasattr(neurons, 'temporal_shift_mask'):
                                    new *= neurons.temporal_shift_mask == (neurons.iteration % neurons.timescale)
                            else:
                               new = np.mean(neurons.buffers[variable][1][0][0:timescale], axis=0)#sum of previously saved value

                            neurons.buffer_roll(neurons.buffers[variable][timescale][offset], new)

                            #if variable in neurons.precompiled_vars:
                            #    new = eval(variable)
                            #else:
                            #    new = getattr(neurons, variable)




        '''
        for variable in neurons.buffers:
            for timescale in neurons.buffers[variable]:
                if timescale == 1:
                    if variable in neurons.precompiled_vars:
                        new = eval(variable)
                    else:
                        new = getattr(neurons, variable)
                    neurons.buffer_roll(neurons.buffers[variable][1][0], new)

        for variable in neurons.buffers:
            for timescale in neurons.buffers[variable]:
                if timescale > 1:
                    for offset in neurons.buffers[variable][timescale]:
                        if neurons.iteration % timescale == timescale - 1 - offset:
                            data = np.mean(neurons.buffers[variable][1][offset][0:timescale], axis=0)
                            neurons.buffer_roll(neurons.buffers[variable][timescale][offset], data)
        '''

class SORN_STDP_simple(Behaviour):
    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('SORN_IP_WTA_apply')
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.00015, neurons)
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses[self.syn_type]:
            pre_post = s.dst.output[:, None] * s.src.output_old[None, :]
            simu = s.dst.output[:, None] * s.src.output[None, :]
            post_pre = s.dst.output_old[:, None] * s.src.output[None, :]

            dw = neurons.eta_stdp * (pre_post - post_pre +simu)

            # dw = neurons.eta_stdp * (pre_post - post_pre + simu)

            # dw = neurons.eta_stdp * (to_new[:, None] * from_old[None, :] - to_old[:, None] * from_new[None, :])

            s.W=np.clip(s.W + dw * s.enabled, 0.0, 1.0)

class SORN_STDP(Behaviour):

    def get_STDP_Function(self):
        return self.get_init_attr('STDP_F', {-1: 1, 1: -1})

    def afferent_buffer_requirement(self, neurons):
        self.STDP_F = self.get_STDP_Function()
        self.data = np.array([[t, s] for t, s in self.STDP_F.items()])
        length = int(np.maximum(np.max(self.data[:, 0]), 1)+1)
        #print('aff', length, self.get_init_attr('STDP_F', {-1: 1, 1: -1}))
        return buffer_reqirement(length=length, variable='output', timescale=neurons.timescale)
        #return int(np.maximum(np.min(self.data[:, 0])*-1, 1)+1), neurons.timescale#, 0

    def own_buffer_requirement(self, neurons):
        self.STDP_F = self.get_STDP_Function()
        self.data = np.array([[t, s] for t, s in self.STDP_F.items()])
        length = int(np.maximum(np.min(self.data[:, 0])*-1, 1)+1)
        #print('own',length, self.get_init_attr('STDP_F', {-1: 1, 1: -1}))
        return buffer_reqirement(length=length, variable='output', timescale=neurons.timescale)
        #return int(np.maximum(np.max(self.data[:, 0]), 1)+1), neurons.timescale#, 0

    def set_variables(self, neurons):
        self.add_tag('STDP')

        self.weight_attr = self.get_init_attr('weight_attr', 'W', neurons)

        self.STDP_F = self.get_STDP_Function()# left(negative t):pre->post right(positive t):post->pre

        self.pre_post_mask = np.array([t in self.STDP_F for t in range(self.afferent_buffer_requirement(neurons).length)])
        self.pre_post_mul = np.array([self.STDP_F[t] for t in range(self.afferent_buffer_requirement(neurons).length) if t in self.STDP_F])

        self.post_pre_mask = np.array([-t in self.STDP_F for t in range(self.own_buffer_requirement(neurons).length)])
        self.post_pre_mul = np.array([self.STDP_F[-t] for t in range(self.own_buffer_requirement(neurons).length) if -t in self.STDP_F])

        self.transmitter = self.get_init_attr('transmitter', 'GLU', neurons)

        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)
        neurons.last_output = neurons.get_neuron_vec()
        for s in neurons.afferent_synapses[self.transmitter]:
            s.src_act_sum_old = np.zeros(s.src.size)

        if self.get_init_attr('plot', False):
            import matplotlib.pyplot as plt
            self.data = np.array([[x, y] for x, y in self.STDP_F.items()])
            plt.bar(self.data[:, 0], self.data[:, 1], 1.0)
            plt.axhline(0, color='black')
            plt.axvline(0, color='black')
            plt.show()

    def new_iteration(self, neurons):
        #if first_cycle_step(neurons):#first????????????????????????????????????????????????????????????????????????
        if last_cycle_step(neurons):

            for s in neurons.afferent_synapses[self.transmitter]:

                post_act = get_buffer(s.dst, 'output', neurons.timescale)#s.dst.get_masked_dict('output_buffer_dict', neurons.timescale)
                pre_act = get_buffer(s.src, 'output', neurons.timescale)#s.src.get_masked_dict('output_buffer_dict', neurons.timescale)

                if not hasattr(s, 'pre_post_mask'):
                    s.pre_post_mask = self.pre_post_mask.copy()
                    if len(post_act) > len(s.pre_post_mask):
                        s.pre_post_mask = np.concatenate([s.pre_post_mask, np.array([False for _ in range(len(post_act) - len(s.pre_post_mask))])])

                if not hasattr(s, 'post_pre_mask'):
                    s.post_pre_mask = self.post_pre_mask.copy()
                    if len(pre_act) > len(s.post_pre_mask):
                        s.post_pre_mask = np.concatenate([s.post_pre_mask, np.array([False for _ in range(len(pre_act) - len(s.post_pre_mask))])])

                summed_up_dact = np.sum(post_act[s.pre_post_mask]*self.pre_post_mul[:, None], axis=0)
                summed_up_sact = np.sum(pre_act[s.post_pre_mask]*self.post_pre_mul[:, None], axis=0)

                dw_pre_post = summed_up_dact[:, None] * pre_act[0][None, :]
                dw_post_pre = post_act[0][:, None] * summed_up_sact[None, :]

                s.dw = neurons.eta_stdp * (dw_pre_post+dw_post_pre) * s.enabled# * (neurons.timescale)

                setattr(s, self.weight_attr, getattr(s, self.weight_attr)+s.dw)

                #W = getattr(s, self.weight_attr)[:]
                #W += s.dw
                #W[W < 0.0] = 0.0


class SORN_Refractory_Digital(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory_D')
        neurons.refractory_counter_digital = neurons.get_neuron_vec()
        self.factor = self.get_init_attr('factor', 0.9, neurons)
        neurons.refractory_counter_threshold = self.get_init_attr('threshold', 0.1, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.refractory_counter_digital *= self.factor
            neurons.refractory_counter_digital += neurons.output


class SORN_Refractory_Analog(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory_A')
        neurons.refractory_counter_analog = neurons.get_neuron_vec()
        self.factor = self.get_init_attr('factor', 0.9, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.refractory_counter_analog *= self.factor
            neurons.refractory_counter_analog += neurons.output


class SORN_SN(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('SN')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)

        neurons.require_synapses(self.syn_type, warning=False)#suppresses error when synapse group does not exist

        self.clip_min = self.get_init_attr('clip_min', None, neurons)
        self.clip_max = self.get_init_attr('clip_max', None, neurons)

        self.only_positive_synapses = self.get_init_attr('only_positive_synapses', True, neurons)
        if self.only_positive_synapses:
            self.clip_min = self.get_init_attr('clip_min', 0.0, neurons)

        self.behaviour_norm_factor = self.get_init_attr('behaviour_norm_factor', 1.0, neurons)
        neurons.weight_norm_factor = neurons.get_neuron_vec()+self.get_init_attr('neuron_norm_factor', 1.0, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            if self.only_positive_synapses:
                for s in neurons.afferent_synapses[self.syn_type]:
                    s.W[s.W < 0.0] = 0.0

            self.normalize_synapse_attr('W', 'W', neurons.weight_norm_factor*self.behaviour_norm_factor, neurons, self.syn_type)

            if self.clip_max is not None:
                for s in neurons.afferent_synapses[self.syn_type]:
                    s.W[s.W > self.clip_max] = self.clip_max

            if self.clip_min is not None:
                for s in neurons.afferent_synapses[self.syn_type]:
                    s.W[s.W < self.clip_min] = self.clip_min

                #s.W = np.clip(s.W, 0, self.clip_max)


class SORN_iSTDP(Behaviour):

    def afferent_buffer_requirement(self, neurons):
        return buffer_reqirement(length=1, variable='output', timescale=neurons.timescale)

    def own_buffer_requirement(self, neurons):
        return buffer_reqirement(length=1, variable='n.excitation+n.inhibition', timescale=neurons.timescale)

    def set_variables(self, neurons):
        self.add_tag('iSTDP')

        self.transmitter = self.get_init_attr('transmitter', 'GABA', neurons)

        neurons.eta_istdp = self.get_init_attr('eta_istdp', 0.001, neurons)
        neurons.h_ip = self.get_init_attr('h_ip', 0.1, neurons)

        #for s in neurons.afferent_synapses[self.transmitter]:
        #    s.iSTDP_src_lag_buffer = np.zeros(s.src.size)

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses[self.transmitter]:
            #s.iSTDP_src_lag_buffer += s.src.output/neurons.timescale
            if last_cycle_step(neurons):

                s.W += -s.dst.eta_istdp * ((1 - get_buffer(s.dst, 'n.excitation+n.inhibition', neurons.timescale, 0)[0] * (1 + 1.0 / s.dst.h_ip))[:, None] * get_buffer(s.src, 'output', neurons.timescale, 0)[0])#(s.dst.excitation+s.dst.inhibition)#s.iSTDP_src_lag_buffer[None, :]
                s.W = np.clip(s.W, 0.001, 1.0)*s.enabled

                #s.iSTDP_src_lag_buffer.fill(0)# *= 0

                #dW_same = -self.eta_istdp * ((1 - (s.dst.output[:, None] * (1 + 1.0 / self.h_ip))) * s.src.output[None, :])


class SORN_SC_TI(Time_Integration_Homeostasis):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('SCTI')
        self.measurement_param = self.get_init_attr('mp', 'n.excitation', neurons)
        self.adjustment_param = 'weight_norm_factor'

        self.set_threshold(self.get_init_attr('h_sc', 0.1, neurons))
        self.adj_strength = self.get_init_attr('eta_sc', 0.001, neurons)

        self.target_clip_min = 0.5


    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            super().new_iteration(neurons)


class SORN_IP_TI(Time_Integration_Homeostasis):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('IPTI')
        self.measurement_param = self.get_init_attr('mp', 'n.output', neurons)
        self.adjustment_param = 'TH'

        self.set_threshold(self.get_init_attr('h_ip', 0.1, neurons))
        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)
        self.target_clip_min=self.get_init_attr('clip_min', -0.001, neurons)
        #target_clip_max

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            super().new_iteration(neurons)



class SORN_diffuse_IP(Time_Integration_Homeostasis):

    def set_variables(self, neurons):
        self.add_tag('diff_IP')
        super().set_variables(neurons)
        self.measurement_param = self.get_init_attr('mp', 'test_val', neurons)#output_new
        self.adjustment_param = 'TH'
        self.measure_group_sum = True

        h_dh = self.get_init_attr('h_dh', 0.1, neurons)

        #if h_dh == 'IPTI_h_ip':
        #    h_dh = np.mean((neurons['IPTI',0].min_th+neurons['IPTI',0].max_th)/2)

        self.set_threshold(h_dh)
        self.adj_strength = -self.get_init_attr('eta_dh', 0.001, neurons)


    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            super().new_iteration(neurons)



'''
def binary_activation_function(neurons):
    if neurons.rnd_act_factor != None:
        sig = neurons.rnd_act_factor * np.random.rand(neurons.size)
    else:
        sig = 0

    if hasattr(neurons, 'nox'):
        nox = neurons.nox
    else:
        nox = 0

    val = ((neurons.activity-neurons.TH-nox+sig >= 0.0) + 0.0)

    if hasattr(neurons, 'refractory_counter'):
        return val * (neurons.refractory_counter < 0.1)
    else:
        return val
    #neurons.output_new *= neurons.refractory_counter < 0.1
'''

#def identity(neurons):
#    return neurons.activity-neurons.TH

#def analog_activation_function(neurons):
#    return np.clip(np.power(neurons.activity, 2.0), 0, 1)

                #print(post_act.shape, self.pre_post_mask.shape, self.pre_post_mul.shape)
                #print(pre_act.shape, self.post_pre_mask.shape, self.post_pre_mul.shape)

                #dw = s.get_synapse_mat()

                #for t, f in self.STDP_F.items():
                #    t_start = neurons.timescale*abs(t)
                #    t_end = neurons.timescale*abs(t)+1
                #    print(t_start, t_end)
                #    if t < 0:
                #        dact = np.sum(s.dst.output_buffer[0:neurons.timescale], axis=0)
                #        sact = np.sum(s.src.output_buffer[t_start:t_end], axis=0)
                #    else:
                #        dact = np.sum(s.dst.output_buffer[t_start:t_end], axis=0)
                #        sact = np.sum(s.src.output_buffer[0:neurons.timescale], axis=0)
                #
                #    dw += f * dact[:, None] * sact[None, :]

                #print('start', neurons.tags)

                #print(list(s.dst.output_buffer_dict.keys()), list(s.src.output_buffer_dict.keys()))
                #print(len(s.dst.output_buffer_dict[neurons.timescale]), len(s.src.output_buffer_dict[neurons.timescale]))

                #dact = s.dst.get_masked_dict('output_buffer_dict', neurons.timescale)
                #sact = s.src.get_masked_dict('output_buffer_dict', neurons.timescale)

                #print(neurons.timescale)

                #print(dact.shape, sact.shape)
                #print(self.pre_post_mask.shape, self.post_pre_mask.shape)

                #masked_dact = dact[self.pre_post_mask]
                #masked_sact = sact[self.post_pre_mask]

                #print(masked_dact.shape, masked_sact.shape)

                #weighted_masked_dact = masked_dact*self.pre_post_mul
                #weighted_masked_sact = masked_sact*self.pre_post_mul

                #print(weighted_masked_dact.shape, weighted_masked_sact.shape)

                #summed_up_dact = np.sum(weighted_masked_dact, axis=0)
                #summed_up_sact = np.sum(weighted_masked_sact, axis=0)

                #print(summed_up_dact.shape, summed_up_sact.shape)

                #current_dact = dact[0]
                #current_sact = sact[0]

                #dw_pre_post = summed_up_dact[:, None] * current_sact[None, :]
                #dw_post_pre = current_dact[:, None] * summed_up_sact[None, :]

                #print(current_dact.shape, current_sact.shape)

                #o_new[:, None] * from_old[None, :] - to_old[:, None] * from_new[None, :]
                #dw = dact[:, None] * sact[None, :]

                #s.src_act_sum_old = src_out_new.copy()
            #neurons.last_output = neurons.output_buffer[0].copy()

        # for ng in self.pre_syn_groups:
        #    if not neurons.timescale in ng.buffer_timescale_sum_dict:
        #        ng.buffer_timescale_sum_dict[neurons.timescale] = np.sum(ng.output_buffer[neurons.timescale - 1:neurons.timescale * 2 - 1], axis=0)/neurons.timescale

        # for s in neurons.afferent_synapses[self.transmitter]:
        #    s.slow_add = s.W.dot(s.src.buffer_timescale_sum_dict[neurons.timescale][s.src.mask]) * self.strength

'''
    def set_variables(self, neurons):
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)
        neurons.last_output = neurons.get_neuron_vec()
        for s in neurons.afferent_synapses['GLU']:
            s.src_act_sum_old = np.zeros(s.src.size)

    def new_iteration(self, neurons):
        if first_cycle_step(neurons):

            for s in neurons.afferent_synapses['GLU']:
                src_out_new = np.sum(s.src.output_buffer[0:neurons.timescale], axis=0)

                grow = s.dst.output_buffer[0][:, None] * s.src_act_sum_old[None, :]
                shrink = s.dst.last_output[:, None] * src_out_new[None, :]

                dw = neurons.eta_stdp * (grow - shrink) / (neurons.timescale*neurons.timescale)

                s.W += dw * s.enabled
                s.W[s.W < 0.0] = 0.0

                s.src_act_sum_old = src_out_new.copy()
            neurons.last_output = neurons.output_buffer[0].copy()
'''


'''
class SORN_STDP_old(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)
        #neurons.prune_stdp = self.get_init_attr('prune_stdp', False, neurons)

        for s in neurons.afferent_synapses['GLU']:
            s.STDP_src_lag_buffer_old = np.zeros(s.src.size)#neurons.size bug?
            s.STDP_src_lag_buffer_new = np.zeros(s.src.size)#neurons.size bug?

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLU']:

            #print(s.src.size, len(s.STDP_src_lag_buffer_new), len(s.src.output_new))

            s.STDP_src_lag_buffer_new += s.src.output_buffer[0]/neurons.timescale

            #buffer previous states

            if last_cycle_step(neurons):

                from_old = s.STDP_src_lag_buffer_old#
                from_new = s.STDP_src_lag_buffer_new#s.src.x_new#

                to_old = s.dst.output_buffer[1]
                to_new = s.dst.output_buffer[0]

                #print(to_new, from_old, to_old, from_new)

                dw = neurons.eta_stdp * (to_new[:, None] * from_old[None, :] - to_old[:, None] * from_new[None, :])

                s.W += dw * s.enabled
                s.W[s.W < 0.0] = 0.0

                #if neurons.prune_stdp:
                #    s.W[s.W < 1e-10] = 0
                #    s.enabled *= (s.W > 0)

                # print('STDP',s.W.sum())

                #clear buffer
                s.STDP_src_lag_buffer_old = s.STDP_src_lag_buffer_new.copy()
                s.STDP_src_lag_buffer_new = np.zeros(s.src.size)#neurons.size bug?
'''

#class SORN_slow_input_collect(Neuron_Behaviour):#has to be executed AFTER intra, inter...behaviours
#
#    def set_variables(self, neurons):
#        self.add_tag('input_collect')
#        neurons.output_new_temp = neurons.get_neuron_vec() #required for STDP todo:remove

#    def new_iteration(self, neurons):
#        if last_cycle_step(neurons):
#            neurons.output_new_temp = neurons.activation_function(neurons)
            #reset moved to init_vars

            #neurons.test_val = (activation_function(neurons.activity, neurons) + activation_function(neurons.slow_act, neurons))/2