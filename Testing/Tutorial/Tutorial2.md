How process synaptic transmission and more complex behaviour.<br>

After we created some randomly spiking neurons we can extend the Network with more complex behaviour.
Because the SynapseGroup are completely useless in the previous example, we will now create a NeuronGroup with behaviours that initialize and use the synaptic weights.

1. First we create an initialization behaviour for the NeuronGroup:

```python
class Easy_neuron_initialize(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_initialize')

        #create neuron group variables
        neurons.activity = neurons.get_neuron_vec()
        neurons.output = neurons.get_neuron_vec()

        #create random synapse weights
        syn_density = self.get_init_attr('syn_density', 0.1, neurons)
        for synapse_group in neurons.afferent_synapses['GLUTAMATE']:
            synapse_group.W = synapse_group.get_random_synapse_mat(density=syn_density)
            synapse_group.enabled *= synapse_group.W>0 #extend the SynapseGroup mask so that all synapses, that are 0 right now will never be able to grow.

        #norm all the synapses accross all afferent synapse groups so that all the "GLUTAMATE" tagged synapses weights add up to neurons.syn_norm
        neurons.syn_norm = self.get_init_attr('syn_norm', 0.8, neurons)
        self.normalize_synapse_attr('W', 'W', neurons.syn_norm, neurons, 'GLUTAMATE')

    def new_iteration(self, neurons):
        neurons.activity *= 0.0
```

2. Now we need a Behaviour, which changes the neurons activity by collecting the input from all the Synapses and adds some noise:<br>
Note that it is better to write "s.dst.activity += ..." instead of "neurons.activity += ...". In most cases both is equivalent but the NeuronGroup object can be partitioned into SubNeuronGroups for increasing the Performance. In his case "neurons.var" would point to the whole vector of the group, while s.dst.var would apply call some masking (neurons.var[mask]) fist.

```python
class Easy_neuron_collect_input(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_collect_input')
        neurons.sensitivity = self.get_init_attr('sensitivity', 1.0, neurons)
        neurons.noise_density = self.get_init_attr('noise_density', 0.01, neurons)
        neurons.noise_strength = self.get_init_attr('noise_strength', 0.1, neurons)

    def new_iteration(self, neurons):
        #collect input from Synapses
        for s in neurons.afferent_synapses['GLUTAMATE']:
            s.dst.activity += s.W.dot(s.src.output)*neurons.sensitivity

        #add random noise
        neurons.activity += neurons.get_random_neuron_vec(density=neurons.noise_density)*neurons.noise_strength
```

3. To produce an output based on the current activity of the neurons we want to apply a threshold function so that the neuron outputs a 1(spike) or a 0.

```python
class Easy_neuron_generate_output(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_generate_output')
        neurons.TH = self.get_init_attr('threshold', 0.1, neurons)

    def new_iteration(self, neurons):
        neurons.output = (neurons.activity > (neurons.TH+neurons.refractory_counter)).astype(np.float64)
```

4. With the previous mechanisms the network can easily be trapped in a state, where all neurons are firing at every timestep. To prevent that we need to add some stabilizing mechanisms.
There are many biological plausible stabilizing mechanisms in real neurons for Example: <br>
SynapticScaling (scale all the synapses up and down with some factor after normalization), <br>
Intrinsic Plasticity (increase and decrease firingthreshold of neurons), <br>
Temporal Weights (parts of synaptic weights return to baseline after some time), <br>
Interneuron Inhibition (Inhibition keeps activity under control) or some <br>
Refractory Period (neuron needs some time to fire again).<br>

Here we will add a simple refractory period to the neurons, which is increased by 1 when the neuron is firing and decays with some factor.

```python
class Easy_neuron_Refractory(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_Refractory')
        neurons.refractory_counter = neurons.get_neuron_vec()
        self.decay = self.get_init_attr('decay', 0.9, neurons)

    def new_iteration(self, neurons):
        neurons.refractory_counter *= self.decay
        neurons.refractory_counter += neurons.output
```

5. Now we have to add the 4 mechanisms to the NeuronGroup defined in the previous ...Main.py file.
 

```python
... = NeuronGroup(..., behaviour={
        1: Easy_neuron_initialize(syn_density=0.05, syn_norm=1.0),
        2: Easy_neuron_collect_input(noise_density=0.01, noise_strength=0.11),
        3: Easy_neuron_generate_output(threshold=0.1),
        4: Easy_neuron_Refractory(decay='0.8;0.99')
    })
```

We should now see some repeated bursting behaviour of the network. By changing the previous parameter in the code or in the UIs "Info Tab" you can completely change the pulse frequency and other dynamics of the network.

