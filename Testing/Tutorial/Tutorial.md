How to create a simple Neural Network?<br>

1. First create a main file (for example Testing/My_Network/my_network_main.py) and import the Network Core components.

```python
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkCore.Neuron_Group import *
from NetworkBehaviour.Structure.Structure import *
```

2. Create a "Network" object where all the Neuron- and Synapse-Groups are attached to.
```python
My_Network = Network()
```

3. Create one or more NeuronGroups, give them a unique tag and pass the previously created Network object to them (net=My_Network), which will add the Neuron Group automatically to the Network.
The get_squared_dim() function returns a NeuronDimension(width=w, height=h, depth=d) object with similar with and height proportions. 
The NeuronDimension class positions the neurons on a grid, which can later be accessed by calling neuron_group.x, neuron_group.y and neuron_group.z. 
It is possible create neurons without a x,y,z parameter by just passing size=number_of_neurons to the constructor, but x,y,z coordinates are an essential requirement for the UI.

```python
number_of_neurons = 900
My_Neurons = NeuronGroup(net=My_Network, tag='neuron_tag', size=get_squared_dim(number_of_neurons), behaviour={})
```

4. In the next step SynapseGroup objects are created to define, which NeuronGroups can form connections to another Neuron Group.
"src=My_Neurons, dst=My_Neurons" means that the NeuronGroup can form recurrent connections to itself.
The "connectivity" parameter is optional and lets you set constraint to the connectivity. "(s_id!=d_id)" mean, that a neuron can not form a connection to itself, while in_box(10)/in_circle(10) means, that each neuron can only connect to other neurons in its receptive field (a box with size 21x21/ a circle with r=10).
The "connectivity" parameter creates a mask stored in (synapse_group.enabled).
To differentiate between different synapse types, you should define a tag (for example 'GLUTAMATE' or 'GABA') and set it to the SynapseGroup

```python
sg=SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE,recurrent', connectivity='(s_id!=d_id)*in_box(10)')
sg.W = sg.get_random_synapse_mat()
```

5. After this, the Network has to be initialized.

```python
My_Network.initialize()
```

6. What is missing are the behaviours of the NeuronGroups, so the next step is to create a class (for example My_Behaviour).

```python
from NetworkBehaviour.Basics.BasicNeuronBehaviour import *

class My_Behaviour(Neuron_Behaviour):

  def set_variables(self, neurons):
    return
    
  def new_iteration(self, neurons):
    return
```

7. "set_variables" is called when the network is initialized. you can also give it a tag, to make later access easier. 
Then you can define the variables of the behaviour. 
Local variables, which are only used by the Behaviour itself can be added with "self.my_var=...". 
If the variables are supposed to be accessed by other Behaviours of the same group you can add them with "neurons.my_var2=...".
"neurons.get_neuron_vec()" is equivalent to "np.zeros(neurons.size)" and returns a vector with a number for each neuron.
"self.get_init_attr('noise_density', 0.01, neurons)" lets you collect the parameters you passed to the Behaviours constructor. 
The first parameter is the name of the parameter, the second the default value of the parameter in case nothin is defined in the constructor and neurons is the current neuron group.
"get_init_attr" also provides additional functionality to give different parameters to each single neuron. By passing a the string '0.01;0.1' the function returns a vector with a value uniformly chosen between 0.01 and 0.1. you can also pass the string "lognormal(...)" or any other distribution from the "numpy.random..." package. Adding ";plot" to the parameter you can also plot your current distrubution.

```python
def set_variables(self, neurons):
  self.add_tag('My_Behaviour')
  neuron.output=neurons.get_neuron_vec()
  self.noise_density = self.get_init_attr('noise_density', 0.01, neurons)
```

8. "new_iteration" is called every timestep of the simulation. Here the Behaviour is created, so that each neuron has a random output with some chance at each timestep.

```python
def new_iteration(self, neurons):
  neuron.output = neurons.get_random_neuron_vec(density=self.noise_density)
```

9. Now the bahaviour has to be passed to the previously created NeuronGroup.

```python
My_Neurons = NeuronGroup(... behaviour={
  1: My_Behaviour(noise_density=0.02)
})
```

10. To simulate one or many iteration of the simulation you have to call:

```python
My_Network.simulate_iteration()
#or
My_Network.simulate_iterations(iterations=1000)
```

11. If you want an interactive UI to evaluate what the network is doing you have to add the following code after the Network is initialized:

```python
import Exploration.UI.Network_UI.Network_UI as NUI

NUI.Network_UI(My_Network, label='My Network', group_display_count=1).show()
```
