import numpy as np
from PymoNNto.NetworkCore.Network import *
from PymoNNto.NetworkCore.Behaviour import *
from PymoNNto.NetworkCore.Neuron_Group import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.NetworkCore.Analysis_Module import *
from PymoNNto.NetworkBehaviour.Structure.Structure import *
from PymoNNto.NetworkBehaviour.Structure.Partition import *
from PymoNNto.NetworkBehaviour.Structure.Receptive_Fields import *
from PymoNNto.NetworkBehaviour.Recorder.Recorder import *
from PymoNNto.Exploration.HelperFunctions import *
from PymoNNto.Exploration.StorageManager.StorageManager import *

#convenience functions:

#add root project folder to import path
add_project_root_path()

#print numpy arrays with commas for easier copy paste
np.set_string_function(lambda x: repr(x), repr=False) 