Add some learning to the network.<br>

1. To be able to learn, the network first needs some external input. We can write our own input generator from scratch similar to the random noise behaviour, we added earlier, but we can also derive our behaviour from the "NeuronActivator" class, which writes its patterns into the 'input' variable. The specific Input-patterns can be added later.

```python
class external_input(NeuronActivator):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.strength = self.get_init_attr('strength', 1.0, neurons)
        neurons.input = np.zeros(neurons.size)
        self.write_to = 'input' #define the neuron group variable the input pattern is added to.

    def new_iteration(self, neurons):
        super().new_iteration(neurons)
        if self.strength != 0:
            neurons.activity += neurons.input * self.strength # add input to the neurons actitiy variable
            neurons.input *= 0
```

2. Now we can add the external_input behaviour to the network. Here the execution order is important. 
We want to add the input to the neurons activity after it has collected the internal input from the other neurons and before the activity is pushed into the threshold function.
We then have to add some actual patterns to the "external_input" class. This Line_Pattern, for example, creates some grid with a vertical line moving from left to right. 
The NeuronGroup has to have at least a 30x30=900 neuron dimension.
Note, that the parameters are slightly different.
When we execute the previous example, we should see a moving bar over the NeuronGrid and some additional UI controlls.

```python
from NetworkBehaviour.Input.TREN.Lines import *
source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)

... = NeuronGroup(..., behaviour={
        1: Easy_neuron_initialize(syn_density=0.5, syn_norm=0.8),
        2: Easy_neuron_collect_input(noise_density=0.1, noise_strength=0.11),
        2.1: external_input(strength=1.0, pattern_groups=[source]),
        3: Easy_neuron_generate_output(threshold=0.1),
        4: Easy_neuron_Refractory(decay='0.8;0.99'),
    })
```

3. After we added some Input, we can finally add some learning. For this we use Spike Timing Dependent Plasticity (STDP), where a synapse from A->B gets smaller when B is active before A and bigger, when A is active before B. 

```python
class STDP(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.output_old = neurons.get_neuron_vec()
        neurons.eta_stdp = self.get_init_attr('eta_stdp', 0.005, neurons)

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLUTAMATE']:
            grow = s.dst.output[:, None] * s.src.output_old[None, :] #source neuron is active before destination neruon => grow
            shrink = s.dst.output_old[:, None] * s.src.output[None, :] #destination neuron is active before source neuron => shrink

            dw = neurons.eta_stdp * (grow - shrink) #the weigt change is computed

            s.W += dw * s.enabled #disabled synapses are excluded from growing.
            s.W[s.W < 0.0] = 0.0  #synapses are constraint to be positive.

        neurons.output_old = neurons.output.copy() # store the last activity of the neurons

        self.normalize_synapse_attr('W', 'W', neurons.syn_norm, neurons, 'GLUTAMATE') #to prevent uncontrolled growth to infinity we normalize the synapses so the "total number of receptors in the neuron" stays the same and the change is only relative to the other Synapses.  
```

4. Now we have to add the STDP-Behaviour to the NeuronGroup and remove the receptive field from the SynapseGroup. 
The last step is optional but allows the neurons on the right to connect to the neurons on the left, so the bar at the right can jump back to the right after the networ is trained.
We can directly see the learning progress of each neuron by looking at the "weights" tab.
After around 1000 steps the neurons should have wired themselfes to the neurons one step to the left.
When we now change the UI input source in the sidebar from "Images" to "None", we should still see a moving bar in the grid.

```python
... = NeuronGroup(..., behaviour={
        1: Easy_neuron_initialize(syn_density=0.5, syn_norm=0.8),
        2: Easy_neuron_collect_input(noise_density=0.1, noise_strength=0.11),
        2.1: external_input(strength=1.0, pattern_groups=[source]),
        3: Easy_neuron_generate_output(threshold=0.1),
        4: Easy_neuron_Refractory(decay='0.8;0.99'),
        5: STDP(eta_stdp=0.001)
    })
    
    SynapseGroup(..., connectivity='(s_id!=d_id)') # remove: *in_box(10)
```
