import sys
sys.path.append('../../')
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from SORNSim.NetworkCore.Neuron_Group import *
from SORNSim.NetworkBehaviour.Logic.EulerEquationModules.EulerClock import *
from SORNSim.NetworkBehaviour.Logic.EulerEquationModules.VariableInitializer import *
from SORNSim.NetworkBehaviour.Logic.EulerEquationModules.Equation import *
from matplotlib.pyplot import *
from SORNSim.Exploration.Network_UI.Network_UI import *
from SORNSim.NetworkBehaviour.Structure.Structure import *











net = Network()

ng = NeuronGroup(net=net, size=get_squared_dim(100), behaviour={
    1: ClockModule(step='1*ms'),
    2: Variable(eq='v=1*mV'),
    3: Variable(eq='tau=100*ms'),
    4: EquationModule(eq='dv/dt=(0*mV-v)/tau'),

    100: Recorder(['n.v', 'n.t'], tag='my_rec')
})

net.initialize(info=False)



my_modules = [
    UI_sidebar_activity_module(add_color_dict={'v': (255, 255, 255)}),
    sidebar_fast_forward_module(),
    sidebar_save_load_module(),
    multi_group_plot_tab(['v']),
    fourier_tab(parameter='v'),
    info_tab(),
]

Network_UI(net, modules=my_modules, label='Differential Equation Test', storage_manager=None, group_display_count=1).show()










