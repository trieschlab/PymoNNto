from NetworkBehaviour.Input.Activator import *
from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *



##########################################################################
#Generate output with k winner takes all algorithm
##########################################################################
class SORN_generate_output_K_WTA(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('K_WTA')

        neurons.output = neurons.get_neuron_vec()

        self.K = self.get_init_attr('K', 10, neurons)

        if self.K < 1:
            self.K = int(neurons.size * self.K)


    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            ind = np.argpartition(neurons.activity, -self.K)[-self.K:]
            neurons.output.fill(0)
            neurons.output[ind] = 1


class SORN_generate_output_K_WTA_partitioned(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('K_WTA_partitioned')

        self.filter_temporal_output = self.get_init_attr('filter_temporal_output', False, neurons)



        self.K = self.get_init_attr('K', 0.1, neurons)#only accepts values between 0 and 1

        partition_size = self.get_init_attr('partition_size', 7, neurons)
        self.partitioned_ng=neurons.partition_size(partition_size)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):

            #for syn in neurons.afferent_synapses['GLU']:
            #    ng=syn.dst
            for ng in self.partitioned_ng:#
                K = ng.size * self.K
                #for non integer K
                K_floor = int(np.floor(K))
                if np.random.rand() < (K-K_floor):
                    K = K_floor+1
                else:
                    K = K_floor

                ng.output *= 0

                if K>0:
                    act = ng.activity.copy()

                    if self.filter_temporal_output:
                        act = ng.activity*ng.output#-(s.dst.output*-10000)

                    ind = np.argpartition(act, -K)[-K:]
                    act_mat = np.zeros(ng.size)
                    act_mat[ind] = 1

                    ng.output += act_mat

                    #s.dst.output = s.dst.output*0.0+act_mat
                    #
                    #s.dst.output[ind] += 1


                #s.dst._temp_act_sum += np.mean(s.src.output)


class SORN_WTA_fast_syn(SORN_signal_propagation_base):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('fast_' + self.transmitter)
        self.get_init_attr('so', None, neurons)#just for error suppression

    def new_iteration(self, neurons):
        if last_cycle_step(neurons) and self.strength != 0:
            for s in neurons.afferent_synapses[self.transmitter]:
                s.fast_add = s.W.dot(s.src.output) * self.strength# / neurons.timescale

                s.dst.activity += s.fast_add
                if self.strength > 0:
                    s.dst.excitation += s.fast_add
                else:
                    s.dst.inhibition += s.fast_add

class SORN_WTA_iSTDP(Behaviour):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('WTA iSTDP')
        self.eta_iSTDP = self.get_init_attr('eta_iSTDP', 0.1, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            for s in neurons.afferent_synapses['GABA']:
                add = s.dst.activity[:, None] * s.src.activity[None, :] * self.eta_iSTDP * s.enabled
                #print(add.shape)
                s.W += add


class SORN_IP_TI_WTA(Time_Integration_Homeostasis):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('IP_TI_WTA')
        self.measurement_param = self.get_init_attr('mp', 'n.output', neurons)
        self.adjustment_param = 'exhaustion_value'

        self.set_threshold(self.get_init_attr('h_ip', 0.1, neurons))
        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)
        self.target_clip_min=self.get_init_attr('clip_min', -0.001, neurons)

        #target_clip_max

        neurons.exhaustion_value = 0

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            super().new_iteration(neurons)
            neurons.activity -= neurons.exhaustion_value


class SORN_IP_WTA(Instant_Homeostasis):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('IP_WTA')
        self.measurement_param = self.get_init_attr('mp', 'n.output', neurons)
        self.adjustment_param = 'exhaustion_value'

        self.set_threshold(self.get_init_attr('h_ip', 0.1, neurons))
        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)

        #target_clip_max

        neurons.exhaustion_value = 0

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            super().new_iteration(neurons)

            neurons.exhaustion_value = neurons.exhaustion_value-np.mean(neurons.exhaustion_value)

            #neurons.activity -= neurons.exhaustion_value

class SORN_IP_WTA_apply(Behaviour):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('SORN_IP_WTA_apply')

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.activity -= neurons.exhaustion_value

'''
class SORN_Neuron_Exhaustion(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('exhaustion')
        neurons.exhaustion_value = neurons.get_neuron_vec()
        self.decay_factor = self.get_init_attr('decay_factor', 0.9, neurons)
        self.strength = self.get_init_attr('strength', 0.1, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.exhaustion_value *= self.decay_factor
            neurons.exhaustion_value += neurons.output

            neurons.activity -= neurons.exhaustion_value * self.strength
'''