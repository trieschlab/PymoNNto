# Brunel Hakim SORNSim Implementation

The following code creates a network of 5000 neurons with recurrent connections and simulates them for 1000 iterations. 

...

```python

from SORNSim import *

#https://brian2.readthedocs.io/en/stable/examples/frompapers.Brunel_Hakim_1999.html

class Brunel_Hakim_main(Behaviour):

    def set_variables(self, n):
        self.Vr = 10 # mV
        self.theta = 20 # mV
        self.tau = 20 # ms
        self.delta = 2 # ms
        self.taurefr = 2 # ms
        self.C = 1000
        n.sparseness = float(self.C) / n.size
        n.J = 0.1 # mV
        self.muext = 25 # mV
        self.sigmaext = 1 # mV

        n.v = n.get_neuron_vec()*self.Vr
        n.spike = n.get_neuron_vec()
        n.refrac = n.get_neuron_vec()

        #self.dt = 0.001


    def new_iteration(self, n):
        n.v += (-n.v+self.muext + self.sigmaext * np.sqrt(self.tau) * ((n.get_random_neuron_vec(density=0.001)>0)*10))/self.tau#*xi

        n.spike = (n.v > self.theta) * (n.refrac > self.taurefr)
        print(np.sum(n.spike), np.mean(n.v))
        n.refrac += 1.0 /self.tau
        n.refrac[n.spike] = 0.0
        n.v[n.spike] = self.Vr


class Brunel_Hakim_input(Behaviour):

    def set_variables(self, n):
        for s in n.afferent_synapses['GLUTAMATE']:
            s.W = (s.get_random_synapse_mat(density=n.sparseness)>0.0).astype(t)*n.J

    def new_iteration(self, n):
        for s in n.afferent_synapses['GLUTAMATE']:
            n.v += np.sum(s.W[:, s.src.spike], axis=1)#'V += -J'





My_Network = Network()

N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=get_squared_dim(5000), behaviour={
    1: Brunel_Hakim_main(),
    2: Brunel_Hakim_input(),
    9: Recorder(tag='my_recorder', variables=['n.v'])
})

SynapseGroup(net=My_Network, src=N_e, dst=N_e, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(1000, measure_block_time=True)

import matplotlib.pyplot as plt
#plt.plot(My_Network['n.v', 0])
#plt.show()

#plt.plot(My_Network['n.u', 0])
#plt.show()

plt.imshow(My_Network['n.v', 0, 'np'].transpose(), cmap='gray', aspect='auto')
plt.show()


#from SORNSim.Exploration.Network_UI import *
#my_UI_modules = get_default_UI_modules(['fired', 'v', 'u'], ['W'])
#Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=2).show()

```





