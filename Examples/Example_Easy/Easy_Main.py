import sys
sys.path.append('../../')

from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from NetworkBehaviour.Logic.Example_Simple_Network.Simple_Network_behaviour import *
from Exploration.UI.Network_UI.Network_UI import *

number_of_neurons = 900

Easy_Network = Network()

Easy_Neurons = NeuronGroup(net=Easy_Network, tag='neurons', size=get_squared_dim(number_of_neurons), behaviour={
        1: Easy_neuron_initialize(syn_density=0.05, syn_norm=1.0),
        2: Easy_neuron_collect_input(noise_density=0.01, noise_strength=0.11),
        3: Easy_neuron_generate_output(threshold=0.1),
        4: Easy_neuron_Refractory(decay='0.8;0.99')
    })

SynapseGroup(net=Easy_Network, src=Easy_Neurons, dst=Easy_Neurons, tag='GLUTAMATE', connectivity='(s_id!=d_id)*in_box(10)')

Easy_Network.initialize(info=False)

Network_UI(Easy_Network, label='Easy Network', group_display_count=1).show()
