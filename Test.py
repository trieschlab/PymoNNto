from SORNSim import *


class Input_Behaviour(Behaviour):

  def set_variables(self, neurons):
    for synapse in neurons.afferent_synapses['GLUTAMATE']:
        synapse.W = synapse.get_random_synapse_mat(density=0.1)

  def new_iteration(self, neurons):
    for synapse in neurons.afferent_synapses['GLUTAMATE']:
        neurons.activity += synapse.W.dot(synapse.src.activity)/synapse.src.size

    neurons.activity += neurons.get_random_neuron_vec(density=0.01)



class Basic_Behaviour(Behaviour):

  def set_variables(self, neurons):
    neurons.activity = neurons.get_random_neuron_vec()
    self.decay_factor = 0.9

  def new_iteration(self, neurons):
    neurons.activity *= self.decay_factor



My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behaviour={
    1: Basic_Behaviour(),
    2: Input_Behaviour(),
    9: Recorder(tag='my_recorder', variables=['n.activity', 'np.mean(n.activity)'])
})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

#My_Network.simulate_iterations(1000)

#import matplotlib.pyplot as plt
#plt.scatter(My_Neurons.x, My_Neurons.y)
#plt.show()

from SORNSim.Exploration.Network_UI import *
from Tab_Test import *
my_UI_modules = [MyUITab()] + get_default_UI_modules(['activity'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
