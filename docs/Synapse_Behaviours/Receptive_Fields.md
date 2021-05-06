#Box Receptive Fields

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Box_Receptive_Fields.png"><br>

The Box Receptive Fields module can be attached to SynapseGroups and changes the enabled matrix so that only close neurons are connected.
Here the x, y and z distances of both neurons have to be <= range, so a box connectivity pattern with a volume of (2*range)^3 is created.

If the source and the destination group is the same, the "remove_autapses" attribute can be used to remove connections with the same source and destination index.
The NeuronDimension module is required so that the neurons have some x,y, and z coordinate.

#Circle Receptive Fields

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Circle_Receptive_Fields.png"><br>

The Circle Receptive Fields module can be attached to SynapseGroups and changes the enabled matrix so that only close neurons are connected.
In contrast to the Box Receptive Fields module, the eurclidian distance is used, so neurons where (dx*dx+dy*dy+dz*dz) is <=radius are connected, where dx is the horizontal distance and so on.

If the source and the destination group is the same, the "remove_autapses" attribute can be used to remove connections with the same source and destination index.
The NeuronDimension module is required so that the neurons have some x,y, and z coordinate.

#Remove Autapses

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Remove_Autapses.png"><br>

If a SynapseGroup has the same source and the destination NeuronGroups, the Remove Autapses module can be used to remove connections with the same source and destination index.
It creates an enabled matrix, where all values are True, except of the diagonal.
