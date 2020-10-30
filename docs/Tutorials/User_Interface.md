### Basic Code Structure - User Interface

If we want to controll and evaluate our model in realtime we can replace the `pyplot` functions, the `recorder` and the `simulate_iterations` with the following Code lines. Similar to the NeuronGroup, the Network_UI is also modular and consists of multiple UI_modules. We can choose them ourselfes or, like in this case, take some default_modules, which should work with most networks. One addition we have to make is to give NeuronGroup some shape with the help of the `get_squared_dim(100)` function, which returns a 10x10 grid `NeuronDimension` object. The neuron-behaviours are not affected by this. The NeuronGroup only receives some additional values like width, height, depth and the vectors x, y, z. The neurons positions can be plotted with `plt.scatter(My_Neurons.x, My_Neurons.y)`



```python
from SORNSim import *


class Input_Behaviour(Behaviour):

  def set_variables(self, neurons):
    for synapse in neurons.afferent_synapses['GLUTAMATE']:
        synapse.W = synapse.get_random_synapse_mat(density=0.1)

  def new_iteration(self, neurons):
    for synapse in neurons.afferent_synapses['GLUTAMATE']:
        neurons.activity += synapse.W.dot(synapse.src.activity)/synapse.src.size

    neurons.activity += neurons.get_random_neuron_vec(density=0.01)



class Basic_Behaviour(Behaviour):

  def set_variables(self, neurons):
    neurons.activity = neurons.get_random_neuron_vec()
    self.decay_factor = 0.99

  def new_iteration(self, neurons):
    neurons.activity *= self.decay_factor



My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behaviour={
    1: Basic_Behaviour(),
    2: Input_Behaviour(),
    9: NeuronRecorder(tag='my_recorder', variables=['n.activity', 'np.mean(n.activity)'])
})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

#My_Network.simulate_iterations(1000)

from SORNSim.Exploration.Network_UI import *
my_UI_modules=get_default_UI_modules(['activity'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()
```


![User interface example](https://raw.githubusercontent.com/gitmv/Self-Organizing-Recurrent-Network-Simulator/Images/UI.png)