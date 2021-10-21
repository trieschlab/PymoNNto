from PymoNNto import *

def behaviour_test_environment(behaviour, size=1, initialize=True, iteration=0):
    net = Network(tag='Network')

    if type(behaviour) != dict:
        behaviour={1:behaviour}

    ng = NeuronGroup(tag='Neuron', net=net, behaviour=behaviour, size=size)

    if initialize:
        net.initialize()

    for i in range(iteration):
        net.simulate_iteration()

    return net, ng, behaviour