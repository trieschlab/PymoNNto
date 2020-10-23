from sympy import symbols
from sympy import solve, symbols, pi, Eq
from sympy.physics.units.systems import SI
from sympy.physics.units import *
from sympy.physics.units import gravitational_constant as G
from sympy.physics.units.systems.si import dimsys_SI
from sympy.physics.units.util import *

import numpy as np

import matplotlib.pyplot as plt

#vec = np.array([1,2,3])



#x = 10*mV

#y = 100*mV

#print(float(x/y))


#F = mass*acceleration
#Dimension(acceleration*mass)
#dimsys_SI.get_dimensional_dependencies(F)
#{'length': 1, 'mass': 1, 'time': -2}
#dimsys_SI.get_dimensional_dependencies(force)
#{'length': 1, 'mass': 1, 'time': -2}


#from sympy.physics.units import Quantity
#def unit(expr):
#    return expr.subs({x: 1 for x in expr.args if not x.has(Quantity)})



#class cl:
#    def __init__(self):
#        self.test=1

#c=cl()

#print(c.__dict__)

#mV = milli*volts

#tau = 1*ms


#tau = solve(tau,T)
#c.x = symbols('c.x')
#setattr(c, 'x', symbols('c.x'))
#print(tau)

#v = (0*volts-c.x*volts)/tau

#dv/dt = (5-v)/tau
#convert_to
#u=unit(v)

#print(unit(v))
#print(convert_to(v*seconds/u, T)) #
#print(check_dimensions(v))





tau = 10*ms#*seconds


print(convert_to(tau, seconds)/second)

scale=float(convert_to(seconds/tau,seconds))

print(scale)

x = 100*volt
# = #/tau

values = []
for i in range(100):
    x = x+(0*volt-x)/scale    #v + (0*volts - v)/(tau/ms)#convert_to(v, volts)
    values.append(x / volts)
    print(x)

plt.plot(values)
plt.show()
