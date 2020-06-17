import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
from NetworkBehaviour.Input.Text.TextActivator import *
#from NetworkBehaviour.Input.Images.Lines import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *
from Testing.Common.Grammar_Helper import *
from Exploration.UI.Network_UI.Network_UI import *


def get_color(type_index, layer):
    dim_value = max(layer * 1.0, 1.0)

    if type_index == 0:
        return (0.0, 0.0, 255.0 / dim_value, 255.0)
    if type_index == 1:
        return (255.0 / dim_value, 0.0, 0.0, 255.0)
    if type_index == 2:
        return (255.0 / dim_value, 150.0 / dim_value, 0.0, 255.0)
    if type_index == 3:
        return (255.0 / dim_value, 80.0 / dim_value, 0.0, 255.0)
    if type_index == 4:
        return (255.0 / dim_value, 0.0 , 150.0/ dim_value, 255.0)


display = False
so = False

def run(tag='hierarchical', ind=[], par={'N_e':900, 'TS':[1]}):
    #print(tag, par)

    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    #source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=15/par['N_e'])#.plot_char_input_statistics()#output_size=par['N_e']#15
    #print(len(source.alphabet))
    source = LongDelayGrammar(tag='grammar_act', output_size=par['N_e'], random_blocks=True, mode=['simple'], input_density=0.015)#.print_test()#.plot_char_input_statistics()#10/par['N_e']
    #source.plot_char_input_statistics()
    #print(len(source.alphabet))
    #source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)
    #print(source.get_text_score('. parrot likes trees. wolf wolf wolf..'))


    SORN = Network()

    last_e_ng = None

    for timecale in par['TS']:

        e_ng = NeuronGroup(net=SORN, tag='PC_{},prediction_source'.format(timecale), size=get_squared_dim(int(par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timecale, init_TH='0.1;+-100%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='13%', distribution='lognormal(0,[0.95#0])', normalize=True, partition_compensation=True),#0.89 uniform(0.1,0.11)
            4: SORN_init_afferent_synapses(transmitter='GABA', density='45%', distribution='lognormal(0,[0.4#1])', normalize=True),#0.80222 uniform(0.1,0.11)

            12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
            13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]', so=False),
            17: SORN_fast_syn(transmitter='GABA', strength='-[0.1#4]', so=False),#0.11045
            18: SORN_input_collect(),

            19: SORN_Refractory(factor='0.5;+-50%'),
            21: SORN_STDP(eta_stdp='[0.00015#5]', prune_stdp=False),
            22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

            23: SORN_IP_TI(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0006#8];+-50%', integration_length='[15#18];+-50%', clip_min=None),#30          #, gap_percent=10 #30;+-50% #0.0003 #np.mean(n.output_new)
            25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
            26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%', integration_length='1'),#60;+-50% #0.05
            27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

            30: SORN_finish(),

        })

        i_ng = NeuronGroup(net=SORN, tag='Inter_{}'.format(timecale), size=get_squared_dim(int(0.2 * par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timecale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,[0.87038#14])', normalize=True),  # 450
            4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),
            14: SORN_fast_syn(transmitter='GLU', strength='[1.5#16]', so=so),#1.5353
            15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            18: SORN_input_collect(),

            19: SORN_Refractory(factor='0.2;0.7'),

            #23: SORN_IP_TI(h_ip='lognormal_real_mean([0.08#6], [0.2944#7])', eta_ip='[0.0003#8];+-50%', integration_length='30;+-50%', clip_min=None),

            30: SORN_finish()
        })

        i_ng['structure', 0].stretch_to_equal_size(e_ng)

        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU', connectivity='(s_id!=d_id)*in_box(10)', partition=True)#.partition([10, 10], [partition, partition])
        SynapseGroup(net=SORN, src=e_ng, dst=i_ng, tag='GLU', connectivity='in_box(10)', partition=True)#.partition([5, 5], [2, 2])
        SynapseGroup(net=SORN, src=i_ng, dst=e_ng, tag='GABA', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=i_ng, dst=i_ng, tag='GABA', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

        #i_ng.add_behaviour(10, SORN_external_input(strength=1.0, pattern_groups=[source]))

        e_ng.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))

        if last_e_ng is not None:
            #forward synapses
            SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GLU', connectivity='in_box(10)', partition=True)#.partition([10, 10], [partition, partition])
            SynapseGroup(net=SORN, src=last_e_ng, dst=i_ng, tag='GABA', connectivity='in_box(10)', partition=True)#.partition([5, 5], [2, 2])
            #backward synapses
            SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GLU', connectivity='in_box(10)', partition=True)#.partition([10, 10], [partition, partition])
            SynapseGroup(net=SORN, src=e_ng, dst=last_i_ng, tag='GABA', connectivity='in_box(10)', partition=True)#.partition([5, 5], [2, 2])

        last_e_ng = e_ng
        last_i_ng = i_ng

        e_ng.color = get_color(0, timecale)
        i_ng.color = get_color(1, timecale)

    SORN.set_marked_variables(ind, info=(ind == []), storage_manager=sm)
    SORN.initialize(info=False)

    ###################################################################################################################

    score = 0

    #Network_UI(SORN, label='SORN UI default setup', storage_manager=sm, group_display_count=2, reduced_layout=True).show()

    score += train_and_generate_text(SORN, 15000, 5000, 2000, display=True, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=2000, storage_manager=sm)#, steps_recovery=15000
    #score += get_oscillation_score_hierarchical(SORN, 0, 5000)
    return score


if __name__ == '__main__':
    ind = []

    #[0, 0, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 1.5,
    # 0.08, 15.0]

    #ind = [1.9885183142193665, 0.3528676114105281, 0.24293073527845382, 0.07814635333232621, 0.10466743169771203,
    # 0.00020040809701738442, 0.029976848527756485, 0.5062951643302883, 0.0003280293532779789, 0.25549904356473374,
    # 0.01186188477659828, 0.30858374631247465, 0.04531339968695495, 0.00015298827333019708, 0.7780073202827255,
    # 0.9592630734316344, 2.6058783963464665, 0.07115721420669135, 9.287972147118964]

    #original
    #ind = [0.89, 0.80222, 0.1383, 0.1698, 0.11045, 0.0001, 0.04, 0.2944, 0.0006, 0.3, 0.01, 0.2944, 0.1, 0.0001, 0.87038,0.82099, 1.5, 0.08, 30.0]
    #bv:
    #ind = [4.24289026824522, 0.1772551762687538, 0.10334918756466115, 0.2689743758706922, 0.041718700386009305, 0.00014380428405254888, 0.044381807703706956, 0.19567408560566968, 0.0010460542504209989, 0.11012200304339823, 0.01588825464021605, 0.22199256517434313, 0.015329201503661292, 5.4803392906312225e-05, 0.5059785852681881, 0.5495712393492611, 1.9563902980182912, 0.040728651397532685, 14.814732459232534]
    #xps:
    #ind = [0.6828200083021586, 0.6050826299550228, 0.27340764947165486, 0.11895670182349916, 0.09240731578767125, 0.00016169410156046727, 0.03073392425413874, 0.3144793476060314, 0.0002815704596128816, 0.22574975043865556, 0.013842493647697771, 0.37396533444265084, 0.11193287910054223, 9.52953796589554e-05, 1.1186328285166929, 0.6188618067727688, 1.4402062021072555, 0.08858786066982591, 22.846206788079957]

    #for i in range(10):
    print('blub', run(tag='test', ind=ind, par={'N_e': 900, 'TS': [1]}))

    #print('score', run(tag='blub', ind=ind, par={'N_e': 900, 'TS': [1]}))

    # 23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=0, gap_percent=10, clip_min=None),
    # 24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=0, gap_percent=0, clip_min=None),

    #while True:
    #    for N_e in [300, 600, 900, 1200, 1500, 1800, 2100]:

    #import Exploration.Evolution.Distributed_Evolution as DistEvo
    #tag, ind = DistEvo.parse_sys(ind=ind)
    #score = run(tag, ind)
    #DistEvo.save_score(score, tag, ind)
