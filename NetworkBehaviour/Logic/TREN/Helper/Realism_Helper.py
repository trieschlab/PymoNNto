def max_neuron_frequency():
    #if pc ...
    return 200.0

def min_spike_interval():
    return 1000.0/max_neuron_frequency()

def GammaBlock_to_ms():
    return 25.0

def GammaBlock_to_Hz(x):
    return x*(1000/(GammaBlock_to_ms()/min_spike_interval()))