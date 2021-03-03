from PymoNNto.NetworkBehaviour.Logic.TensorflowModules.TensorflowBehaviour import *
import numpy as np

from PymoNNto.NetworkBehaviour.Input.Activator import *
from PymoNNto.NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *

dtype = 'float32'

class init(TensorflowBehaviour):

    def set_variables(self, neurons):
        self.add_tag('')

        neurons.voltage = tf.Variable(neurons.get_neuron_vec()+1, dtype='float32')
        neurons.decrease = tf.constant(0.9, dtype='float32')

        print('shape', neurons.voltage.shape)

        print(type(neurons.voltage), type(neurons.decrease))



    def new_iteration(self, neurons):
        temp = tf.math.multiply(neurons.voltage, neurons.decrease)
        neurons.voltage.assign(temp)
        #print(np.array(neurons.voltage))




class SORN_init_neuron_varsTF(TensorflowBehaviour):

    def set_variables(self, neurons):
        self.add_tag('init_neuron_varsTF')

        neurons.activity = tf.Variable(neurons.get_neuron_vec(), dtype=dtype)
        neurons.excitation = tf.Variable(neurons.get_neuron_vec(), dtype=dtype)
        neurons.inhibition = tf.Variable(neurons.get_neuron_vec(), dtype=dtype)
        neurons.input_act = tf.Variable(neurons.get_neuron_vec(), dtype=dtype)

        neurons.output = tf.Variable(neurons.get_neuron_vec(), dtype='float32')
        neurons.output_old = tf.Variable(neurons.get_neuron_vec(), dtype='float32')

        #neurons.timescale = self.get_init_attr('timescale', 1)

    def new_iteration(self, neurons):
        neurons.activity.assign(tf.math.multiply(neurons.activity, 0.0))
        neurons.excitation.assign(tf.math.multiply(neurons.activity, 0.0))
        neurons.inhibition.assign(tf.math.multiply(neurons.activity, 0.0))
        neurons.input_act.assign(tf.math.multiply(neurons.activity, 0.0))

        neurons.output_old.assign(neurons.output)

        #neurons.activity.fill(0)
        #neurons.excitation.fill(0)# *= 0
        #neurons.inhibition.fill(0)# *= 0
        #neurons.input_act.fill(0)# *= 0

class WTA_refracTF(TensorflowBehaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory_A_TF')
        neurons.refractory_counter_analog = tf.Variable(neurons.get_neuron_vec(), dtype=dtype)
        self.decayfactor = tf.constant(self.get_init_attr('decayfactor', 0.5, neurons), dtype='float32')


    def new_iteration(self, neurons):
        neurons.refractory_counter_analog.assign(tf.math.multiply(neurons.refractory_counter_analog, self.decayfactor))
        neurons.refractory_counter_analog.assign(tf.math.add(neurons.refractory_counter_analog, neurons.output))


class WTA_refrac_applyTF(TensorflowBehaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory_Apply')
        self.strengthfactor = tf.constant(self.get_init_attr('strengthfactor', 1.0, neurons), dtype='float32')

    def new_iteration(self, neurons):
        neurons.activity.assign(tf.math.subtract(neurons.activity, tf.math.multiply(neurons.refractory_counter_analog, self.strengthfactor)))
        #neurons.activity -= neurons.refractory_counter_analog * self.strengthfactor


class SORN_slow_syn_simpleTF(SORN_signal_propagation_base):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.strength = tf.constant(self.strength, dtype='float32')
        self.add_tag('slow_simpleTF' + self.transmitter)

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.transmitter]:

            #print(s.W, s.src.output)

            #s.slow_add = tf.multiply(tf.tensordot(s.W, s.src.output, axes=0), self.strength)#matmul???

            s.dst.activity.assign(tf.add(s.dst.activity, s.slow_add))
            if self.strength > 0:
                s.dst.excitation.assign(tf.add(s.dst.excitation, s.slow_add))
            else:
                s.dst.inhibition.assign(tf.add(s.dst.inhibition, s.slow_add))

class SORN_init_afferent_synapsesTF(SORN_init_afferent_synapses):

    def set_variables(self, neurons):
        super().set_variables(neurons)

        for s in neurons.afferent_synapses[self.transmitter]:

            s.W = tf.Variable(s.W, dtype='float32')
            print(s.W)
            s.enabled = tf.Variable(s.enabled, dtype='float32')
            s.slow_add = tf.Variable(s.slow_add, dtype='float32')
            s.fast_add = tf.Variable(s.fast_add, dtype='float32')

class SORN_generate_output_K_WTA_partitionedTF_Experimental(TensorflowBehaviour):

    def set_variables(self, neurons):
        self.add_tag('K_WTA_partitionedTF')

        self.K = self.get_init_attr('K', 0.1, neurons)

        partition_size = self.get_init_attr('partition_size', 7, neurons)
        self.partitioned_ng=neurons.partition_size(partition_size)

    def new_iteration(self, neurons):

        neurons.output_temp = neurons.get_neuron_vec()
        neurons.activity_temp = neurons.activity.numpy()

        for ng in self.partitioned_ng:  #
            K = ng.size * self.K
            # for non integer K
            K_floor = int(np.floor(K))
            if np.random.rand() < (K - K_floor):
                K = K_floor + 1
            else:
                K = K_floor

            if K > 0:
                ind = np.argpartition(ng.activity_temp, -K)[-K:]
                act_mat = np.zeros(ng.size)
                act_mat[ind] = 1

                ng.output_temp += act_mat

        neurons.output.assign(neurons.output_temp)


class SORN_generate_output_K_WTA_partitionedTF(TensorflowBehaviour):

    def set_variables(self, neurons):
        self.add_tag('K_WTA_partitionedTF')

        #self.filter_temporal_output = self.get_init_attr('filter_temporal_output', False, neurons)

        neurons.output = tf.Variable(neurons.get_neuron_vec(), dtype='float32')
        neurons.output_old = tf.Variable(neurons.get_neuron_vec(), dtype='float32')

        self.K = tf.constant(self.get_init_attr('K', 0.1, neurons), dtype='float32')#only accepts values between 0 and 1

        partition_size = self.get_init_attr('partition_size', 7, neurons)
        self.partitioned_ng=neurons.partition_size(partition_size)


    def new_iteration(self, neurons):

        neurons.output.assign(tf.math.multiply(neurons.output, 0.0))

        for ng in self.partitioned_ng:#:

            K = ng.size * self.K
            #for non integer K
            K_floor = int(np.floor(K))
            if np.random.rand() < (K-K_floor):
                K = K_floor+1
            else:
                K = K_floor

            #ng.output = tf.multiply(ng.output, 0.0)

            if K > 0:
                values, indices = tf.math.top_k(ng.activity, k=K)

                if type(ng) is NeuronSubGroup:
                    real_indices = tf.gather(ng.id_mask, indices)
                    tf.compat.v1.scatter_update(neurons.output, real_indices, np.ones(K))
                else:
                    tf.compat.v1.scatter_update(ng.output, indices, np.ones(K))

                #ng.id_mask[indices]

                #ng.BaseNeuronGroup.output[]

                #var = tf.Variable(np.zeros(ng.size), dtype='float32')

                #var[indices] = 1.0

                #new = tf.compat.v1.scatter_update(ng.output, indices, np.ones(K))
                #ng.output = new

                #ind = np.argpartition(ng.activity, -K)[-K:]
                #act_mat = np.zeros(ng.size)
                #act_mat[ind] = 1

                #ng.output += act_mat


class SORN_IP_WTA_TF(TensorflowBehaviour):

    def set_variables(self, neurons):
        #super().set_variables(neurons)
        self.add_tag('IP_WTA')
        self.measurement_param = self.get_init_attr('mp', 'n.output', neurons)
        self.adjustment_param = 'exhaustion_value'

        self.max_th = self.get_init_attr('h_ip', 0.1, neurons)
        self.min_th = self.max_th

        self.adj_strength = -self.get_init_attr('eta_ip', 0.001, neurons)

        #target_clip_max

        neurons.exhaustion_value = tf.Variable(neurons.get_neuron_vec(), dtype='float32')

    def new_iteration(self, neurons):
        greater = tf.multiply(tf.cast(tf.greater(neurons.output, self.max_th), dtype='float32'), -1.0)
        smaller = tf.multiply(tf.cast(tf.less(neurons.output, self.min_th), dtype='float32'), 1.0)

        #greater = (neurons.output > self.max_th) * (-self.dec)
        #smaller = (neurons.output < self.min_th) * self.inc

        greater = tf.multiply(greater, tf.subtract(neurons.output, self.max_th))
        smaller = tf.multiply(smaller, tf.subtract(self.min_th, neurons.output))

        #greater *= neurons.output - self.max_th
        #smaller *= self.min_th - neurons.output

        change = tf.multiply(tf.add(greater, smaller), self.adj_strength)
        #change = (greater + smaller) * self.adj_strength

        neurons.exhaustion_value.assign(tf.add(neurons.exhaustion_value, change))
        #neurons.exhaustion_value = neurons.exhaustion_value + change

        neurons.exhaustion_value.assign(tf.subtract(neurons.exhaustion_value, tf.reduce_mean(neurons.exhaustion_value)))
        #neurons.exhaustion_value = neurons.exhaustion_value - np.mean(neurons.exhaustion_value)

        # neurons.activity -= neurons.exhaustion_value



class SORN_IP_WTA_apply_TF(TensorflowBehaviour):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('SORN_IP_WTA_apply')

    def new_iteration(self, neurons):
        neurons.activity.assign(tf.subtract(neurons.activity, neurons.exhaustion_value))
        #neurons.activity -= neurons.exhaustion_value

class STDP_TF(TensorflowBehaviour):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('SORN_IP_WTA_apply')
        neurons.eta_stdp = tf.constant(self.get_init_attr('eta_stdp', 0.00015, neurons), dtype='float32')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            pre_post = tf.tensordot(s.dst.output, s.src.output_old, axes=0)
            simu = tf.tensordot(s.dst.output, s.src.output, axes=0)
            post_pre = tf.tensordot(s.dst.output_old, s.src.output, axes=0)

            dw = tf.multiply(neurons.eta_stdp, tf.add(tf.subtract(pre_post, post_pre), simu))

            s.W.assign(tf.clip_by_value(tf.add(s.W, tf.multiply(dw, s.enabled)), 0.0, 1.0))

class STDP_TF_simu(TensorflowBehaviour):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('SORN_IP_WTA_apply')
        neurons.eta_stdp = tf.constant(self.get_init_attr('eta_stdp', 0.00015, neurons), dtype='float32')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            simu = tf.tensordot(s.dst.output, s.src.output, axes=0)

            dw = tf.multiply(neurons.eta_stdp, simu)

            s.W.assign(tf.clip_by_value(tf.add(s.W, tf.multiply(dw, s.enabled)), 0.0, 1.0))

class SORN_SN_TF(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('SN')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)

        neurons.require_synapses(self.syn_type, warning=False)#suppresses error when synapse group does not exist

        self.clip_min = self.get_init_attr('clip_min', 0.0, neurons)
        self.clip_max = self.get_init_attr('clip_max', 1000000.0, neurons)

        self.norm_factor = tf.constant(self.get_init_attr('norm_factor', 1.0, neurons), dtype='float32')

        neurons.temp_weight_sum = tf.Variable(neurons.get_neuron_vec(), dtype='float32')

    def new_iteration(self, neurons):

        neurons.temp_weight_sum.assign(tf.multiply(neurons.temp_weight_sum, 0.0))

        for s in neurons.afferent_synapses[self.syn_type]:
            s.dst.temp_weight_sum.assign(tf.add(s.dst.temp_weight_sum, tf.math.reduce_sum(s.W, axis=1)))
            #s.dst.temp_weight_sum += np.sum(np.abs(s.W), axis=1)

        neurons.temp_weight_sum.assign(tf.divide(neurons.temp_weight_sum, self.norm_factor))

        #print(neurons.temp_weight_sum.numpy()[0])
        # neurons.temp_weight_sum /= self.norm_factor

        for s in neurons.afferent_synapses[self.syn_type]:
            #d = tf.add(s.dst.temp_weight_sum, tf.cast(tf.math.equal(s.dst.temp_weight_sum, 0.0), dtype='float32'))
            d = s.dst.temp_weight_sum
            s.W.assign(tf.transpose(tf.divide(tf.transpose(s.W), d)))
            #s.W.assign(tf.math.divide(s.W, d))
            # s.W = tf.linalg.normalize()
            #s.W = s.W / (s.dst.temp_weight_sum[:, None] + (s.dst.temp_weight_sum[:, None] == 0))

        #for s in neurons.afferent_synapses[self.syn_type]:
        #    s.W.assign(tf.clip_by_value(s.W, self.clip_min, self.clip_max))



class SORN_external_inputTF(NeuronActivator):

    def set_variables(self, neurons):
        super().set_variables(neurons)

        self.strength = tf.constant(self.get_init_attr('strength', 1.0, neurons), dtype='float32')
        neurons.input = np.zeros(neurons.size)
        self.write_to = 'input'
        neurons.add_tag('text_input_group')
        #pre_syn = neurons.connected_NG_param_list('afferent_buffer_requirement', same_NG=True, search_behaviours=True)
        #neurons.input_buffer = neurons.get_neuron_vec_buffer(neurons.timescale)#pre_syn[0][0]


    def new_iteration(self, neurons):
        super().new_iteration(neurons)

        #add = np.sum(neurons.input_buffer[neurons.timescale - 1:neurons.timescale * 2 - 1], axis=0) / neurons.timescale * self.strength  # neurons.input * self.strength / neurons.timescale
        neurons.activity.assign(tf.add(neurons.activity, neurons.input))
        neurons.input*=0.0
        neurons.input_act.assign(tf.math.add(neurons.input_act, neurons.input))

        #neurons.input_buffer = neurons.buffer_roll(neurons.input_buffer, neurons.input)

        #if last_cycle_step(neurons) and self.strength != 0:
