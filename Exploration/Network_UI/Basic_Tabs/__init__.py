
from PymoNNto.Exploration.Network_UI.Basic_Tabs.sidebar_fast_forward_module import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.sidebar_save_load_module import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.multi_group_plot_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.hist_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.info_tabs import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.single_group_plot_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.stability_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.weight_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.fourier_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.partition_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.spiketrain_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.individual_weight_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.PCA_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.isi_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.code_execution_tab import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.module_visualizer_tab import *

from PymoNNto.Exploration.Network_UI.Basic_Tabs.sidebar_neuron_grid import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.Analysis_Module_tab import *

from PymoNNto.Exploration.Network_UI.Basic_Tabs.event_tab import *


def get_default_UI_modules(neuron_parameters=['output'], synapse_parameters=['W']):
    return [
    UI_sidebar_neuron_grid_module(1, neuron_parameters[0]),
    multi_group_plot_tab(neuron_parameters),#['output', 'TH', 'weight_norm_factor', 'nox', 'refractory_counter']
    spiketrain_tab(parameter=neuron_parameters[0]),
    weight_tab(weight_attrs=synapse_parameters),#, 'W_temp', 'W_stable'
    partition_tab(),
    PCA_tab(parameter=neuron_parameters[0]),
    #individual_weight_tab(),
    isi_tab(param=neuron_parameters[0]),
    hist_tab(weight_attr=synapse_parameters[0]),
    single_group_plot_tab(neuron_parameters),#, 'excitation':(0, 0, 255), 'inhibition':(255, 0, 0), 'input_act':(255, 0, 255), 'TH':(0, 255, 0)}),
    stability_tab(parameter=neuron_parameters[0]),
    fourier_tab(parameter=neuron_parameters[0]),
    Analysis_Module_tab(),
    info_tab(),
    sidebar_fast_forward_module(),
    sidebar_save_load_module(),
    code_execution_tab(),
    event_tab(),
    #module_visualizer_tab()
]

def get_modules_dict(*args): #get_modules_dict([m1,m2,m3],m4,[m5],{1:m6,2:m7},...)
    result = {}



    for arg in args:
        if type(arg) is list:
            for a in arg:
                result[a.__class__] = a

        elif type(arg) is dict:
            for k in arg:
                result[arg[k].__class__] = arg[k]

        else:
            result[arg.__class__] = arg


    #for module in modules:
    #    result[module.__class__.__name__] = module
    return result