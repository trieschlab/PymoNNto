# Fast Processing

Here we describe a few tipps how to speed up PymoNNto networks with a few simple steps.
We mostly focus on synapse operations where `src` is the presynaptic neuron group and `dst` is the postsynaptic one. 
Both spike vectors could look like this: 

```python
src = np.random.rand(5000) < 0.01    # 5k pre synaptic neurons (1% spikes)
dst = np.random.rand(10000) < 0.01   # 10k post synaptic neurons (1% spikes)
```

## Efficient Storage of Synapse Matrices

We have two ways to store the synapse matrix between the two groups. 
The first version has a DxS and the second one a SxD dimension.
Here S is the size of the source group (5000) and D is the size of the destination group (10000).

In most cases we want to use the synapses to compute the forward synapse operation where the source group activates the destination group.  
Here the SxD version is far more efficient.
The reason is that we have to sum up the input each dst neuron receives somehow.
In the SxD version, the weights pointing to one dst neuron are stored next to each other in memory and can be collected togeteher.
However, in the DxS version they are scattered all over the memory block and have to be addressed individually.
DxS is only better if we want to send data from the destination to the source group or if we want the code to match the standart mathematical notation.

Numpy:
```python
# naive / slow:
W1 = np.random.rand(10000, 5000) # dense DxS synapses

# better:
W2 = np.random.rand(5000, 10000) # dense SxD synapses
```

PymoNNto:
```python
from PymoNNto import *

# naive / slow:
settings = {'synapse_mode': DxS}
Network(settings=settings)
W1 = synapses.matrix('random')

# better:
settings = {'synapse_mode': SxD}
Network(settings=settings)
W2 = synapses.matrix('random')
```

So, if possible, always use the SxD version for better performance!

## Efficient synapse operation:
The second trick to increase the perfromance is to change the forward synapse operation itself.
The easiest way is to use a simple dot product, but it is rather slow.
A far better way is to use indexing and summations.
This is only possible if we have a spiking network with binary spikes which can be used for indexing.
Here, instead of multiplying each spike value with one row/column of the weight matrix we just index the rows/columns where src is 1 and ignore the columns where src is 0.
After this, we only have to sum up the columns/rows which remain to receive our destination activation.

The resuls of this operations are the same given that src is a binary vector.
The latter version with the efficient SxD version is 20 times faster than the simple dot product.

```python
W1.dot(src) # 23ms (naive)

np.sum(W1[:, src] , axis=1) # 11ms (2.2x)

np.sum(W2[src] , axis=0) # 1.16ms (20x)
```

## Efficient STDP:
The next trick is the modification of STDP.
Again, the simples STDP version is the dot product of the two spike vectors. 
This creates a new matrix where most values are 0 and few are 1.
This can then be used to update the weight matrix.

However, this is very inefficient.

By using the ix_ function, we can create a sparse mesh which only contains the indices of the matrix which are 1.
Instead of updating every value in the giant matrix, use this sparse mesh to index only the parts of the matrix which is supposed to change.
With this, the same simple STDP rule can be nearly three orders of magnitudes faster.

```python
W1 += dst[:,None] * src[None,:] # 77ms (naive)

W1[np.ix_(dst, src)] += 1    # 0.0776ms (997x)

W2[np.ix_(src, dst)] += 1    # same as previous
```

If we want to clip the weights after the STDP update, we can simply reuse the sparse mesh and only update and clipp the weights which actually change.
```python
mask = np.ix_(src, dst)
W2[mask] += 1
W2[mask] = np.clip(W2[mask], W_min, W_max)
```

## Efficient Normalization

Normalization is another costly operation.
Here there is no easy trick to speed up the computation, but in many cases we can execute the operation only at a given interval.
The interval highly depends on the network, the STDP learning rate, the network activity, and other factors.

```python
if iteration % 100 == 0:            # normalize only every 100 iterations
    W /= np.sum(W, axis=1)[:, None] # afferent (DxS) efferent (SxD)
    W /= np.sum(W, axis=0)          # efferent (DxS) afferent (SxD)
```

## Best Datatype

Use the datatype which is best for your system.
In most cases float32 is the best choice.

```python
# synapse operation with:
dtype = np.float64 # 1.24ms (default)
dtype = np.float32 # 0.74ms (1.7$\times$)
dtype = np.float16 # 4.12ms (0.3$\times$) !!!

from PymoNNto import *
settings = {'dtype': dtype}
Network(settings=settings)
```