# Weight initialization behavior

This is a sample implementation of a behavior which can be attached to synapse groups, which initializes their weight matrices.

```python
# /NetworkBehavior/Basics/Behavior_Weight_Initialization.py
from PymoNNto import *

class CreateWeights(Behavior):

    def initialize(self, synapses):
        distribution = self.parameter('distribution', 'uniform(0.0,1.0)')  # ones
        density = self.parameter('density', 1.0)

        synapses.W = synapses.matrix(distribution, density=density) * synapses.enabled

        #  self.remove_autapses = self.parameter('remove_autapses', False) and synapses.src == synapses.dst

        if self.parameter('normalize', True):
            for i in range(10):
                synapses.W /= np.sum(synapses.W, axis=1)[:, None]
                synapses.W /= np.sum(synapses.W, axis=0)

            synapses.W *= self.parameter('nomr_fac', 1.0)


    def iteration(self, synapses):
        return
        #  if self.remove_autapses:
        #    np.fill_diagonal(synapses.W, 0.0)
```