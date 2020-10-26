from NetworkCore.Behaviour import *
from NetworkBehaviour.Logic.EulerEquationModules.Helper.Helper import *
import numpy as np
from sympy import symbols
import sympy.physics.units as units
from sympy import symbols
from sympy.physics.units import *

print('blub' in units.__dict__)

class EquationModule(Behaviour):

    def set_variables(self, neurons):
        n=neurons
        self.add_tag('EquationModule')
        self.step_size = self.get_init_attr('step_size', '1*ms', neurons)
        eq_parts = eq_split(self.get_init_attr('eq', None))

        #print(eq_parts)

        if eq_parts[0][0] == 'd' and eq_parts[1] == '/' and eq_parts[2] == 'dt' and eq_parts[3] == '=':
            self.variable = eq_parts[0][1:]
            symbols('n.' + self.variable)
        else:
            print('invalid equation')

        for i in range(4, len(eq_parts)):
            if eq_parts[i] in neurons.__dict__:
                eq_parts[i] = 'n.'+eq_parts[i]

        i=4
        while i<len(eq_parts):
            if eq_parts[i] == 'ms':

                t = float(convert_to(eval(eq_parts[i - 2]+eq_parts[i - 1]+eq_parts[i]), seconds) / second)

                #print(t)

                eq_parts[i - 2] = '{}'.format(t)

                #eq_parts[i-2] = '1000/'+eq_parts[i-2]
                eq_parts.pop(i)
                eq_parts.pop(i-1)
                i -= 2

            elif eq_parts[i] in units.__dict__ or eq_parts[i] in myUnits: #remove units
                eq_parts.pop(i)
                eq_parts.pop(i-1)
                i -= 2

            i += 1

        self.evaluation = 'n.' + self.variable + '+(' + ''.join(eq_parts[4:])+')*{}'.format(neurons.clock_step_size)


        #self.evaluation += ''#*{}'.format(neurons['Clock', 0].)

        print(self.evaluation)
        #print('conv:',convert_to(eval(self.evaluation),second))


        #print(self.variable, self.evaluation)


    def new_iteration(self, n):
        new = eval(self.evaluation)
        #print(new)
        setattr(n, self.variable, new)

