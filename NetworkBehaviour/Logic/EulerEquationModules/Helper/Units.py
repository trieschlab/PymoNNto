
#def evaluate_unit(unit_string):
#    if time in unit_string

time_units = ['seconds', 'minutes', 'hours', 'milliseconds', 'ms']

seconds = 1.0
minutes = seconds*60
hours = minutes*60
milliseconds = seconds/1000
ms = milliseconds

units = time_units+[]

def initialize_object_variable_unit_dict(obj):
    if not hasattr(obj, 'variable_unit_dict'):
        obj.variable_unit_dict = {}

def split_equation_and_unit(str):
    str=str.replace(' ','')
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


    quantity_formula_parts = []
    unit_formula_parts = []
    for part in parts:
        if part in units:
            quantity_formula_parts.append('1.0')
            unit_formula_parts.append(part)
        elif not part in unit:
            quantity_formula_parts.append(part)
            unit_formula_parts.append(part)
        else:#operators
            quantity_formula_parts.append(part)
            unit_formula_parts.append(part)

    equation = ''.join(parts)
    unit = ''.join(parts)

    return equation, unit



