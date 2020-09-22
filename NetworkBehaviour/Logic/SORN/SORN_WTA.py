from NetworkBehaviour.Input.Activator import *
from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *

class SORN_init_neuron_vars_decay(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('init_neuron_vars')

        neurons.activity = neurons.get_neuron_vec()
        neurons.excitation = neurons.get_neuron_vec()
        neurons.inhibition = neurons.get_neuron_vec()
        neurons.input_act = neurons.get_neuron_vec()

        neurons.timescale = self.get_init_attr('timescale', 1)

    def new_iteration(self, neurons):
        if first_cycle_step(neurons):
            neurons.activity *= 0.9
            neurons.excitation.fill(0)# *= 0
            neurons.inhibition.fill(0)# *= 0
            neurons.input_act.fill(0)# *= 0

class WTA_refrac(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory_A')
        neurons.refractory_counter_analog = neurons.get_neuron_vec()
        self.decayfactor = self.get_init_attr('decayfactor', 0.5, neurons)


    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            #neurons.activity -= neurons.refractory_counter_analog * self.strengthfactor

            neurons.refractory_counter_analog *= self.decayfactor
            neurons.refractory_counter_analog += neurons.output

class WTA_refrac_apply(Neuron_Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Refractory_Apply')
        self.strengthfactor = self.get_init_attr('strengthfactor', 1.0, neurons)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons):
            neurons.activity -= neurons.refractory_counter_analog * self.strengthfactor

class SORN_slow_syn_simple(SORN_signal_propagation_base):

    def set_variables(self, neurons):
        super().set_variables(neurons)
        self.add_tag('slow_simple' + self.transmitter)

    def new_iteration(self, neurons):
        if last_cycle_step(neurons) and self.strength != 0:

            for s in neurons.afferent_synapses[self.transmitter]:
                s.slow_add = s.W.dot(s.src.output) * self.strength

                s.dst.activity += s.slow_add
                if self.strength > 0:
                    s.dst.excitation += s.slow_add
                else:
                    s.dst.inhibition += s.slow_add
