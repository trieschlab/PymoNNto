from NetworkCore.Behaviour import *
import numpy as np

import os
#os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

voltage = tf.Variable(np.zeros(10), dtype='float32')
mask=[0,1,1,0,0,1,0,0,0,0]
decrease = tf.constant(0.9, dtype='float32')

masked_voltage = tf.boolean_mask(voltage, mask, axis=0)

#tf.multiply(masked_voltage,decrease)

tf.compat.v1.scatter_update(voltage, np.where(mask), decrease)#for indexes

print(np.array(voltage))

#masked_voltage+=10

# tf function decorator


class TestModuleTensorflow(Behaviour):

    def set_variables(self, neurons):
        if not hasattr(neurons, 'tf'):
            neurons.tf = tf

        self.add_tag('TF_Test,TF')
        #self.get_init_attr('step', '1*ms')

        neurons.voltage = tf.Variable(neurons.get_random_neuron_vec()+1, dtype='float32')
        neurons.decrease = tf.constant(0.99, dtype='float32')

        print('shape', neurons.voltage.shape)

        print(type(neurons.voltage), type(neurons.decrease))

        #v.assign(2.)
        #neurons.c = tf.constant([[1, 2, 3, 4], [-1, -2, -3, -4], [5, 6, 7, 8]])
        #tf.
        #tf.math.segment_sum(c, tf.constant([0, 0, 1]))


    def new_iteration(self, neurons):
        temp = tf.math.multiply(neurons.voltage, neurons.decrease)
        neurons.voltage.assign(temp)
        #print(np.array(neurons.voltage))


class TestModuleNumpy(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('TF_Test')
        #self.get_init_attr('step', '1*ms')

        neurons.voltage = neurons.get_neuron_vec().astype(def_dtype)+1
        neurons.decrease = 0.9

        #v.assign(2.)
        #neurons.c = tf.constant([[1, 2, 3, 4], [-1, -2, -3, -4], [5, 6, 7, 8]])
        #tf.
        #tf.math.segment_sum(c, tf.constant([0, 0, 1]))


    def new_iteration(self, neurons):
        temp = neurons.voltage*neurons.decrease
        neurons.voltage=temp
        #print(np.array(neurons.voltage))
