from PymoNNto import *
from Examples_Paper.STDP_Hom_Norm.Normalization import *
from Examples_Paper.STDP_Hom_Norm.STDP import *
from Examples_Paper.STDP_Hom_Norm.Homeostasis import *

class Basic_Behavior(Behavior):

    def initialize(self, neurons):
        neurons.voltage = neurons.vector('uniform')
        self.leak_factor = 0.9

    def iteration(self, neurons):
        neurons.voltage *= self.leak_factor

class Input_Behavior(Behavior):

    def initialize(self, neurons):
        for synapse in neurons.synapses(afferent, 'GLUTAMATE'):
            synapse.W = synapse.matrix('uniform', density=0.1)

    def iteration(self, neurons):
        for synapse in neurons.synapses(afferent, 'GLUTAMATE'):
            neurons.voltage += synapse.W.dot(synapse.src.voltage)/synapse.src.size

        neurons.voltage += neurons.vector('uniform',density=0.01)

My_Network = Network()

My_Neurons1 = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behavior={
    1: Basic_Behavior(),
    2: Input_Behavior(),
    3: Homeostasis(target_voltage=0.05),
    4: STDP(stdp_factor=0.00015),
    5: Normalization(norm_factor=10),
    9: Recorder(['voltage', 'np.mean(voltage)'], tag='my_recorder')
})

my_syn = SynapseGroup(net=My_Network, src=My_Neurons1, dst=My_Neurons1, tag='GLUTAMATE')
My_Neurons1.z+=1.0+np.random.rand(My_Neurons1.size)-0.5

My_Neurons2 = NeuronGroup(net=My_Network, tag='my_neurons2', size=get_squared_dim(100), behavior={
    1: Basic_Behavior(),
    2: Input_Behavior(),
    3: Homeostasis(target_voltage=0.05),
    4: STDP(stdp_factor=0.00015),
    5: Normalization(norm_factor=10),
    9: Recorder(['voltage', 'np.mean(voltage)'], tag='my_recorder')
})

My_Neurons2['structure',0].stretch_to_equal_size(My_Neurons1)

My_Neurons2.z+=-1.0+np.random.rand(My_Neurons2.size)-0.5
My_Neurons2.color=(255,0,0,255)

my_syn = SynapseGroup(net=My_Network, src=My_Neurons2, dst=My_Neurons2, tag='GLUTAMATE')

My_Network.initialize()

my_syn.enabeled = my_syn.W > 0

My_Network.simulate_iterations(1000)

import matplotlib.pyplot as plt
plt.plot(My_Network['n.voltage', 0])
plt.plot(My_Network['np.mean(n.voltage)', 0], color='black')
plt.show()

import matplotlib.pyplot as plt
plt.scatter(My_Neurons1.x, My_Neurons1.y)
plt.show()

from PymoNNto.Exploration.Network_UI import *
from Examples_Paper.Basic.Basic_Tab import *
from Examples_UI.OpenGLTab import *
#+ [OpenGLTab()]

my_UI_modules = [MyUITab()] + get_default_UI_modules(['voltage', 'exhaustion'], ['W'])+ [OpenGLTab()]
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=2).show()