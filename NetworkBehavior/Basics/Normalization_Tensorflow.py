from PymoNNto.NetworkCore.Behavior import *
import numpy as np
import tensorflow as tf

class Synaptic_Normalization_TF(Behavior):

    def initialize(self, neurons):
        self.syn_type = self.parameter('syn_type', 'GLU', neurons)

        neurons.require_synapses(self.syn_type, warning=False)#suppresses error when synapse group does not exist

        self.clip_min = self.parameter('clip_min', 0.0, neurons)
        self.clip_max = self.parameter('clip_max', 1000000.0, neurons)

        self.norm_factor = tf.constant(self.parameter('norm_factor', 1.0, neurons), dtype='float32')

        neurons.temp_weight_sum = tf.Variable(neurons.vector(), dtype='float32')

    def iteration(self, neurons):
        neurons.temp_weight_sum.assign(tf.multiply(neurons.temp_weight_sum, 0.0))

        for s in neurons.afferent_synapses[self.syn_type]:
            s.dst.temp_weight_sum.assign(tf.add(s.dst.temp_weight_sum, tf.math.reduce_sum(s.W, axis=1)))

        neurons.temp_weight_sum.assign(tf.divide(neurons.temp_weight_sum, self.norm_factor))

        for s in neurons.afferent_synapses[self.syn_type]:
            #d = tf.add(s.dst.temp_weight_sum, tf.cast(tf.math.equal(s.dst.temp_weight_sum, 0.0), dtype='float32'))
            d = s.dst.temp_weight_sum
            s.W.assign(tf.transpose(tf.divide(tf.transpose(s.W), d)))
