import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *
from NetworkBehaviour.Input.Images.MNIST_Patterns import *
from Testing.Common.Grammar_Helper import *

display = False
so = True

def run(tag='hierarchical', ind=[], par={'N_e':900, 'TS':[1]}):
    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    #source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=15/par['N_e'])#.plot_char_input_statistics()#output_size=par['N_e']#15
    #source = LongDelayGrammar(tag='grammar_act', output_size=par['N_e'], random_blocks=True, mode=['very simple'], input_density=10/par['N_e'])#.print_test().plot_char_input_statistics()
    #source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=20, grid_height=20, center_x=list(range(20)), center_y=30 / 2, degree=90, line_length=60)
    #print(source.get_text_score('. parrot likes trees. wolf wolf wolf..'))
    source = MNIST_Patterns(tag='image_act', group_possibility=1.0, repeat_same_label_time=1)

    SORN = Network()

    for timecale in par['TS']:

        e_ng = NeuronGroup(net=SORN, tag='PC_Neurons_{},prediction_source'.format(timecale), size=get_squared_dim(int(par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timecale, init_TH='0.05;+-80%', activation_function='binary'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='13%', distribution='lognormal(0,[0.89#0])', normalize=True, partition_compensation=True),
            4: SORN_init_afferent_synapses(transmitter='GABA', density='45%', distribution='lognormal(0,[0.80222#1])', normalize=True),#electrical synapses

            12: SORN_slow_syn(transmitter='GLU', strength='[0.14#2]'),
            13: SORN_slow_syn(transmitter='GABA', strength='-[0.14#3]'),
            17: SORN_fast_syn(transmitter='GABA', strength='-[0.03#4]'),

            18: SORN_random_act(chance=0.001),

            19: SORN_input_collect(),

            #20: SORN_Refractory(strength=1, factor='0.5;+-50%'),

            21: SORN_STDP(eta_stdp='[0.0001#5]', prune_stdp=False),
            22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

            23: SORN_IP_TI(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0006#8];+-50%', integration_length='[30#18];+-50%', clip_min=0.0),
            25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.0005#9];+-50%'),#0.4
            26: SORN_SC_TI(h_sc='lognormal_real_mean([0.01#10], [0.2944#11])', eta_sc='[0.1#12];+-50%', integration_length='1'),
            #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

            30: SORN_finish()
        })

        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,e->e', connectivity='(s_id!=d_id)*in_box(10)', partition=True)#.partition([10, 10], [6, 6])
        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GABA,e->e', connectivity='(s_id!=d_id)*in_box(10)', partition=True)#.partition([10, 10], [6, 6])

        e_ng.add_behaviour(9, SORN_external_input(strength=0.3, pattern_groups=[source]))
        if timecale == 1:
            e_ng.add_behaviour(101, NeuronRecorder(['n.pattern_index'], tag='inp_rec'))
        else:
            #forward synapses
            SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GLU,e->e(+1)', connectivity='in_box(10)', partition=True)#.partition([10, 10], [6, 6])
            SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GABA,e->i(+1)', connectivity='in_box(10)', partition=True)#.partition([10, 10], [2, 2])
            #backward synapses
            SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GLU,e(+1)->e', connectivity='in_box(10)', partition=True)#.partition([10, 10], [6, 6])
            SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GABA,e(+1)->i', connectivity='in_box(10)', partition=True)#.partition([10, 10], [2, 2])

        last_e_ng = e_ng
        e_ng.color = (0, 0, 255, 255)


    SORN.set_marked_variables(ind, info=(ind == []))
    SORN.initialize(info=False)

    ############################################################################################################################################################

    score = 0

    #SORN.simulate_iterations(10000, 100, measure_block_time=True, disable_recording=True)


    Network_UI(SORN, label='no inh neurons', storage_manager=sm, group_display_count=1).show()

    score += train_and_generate_text(SORN, 15000, 5000, 2000, display=False, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=15000)#, steps_recovery=15000
    #score += get_oscillation_score_hierarchical(SORN, 0, 5000)
    return score



if __name__ == '__main__':
    ind = []

    print('score', run(ind=ind, par={'N_e': 2900, 'TS':[1]}))#1400


    # 23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=0, gap_percent=10, clip_min=None),
    # 24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=0, gap_percent=0, clip_min=None),

    #while True:
    #    for N_e in [300, 600, 900, 1200, 1500, 1800, 2100]:

    #import Exploration.Evolution.Distributed_Evolution as DistEvo
    #tag, ind = DistEvo.parse_sys(ind=ind)
    #score = run(tag, ind)
    #DistEvo.save_score(score, tag, ind)
