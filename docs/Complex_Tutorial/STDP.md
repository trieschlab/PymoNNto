#STDP

This module allows synapses to adjust their strengths based on the temporal relation between the pre- and post-synaptic voltages.
The core of the learning rule consists of a discrete kernel with three elements.
Each element compares pre- and postsynaptic voltages across subsequent, pre_post or post_pre, or simultaneous time steps, simu (see figure).
The global learning rate is defined by stdp_factor
After modifying synapses for which plasticity has been enabled, s.enabled, synaptic weights are clipped to values between 0 and 10.
Since the weight change depends on the temporal relation between current and preceding activities, we store activities of the preceding time step in the \textit{voltage\_old}.

This stdp module is a NeuronGroup module, therefore it iterates over all the synapses of a given NeuronGroup of a specific type (GLUTAMATE).
By removing the for-loop, a similar module could, however, also be added to the behavior of a SynapseGroups directly. 

<img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/STDP_beh.png"><img width="300" src="https://raw.githubusercontent.com/trieschlab/PymoNNto/Images/STDP_vg.png"><br>

```python
# /Examples_Paper/STDP_Hom_Norm/STDP.py
from PymoNNto.NetworkCore.Behavior import *

class STDP(Behavior):

    def initialize(self, neurons):
        self.stdp_factor = self.parameter('stdp_factor', 0.0015, neurons)
        self.syn_type = self.parameter('syn_type', 'GLUTAMATE', neurons)
        neurons.spike_old = neurons.vector()

    def iteration(self, neurons):

        for s in neurons.synapses(afferent, self.syn_type):

            pre_post = s.dst.spike[:, None] * s.src.spike_old[None, :]
            simu = s.dst.spike[:, None] * s.src.spike[None, :]
            post_pre = s.dst.spike_old[:, None] * s.src.spike[None, :]

            dw = self.stdp_factor * (pre_post - post_pre + simu)

            #print(np.sum(pre_post),np.sum(post_pre),np.sum(simu))

            s.W = np.clip(s.W+dw*s.enabled, 0.0, 10.0)

        neurons.spike_old = neurons.spike.copy()

```