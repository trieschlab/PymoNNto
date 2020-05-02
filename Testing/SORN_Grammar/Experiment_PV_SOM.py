import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *
from NetworkBehaviour.Input.Text.TextActivator import *
#from NetworkBehaviour.Input.Images.Lines import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *
from Testing.Common.Grammar_Helper import *
if __name__ == '__main__':
    from Exploration.UI.Network_UI.Network_UI import *



def run(attrs={'name':'PV_SOM', 'ind':[], 'N_e':900, 'TS':[1]}):
    so = True

    print_info = attrs.get('print', True)

    if print_info:
        print(attrs)

    sm = StorageManager(attrs['name'], random_nr=True, print_msg=print_info)
    sm.save_param_dict(attrs)

    #source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=15/par['N_e'])#.plot_char_input_statistics()#output_size=par['N_e']#15
    #print(len(source.alphabet))
    source = LongDelayGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, mode=['simple'], input_density=0.015)#.print_test().plot_char_input_statistics()#10/par['N_e']
    #source.plot_char_input_statistics()
    #print(len(source.alphabet))
    #source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)
    #source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)
    #print(source.get_text_score('. parrot likes trees. wolf wolf wolf..'))

    SORN = Network()#[], [], initialize=False
    last_PC = None

    for timescale in attrs['TS']:

        PC = NeuronGroup(net=SORN, tag='Pyramidal Cell {},prediction_source'.format(timescale), size=get_squared_dim(int(attrs['N_e'])), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale, init_TH='0.1;+-100%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='[50#0]%', distribution='lognormal(0,0.6)', normalize=True, partition_compensation=True), #lognormal(0,0.6)
            4: SORN_init_afferent_synapses(transmitter='GABA_Dendrite', density='[30#1]%', distribution='uniform(0.1,0.11)', normalize=True),
            5: SORN_init_afferent_synapses(transmitter='GABA_Soma', density='[30#2]%', distribution='uniform(0.1,0.11)', normalize=True),
            6: SORN_init_afferent_synapses(transmitter='GABA_AIS', density='[30#3]%', distribution='uniform(0.1,0.11)', normalize=True),
            #7: SORN_init_afferent_synapses(transmitter='GABA_NOX', density='full', distribution=None, normalize=True),

            12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#4]', so=so),
            13: SORN_slow_syn(transmitter='GABA_Dendrite', strength='-0.1', so=False),

            17: SORN_fast_syn(transmitter='GABA_Soma', strength='-0.1', so=False),
            17.1: SORN_fast_syn(transmitter='GABA_AIS', strength='-0.1', so=False),
            #17.2: SORN_fast_syn(transmitter='GABA_NOX', strength='-0.1', so=False),
            18: SORN_generate_output(),
            19: SORN_buffer_variables(),

            20: SORN_Refractory(factor='[0.5#5];+-50%'),
            21: SORN_STDP(eta_stdp='[0.0015#6]'),#0.1#todo: test!!!, prune_stdp=False, excitation_punishment=0.0
            22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

            23: SORN_IP_TI(mp='n.output', h_ip='lognormal_real_mean([0.04#7], [0.2944#8])', eta_ip='[0.0006#9];+-50%', integration_length='[15#10];+-50%', clip_min=None),#mp='n.output_new/2.0+n.output_new_temp/2.0'
            25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='0.5;+-50%', h_dh=0.0),#0.9#0.3
            26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#11], [0.2944#12])', eta_sc='[0.1#13];+-50%', integration_length='1'),
            #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),
        })

        MT_SOM = NeuronGroup(net=SORN, tag='Martinotti Cell {},Somatostatin'.format(timescale), size=get_squared_dim(int(0.07 * attrs['N_e'])), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            10: SORN_slow_syn(transmitter='GLU', strength='0.6', so=so),  # 1.5353
            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),

            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            18: SORN_generate_output(),
            19: SORN_buffer_variables(),
            #20: SORN_Refractory(factor='0.2;0.7'),
        })

        EXP_NOX_CELL = NeuronGroup(net=SORN, tag='NOX Cell {}'.format(timescale), size=get_squared_dim(int(16)), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale, init_TH='0.0', digital_output=False),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution=None, normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            10: SORN_slow_syn(transmitter='GLU', strength='9.0', so=so),#1.5353
            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),

            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            18: SORN_generate_output(),
            19: SORN_buffer_variables(),
            #20: SORN_Refractory(factor='0.2;0.7'),
        })

        BA_PV = NeuronGroup(net=SORN, tag='Basket Cell {},Parvalbumin'.format(timescale), size=get_squared_dim(int(0.07 * attrs['N_e'])), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            10: SORN_slow_syn(transmitter='GLU', strength='0.6', so=so),  # 1.5353
            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),

            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            18: SORN_generate_output(),
            19: SORN_buffer_variables(),
            #20: SORN_Refractory(factor='0.2;0.7'),
        })

        CH_PV = NeuronGroup(net=SORN, tag='Chandelier Cell {},Parvalbumin'.format(timescale), size=get_squared_dim(int(0.07 * attrs['N_e'])), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),
            14: SORN_fast_syn(transmitter='GLU', strength='0.2', so=so),#1.5353
            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08

            18: SORN_generate_output(),
            19: SORN_buffer_variables(),
            #19: SORN_Refractory(factor='0.2;0.7'),
        })

        MT_SOM['structure', 0].stretch_to_equal_size(PC)
        BA_PV['structure', 0].stretch_to_equal_size(PC)
        CH_PV['structure', 0].stretch_to_equal_size(PC)
        EXP_NOX_CELL['structure', 0].stretch_to_equal_size(PC)

        #plt.scatter(PC.x, PC.y)
        #plt.scatter(MT_SOM.x, MT_SOM.y)
        #plt.scatter(BA_PV.x, BA_PV.y)
        #plt.scatter(CH_PV.x, CH_PV.y)
        #plt.scatter(EXP_NOX_CELL.x, EXP_NOX_CELL.y)
        #plt.show()

        #print(np.min(EXP_NOX_CELL.x), np.max(EXP_NOX_CELL.x))
        #print(np.min(EXP_NOX_CELL.y), np.max(EXP_NOX_CELL.y))

        #print(np.min(PC.x), np.max(PC.x))
        #print(np.min(PC.y), np.max(PC.y))

        SynapseGroup(net=SORN, src=PC, dst=PC, tag='GLU', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=PC, dst=MT_SOM, tag='GLU', connectivity='in_box(2)', partition=True)
        SynapseGroup(net=SORN, src=PC, dst=BA_PV, tag='GLU', connectivity='in_box(2)', partition=True)
        SynapseGroup(net=SORN, src=PC, dst=CH_PV, tag='GLU', connectivity='in_box(2)', partition=True)

        SynapseGroup(net=SORN, src=PC, dst=EXP_NOX_CELL, tag='GLU', connectivity='in_box(3.75)', partition=True)

        SynapseGroup(net=SORN, src=MT_SOM, dst=PC, tag='GABA_Dendrite', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=BA_PV, dst=PC, tag='GABA_Soma', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=CH_PV, dst=PC, tag='GABA_AIS', connectivity='in_box(10)', partition=True)

        SynapseGroup(net=SORN, src=EXP_NOX_CELL, dst=PC, tag='GABA_NOX', connectivity='in_box(3.75)', partition=True)

        #SynapseGroup(net=SORN, src=SOM, dst=SOM, tag='GABA_D,SOM->SOM', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)
        #SynapseGroup(net=SORN, src=SOM, dst=PV, tag='GABA_D,SOM->PV', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)
        ##SynapseGroup(net=SORN, src=PV, dst=SOM, tag='GABA_P,PV->SOM')#not realistic?
        #SynapseGroup(net=SORN, src=PV, dst=PV, tag='GABA_P,PV->PV', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)

        if last_PC is None:
            PC.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))
            #MT_SOM.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))
            #BA_PV.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))
            #CH_PV.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))
        #else:
        #    #forward synapses
        #    SynapseGroup(net=SORN, src=last_PC, dst=PC, tag='GLU,PC->PC(+1)', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)#.partition([10, 10], [partition, partition])
        #    SynapseGroup(net=SORN, src=last_PC, dst=SOM, tag='GABA,PC->SOM(+1)', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)#.partition([5, 5], [2, 2])
        #    #backward synapses
        #    SynapseGroup(net=SORN, src=PC, dst=last_PC, tag='GLU,PC(+1)->PC', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)#.partition([10, 10], [partition, partition])
        #    SynapseGroup(net=SORN, src=PC, dst=last_SOM, tag='GABA,PC(+1)->SOM', connectivity='(s_id!=d_id)*(np.abs(sx-dx)<=10)*(np.abs(sy-dy)<=10)', partition=True)#.partition([5, 5], [2, 2])

        last_PC = PC
        #last_MT_SOM = MT_SOM
        #last_BA_PV = BA_PV
        #last_CH_PV = CH_PV
        #last_EXP_NOX_CELL = EXP_NOX_CELL

        if __name__ == '__main__':
            PC.color = get_color(0, timescale)
            MT_SOM.color = get_color(1, timescale)
            BA_PV.color = get_color(2, timescale)
            CH_PV.color = get_color(3, timescale)
            EXP_NOX_CELL.color = get_color(4, timescale)
            #EXP_NOX_CELL.display_min_max_act = (0, 0.3)

    SORN.set_marked_variables(attrs['ind'], info=print_info, storage_manager=sm)
    SORN.initialize(info=False)

    ###################################################################################################################

    if __name__ == '__main__':
        Network_UI(SORN, label='SORN UI PC PV SOM', storage_manager=sm, group_display_count=5).show()#'GLU', 'GABA_Dendrite', 'GABA_Soma', 'GABA_AIS'

    score = 0
    score += train_and_generate_text(SORN, 15000, 5000, 2000, display=print_info, stdp_off=True, same_timestep_without_feedback_loop=False, steps_recovery=0, storage_manager=sm)#, steps_recovery=15000
    #score += get_oscillation_score_hierarchical(SORN, 0, 5000)
    return score

if __name__ == '__main__':
    ind = []#
    #['density', 'density', 'density', 'density', 'strength', 'factor', 'eta_stdp', 'h_ip', 'h_ip', 'eta_ip', 'integration_length', 'h_sc', 'h_sc', 'eta_sc']
    #ind = [39.554, 16.13, 26.068, 20.96, 0.1158, 0.5067, 0.000112073, 0.05369, 0.17177, 0.00030581, 10.836, 0.00533, 0.4372, 0.0491]
    #ind = [50.0,   30.0,  30.0,   30.0,  0.1383, 0.5,    0.0015,      0.04,    0.2944,  0.0006,     15.0,   0.015,   0.2944, 0.1]

    #ind = [43.79804446004616, 19.467895828002142, 20.723331106881577, 14.58778050582485, 0.18989074665316877, 0.424770865064861, 0.00020765235989644087, 0.051324555253239916, 0.33960912587182096, 0.00044854320463179613, 11.797617914320949, 0.01316824405689011, 0.2854104398700873, 0.10946615640551477]

    #ind = [38.8625546443657, 21.9937736664673, 20.151121013660898, 20.649607697943942, 0.16493763706374245,
    #       0.4352654609703594, 0.00019646851918354565, 0.04808047509159995, 0.3118889016370322, 0.000492490484253376,
    #       12.684584332998586, 0.014001483936687523, 0.2861150519948995, 0.0919936755950066]

    #ind=[38.8625546443657, 21.9937736664673, 20.151121013660898, 20.649607697943942, 0.16493763706374245, 0.4352654609703594, 0.00019646851918354565, 0.04808047509159995, 0.3118889016370322, 0.000492490484253376, 12.684584332998586, 0.014001483936687523, 0.2861150519948995, 0.0919936755950066]
    #original
    #ind = [0.89, 0.80222, 0.1383, 0.1698, 0.11045, 0.0001, 0.04, 0.2944, 0.0006, 0.3, 0.01, 0.2944, 0.1, 0.0001, 0.87038,0.82099, 1.5, 0.08, 30.0]
    #bv:
    #ind = [4.24289026824522, 0.1772551762687538, 0.10334918756466115, 0.2689743758706922, 0.041718700386009305, 0.00014380428405254888, 0.044381807703706956, 0.19567408560566968, 0.0010460542504209989, 0.11012200304339823, 0.01588825464021605, 0.22199256517434313, 0.015329201503661292, 5.4803392906312225e-05, 0.5059785852681881, 0.5495712393492611, 1.9563902980182912, 0.040728651397532685, 14.814732459232534]
    #xps:
    #ind = [0.6828200083021586, 0.6050826299550228, 0.27340764947165486, 0.11895670182349916, 0.09240731578767125, 0.00016169410156046727, 0.03073392425413874, 0.3144793476060314, 0.0002815704596128816, 0.22574975043865556, 0.013842493647697771, 0.37396533444265084, 0.11193287910054223, 9.52953796589554e-05, 1.1186328285166929, 0.6188618067727688, 1.4402062021072555, 0.08858786066982591, 22.846206788079957]

    #for i in range(10):
    #    print('score', run(tag='1600_two_layer_1l_exc_act_0015_inpd', ind=ind, par={'N_e': 1600, 'TS': [1,2]}))

    #for i in range(15):
    #    print('score', run(tag='old_STDP_nox_same_05_900_01_04_20', ind=ind, par={'N_e': 900, 'TS': [1]}))

    print('score', run(attrs={'name':'test', 'ind':ind, 'N_e':900, 'TS':[1]}))

    # 23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=0, gap_percent=10, clip_min=None),
    # 24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=0, gap_percent=0, clip_min=None),

    #while True:
    #    for N_e in [300, 600, 900, 1200, 1500, 1800, 2100]:

    #import Exploration.Evolution.Distributed_Evolution as DistEvo
    #tag, ind = DistEvo.parse_sys(ind=ind)
    #score = run(tag, ind)
    #DistEvo.save_score(score, tag, ind)
