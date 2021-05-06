#User Interface

To control and evaluate the model from the "Basics" section with PymoNNto's interactive graphical user interface we can replace the pyplot functions, the recorder and the simulate_iterations with code to launch the Network_UI.

Like other parts of PymoNNto, the Network_UI is modular.
It consists of multiple UI_modules, which we can be freely chosen.
Here, we use the function get_default_UI_modules to get a list of standard modules applicable to most networks.

To correctly render the output, some UI_modules require additional specifications or adjustment of the code.
In this example, the sidebar_activity_module, displays the activity of the neurons on a grid and allows to select individual neurons.
The size of the grid is specified as a property of the neuron group via a NeuronDimension module (here replaced with get_squared_dim(100)), which creates spatial coordinates for each neuron stored in the vectors x, y and z.

```python
from PymoNNto import *

class Basic_Behaviour(Behaviour):

    def set_variables(self, neurons):
        neurons.voltage = neurons.get_neuron_vec()
        self.leak_factor = 0.9
        self.threshold = 0.5

    def new_iteration(self, neurons):
        firing = neurons.voltage > self.threshold
        neurons.spike = firing.astype(def_dtype) #spikes
        neurons.voltage[firing] = 0.0#reset

        neurons.voltage *= self.leak_factor #voltage decay
        neurons.voltage += neurons.get_random_neuron_vec(density=0.01) #noise

class Input_Behaviour(Behaviour):

    def set_variables(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            synapse.W = synapse.get_random_synapse_mat(density=0.1)
            synapse.enabled = synapse.W > 0

    def new_iteration(self, neurons):
        for synapse in neurons.afferent_synapses['GLUTAMATE']:
            neurons.voltage += synapse.W.dot(synapse.src.spike)/synapse.src.size*10



My_Network = Network()

My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=get_squared_dim(100), behaviour={
    1: Basic_Behaviour(),
    2: Input_Behaviour()
})

My_Neurons.visualize_module()

my_syn = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000, measure_block_time=True)


from PymoNNto.Exploration.Network_UI import *
my_UI_modules = get_default_UI_modules(['voltage', 'spike'], ['W'])
Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=1).show()

```

<img width="600" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Basic_Tab.png"><br>
