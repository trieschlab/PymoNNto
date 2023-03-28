#Neuron Dimension

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/Neuron_Dimension.png"><br>

The NeuronDimension behavior can be used to give a NeuronGroup some spacial dimensions. 
It overrides the neurons.size variable and adds x,y, and z vectors, as well as width, height and depth variables.
The Behavior is special, because its initialize function is executed when the NeuronGroup is created and not when network.initialize() is called.

The neurons are arranged in a 3-dimensional grid with size=width * height * depth.

The module is required for many user interface tabs as well as some Receptive Field and Partitioning modules.

Because is overrides the "size" variable, it does not have to be added in the behavior dictionary directly, but also indirectly with NeuronGroup(size=NeuronDimension(),...).
In this case it will be added to position "0" in the dictionary.

```python


My_Neurons = NeuronGroup(..., size=NeuronDimension(width=10,height=10,depth=1), behavior={
...
})

#equivalent to

My_Neurons = NeuronGroup(..., size=???, behavior={
    0: NeuronDimension(width=10,height=10,depth=1),
...
})

#equivalent to

My_Neurons = NeuronGroup(..., size=get_squared_dim(100), behavior={
...
})

```