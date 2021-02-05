from SORNSim.NetworkCore.Behaviour import *

class STDP(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('STDP')
        neurons.stdp_factor = self.get_init_attr('stdp_factor', 0.00015, neurons)
        self.syn_type = self.get_init_attr('syn_type', 'GLUTAMATE', neurons)
        neurons.voltage_old = neurons.get_neuron_vec()

    def new_iteration(self, neurons):

        for s in neurons.afferent_synapses[self.syn_type]:

            pre_post = s.dst.voltage[:, None] * s.src.voltage_old[None, :]
            simu = s.dst.voltage[:, None] * s.src.voltage[None, :]
            post_pre = s.dst.voltage_old[:, None] * s.src.voltage[None, :]

            dw = neurons.stdp_factor * (pre_post - post_pre + simu)

            s.W = np.clip(s.W+dw*s.enabled, 0.0, 10.0)

        neurons.voltage_old = neurons.voltage.copy()
