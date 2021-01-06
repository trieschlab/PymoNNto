from sympy import symbols
import sympy.physics.units as units
from sympy.physics.units import *

def eq_split(eq):
    str=eq.replace(' ', '')
    parts = []
    str_buf = ''
    for s in str:
        if s in ['*', '/', '+', '-', '%', ':', ';', '=', '!', '(', ')', '[', ']']:
            parts.append(str_buf)
            parts.append(s)
            str_buf = ''
        else:
            str_buf += s

    parts.append(str_buf)
    return parts

def remove_units(eq_parts, i):

    while i < len(eq_parts):

        if eq_parts[i] == 'ms':

            t = float(convert_to(eval(eq_parts[i - 2] + eq_parts[i - 1] + eq_parts[i]), seconds) / second)

            eq_parts[i - 2] = '{}'.format(t)

            # eq_parts[i-2] = '1000/'+eq_parts[i-2]
            eq_parts.pop(i)
            eq_parts.pop(i - 1)
            i -= 2

        if eq_parts[i] in units.__dict__ or eq_parts[i] in myUnits:  # remove units
            eq_parts.pop(i)
            eq_parts.pop(i - 1)
            i -= 2
        i += 1

    return eq_parts

myUnits=['mV']