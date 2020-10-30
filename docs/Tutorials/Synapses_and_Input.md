# Synapses and Input

We can add more behaviour modues to make the activity of the neurons more complex. Here the module `Input_Behaviour` is added. In `set_variables` the synapse matrix is created, which stores one weight-value from each neuron to each neuron. The Function `new_iteration` defines how the information is propagated to each neuron (dot product) and adds some term for random input. 
The for loops are not neccessary here, because we only have one SynapseGroup. This solution, however, also works with multiple Neuron- and SynapseGroups. With `synapse.src` and `synapse.dst` you can access the source and destination NeuronGroups assigned to a SynapseGroup.

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

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={
    1: Basic_Behaviour(),
    2: Input_Behaviour(),
    9: NeuronRecorder(tag='my_recorder', variables=['n.activity', 'np.mean(n.activity)'])
})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000)



import matplotlib.pyplot as plt
plt.plot(My_Network['n.activity', 0])
plt.plot(My_Network['np.mean(n.activity)', 0], color='black')
plt.show()
```

![User interface example](https://raw.githubusercontent.com/gitmv/Self-Organizing-Recurrent-Network-Simulator/Images/input.png)