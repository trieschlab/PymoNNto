from NetworkCore.Network import *
from NetworkCore.Behaviour import *
from NetworkCore.Neuron_Group import *
from NetworkCore.Synapse_Group import *
from NetworkCore.Analysis_Module import *

from Exploration.HelperFunctions import *
from Exploration.StorageManager.StorageManager import *

class counter(Behaviour):
    def set_variables(self, neurons):
        neurons.count = neurons.get_neuron_vec()
    def new_iteration(self, neurons):
        neurons.count += 1


def test_basics():
    #basic network
    My_Network = Network()
    My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={
        1:counter()
    })
    My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')
    My_Network.initialize()
    My_Network.simulate_iterations(1000)

    assert My_Network.iteration == 1000
    assert np.sum(My_Neurons.count) == My_Neurons.size*1000

    assert My_Synapses.src == My_Neurons
    assert My_Synapses.dst == My_Neurons

    assert My_Neurons.afferent_synapses['GLUTAMATE'] == [My_Synapses]

    #tagging system
    assert My_Network['my_neurons']==[My_Neurons]