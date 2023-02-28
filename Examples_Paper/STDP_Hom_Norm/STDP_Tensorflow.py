from PymoNNto.NetworkCore.Behaviour import *
import tensorflow as tf

class STDP_TF(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP_TF')
        eta_stdp = self.parameter('eta_stdp', 0.0015, neurons)
        neurons.eta_stdp = tf.constant(eta_stdp, dtype='float32')
        self.syn_type = self.parameter('syn_type', 'GLU', neurons)
        neurons.spike_old = neurons.vector()

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            pre_post = tf.tensordot(s.dst.spike, s.src.spike_old, axes=0)
            simu = tf.tensordot(s.dst.spike, s.src.spike, axes=0)
            post_pre = tf.tensordot(s.dst.spike_old, s.src.spike, axes=0)

            dw = tf.multiply(neurons.eta_stdp, tf.add(tf.subtract(pre_post, post_pre), simu))

            s.W.assign(tf.clip_by_value(tf.add(s.W, tf.multiply(dw, s.enabled)), 0.0, 1.0))

        neurons.spike_old.assign(neurons.spike)

