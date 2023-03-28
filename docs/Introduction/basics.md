# Basic Code Structure

The following code creates a network of 100 neurons with recurrent connections and simulates them for 1000 iterations. What is still missing are some behavior modules. This modules have to be passed to the NeuronGrop to definde what the neurons are supposed to do at each timestep.


```python
from PymoNNto import *

net = Network()

NeuronGroup(net=net, tag='my_neurons', size=100, behavior={})

SynapseGroup(net=net, src='my_neurons', dst='my_neurons', tag='GLUTAMATE')

net.initialize()

net.simulate_iterations(1000)
```

## Behavior

Each Behavior Module has the following layout where `initialize` is called when the Network is initialized, while
`iteration` is called repeatedly every timestep. `neurons` points to the parent neuron group the behavior belongs to.

In this example we define a variable `activity` and a `decay_factor`. The activity-vector is initialized with random values for each neuron. At each timestep the activity-vector is decreased.


```python
class Basic_Behavior(Behavior):

  def initialize(self, neurons):
    neurons.activity = neurons.vector('uniform')
    self.decay_factor = 0.99

  def iteration(self, neurons):
    neurons.activity *= self.decay_factor
```

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Basic_Behavior.png"><br>

## Simple Example

When we combine the previous code blocks we can add the `Basic_Behavior` to the NeuronGroup.
To plot the neurons activity over time, we also have to create a `Recorder`. Here the activity and the mean-activity are stored at each timestep.
At the end the data is plotted.

PymoNNto has a tagging system to make access to the NeuronGroups, SynapseGroups, Behaviors and recorded variables inside of the network more convenient.

The number in front of each behavior (1 and 9) have to be positive and determine the order of execution for each module inside and accross NeuronGroups.

```python
from PymoNNto import *


class Basic_Behavior(Behavior):

    def initialize(self, neurons):
        neurons.activity = neurons.vector('uniform')
        self.decay_factor = 0.99

    def iteration(self, neurons):
        neurons.activity *= self.decay_factor


net = Network()

NeuronGroup(net=net, tag='my_neurons', size=100, behavior={
    1: Basic_Behavior(),
    9: Recorder(['activity', 'np.mean(activity)'], tag='my_recorder')
})

SynapseGroup(net=net, src='my_neurons', dst='my_neurons', tag='GLUTAMATE')

net.initialize()

net.simulate_iterations(1000)

import matplotlib.pyplot as plt

plt.plot(net['activity', 0])
plt.plot(net['np.mean(activity)', 0], color='black')
plt.show()
```

# Synapses and Input

We can add more behavior modues to make the activity of the neurons more complex. Here the module `Input_Behavior` is added. In `initialize` the synapse matrix is created, which stores one weight-value from each neuron to each neuron. The Function `iteration` defines how the information is propagated to each neuron (dot product) and adds some term for random input. 
The for loops are not neccessary here, because we only have one SynapseGroup. This solution, however, also works with multiple Neuron- and SynapseGroups. With `synapse.src` and `synapse.dst` you can access the source and destination NeuronGroups assigned to a SynapseGroup.

```python
from PymoNNto import *


class Input_Behavior(Behavior):

    def initialize(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            synapse.W = synapse.matrix('uniform', density=0.1)

    def iteration(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            neurons.activity += synapse.W.dot(synapse.src.activity) / synapse.src.size

        neurons.activity += neurons.vector('uniform', density=0.01)


class Basic_Behavior(Behavior):

    def initialize(self, neurons):
        neurons.activity = neurons.vector('uniform')
        self.decay_factor = 0.99

    def iteration(self, neurons):
        neurons.activity *= self.decay_factor


My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behavior={
    1: Basic_Behavior(),
    2: Input_Behavior(),
    9: Recorder(['activity', 'np.mean(activity)'], tag='my_recorder')
})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000)

import matplotlib.pyplot as plt

plt.plot(My_Network['activity', 0])
plt.plot(My_Network['np.mean(activity)', 0], color='black')
plt.show()
```

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Input_Behavior.png"><br>

![User interface example](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/input.png)

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/voltages.png"><img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/spikes.png"><br>
