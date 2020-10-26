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

myUnits=['mV']