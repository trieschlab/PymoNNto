from PymoNNto.NetworkCore.Network import *
from PymoNNto.NetworkCore.Behaviour import *
from PymoNNto.NetworkCore.Neuron_Group import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.NetworkBehaviour.Structure.Structure import *
from PymoNNto.NetworkBehaviour.Structure.Partition import *
from PymoNNto.NetworkBehaviour.Structure.Receptive_Fields import *
from PymoNNto.NetworkBehaviour.Recorder.Recorder import *

#from PymoNNto.NetworkBehaviour.Structure.Structure import get_squared_dim

from PymoNNto.Exploration.StorageManager.StorageManager import *


def behaviour_test_environment(behaviour, size=1):
    net = Network(tag='Network')
    ng = NeuronGroup(tag='Neuron', net=net, behaviour={1:behaviour}, size=size)
    return net, ng, behaviour
