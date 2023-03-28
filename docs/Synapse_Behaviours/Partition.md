#Partition

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Partition.png"><br>

The Partition module can be attached to a SynapseGroup to split the Synapse group into many smaller SynapseGroups with masked subNeuronGroups.
After that, the module removes the old original SynapseGroup from the Network. 
The small SynapseGroups are copies of the original one, except of the source and destination(masked afterwards), so they have the same Behaviors(copies).

The Partition modules initialize function is executed when the SynapseGroup is initialized and not when the network.initialize function is called.

The attribute "split_size" determines the size of the pieces, the destination NeuronGroup is splitted into in each direction.
split_size=5 means, that the Group is splitted into 25 (5*5) subgroups when the Neurons are oriented into a two dimensional Grid and 125 (5*5*5) subgroups when the neurons also have different z dimensions.
The split size of the source Neuron Group is determined automatically based on the receptive fields.
