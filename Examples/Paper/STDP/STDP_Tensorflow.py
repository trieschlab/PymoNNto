from SORNSim.NetworkCore.Behaviour import *
import tensorflow as tf

class STDP_TF(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP_TF')
        eta_stdp = self.get_init_attr('eta_stdp', 0.00015, neurons)
        neurons.eta_stdp = tf.constant(eta_stdp, dtype='float32')
        self.syn_type = self.get_init_attr('syn_type', 'GLU', neurons)
        neurons.voltage_old = neurons.get_neuron_vec()

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            pre_post = tf.tensordot(s.dst.voltage, s.src.voltage_old, axes=0)
            simu = tf.tensordot(s.dst.voltage, s.src.voltage, axes=0)
            post_pre = tf.tensordot(s.dst.output_old, s.src.voltage, axes=0)

            dw = tf.multiply(neurons.eta_stdp, tf.add(tf.subtract(pre_post, post_pre), simu))

            s.W.assign(tf.clip_by_value(tf.add(s.W, tf.multiply(dw, s.enabled)), 0.0, 1.0))

        neurons.voltage_old.assign(neurons.voltage)

