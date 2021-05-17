from PymoNNto.NetworkCore.Behaviour import *
from PymoNNto.NetworkBehaviour.EulerEquationModules.Helper import *

class Variable(Behaviour):

    def set_variables(self, neurons):
        n = neurons

        eq_parts = eq_split(self.get_init_attr('eq', None))

        if eq_parts[1] == '=' and len(eq_parts) >= 3:
            self.var_name = eq_parts[0]
        else:
            print('invalid formula')

        self.add_tag('Variable '+self.var_name)

        eq_parts = remove_units(eq_parts, 2)

        self.var_init = ''.join(eq_parts[2:])

        setattr(n, self.var_name, neurons.get_neuron_vec() + eval(self.var_init))#symbols('n.'+self.var_name) #+

        setattr(n, self.var_name+'_new', neurons.get_neuron_vec() + eval(self.var_init))

    def new_iteration(self, n):
        setattr(n, self.var_name, getattr(n, self.var_name+'_new'))#apply the new value to variable


class Syn_Variable(Behaviour):

    def set_variables(self, synapse):
        s = synapse

        eq_parts = eq_split(self.get_init_attr('eq', None))

        if eq_parts[1] == '=' and len(eq_parts) >= 3:
            self.var_name = eq_parts[0]
        else:
            print('invalid formula')

        self.add_tag('Syn_Variable '+self.var_name)

        eq_parts = remove_units(eq_parts, 2)

        self.var_init = ''.join(eq_parts[2:])

        setattr(s, self.var_name, synapse.get_synapse_mat() + eval(self.var_init))#symbols('n.'+self.var_name) #+

        setattr(s, self.var_name+'_new', synapse.get_synapse_mat() + eval(self.var_init))

    def new_iteration(self, s):
        setattr(s, self.var_name, getattr(s, self.var_name+'_new'))#apply the new value to variable

