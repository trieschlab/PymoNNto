from PymoNNto import *

class Basic_Behaviour(Behaviour):

    def set_variables(self, neurons):
        neurons.voltage = neurons.get_neuron_vec()
        self.threshold = 0.5
        self.leak_factor = self.get_init_attr('leak_factor', 0.9, neurons)

    def new_iteration(self, neurons):
        firing = neurons.voltage > self.threshold
        neurons.spike = firing.astype(def_dtype) #spikes
        neurons.voltage[firing] = 0.0 #reset

        neurons.voltage *= self.leak_factor #voltage decay
        neurons.voltage += neurons.get_neuron_vec('uniform',density=0.01) #noise

class Input_Behaviour(Behaviour):

    def set_variables(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            synapse.W = synapse.get_synapse_mat('uniform', density=0.1)
            synapse.enabled = synapse.W > 0

    def new_iteration(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            neurons.voltage += synapse.W.dot(synapse.src.spike)/synapse.src.size*10



My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behaviour={
    1: Basic_Behaviour(),
    2: Input_Behaviour(),
    9: Recorder(tag='my_recorder', variables=['n.voltage', 'np.mean(n.voltage)']),
    10: EventRecorder(tag='my_event_recorder', variables=['n.spike'])
})

My_Neurons.visualize_module()

my_syn = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

#my_syn.enabeled = my_syn.W > 0

My_Network.simulate_iterations(200, measure_block_time=True)

import matplotlib.pyplot as plt
plt.plot(My_Network['n.voltage', 0, 'np'][:, 0:10])
plt.plot(My_Network['np.mean(n.voltage)', 0], color='black')
plt.axhline(My_Neurons['Basic_Behaviour', 0].threshold, linestyle='dashed')
plt.xlabel('iterations (ms)')
plt.ylabel('voltage')
plt.show()

plt.plot(My_Network['n.spike.t', 0], My_Network['n.spike.i', 0], '.k')
plt.xlabel('iterations (ms)')
plt.ylabel('neuron index')
plt.show()

from PymoNNto.Exploration.Network_UI import *
from Examples_Paper.Basic.Basic_Tab import *
my_UI_modules = [MyUITab()] + get_default_UI_modules(['voltage', 'spike'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
