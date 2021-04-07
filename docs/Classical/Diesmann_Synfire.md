# Diesmann Synfire Chain PymoNNto Implementation

The following code creates a synfire chain network with 10 neuron groups and 100 neurons per group. 
The groups have feed forward connections and receive external and internal noise.
Every neuron in the group is updated with rules derived from "Diesmann et al 1999".


```python
from PymoNNto import *

#https://brian2.readthedocs.io/en/stable/examples/frompapers.Diesmann_et_al_1999.html

class Diesmann_main(Behaviour):

    def set_variables(self, n):
        self.set_init_attrs_as_variables(self)
        n.dt = 0.01
        n.v = n.get_neuron_vec() - self.Vr + n.get_random_neuron_vec() * (self.Vt - self.Vr)
        n.x = n.get_neuron_vec()
        n.y = n.get_neuron_vec()

    def new_iteration(self, n):
        v, x, y = n.v.copy(), n.x.copy(), n.y.copy()

        n.v += (-(v - self.Vr) + x) * (1. / self.taum) * n.dt#: volt
        n.x += (-x + y) * (1. / self.taupsp) * n.dt#: volt
        n.y += (-y * (1. / self.taupsp) + 25.27 + (39.24 ** 0.5) * n.get_random_neuron_vec()*10) * n.dt#: volt

        n.spike = (n.v > self.Vt)
        n.v[n.spike] = self.Vr


class Diesmann_input(Behaviour):

    def set_variables(self, n):
        self.set_init_attrs_as_variables(self)

        for s in n.afferent_synapses['GLUTAMATE']:
            s.W = s.get_random_synapse_mat()

        #[k for k in range((int(i/group_size)+1)*group_size, (int(i/group_size)+2)*group_size) if i<N_pre-group_size]

    def new_iteration(self, n):
        for s in n.afferent_synapses['GLUTAMATE']:
            n.v += np.sum(s.W[:, s.src.spike], axis=1)

        if self.external_noise:
            n.v += n.get_random_neuron_vec()


#Pinput = SpikeGeneratorGroup(85, np.arange(85), np.random.randn(85) + 50)

My_Network = Network()

n_groups = 10
group_size = 100
groups=[]

for group in range(n_groups):
    N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=get_squared_dim(group_size), behaviour={
        1: Diesmann_main(Vr=-70, Vt=-55, taum=10, taupsp=0.325, weight=4.86),
        2: Diesmann_input(external_noise=group==0),
        9: Recorder(tag='my_recorder', variables=['n.v', 'n.spike'])
    })
    groups.append(N_e)

for i in range(n_groups-1):
    SynapseGroup(net=My_Network, src=groups[i], dst=groups[i+1], tag='GLUTAMATE')


My_Network.initialize()

My_Network.simulate_iterations(100, measure_block_time=True)

import matplotlib.pyplot as plt
spikes = np.hstack(My_Network['n.spike'])
plt.imshow(spikes.transpose(),cmap='gray', aspect='auto')
plt.show()

#from PymoNNto.Exploration.Network_UI import *
#my_UI_modules = get_default_UI_modules(['spike', 'v'], ['W'])
#Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=10).show()
```



















