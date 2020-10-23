from NetworkCore.Behaviour import *
from NetworkBehaviour.Logic.EulerEquationModules.Helper.Helper import *
from sympy import symbols
import numpy as np
import sympy.physics.units as units
from sympy.physics.units import *

class Variable(Behaviour):

    def set_variables(self, neurons):
        n = neurons

        eq_parts = eq_split(self.get_init_attr('eq', None))

        if eq_parts[1] == '=' and len(eq_parts) >= 3:
            self.var_name = eq_parts[0]
        else:
            print('invalid formula')

        #self.var_name = self.get_init_attr('var_name', '1')
        self.add_tag('Variable '+self.var_name)
        #self.var_value = self.get_init_attr('var_value', '1', neurons)
        #self.var_unit= self.get_init_attr('var_unit', '1', neurons)

        i = 2
        while i<len(eq_parts):

            if eq_parts[i] == 'ms':

                t = float(convert_to(eval(eq_parts[i - 2]+eq_parts[i - 1]+eq_parts[i]), seconds) / second)

                #print(t)

                eq_parts[i - 2] = '{}'.format(t)

                #eq_parts[i-2] = '1000/'+eq_parts[i-2]
                eq_parts.pop(i)
                eq_parts.pop(i-1)
                i -= 2

            if eq_parts[i] in units.__dict__ or eq_parts[i] in myUnits: #remove units
                eq_parts.pop(i)
                eq_parts.pop(i-1)
                i -= 2
            i+=1

        self.var_init = ''.join(eq_parts[2:])

        print(self.var_init)

        setattr(n, self.var_name, neurons.get_neuron_vec()+eval(self.var_init))#symbols('n.'+self.var_name) #+



