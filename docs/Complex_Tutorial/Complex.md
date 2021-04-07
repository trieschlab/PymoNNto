# Complex Example Implementation

The following network utilizes the Homeostasis, the Normalization and the STDP behaviour from the current section.

```python
from PymoNNto import *
from Examples_Paper.STDP_Hom_Norm.Normalization import *
from Examples_Paper.STDP_Hom_Norm.STDP import *
from Examples_Paper.STDP_Hom_Norm.Homeostasis import *

class Basic_Behaviour(Behaviour):

    def set_variables(self, neurons):
        neurons.voltage = neurons.get_random_neuron_vec()
        self.leak_factor = 0.9

    def new_iteration(self, neurons):
        neurons.voltage *= self.leak_factor

class Input_Behaviour(Behaviour):

    def set_variables(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            synapse.W = synapse.get_random_synapse_mat(density=0.1)

    def new_iteration(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            neurons.voltage += synapse.W.dot(synapse.src.voltage)/synapse.src.size

        neurons.voltage += neurons.get_random_neuron_vec(density=0.01)

My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behaviour={
    1: Basic_Behaviour(),
    2: Input_Behaviour(),
    3: Homeostasis(target_voltage=0.05),
    4: STDP(stdp_factor=0.00015),
    5: Normalization(norm_factor=10),
    9: Recorder(tag='my_recorder', variables=['n.voltage', 'np.mean(n.voltage)'])
})

my_syn = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

my_syn.enabeled = my_syn.W > 0

My_Network.simulate_iterations(1000)

import matplotlib.pyplot as plt
plt.plot(My_Network['n.voltage', 0])
plt.plot(My_Network['np.mean(n.voltage)', 0], color='black')
plt.show()

import matplotlib.pyplot as plt
plt.scatter(My_Neurons.x, My_Neurons.y)
plt.show()

from PymoNNto.Exploration.Network_UI import *
from Examples_Paper.Basic.Basic_Tab import *

my_UI_modules = [MyUITab()] + get_default_UI_modules(['voltage', 'exhaustion'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
```