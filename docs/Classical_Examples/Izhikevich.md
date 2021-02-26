# Izhikevich Neuron SORNSim Implementation

The following code creates a network with 800 excitatory neurons, 200 inhibitory neurons and all the connections between them.
The neurons have different parameters and are updated with rules derived form the original Izhikevich paper.




```python

from SORNSim import *

class Izhikevich_main(Behaviour):

    def set_variables(self, n):
        self.set_init_attrs_as_variables(n)
        n.I = n.get_neuron_vec()
        n.a += n.get_neuron_vec()
        n.b += n.get_neuron_vec()
        n.c += n.get_neuron_vec()
        n.d += n.get_neuron_vec()
        n.v *= n.get_random_neuron_vec()
        n.u *= n.get_random_neuron_vec()
        n.fired = n.get_neuron_vec() > 0
        n.dt = 0.5

    def new_iteration(self, n):
        n.fired = n.v > 30
        if np.sum(n.fired) > 0:
            n.v[n.fired] = n.c[n.fired]
            n.u[n.fired] = n.u[n.fired] + n.d[n.fired]

        n.v += n.dt * (0.04 * n.v**2 + 5*n.v + 140 - n.u + n.I)
        n.u += n.dt * (n.a * (n.b * n.v - n.u))


class Izhikevich_input(Behaviour):

    def set_variables(self, n):
        for s in n.afferent_synapses['All']:
            s.W = s.get_random_synapse_mat()

    def new_iteration(self, n):

        n.I = 20 * n.get_random_neuron_vec()

        for s in n.afferent_synapses['GLUTAMATE']:
            n.I += 0.5 * np.sum(s.W[:, s.src.fired], axis=1)

        for s in n.afferent_synapses['GABA']:
            n.I -= np.sum(s.W[:, s.src.fired], axis=1)






My_Network = Network()

N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=get_squared_dim(800), behaviour={
    1: Izhikevich_main(a=0.02, b=0.2, c=-65, d=8.0, v='0;-65', u='0;-8.0'),
    2: Izhikevich_input(),
    9: Recorder(tag='my_recorder', variables=['n.v', 'n.u', 'n.fired'])
})

N_i = NeuronGroup(net=My_Network, tag='inhibitory_neurons', size=get_squared_dim(200), behaviour={
    1: Izhikevich_main(a=0.02, b=0.2, c=-65, d=8.0, v='0;-65', u='0;-8.0'),
    2: Izhikevich_input(),
    9: Recorder(tag='my_recorder', variables=['n.v', 'n.u', 'n.fired'])
})

SynapseGroup(net=My_Network, src=N_e, dst=N_e, tag='GLUTAMATE')
SynapseGroup(net=My_Network, src=N_e, dst=N_i, tag='GLUTAMATE')
SynapseGroup(net=My_Network, src=N_i, dst=N_e, tag='GABA')
SynapseGroup(net=My_Network, src=N_i, dst=N_i, tag='GABA')

My_Network.initialize()

My_Network.simulate_iterations(1000, measure_block_time=True)

import matplotlib.pyplot as plt
plt.plot(My_Network['n.v', 0])
plt.show()

plt.plot(My_Network['n.u', 0])
plt.show()

plt.imshow(My_Network['n.fired', 0, 'np'].transpose(), cmap='gray', aspect='auto')
plt.show()


#from SORNSim.Exploration.Network_UI import *
#my_UI_modules = get_default_UI_modules(['fired', 'v', 'u'], ['W'])
#Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=2).show()

```





