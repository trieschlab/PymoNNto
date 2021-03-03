# Hindmarsh Rose PymoNNto Implementation

The following code creates three neurons with different external input. All neurons are independent and updated with rules derived from "Hindmarsh Rose 1984".





```python

from PymoNNto import *

#https://brian2.readthedocs.io/en/stable/examples/frompapers.Hindmarsh_Rose_1984.html

def exp(x):
    return np.e**x

def exprel(x):
    return (exp(x) - 1)/x

class Hindmarsh_Rose_main(Behaviour):

    def set_variables(self, n):
        self.set_init_attrs_as_variables(self)
        self.dt = 0.01# * ms
        self.I=np.array(self.I)

        n.x = n.get_neuron_vec()+self.x_1
        n.y = n.get_neuron_vec()+self.c - self.d*n.x**2
        n.z = n.get_neuron_vec()+self.r*(self.s*(n.x - self.x_1))


    def new_iteration(self, neurons):
        x, y, z = neurons.x.copy(), neurons.y.copy(), neurons.z.copy()

        neurons.x += (y - self.a*x**3 + self.b*x**2 + self.I - z)*self.dt
        neurons.y += (self.c - self.d*x**2 - y)*self.dt
        neurons.z += self.r*(self.s*(x - self.x_1) - z)*self.dt

My_Network = Network()


N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=3, behaviour={
    1: Hindmarsh_Rose_main(x_1=-1.6, a=1, b=3, c=1, d=5, r=0.001, s=4, I=[0.4, 2, 4]),
    9: Recorder(tag='my_recorder', variables=['n.x'])
})

My_Network.initialize()

My_Network.simulate_iterations(200000, measure_block_time=True)

import matplotlib.pyplot as plt

plt.plot(My_Network['n.x', 0, 'np'][:, 0])
plt.show()
plt.plot(My_Network['n.x', 0, 'np'][:, 1])
plt.show()
plt.plot(My_Network['n.x', 0, 'np'][:, 2])
plt.show()

```





