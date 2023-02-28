from PymoNNto import *

#https://brian2.readthedocs.io/en/stable/examples/frompapers.Wang_Buszaki_1996.html

def exp(x):
    return np.e**x

def exprel(x):
    return (exp(x) - 1)/x

class Wang_Buzaki_main(Behaviour):

    def set_variables(self, n):
        self.set_parameters_as_variables(self)
        self.dt = 0.01# * ms

        #Cm = 1# * uF  # /cm**2
        #Iapp = 2# * uA
        #gL = 0.1# * msiemens
        #EL = -65# * mV
        #ENa = 55# * mV
        #EK = -90# * mV
        #gNa = 35# * msiemens
        #gK = 9# * msiemens

        n.v = n.vector()-70
        n.h = n.vector()+1
        n.n = n.vector()


    def new_iteration(self, neurons):
        v, h, n=neurons.v.copy(), neurons.h.copy(), neurons.n.copy()

        alpha_m = 0.1 * 10 / exprel(-(v + 35) / 10)#: Hz
        beta_m = 4 * exp(-(v + 60) / (18))#: Hz
        m = alpha_m / (alpha_m + beta_m)  #: 1
        alpha_h = 0.07 * exp(-(v + 58) / (20))#: Hz
        beta_h = 1. / (exp(-0.1 * (v + 28)) + 1)#: Hz
        alpha_n = 0.01 * 10 / exprel(-(v + 34) / (10))#: Hz
        beta_n = 0.125 * exp(-(v + 44) / (80))#: Hz

        neurons.v += (-self.gNa * m ** 3 * h * (v - self.ENa) - self.gK * n ** 4 * (v - self.EK) - self.gL * (v - self.EL) + self.Iapp) / self.Cm * self.dt#: volt
        neurons.h += 5 * (alpha_h * (1 - h) - beta_h * h) * self.dt#: 1
        neurons.n += 5 * (alpha_n * (1 - n) - beta_n * n) * self.dt#: 1


My_Network = Network()

N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=1, behaviour={
    1: Wang_Buzaki_main(Cm=1, Iapp=2, gL=0.1, EL=-65, ENa=55, EK=-90, gNa=35, gK=9),
    9: Recorder('v', tag='my_recorder')
})

My_Network.initialize()

My_Network.simulate_iterations(10000, measure_block_time=True)

import matplotlib.pyplot as plt

plt.plot(My_Network['v', 0, 'np'][:, 0])
plt.show()