import sys
sys.path.append('../../TREN2')

from Testing.Old.SORN_simple_behaviour import *
from NetworkCore.Network import *
from NetworkCore.Neuron_Group import *
from NetworkCore.Synapse_Group import *


SORN_1_e = NeuronGroup(size=1600, behaviour={
    0: NeuronActivator(write_to='input', pattern_groups=[GrammarActivator(N_e=1600)]),
    1: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=10),
    2: SORN_STDP(eta_stdp=0.005, prune_stdp=False),
    3: SORN_SN(syn_type='GLU'),
    4: SORN_iSTDP(eta_istdp=0.001, h_ip=0.1),
    5: SORN_SN(syn_type='GABA'),
    6: SORN_IP(h_ip=0.1, eta_ip=0.001),
    7: SORN_SP(sp_prob=0.1, sp_init=0.001, syn_type='GLU'),
    8: SORN_finish(),
    9: Recorder(['np.sum(n.x)', 'n.x', 'n.input', 'n.pattern_index'])
})


SORN_1_i = NeuronGroup(size=int(0.2*1600), behaviour={
    1: SORN_Input_collect(T_min=0.0, T_max=0.5),
    8: SORN_finish()
})

ee = SynapseGroup(src=SORN_1_e, dst=SORN_1_e, connectivity='s_id!=d_id').add_tag('GLU')
ie = SynapseGroup(src=SORN_1_e, dst=SORN_1_i).add_tag('GLU')
ei = SynapseGroup(src=SORN_1_i, dst=SORN_1_e).add_tag('GABA')

SORN_Global = Network([SORN_1_e, SORN_1_i], [ee, ie, ei])


#for i in range(1000):
#    SORN_Global.simulate_iteration()
#    print(i)

SORN_Global.simulate_iterations(10, 10, True)


import matplotlib.pyplot as plt
plt.plot(SORN_1_e[9]['n.pattern_index'])
#print(SORN_1_e[9]['np.sum(n.x)'])
#print(SORN_1_e[9]['n.pattern_index'])
plt.show()


#path='../../Data/test/'
#print((SORN_1_e[9]['np.sum(n.x)']))
#SORN_1_e[9].save_all(path)
#vars=load_all(path)
#print((vars['np.sum(n.x)']))