#Normalization

This module can be used to normalize all synapses connected to a NeuronGroup of a given type.
The Normalization module follows a simple logic:
At each time step, we sum the synaptic weights of all synapses selected by a tag, here GLUTAMATE, in the temporary variable temp_weight_sum.
Then, we use this variable to normalize the weights.
If the normalized sum of weights should be other than one, we can use the scaling variable norm_factor.

Because the normalization can include multiple synapse groups, summation and division is performed during for-loops.
To avoid division by zero, each calculated normalization value is increased by one if it is zero before the scaled normalization is applied.

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Normalization_beh.png"><br>

```python

from PymoNNto.NetworkCore.Behaviour import *

class Normalization(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Normalization')
        self.syn_type = self.get_init_attr('syn_type', 'GLUTAMATE', neurons)
        self.norm_factor = self.get_init_attr('norm_factor', 1.0, neurons)
        neurons.temp_weight_sum = neurons.get_neuron_vec()

    def new_iteration(self, neurons):

        neurons.temp_weight_sum *= 0.0

        for s in neurons.afferent_synapses[self.syn_type]:
            s.dst.temp_weight_sum += np.sum(np.abs(s.W), axis=1)

        neurons.temp_weight_sum /= self.norm_factor

        for s in neurons.afferent_synapses[self.syn_type]:
            s.W = s.W / (s.dst.temp_weight_sum[:, None] + (s.dst.temp_weight_sum[:, None] == 0))

```