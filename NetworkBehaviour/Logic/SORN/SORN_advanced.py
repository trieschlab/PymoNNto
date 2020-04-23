from NetworkBehaviour.Input.Activator import *

#import matplotlib.pyplot as plt

def identity(neurons):
    return neurons.activity-neurons.TH

def analog_activation_function(neurons):
    return np.clip(np.power(neurons.activity, 2.0), 0, 1)

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

def last_cycle_step(neurons):
    return neurons.iteration % neurons.iteration_lag == neurons.iteration_lag-1

def first_cycle_step(neurons):
    return neurons.iteration % neurons.iteration_lag == 0




class SORN_init_afferent_synapses(Neuron_Behaviour):

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

        self.group_weighting = self.get_init_attr('group_weighting', False, neurons)

        for s in neurons.afferent_synapses[self.transmitter]:
            if self.group_weighting == False:
                weighting = 1
            else:
                weighting = s.get_synapse_group_size_factor(s, self.transmitter)#todo test

            if partition_compensation:
                pc = s.src.group_without_subGroup().size/s.src.size
                weighting *= pc

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

class SORN_init_neuron_vars(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('init_neuron_vars')

        af=self.get_init_attr('activation_function', 'binary', neurons)
        if af=='binary':
            neurons.activation_function = binary_activation_function
        elif af=='analog':
            neurons.activation_function = analog_activation_function
        else:
            neurons.activation_function=eval(af)
            #print('warning: no activation function defined')

        neurons.activity = neurons.get_neuron_vec()
        neurons.excitation = neurons.get_neuron_vec()
        neurons.inhibition = neurons.get_neuron_vec()
        neurons.input_act = neurons.get_neuron_vec()

        #neurons.slow_act=neurons.get_neuron_vec()

        neurons.TH = neurons.get_neuron_vec()+self.get_init_attr('init_TH', 0.5, neurons)#neurons.get_random_neuron_vec()*0.5

        neurons.iteration_lag = self.get_init_attr('iteration_lag', 1, neurons)
        neurons.rnd_act_factor = self.get_init_attr('rnd_act_factor', None, neurons)#sigma

    def new_iteration(self, neurons):
        if first_cycle_step(neurons):
            neurons.activity.fill(0)# *= 0
            neurons.excitation.fill(0)# *= 0
            neurons.inhibition.fill(0)# *= 0
            neurons.input_act.fill(0)# *= 0

            #neurons.slow_act *= 0

class SORN_NOX(Instant_Homeostasis):

    def partition_sum(self, neurons):
        neurons._temp_act_sum = neurons.get_neuron_vec()
        for s in neurons.afferent_synapses['GLU']:
            s.dst._temp_act_sum += np.mean(s.src.output_new)
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

            #print(self.measurement_param)
            #neurons.nox *= 0.5#0.9


class SORN_signal_propagation_base(Neuron_Behaviour):

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


class SORN_external_input(NeuronActivator):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.strength = self.get_init_attr('strength', 1.0, neurons)
        neurons.input = np.zeros(neurons.size)
        self.write_to = 'input'
        neurons.add_tag('text_input_group')


    def new_iteration(self, neurons):
        super().new_iteration(neurons)
        if self.strength!=0:
            add = neurons.input * self.strength / neurons.iteration_lag
            neurons.activity += add

            #neurons.excitation += add #Todo:test

            neurons.input.fill(0)# *= 0
            neurons.input_act += add


class SORN_slow_syn(SORN_signal_propagation_base):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('slow_' + self.transmitter)
        self.sparse_optimization = self.get_init_attr('so', False, neurons)

    def new_iteration(self, neurons):
        if self.strength!=0:
            for s in neurons.afferent_synapses[self.transmitter]:
                if self.sparse_optimization:
                    s.slow_add = (np.sum(s.W[:, s.src.output.astype(np.bool)], axis=1) * self.strength) / neurons.iteration_lag
                    #add = (np.sum(s.W.transpose()[s.src.output.astype(np.bool)], axis=0) * self.strength) / neurons.iteration_lag
                else:
                    s.slow_add = (s.W.dot(s.src.output) * self.strength) / neurons.iteration_lag

                #neurons.slow_act += add

                s.dst.activity += s.slow_add
                if self.strength>0:
                    s.dst.excitation+=s.slow_add
                else:
                    s.dst.inhibition+=s.slow_add

        #if self.input_strength is not None:
        #    add = neurons.input * self.input_strength / neurons.iteration_lag
        #    neurons.activity += add

        #    #neurons.excitation += add #Todo:test
        #    neurons.input *= 0
        #    neurons.input_act += add



class SORN_fast_syn(SORN_signal_propagation_base):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('fast_' + self.transmitter)
        self.sparse_optimization = self.get_init_attr('so', False, neurons)

    def new_iteration(self, neurons):
        if self.strength!=0:
            for s in neurons.afferent_synapses[self.transmitter]:
                if self.sparse_optimization:
                    s.fast_add = (np.sum(s.W[:, s.src.activation_function(s.src).astype(np.bool)], axis=1) * self.strength) / neurons.iteration_lag
                    #add = (np.sum(s.W.transpose()[s.src.output.astype(np.bool)], axis=0) * self.strength) / neurons.iteration_lag
                else:
                    s.fast_add = s.W.dot(s.src.activation_function(s.src)) * self.strength / neurons.iteration_lag

                s.dst.activity += s.fast_add
                if self.strength > 0:
                    s.dst.excitation += s.fast_add
                else:
                    s.dst.inhibition += s.fast_add


class SORN_slow_input_collect(Neuron_Behaviour):#has to be executed AFTER intra, inter...behaviours

    def set_variables(self, neurons):
        self.add_tag('input_collect')
        neurons.output_new_temp = neurons.get_neuron_vec() #required for STDP todo:remove

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.output_new_temp = neurons.activation_function(neurons)
            #reset moved to init_vars

            #neurons.test_val = (activation_function(neurons.activity, neurons) + activation_function(neurons.slow_act, neurons))/2


class SORN_input_collect(Neuron_Behaviour):#has to be executed AFTER intra, inter...behaviours

    def set_variables(self, neurons):
        self.add_tag('input_collect')
        neurons.output = neurons.get_neuron_vec()
        neurons.output_new = neurons.get_neuron_vec() #required for STDP todo:remove

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.output_new = neurons.activation_function(neurons)
            #reset moved to init_vars

            #neurons.test_val = (activation_function(neurons.activity, neurons) + activation_function(neurons.slow_act, neurons))/2


class SORN_Refractory(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory')
        neurons.refractory_counter = neurons.get_neuron_vec()
        self.factor = self.get_init_attr('factor', 0.9, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            #neurons.output_new *= neurons.refractory_counter < 0.1
            neurons.refractory_counter *= self.factor
            neurons.refractory_counter += neurons.output_new

class SORN_STDP_new(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)
        neurons.excitation_punishment = self.get_init_attr('excitation_punishment', 1, neurons)
        neurons.prune_stdp = self.get_init_attr('prune_stdp', False, neurons)


        for s in neurons.afferent_synapses['GLU']:
            s.STDP_src_lag_buffer_old = np.zeros(s.src.size)#neurons.size bug?
            s.STDP_src_lag_buffer_new = np.zeros(s.src.size)#neurons.size bug?

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLU']:
            grow=s.dst.output_new[:, None] * s.src.output[None, :]
            shrink=neurons.excitation_punishment * s.dst.excitation[:, None] * s.src.output[None, :]
            exc_shrink=s.dst.output[:, None] * s.src.output_new[None, :]

            #print(np.sum(grow),np.sum(shrink),np.sum(exc_shrink))

            dw = neurons.eta_stdp * (grow - shrink - exc_shrink)

            s.W += dw * s.enabled
            s.W[s.W < 0.0] = 0.0


class SORN_STDP(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)
        neurons.prune_stdp = self.get_init_attr('prune_stdp', False, neurons)

        for s in neurons.afferent_synapses['GLU']:
            s.STDP_src_lag_buffer_old = np.zeros(s.src.size)#neurons.size bug?
            s.STDP_src_lag_buffer_new = np.zeros(s.src.size)#neurons.size bug?

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLU']:

            #print(s.src.size, len(s.STDP_src_lag_buffer_new), len(s.src.output_new))

            s.STDP_src_lag_buffer_new += s.src.output_new/neurons.iteration_lag

            #buffer previous states

            if last_cycle_step(neurons):

                from_old = s.STDP_src_lag_buffer_old#
                from_new = s.STDP_src_lag_buffer_new#s.src.x_new#

                to_old = s.dst.output
                to_new = s.dst.output_new

                dw = neurons.eta_stdp * (to_new[:, None] * from_old[None, :] - to_old[:, None] * from_new[None, :])

                s.W += dw * s.enabled
                s.W[s.W < 0.0] = 0.0

                if neurons.prune_stdp:
                    s.W[s.W < 1e-10] = 0
                    s.enabled *= (s.W > 0)

                # print('STDP',s.W.sum())

                #clear buffer
                s.STDP_src_lag_buffer_old = s.STDP_src_lag_buffer_new.copy()
                s.STDP_src_lag_buffer_new = np.zeros(s.src.size)#neurons.size bug?






class SORN_SN(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('SN')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)
        self.clip_max = self.get_init_attr('clip_max', None, neurons)
        neurons.weight_norm_factor = neurons.get_neuron_vec()+self.get_init_attr('init_norm_factor', 1.0, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            self.normalize_synapse_attr('W', 'W', neurons.weight_norm_factor, neurons, self.syn_type)
            for s in neurons.afferent_synapses[self.syn_type]:
                s.W=np.clip(s.W, 0, self.clip_max)


class SORN_iSTDP(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('iSTDP')

        self.transmitter = self.get_init_attr('transmitter', 'GABA', neurons)

        neurons.eta_istdp = self.get_init_attr('eta_istdp', 0.001, neurons)
        neurons.h_ip = self.get_init_attr('h_ip', 0.1, neurons)

        for s in neurons.afferent_synapses[self.transmitter]:
            s.iSTDP_src_lag_buffer = np.zeros(s.src.size)

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses[self.transmitter]:
            s.iSTDP_src_lag_buffer += s.src.output/neurons.iteration_lag
            if last_cycle_step(neurons):

                s.W += -s.dst.eta_istdp * ((1 - (s.dst.excitation+s.dst.inhibition) * (1 + 1.0 / s.dst.h_ip))[:, None] * s.iSTDP_src_lag_buffer[None, :])
                s.W = np.clip(s.W, 0.001, 1.0)*s.enabled

                s.iSTDP_src_lag_buffer.fill(0)# *= 0

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
        self.measurement_param = self.get_init_attr('mp', 'n.output_new', neurons)
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

        h_dh=self.get_init_attr('h_dh', 0.1, neurons)

        #if h_dh == 'IPTI_h_ip':
        #    h_dh = np.mean((neurons['IPTI',0].min_th+neurons['IPTI',0].max_th)/2)

        self.set_threshold(h_dh)
        self.adj_strength = -self.get_init_attr('eta_dh', 0.001, neurons)


    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            super().new_iteration(neurons)



class SORN_finish(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('finish')

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.output = neurons.output_new
            #neurons.exc=neurons.excitation.copy()


class SORN_random_act(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('rnd_act')
        self.chance = self.get_init_attr('chance', 10.0, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            e = np.mean(neurons.excitation)
            c = self.chance*np.abs(0.005-e)
            add=0.1*(neurons.get_random_neuron_vec()<c)
            neurons.excitation += add
            neurons.activity += add






'''
class SORN_init_variables(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('init vars')
        neurons.iteration_lag = self.get_init_attr('iteration_lag', 1, neurons)

        neurons.require_synapses('GLU')
        neurons.require_synapses('GABA')

        neurons.inh_strength = self.get_init_attr('inh_strength', 1.0, neurons)

        neurons.x = (np.random.random(neurons.size) < 0.5) + 0
        neurons.T_min = self.get_init_attr('T_min', 0.0, neurons)
        neurons.T_max = self.get_init_attr('T_max', 0.5, neurons)
        neurons.T = neurons.T_min + np.random.random(neurons.size) * (neurons.T_max - neurons.T_min)
        neurons.input_gain = self.get_init_attr('input_gain', 1.0, neurons)
        neurons.sigma = self.get_init_attr('sigma', None, neurons)
        neurons.R_x = np.zeros(neurons.size)
        neurons.lamb = self.get_init_attr('lamb', -1, neurons)#10 -1=full
        neurons.x_new = np.zeros(neurons.size)
        neurons.input = np.zeros(neurons.size)

        neurons.FSC = self.get_init_attr('fixed_synapse_count', False, neurons)

        #todo: calculate distributed lamb for every synapse group

        for s in neurons.afferent_synapses['GLU']:
            syn_lamb = neurons.lamb#*s.get_synapse_group_size_factor(neurons, 'GLU')
            if neurons.lamb == -1:
                syn_lamb = neurons.size

            if neurons.FSC:
                s.W = s.get_random_synapse_mat_fixed(syn_lamb)*s.enabled
            else:
                s.W = s.get_random_synapse_mat(density=syn_lamb / float(neurons.size))*s.enabled
            s.enabled *= (s.W > 0)


        for s in neurons.afferent_synapses['GLU']:
            if 'sparse' in s.tags:
                s.W = sp.csc_matrix(s.W)
                #s.W.eliminate_zeros()

        for s in neurons.afferent_synapses['GABA']:
            s.W = s.get_random_synapse_mat()

        self.normalize_synapse_attr('W', 'W', 1.0, neurons, 'GLU')
        self.normalize_synapse_attr('W', 'W', 1.0, neurons, 'GABA')

    def new_iteration(self, neurons):
        return
'''
