import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
from NetworkBehaviour.Input.Text.TextActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *

display = False

def run(tag='test', ind=[], par={'N_e':900}):
    #print(ind)
    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    #source = FDTGrammarActivator_New(tag='grammar_act', output_size=par['N_e'], random_blocks=True)

    source = LongDelayGrammar(tag='grammar_act', output_size=par['N_e'], random_blocks=True, mode=['simple'])#.print_test()

    #[0.13, 0.169, 0.113, 0.15, 1.525, 0.08, 0.28758, 0.001015, 0.836, 0.792, 0.8659, 0.83678, 0.05]

    lag=1
    e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(par['N_e']),
                       behaviour={
                           1: NeuronActivator(write_to='input', pattern_groups=[source]),
                           2: SORN_init_neuron_vars(iteration_lag=lag, init_TH='0.0;0.2'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density='13%', distribution='lognormal(0,[0.89#0])', normalize=True, partition_compensation=True),  # 100
                           4: SORN_init_afferent_synapses(transmitter='GABA', density='45%', distribution='lognormal(0,[0.80222#1])', normalize=True),
                           # 90

                           12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', input_strength=1.0),
                           13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]'),

                           17: SORN_fast_syn(transmitter='GABA', strength='-[0.11045#4]'),
                           18: SORN_input_collect(),

                           19: SORN_Refractory(strength=1, factor='0.2;0.7'),  # 0.5;0.9 #0.8;0.99

                           21: SORN_STDP(eta_stdp='[0.01#5]', prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),
                           23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=1, gap_percent=10, clip_min=None),
                           24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=1, gap_percent=0, clip_min=None),

                           25: SORN_SC_TI(mp='excitation', h_sc='lognormal_real_mean([0.01#10], [0.2944#11])', eta_sc='[0.1#12];+-30%'),
                           26: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

                           30: SORN_finish(),

                           100: NeuronRecorder(['n.output'], tag='exc_out_rec'),
                           101: NeuronRecorder(['n.pattern_index'], tag='inp_rec')
                       })

    i_ng = NeuronGroup(tag='main_inh_group', size=get_squared_dim(int(0.2 * par['N_e'])), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=lag, init_TH='0.1'),
        3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,[0.87038#14])', normalize=True),  # 450
        4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

        11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]'),
        14: SORN_fast_syn(transmitter='GLU', strength='[1.5353#17]'),
        15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#18]'),
        18: SORN_input_collect(),

        19: SORN_Refractory(strength=1, factor='0.2;0.7'),

        30: SORN_finish(),

        100: NeuronRecorder(['n.output'], tag='inh_out_rec')
    })

    ee_syn = SynapseGroup(src=e_ng, dst=e_ng, connectivity='s_id!=d_id', tag='GLU')
    ie_syn = SynapseGroup(src=e_ng, dst=i_ng, tag='GLU')
    ei_syn = SynapseGroup(src=i_ng, dst=e_ng, tag='GABA')
    ii_syn = SynapseGroup(src=i_ng, dst=i_ng, tag='GABA')

    SORN_Global = Network([e_ng, i_ng], [ee_syn, ie_syn, ei_syn, ii_syn], initialize=False)

    SORN_Global.set_marked_variables(ind, info=(ind == []))

    SORN_Global.partition_Synapse_Group(ee_syn, [10, 10], [4, 4])
    SORN_Global.partition_Synapse_Group(ie_syn, [5, 5], [2, 2])
    ##SORN_Global.partition_Synapse_Group(ei_syn, [5, 5], [2, 2])

    SORN_Global.initialize(info=False)

    ####################################################
    ####################################################
    ####################################################

    #return SORN_Global.simulate_iterations(100, measure_block_time=True)

    #import Exploration.UI.Network_UI as SUI
    #SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    return 100+get_spontaneous_grammar_score(SORN_Global, 'main_exc_group', 'exc_out_rec', 'inp_rec', 20000, 5000, 0, 2000, display=True, stdp_off=True)
    #return get_evolution_score_words(SORN_Global, 20000, 5000, 2000, display=True, stdp_off=True, storage_manager=sm)
    #return get_evolution_score(SORN_Global, 5000, 3000, 0.2, e_ng, i_ng)#0.04
    #return get_evolution_score_simple(SORN_Global, 5000, 4000, e_ng)



if __name__ == '__main__':
    run(par={'N_e': 900})


    #a=[]
    #b=[]
    #c=[]
    #for _ in range(5):
    #    for x in range(8):
    #        for y in range(8):
    #            a.append(x+1)
    #            b.append(y+1)
    #            c.append(run(par={'N_e': 900, 'xs':x+1, 'ys':y+1}))

    #import matplotlib.pyplot as plt
    #fig = plt.figure()
    #ax = fig.gca(projection='3d')
    #ax.scatter(a, b, c, marker='o')
    #a, b = np.meshgrid(a, b)
    #ax.plot_surface(a, b, np.array(c).reshape((5,5)))
    #plt.show()


    #while True:
    #    for N_e in [300, 600, 900, 1200, 1500, 1800, 2100, 2400, 2700]:
    #        run('size_comp', ind, par={'N_e': N_e})

    #import Exploration.Evolution.Distributed_Evolution as DistEvo
    #tag, ind = DistEvo.parse_sys(ind=ind)
    #score = run(tag, ind)
    #DistEvo.save_score(score, tag, ind)

#ind = [0.13836856717331408,
#       0.16982974221677782,
#       0.11045406247494298,
#       0.1838996599635843,
#       1.5353184446420107,
#       0.08049924935792714,
#       0.2943968676418953,
#       0.0009456577980814013,
#       0.8900762238158484,
#       0.8022238912339718,
#       0.8703833239674005,
#       0.8209942320661112, 0.051296268342171394, 0.050399158855638226]