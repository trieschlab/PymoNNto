from PymoNNto import *
import tensorflow as tf

class Basic_Behaviour_Tensorflow(Behaviour):

    def set_variables(self, neurons):
        neurons.voltage = tf.Variable(neurons.get_neuron_vec(), dtype='float32')
        neurons.spike = tf.Variable(neurons.get_neuron_vec(), dtype='bool')
        self.threshold = tf.constant(0.5, dtype='float32')
        self.decay_factor = tf.constant(0.9, dtype='float32')

    def new_iteration(self, neurons):
        neurons.spike.assign(tf.greater(neurons.voltage, self.threshold))#spikes

        not_firing = tf.cast(tf.math.logical_not(neurons.spike), dtype='float32')#reset
        neurons.voltage.assign(tf.multiply(neurons.voltage, not_firing))

        new_voltage = tf.multiply(neurons.voltage, self.decay_factor)#voltage decay
        rnd_act = tf.constant(neurons.get_neuron_vec('uniform', density=0.01), dtype='float32')
        neurons.voltage.assign(tf.add(new_voltage, rnd_act)) #noise


class Input_Behaviour_Tensorflow(Behaviour):

    def set_variables(self, neurons):
        for syn in neurons.afferent_synapses['GLUTAMATE']:
            syn.W = tf.Variable(syn.get_synapse_mat('uniform', density=0.1), dtype='float32')

    def new_iteration(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            W_act_mul = tf.linalg.matvec(synapse.W, tf.cast(synapse.src.spike, dtype='float32'))
            delta_act = tf.divide(W_act_mul, synapse.src.size/10.0)
            neurons.voltage.assign(tf.add(neurons.voltage, delta_act))

My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(1000), behaviour={
    1: Basic_Behaviour_Tensorflow(),
    2: Input_Behaviour_Tensorflow(),
    9: Recorder(tag='my_recorder', variables=['n.voltage.numpy()', 'np.mean(n.voltage.numpy())'])
})

my_syn=SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000, measure_block_time=True)

import matplotlib.pyplot as plt
plt.plot(My_Network['n.voltage.numpy()', 0])
plt.plot(My_Network['np.mean(n.voltage.numpy())', 0], color='black')
plt.show()

import matplotlib.pyplot as plt
plt.scatter(My_Neurons.x, My_Neurons.y)
plt.show()

from PymoNNto.Exploration.Network_UI import *
my_UI_modules = get_default_UI_modules(['voltage.numpy()'], ['W.numpy()'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
