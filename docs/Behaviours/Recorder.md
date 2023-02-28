#Recorder

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Recorder.png"><br>

The Recorder can be used to save a variable or some value over time.
It evaluates the variable string and saves the result into a list or a numpy array.
This list can later be accessed via the tagging system.

Recorders can be attached to NeuronGroups, SynapseGroups and the Network object.

```python
Recorder(['voltage', 'np.mean(voltage)'], tag='my_recorder')

...

MyNeuronGroup['voltage', 0, 'np']# "np" converts the list to a numpy array
MyNeuronGroup['np.mean(voltage)', 0]

#[array(data iteration 1), array(data iteration 2), array(data iteration 3), ...]
```

