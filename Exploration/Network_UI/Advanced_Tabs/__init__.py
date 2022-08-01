from PymoNNto.Exploration.Network_UI.Advanced_Tabs.stdp_buffer_tab import *
from PymoNNto.Exploration.Network_UI.Advanced_Tabs.criticality_tab import *
from PymoNNto.Exploration.Network_UI.Advanced_Tabs.buffer_tab import *
from PymoNNto.Exploration.Network_UI.Advanced_Tabs.scatter_tab import *
from PymoNNto.Exploration.Network_UI.Advanced_Tabs.afferent_syn_attr_plot_tab import *
from PymoNNto.Exploration.Network_UI.Advanced_Tabs.similarity_matrix_tab import *

def get_advanced_UI_modules(neuron_parameters=['output'], synapse_parameters=['W']):
    return [
    stdp_buffer_tab(),
    criticality_tab(),
    buffer_tab(),
    scatter_tab(x_var='excitation', y_var='inhibition'),
    afferent_syn_attr_plot_tab(syn_vars=['slow_add', 'fast_add']),
    similarity_matrix_tab()
]