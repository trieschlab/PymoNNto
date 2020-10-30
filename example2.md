# Tensorflow Modules

To speed up SORNSim you can also use Tensorflow

## Tensorflow Code

`pip install SORNSim`

### Basic Code Structure

The following code creates a network of 100 neurons with recurrent connections and simulates them for 1000 iterations. What is still missing are some behaviour modules. This modules have to be passed to the NeuronGrop to definde what the neurons are supposed to do at each timestep.

```python
from SORNSim import *


```

```python
from SORNSim import *

My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behaviour={})

SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000)
```

