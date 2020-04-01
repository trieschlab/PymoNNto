import sys
sys.path.append('../../')

#from NetworkBehaviour.Input.TREN.Lines import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Testing.Example_Easy.Easy_Neuron_Behaviour import *
import Exploration.UI.SORN_UI.SORN_UI as SUI
from Exploration.UI.SORN_UI.Tabs.SORN_activity_tab import *
from Exploration.UI.SORN_UI.Tabs.SORN_UI_Sidebar_activity import *

number_of_neurons = 900

Easy_Network = Network()

Easy_Neurons = NeuronGroup(net=Easy_Network, tag='neurons', size=get_squared_dim(number_of_neurons), behaviour={
        1: Easy_neuron_initialize(),
        2: Easy_neuron_collect_input(),
        3: Easy_neuron_generate_output(threshold=0.1)
    })

SynapseGroup(net=Easy_Network, src=Easy_Neurons, dst=Easy_Neurons, tag='GLUTAMATE', connectivity='(s_id!=d_id)*in_box(10)')

Easy_Network.initialize(info=False)

SUI.SORN_UI(Easy_Network, label='Easy_Network', group_display_count=1, modules=[
    SORN_UI_sidebar_activity(1),
    SORN_activity_tab(['output','activation','TH'])
]).show()