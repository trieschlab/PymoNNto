#Event Recorder

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Event_Recorder.png"><br>

The EventRecorder can be used to store sparse boolean vectors over time in an efficient way.

In contrast to the Recorder the EventRecorder only works if the evaluation of the variable string returns a vector.
It does not save the whole vector at every time step [vec_t1, vec_t2, vec_t3, ...], but only a list of tuples [(t1, index),(t1, index),(t1, index),(t2, index),(t3, index)]. 
Here the first value is the time step and the second one is the index of the vector element that is True or >0.

The list of tuples can be accessed directly with "n.spikes" where result[:,0] is the list of timesteps and result[:,1] the list of indices. 
The second way is to use "n.spikes.t" to access the timesteps and "n.spikes.i" for the indices.

EventRecorders can be attached to NeuronGroups, SynapseGroups and the Network object.

```python
EventRecorder('spikes', tag='my_recorder')

...

result = MyNeuronGroup['spikes', 0]

MyNeuronGroup['spikes.t', 0] # equivalent to result[:,0]
MyNeuronGroup['spikes.i', 0] # equivalent to result[:,1]

plt.plot(MyNeuronGroup['spikes.t', 0], MyNeuronGroup['spikes.i', 0], '.k')
```