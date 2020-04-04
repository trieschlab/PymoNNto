import sys
sys.path.append('../../')

from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from NetworkBehaviour.Logic.Example_Simple_Network.Simple_Network_behaviour import *
import Exploration.UI.Network_UI.Network_UI as NUI
from Exploration.UI.Network_UI.Tabs.activity_tab import *
from Exploration.UI.Network_UI.Tabs.sidebar_activity_module import *
from Exploration.UI.Network_UI.Tabs.spiketrain_tab import *
from Exploration.UI.Network_UI.Tabs.fourier_tab import *
from Exploration.UI.Network_UI.Tabs.weight_tab import *
from Exploration.UI.Network_UI.Tabs.sidebar_fast_forward_module import *
from Exploration.UI.Network_UI.Tabs.sidebar_save_load_module import *
from Exploration.UI.Network_UI.Tabs.stability_tab import *
from Exploration.UI.Network_UI.Tabs.hist_tab import *

number_of_neurons = 900

Easy_Network = Network()

Easy_Neurons = NeuronGroup(net=Easy_Network, tag='neurons', size=get_squared_dim(number_of_neurons), behaviour={
        1: Easy_neuron_initialize(syn_density=0.05),
        2: Easy_neuron_collect_input(noise_density=0.1, noise_strength=0.11),
        3: Easy_neuron_generate_output(threshold=0.1),
        4: Easy_neuron_Refractory(decay='0.8;0.99')
    })

SynapseGroup(net=Easy_Network, src=Easy_Neurons, dst=Easy_Neurons, tag='GLUTAMATE', connectivity='(s_id!=d_id)*in_box(10)')

Easy_Network.initialize(info=False)

NUI.Network_UI(Easy_Network, label='Easy Network', group_display_count=1, modules=[
    UI_sidebar_activity_module(1),
    activity_tab(['output', 'activation', 'TH', 'refractory_counter']),
    spiketrain_tab(),
    stability_tab(),
    fourier_tab(),
    hist_tab(),
    weight_tab(),
    info_tab(),
    sidebar_fast_forward_module(),
    sidebar_save_load_module()
]).show()
