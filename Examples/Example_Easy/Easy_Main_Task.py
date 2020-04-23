import sys
sys.path.append('../../')

from NetworkBehaviour.Structure.Structure import *
from NetworkBehaviour.Logic.Example_Simple_Network.Simple_Network_behaviour import *

from Examples.Example_Easy.Behaviour_Task import *

from Exploration.UI.Network_UI.Network_UI import *
from NetworkBehaviour.Input.Images.Lines import *
source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)


number_of_neurons = 900

Easy_Network = Network()

Easy_Neurons = NeuronGroup(net=Easy_Network, tag='neurons', size=get_squared_dim(number_of_neurons), behaviour={
        1: Easy_neuron_initialize(syn_density=0.5, syn_norm=0.8),
        2: Easy_neuron_collect_input(noise_density=0.1, noise_strength=0.11),
        2.1: external_input(strength=1.0, pattern_groups=[source]),
        3: Easy_neuron_generate_output(threshold=0.1),
        4: Easy_neuron_Refractory(decay='0.8;0.99'),
        5: STDP(eta_stdp=0.001),
        #6: IP()
    })

SynapseGroup(net=Easy_Network, src=Easy_Neurons, dst=Easy_Neurons, tag='GLUTAMATE', connectivity='(s_id!=d_id)')#*in_box(10), partition=True

Easy_Network.initialize(info=False)


Network_UI(Easy_Network, label='Easy Network', group_display_count=1, modules=[
    UI_sidebar_activity_module(1),
    multi_group_plot_tab(['output', 'activity', 'TH', 'refractory_counter']),
    spiketrain_tab(),
    stability_tab(),
    fourier_tab(),
    hist_tab(),
    weight_tab(),
    info_tab(),
    sidebar_image_module(),
    sidebar_fast_forward_module(),
    sidebar_save_load_module()
]).show()
