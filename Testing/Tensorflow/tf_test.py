import sys
sys.path.append('../../')
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from SORNSim.NetworkCore.Neuron_Group import *
from SORNSim.NetworkBehaviour.Logic.TensorflowModules.test import *
from matplotlib.pyplot import *
from SORNSim.Exploration.Network_UI.Network_UI import *
from SORNSim.NetworkBehaviour.Structure.Structure import *



#print('\r\n\r\nNumpy Version:')

#net = Network()

#ng = NeuronGroup(net=net, size=1000000, behaviour={
#    1: TestModuleNumpy(),
#})
#net.initialize(info=False)
#net.simulate_iterations(1000, batch_size=1000, measure_block_time=True)


#print('\r\n\r\nTensorflow Version:')

net = Network()
ng = NeuronGroup(net=net, size=get_squared_dim(100000), behaviour={
    1: TestModuleTensorflow(),
})
mask = np.zeros(ng.size)
mask[1] = 1
mask[5] = 1
sub_ng = ng.subGroup(mask)

net.initialize(info=False)

#sub_ng.voltage = [5, 1]

#print(np.array(ng.voltage))

#net.simulate_iterations(1000, batch_size=1000, measure_block_time=True)

my_modules = [
    UI_sidebar_activity_module(add_color_dict={'voltage': (255, 255, 255)}),
    sidebar_fast_forward_module(),
    sidebar_save_load_module(),
    multi_group_plot_tab(['voltage']),
    #fourier_tab(parameter='voltage'),
    info_tab(),
]

Network_UI(net, modules=my_modules, label='Tensorflow Test', storage_manager=None, group_display_count=1).show()




