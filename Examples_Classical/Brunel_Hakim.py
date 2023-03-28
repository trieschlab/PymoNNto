from PymoNNto import *
import matplotlib.pyplot as plt
#https://brian2.readthedocs.io/en/stable/examples/frompapers.Brunel_Hakim_1999.html

tau = 20 #20 # ms
dt=0.2


class Brunel_Hakim_main(Behavior):

    def initialize(self, n):
        self.Vr = 10 # mV
        self.theta = 20 # mV

        self.delta = 2 # ms
        self.taurefr = 2 # ms
        self.C = 1000
        n.sparseness = float(self.C) / n.size
        n.J = 0.1 # mV
        self.muext = 25 # mV
        self.sigmaext = 1 # mV

        n.v = n.vector()+self.Vr
        n.spike = n.vector()
        n.refrac = n.vector()+10

        n.spikes = [n.vector()>0 for i in range(tau*self.delta)]
        print(len(n.spikes))

        #self.dt = 0.001

        #self.rnd()

        #n.xi = n.vector()

    def iteration(self, n):
        #xi = (n.vector('uniform',density=0.5)>0)
        xi = np.random.normal(loc=0.0, scale=1.0, size=n.size)*13#*5

        #xi = np.sqrt(1/tau)*np.random.normal(loc=0.0, scale=1.0, size=n.size)

        #n.xi = dt * (-(n.xi - 0) / tau) + 1 * np.sqrt(dt) * np.random.randn()

        n.v += (-n.v + self.muext + self.sigmaext * np.sqrt(tau) * xi)/tau*dt

        n.spike = (n.v > self.theta) * (n.refrac > self.taurefr)
        #print(np.sum(n.spike), np.mean(n.v))
        n.refrac += 1.0 / tau*dt
        #print(n.refrac)
        n.v[n.spike] = self.Vr

        #n.spike *=
        n.refrac[n.spike] = 0.0

        n.spikes = np.roll(n.spikes, 1, axis=0)
        n.spikes[0] = n.spike.copy()
        #print(np.sum(n.spikes[-1]))



class Brunel_Hakim_input(Behavior):

    def initialize(self, n):
        for s in n.afferent_synapses['GLUTAMATE']:
            s.W = (s.matrix('uniform')<n.sparseness).astype(n.def_dtype) * (-n.J)#density=n.sparseness

            #print(s.W)

    def iteration(self, n):
        for s in n.afferent_synapses['GLUTAMATE']:
            act = s.W.dot(n.spikes[-1])#
            #act = np.sum(s.W[:, s.src.spikes[-1]], axis=1)
            print(np.sum(act), np.sum(n.spike))
            n.v += act#'V += -J'





My_Network = Network()

N_e = NeuronGroup(net=My_Network, tag='excitatory_neurons', size=get_squared_dim(1000), behavior={
    1: Brunel_Hakim_main(),
    2: Brunel_Hakim_input(),
    9: Recorder(['np.sum(spike)', 'spike'], tag='my_recorder', )
})

SynapseGroup(net=My_Network, src=N_e, dst=N_e, tag='GLUTAMATE')

My_Network.initialize()

My_Network.simulate_iterations(100*tau, measure_block_time=True)


#plt.plot(My_Network['v', 0])
#plt.show()

#plt.plot(My_Network['u', 0])
#plt.show()

w=5
data = My_Network['np.sum(spike)', 0, 'np']
data_smooth = data.copy()
for i in range(len(data)):
    mi = np.maximum(i-w, 0)
    ma = np.minimum(i+w, len(data)-1)
    data_smooth[i] = np.sum(data[mi:ma])/(ma-mi)

plt.plot(np.arange(len(data))/tau, data)
plt.show()

plt.plot(np.arange(len(data))/tau, data_smooth)
plt.show()

plt.imshow(My_Network['spike', 0, 'np'].transpose(), cmap='gray', aspect='auto')#, interpolation='none'
plt.show()


#from PymoNNto.Exploration.Network_UI import *
#my_UI_modules = get_default_UI_modules(['fired', 'v', 'u'], ['W'])
#Network_UI(My_Network, modules=my_UI_modules, label='My_Network_UI', group_display_count=2).show()