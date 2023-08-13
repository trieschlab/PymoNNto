## Tagging System

To access the tagged objects we can use the `[]` operator which returns a list of objects tagged with the given tag.
E.g. `['my_tag']` gives you a list of all objects tagged with `my_tag`. 
Tags searches use a caching system so it is very fast an can be used for repeated calls inside of Behaviors.
Unique tags can be accessed like simple variables via their parents like `My_Network.my_neurons`.


Here are some examples:

```python
My_Network = Network()
NeuronGroup(net=My_Network, tag='my_neurons', size=100, behavior={
    1: Basic_Behavior(),
    9: Recorder(['voltage', 'np.mean(voltage)'], tag='my_recorder')
})
SynapseGroup(net=My_Network, src='my_neurons', dst='my_neurons', tag='S1,GLUTAMATE')

################################
################################
################################

#Unique tag access:
My_Network.my_neurons
My_Network.my_neurons.Basic_Behavior
My_Network.my_neurons.Recorder
My_Network.my_neurons.my_recorder
My_Network.S1

#[] tag search
My_Network['my_neurons']
=> [<PymoNNto.NetworkCore.Neuron_Group.NeuronGroup object at 0x00000195F4878670>]

My_Network['my_recorder']
My_Network.my_neurons['my_recorder'] 
=> [<PymoNNto.NetworkBehavior.Recorder.Recorder.Recorder object at 0x0000021F1B61D5E0>]

My_Network['np.mean(voltage)']
My_Network.my_neurons['voltage']
My_Network.my_neurons.my_recorder['np.mean(voltage)']
=> [[array(data iteration 1), array(data iteration 2), array(data iteration 3), ...]]

My_Neurons['voltage', 0] 
#is equivalent to 
My_Neurons['voltage'][0] 
```