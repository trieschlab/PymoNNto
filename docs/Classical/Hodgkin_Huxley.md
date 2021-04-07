# Hodgkin Huxley PymoNNto Implementation

The following code creates a Neuron with multiple Hodgkin Huxley segments. Over time the input current of the first compartment changes, which creates different spike patterns flowing through the segments.


```python
from PymoNNto import *
import scipy as sp
import matplotlib.pyplot as plt

#multi compartment version of
#https://hodgkin-huxley-tutorial.readthedocs.io/en/latest/_static/Hodgkin%20Huxley.html
#with a simplified version of the cable theory to connect compartments

class HH_main(Behaviour):

    def alpha_m(self, V):#Channel gating kinetics. Functions of membrane voltage
        return 0.1*(V+40.0)/(1.0 - np.exp(-(V+40.0) / 10.0))

    def beta_m(self, V): #Channel gating kinetics. Functions of membrane voltage
        return 4.0*np.exp(-(V+65.0) / 18.0)

    def alpha_h(self, V): #Channel gating kinetics. Functions of membrane voltage
        return 0.07*np.exp(-(V+65.0) / 20.0)

    def beta_h(self, V): #Channel gating kinetics. Functions of membrane voltage
        return 1.0/(1.0 + np.exp(-(V+35.0) / 10.0))

    def alpha_n(self, V): #Channel gating kinetics. Functions of membrane voltage
        return 0.01*(V+55.0)/(1.0 - np.exp(-(V+55.0) / 10.0))

    def beta_n(self, V): #Channel gating kinetics. Functions of membrane voltage
        return 0.125*np.exp(-(V+65) / 80.0)

    def I_Na(self, V, m, h): #Membrane current (in uA/cm^2) Sodium (Na = element name)
        return self.g_Na * m**3 * h * (V - self.E_Na)

    def I_K(self, V, n): #Membrane current (in uA/cm^2) Potassium (K = element name)
        return self.g_K  * n**4 * (V - self.E_K)

    def I_L(self, V):#Membrane current (in uA/cm^2) Leak
        return self.g_L * (V - self.E_L)

    def I_inj(self, i): #External Current
        return 5*(i*self.dt>100) - 5*(i*self.dt>200) + 10*(i*self.dt>300) - 10*(i*self.dt>400)

    def set_variables(self, n):
        self.set_init_attrs_as_variables(self)
        #C_m = 1.0  # membrane capacitance, in uF/cm^2
        #g_Na = 120.0  # Sodium (Na) maximum conductances, in mS/cm^2
        #g_K = 36.0  # Postassium (K) maximum conductances, in mS/cm^2
        #g_L = 0.3  # Leak maximum conductances, in mS/cm^2
        #E_Na = 50.0  # Sodium (Na) Nernst reversal potentials, in mV
        #E_K = -77.0  # Postassium (K) Nernst reversal potentials, in mV
        #E_L = -54.387  # Leak Nernst reversal potentials, in mV

        #b_r = 0.13 #Resistance between blocks in ohms between blocks

        self.dt = 0.01

        n.v = np.array([n.get_neuron_vec()*self.v for i in range(self.blocks)])
        n.h = np.array([n.get_neuron_vec()*self.h for i in range(self.blocks)])
        n.m = np.array([n.get_neuron_vec()*self.m for i in range(self.blocks)])
        n.n = np.array([n.get_neuron_vec()*self.n for i in range(self.blocks)])
        n.I = np.array([n.get_neuron_vec() for i in range(self.blocks)])




    def new_iteration(self, neurons):

        v, h, m, n = neurons.v.copy(), neurons.h.copy(), neurons.m.copy(), neurons.n.copy()

        I = neurons.I*0

        #external current on first block of all neurons in group
        I[0, :] = self.I_inj(neurons.iteration)


        # Warning: this is a very simplified way to connect the compartments.
        # The version is broadly based on the cable theory with a simple resistance between the compartments.
        # It is NOT physically accurate and only there to demonstrate some form of spike propagation.
        # Do not use this transition function for scientific research without further testing!

        # current input to next block
        for i in range(self.blocks-1):
            I[i + 1] += ((v[i]-v[i+1])/self.b_r) * self.dt

        # current input from previous block
        for i in range(self.blocks-1):
            I[i] += ((v[i + 1]-v[i])/self.b_r) * self.dt

        ##############################################################

        neurons.v += ((I - self.I_Na(v, m, h) - self.I_K(v, n) - self.I_L(v)) / self.C_m) * self.dt
        neurons.m += (self.alpha_m(v)*(1.0-m) - self.beta_m(v)*m) * self.dt
        neurons.h += (self.alpha_h(v)*(1.0-h) - self.beta_h(v)*h) * self.dt
        neurons.n += (self.alpha_n(v)*(1.0-n) - self.beta_n(v)*n) * self.dt



My_Network = Network()

N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=1, behaviour={
    1: HH_main(blocks=20, b_r=0.15, v=-65, m=0.05, h=0.6, n=0.32, C_m=1.0, g_Na=120.0, g_K=36.0, g_L=0.3, E_Na=50.0, E_K=-77.0, E_L=-54.387),
    9: Recorder(tag='my_recorder', variables=['n.v','n.m','n.h','n.n'])
})

SynapseGroup(net=My_Network, src=N_e, dst=N_e, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(50000, measure_block_time=True)


data = My_Network['n.v', 0, 'np'][:, :, 0]#numpy array of first recorder \ only the forst neuron and all compartments

for d in range(data.shape[1]):
    plt.plot(data[:, d]-10*d)
plt.show()

plt.imshow(data.transpose(), cmap='gray', aspect='auto', interpolation='none')
plt.show()

```



















