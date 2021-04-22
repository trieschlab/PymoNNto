#Connectivity and Partitioning

One helpful function when designing bigger networks is the partitioning system.
When the implemented model is based on vector and matrix operations, the NeuronGroups can be divided into SubNeuronGroups with a mask.
Such a SubNeuronGroup allows partial access to variables of the original NeuronGroup.
To avoid giant connection matrices, the partitioning system can automatically divide the NeuronGroup into subgroups that are connected by many small SynapseGroups.
With this, we can conveniently combine fast processing with small computational overhead and avoid the quadratic growth of synaptic weight matrices for increasing numbers of neurons.

The following code creates a SynapseGroup with a specific connectivity, which is then partitioned into many smaller sub synapse groups.
"(s_id!=d_id)" means that the source id and the target id of the neurons have to be different to form a synapse.
"in_box(10)" means, that the neurons have a receptive field of 10 neurons in each direction, so the resulting patch has the size 11x11.
Because s_id, and the output of in_box() are boolean vectors, we cannot use "and" or "or", so we just multiply them to replace an "and" operator.
The connectivity attribute only changes the enabeled attribute of the synapse matrix.

If the partitioning attribute is True, the single Synapse group is splitted into many smaller SynapseGroups based on the enabeled matrix.
Only the SubSynapseGroups are added to MyNetwork and sg.dst as well as sg.src point to SubNeuronGroups is sg is one of the SubSynapseGroups.


```python
SynapseGroup(net=MyNetwork, src=sourceNG, dst=destinationNG, tag='GLU', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
```
