from PymoNNto.NetworkCore.Behavior import *

class STDP(Behavior):

    def initialize(self, neurons):
        self.stdp_factor = self.parameter('stdp_factor', 0.0015, neurons)
        self.syn_type = self.parameter('syn_type', 'GLUTAMATE', neurons)
        neurons.spike_old = neurons.vector()

    def iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            pre_post = s.dst.spike[:, None] * s.src.spike_old[None, :]
            simu = s.dst.spike[:, None] * s.src.spike[None, :]
            post_pre = s.dst.spike_old[:, None] * s.src.spike[None, :]

            dw = self.stdp_factor * (pre_post - post_pre + simu)

            #print(np.sum(pre_post),np.sum(post_pre),np.sum(simu))

            s.W = np.clip(s.W+dw*s.enabled, 0.0, 10.0)

        neurons.spike_old = neurons.spike.copy()
