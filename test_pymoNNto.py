from PymoNNto.NetworkCore.Network import *
from PymoNNto.NetworkCore.Behaviour import *
from PymoNNto.NetworkCore.Neuron_Group import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.NetworkCore.Analysis_Module import *

from PymoNNto.Exploration.HelperFunctions import *
from PymoNNto.Exploration.StorageManager.StorageManager import *

import os

class Counter(Behaviour):
    def set_variables(self, neurons):
        neurons.count = neurons.get_neuron_vec()
    def new_iteration(self, neurons):
        neurons.count += 1


def test_basics():
    #basic network
    My_Network = Network()
    My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={
        1: Counter(),
        2: Recorder(variables=['n.count'])
    })
    My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

    sm = StorageManager('test', random_nr=False, print_msg=False)

    My_Network.initialize(storage_manager=sm)
    My_Network.simulate_iterations(1000)

    assert My_Network.iteration == 1000
    assert np.sum(My_Neurons.count) == My_Neurons.size*1000

    assert My_Synapses.src == My_Neurons
    assert My_Synapses.dst == My_Neurons

    assert My_Neurons.afferent_synapses['GLUTAMATE'] == [My_Synapses]

    #tagging system
    assert My_Network['my_neurons'] == [My_Neurons]
    assert len(My_Neurons['n.count', 0]) == 1000

    #Storage Manager
    assert os.path.isfile('Data/StorageManager/test/test/config.ini')
    sm.save_param('k', 'v')
    assert sm.load_param('k') == 'v'