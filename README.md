# Self-Organizing-Recurrent-Network-Simulator
The "Self Organizing Recurrent Network Simulator" allows you to create different Neuron-Groups, define their Behaviour and connect them with Synapse-Groups.

With this Simulator you can create all kinds of biological plausible networks, which, for example, mimic the learning mechanisms of cortical structures.

The user interface allows you to display your network in an interactive way and you can add new visualization modules, too.

![User interface example](https://raw.githubusercontent.com/gitmv/Self-Organizing-Recurrent-Network-Simulator/Images/simple_UI_1.png)

A basic network grid with three behaviours (index defines execution order), recurrent connections and local receptive fields can be created like this:

```python
Easy_Network = Network()

Easy_Neurons = NeuronGroup(net=Easy_Network, tag='neurons', size=get_squared_dim(number_of_neurons), behaviour={
        1: Easy_neuron_initialize(),
        2: Easy_neuron_collect_input(),
        3: Easy_neuron_generate_output(threshold=0.1)
    })

SynapseGroup(net=Easy_Network, src=Easy_Neurons, dst=Easy_Neurons, tag='GLUTAMATE', connectivity='(s_id!=d_id)*in_box(10)')

Easy_Network.initialize()
```

Each Behaviour has the following layout where "set_variables" is called when the Neuron Group is initialized while "new_iteration" is called repeatedly every timestep. "neurons" points to the parent neuron group the behaviour belongs to.

```python
class Basic_Behaviour(Neuron_Behaviour):

  def set_variables(self, neurons):
    return
    
  def new_iteration(self, neurons):
    return
```

A behaviour that collects all the inputs from the Synapses tagged with "GLUTAMATE" and adds some random noise can looks like this:

```python
class Easy_neuron_collect_input(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Easy_neuron_collect_input')
        neurons.sensitivity = self.get_init_attr('sensitivity', 1.0, neurons)
        
        #create random synapse weights
        for synapse_group in neurons.afferent_synapses['GLUTAMATE']:
            synapse_group.W = synapse_group.get_random_synapse_mat()*0.0001
            #synapse_group.get_synapse_mat() #equivalent to np.zeros(s.get_synapse_mat_dim())

    def new_iteration(self, neurons):
        for s in neurons.afferent_synapses['GLUTAMATE']:
            neurons.activation += s.W.dot(s.src.output)

        neurons.activation += neurons.get_random_neuron_vec(density=0.1)
```

To simulate timesteps you can use the following commands:
```python
network.simulate_iteration()
network.simulate_iterations(iterations=1000)
```

The Network activity and the Neurons positions can be plotted like this:

```python
recorder=NeuronRecorder(['n.output'], tag='my_recorder')
Easy_Network.add_behaviours_to_neuron_group({100: recorder}, Easy_Neurons)
Easy_Network.simulate_iterations(iterations=1000)

plt.plot(Easy_Network['n.output',0,'np'])
plt.show()

plt.scatter(Easy_Neurons.x, Easy_Neurons.y)
plt.show()
```

The tagging system allows you to access all kinds of synases, neuron groups, behaviours and recorded values in an efficiant way with one  command:

```python

#returns a list of all neuron groups tagged with "neurons"
Easy_Network['neurons']   

#returns a list of all synapse groups tagged with "GLUTAMATE"
Easy_Network['GLUTAMATE'] 

#retruns the first neuron group tagged with "neurons" (equivalent to Easy_Network['neurons'][0])
Easy_Network['neurons', 0] 

#returns a list of all behaviours tagged with "Easy_neuron_collect_input" from all neuron groups
Easy_Network['Easy_neuron_collect_input'] 

#returns a list of all behaviours tagged with "my_recorder" from Easy_Neurons
Easy_Neurons['my_recorder']

#returns one output recording and casts it to numpy array.
Easy_Neurons['n.output',0,'np']
#equivalent to:
np.array(Easy_Network.NeuronGroups[0].behaviour[100].variables['n.output'])

#the commands can also be combined. Here the command returns output recording of the neuron group tagged with "neurons" and casts it to an numpy array.
Easy_Network['neurons', 0]['n.output',0,'np'] 
```
