import sys
sys.path.append('../../')
import time

t=time.time()

from PymoNNto import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs import *
from NetworkBehaviour.EulerEquationModules.VariableInitializer import *
from NetworkBehaviour.EulerEquationModules.Equation import *
from NetworkBehaviour.EulerEquationModules.EulerClock import *
from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.NetworkBehaviour.Structure.Structure import *





net = Network()

ng = NeuronGroup(net=net, size=get_squared_dim(100), behaviour={
    1: Clock(step='1*ms'),
    2: Variable(eq='v=1*mV'),
    3: Variable(eq='tau=100*ms'),
    4: Equation(eq='dv/dt=(0*mV-v)/tau'),

    9: Recorder(['n.v', 'n.t'], tag='my_rec')
})

net.initialize()



my_modules = [
    UI_sidebar_activity_module(add_color_dict={'v': (255, 255, 255)}),
    sidebar_fast_forward_module(),
    sidebar_save_load_module(),
    multi_group_plot_tab(['v']),
    fourier_tab(parameter='v'),
    info_tab(),
]

Network_UI(net, modules=my_modules, label='Differential Equation Test', group_display_count=1).show()










