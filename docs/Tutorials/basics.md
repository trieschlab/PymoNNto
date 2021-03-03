# Basic Code Structure

The following code creates a network of 100 neurons with recurrent connections and simulates them for 1000 iterations. What is still missing are some behaviour modules. This modules have to be passed to the NeuronGrop to definde what the neurons are supposed to do at each timestep.


```python
from PymoNNto import *

My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000)
```

## Behaviour

Each Behaviour Module has the following layout where `set_variables` is called when the Network is initialized, while
`new_iteration` is called repeatedly every timestep. `neurons` points to the parent neuron group the behaviour belongs to.

In this example we define a variable `activity` and a `decay_factor`. The activity-vector is initialized with random values for each neuron. At each timestep the activity-vector is decreased.


```python
class Basic_Behaviour(Behaviour):

  def set_variables(self, neurons):
    neurons.activity = neurons.get_random_neuron_vec()
    self.decay_factor = 0.99

  def new_iteration(self, neurons):
    neurons.activity *= self.decay_factor
```

## Simple Example

When we combine the previous code blocks we can add the `Basic_Behaviour` to the NeuronGroup.
To plot the neurons activity over time, we also have to create a `Recorder`. Here the activity and the mean-activity are stored at each timestep.
At the end the data is plotted.

PymoNNto has a tagging system to make access to the NeuronGroups, SynapseGroups, Behaviours and recorded variables inside of the network more convenient.

The number in front of each behaviour (1 and 9) have to be positive and determine the order of execution for each module inside and accross NeuronGroups.

```python
from PymoNNto import *


class Basic_Behaviour(Behaviour):

  def set_variables(self, neurons):
    neurons.activity = neurons.get_random_neuron_vec()
    self.decay_factor = 0.99

  def new_iteration(self, neurons):
    neurons.activity *= self.decay_factor



My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={
    1: Basic_Behaviour(),
    9: Recorder(tag='my_recorder', variables=['n.activity', 'np.mean(n.activity)'])
})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000)



import matplotlib.pyplot as plt
plt.plot(My_Network['n.activity', 0])
plt.plot(My_Network['np.mean(n.activity)', 0], color='black')
plt.show()
```
![User interface example](https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/both.png)

## Tagging System

To access the tagged objects we can use the `[]` operator. `['my_tag']` gives you a list of all objects tagged with `my_tag`. Here are some examples:

```python
My_Network['my_neurons']
=> [<PymoNNto.NetworkCore.Neuron_Group.NeuronGroup object at 0x00000195F4878670>]

My_Network['my_recorder']
My_Neurons['my_recorder'] 
=> [<PymoNNto.NetworkBehaviour.Recorder.Recorder.Recorder object at 0x0000021F1B61D5E0>]

My_Neurons['n.activity']
My_Neurons['my_recorder', 0]['n.activity']
=> [[array(data iteration 1), array(data iteration 2), array(data iteration 3), ...]]

My_Neurons['n.activity', 0] 
is equivalent to 
My_Neurons['n.activity'][0] 
```