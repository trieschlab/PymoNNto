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
        self.inc = self.get_init_attr('inc', 1)
        neurons.count = neurons.get_neuron_vec()
    def new_iteration(self, neurons):
        neurons.count += self.inc

v = 1

def test_basics():
    set_genome({'I':1})

    #basic network
    My_Network = Network()
    My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={
        1: Counter(inc='[2#I]'),
        2: Recorder(variables=['n.count'])
    })
    My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

    sm = StorageManager('test', random_nr=False, print_msg=False)

    My_Network.initialize(storage_manager=sm)
    My_Network.simulate_iterations(1000)

    My_Network.deactivate_behaviours('Counter')
    My_Network.simulate_iterations(10)

    My_Network.activate_behaviours('Counter')
    My_Network.simulate_iterations(20)

    My_Network.recording_off()
    My_Network.simulate_iterations(30)

    assert My_Network.iteration == 1000+10+20+30
    assert np.mean(My_Neurons.count) == 1000+20+30

    assert My_Synapses.src == My_Neurons
    assert My_Synapses.dst == My_Neurons

    assert My_Neurons.afferent_synapses['GLUTAMATE'] == [My_Synapses]

    assert len(My_Network.all_objects()) == 3

    #tagging system
    assert My_Network['my_neurons'] == [My_Neurons]
    assert len(My_Network['n.count', 0]) == My_Network.iteration-30

    My_Network.clear_recorder()
    assert len(My_Neurons['n.count', 0]) == 0

    assert My_Network.tag_shortcuts['my_neurons'] == My_Network['my_neurons']

    #Storage Manager
    assert os.path.isfile('Data/StorageManager/test/test/config.ini')
    sm.save_param('k', 'v')
    assert sm.load_param('k') == 'v'

    My_Neurons.count *= 0
    My_Neurons.remove_behaviour('Counter')
    My_Network.simulate_iterations(10)
    assert np.mean(My_Neurons.count) == 0

    My_Neurons.add_behaviour(0.5, Counter(inc='2'), initialize=True)
    My_Network.simulate_iterations(10)
    assert np.mean(My_Neurons.count) == 2*10

    My_Neurons.remove_behaviour('Counter')
    My_Neurons.add_behaviour(4, Counter(inc='2'), initialize=False)
    assert np.mean(My_Neurons.count) == 2*10
