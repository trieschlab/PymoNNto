from PymoNNto import *

def behavior_test_environment(behavior, size=1, initialize=True, iteration=0):
    net = Network(tag='Network')

    if type(behavior) != dict:
        behavior={1:behavior}

    ng = NeuronGroup(tag='Neuron', net=net, behavior=behavior, size=size)

    if initialize:
        net.initialize()

    for i in range(iteration):
        net.simulate_iteration()

    return net, ng, behavior