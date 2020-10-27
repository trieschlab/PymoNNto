import sys
sys.path.append('../../')

from SORNSim.NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *
from SORNSim.NetworkBehaviour.Input.Text.TextActivator import *
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from SORNSim.NetworkBehaviour.Structure.Structure import *
from SORNSim.Exploration.StorageManager.StorageManager import *
from Testing.Common.Grammar_Helper import *
if __name__ == '__main__':
    pass

def run(attrs={'name':'hierarchical', 'ind':[], 'N_e':900, 'TS':[1], 'ff':True, 'fb':True, 'plastic':15000}):

    so = True

    print_info = attrs.get('print', True)

    if print_info:
        print(attrs)

    #sm = None
    sm = StorageManager(attrs['name'], random_nr=True, print_msg=print_info)
    sm.save_param_dict(attrs)

    #grammar mode: what level17_short simple

    #source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=0.015)#15/par['N_e']#.plot_char_input_statistics()#output_size=par['N_e']#15
    #print(len(source.alphabet))
    #source = LongDelayGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, mode=['level17_short'], input_density=0.015)#.print_test()#.plot_char_input_statistics()#10/par['N_e']

    #source = SingleWordGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)

    source = FewSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)

    #print(source.print_test())

    #print([t for t in source.get_all_grammar_transitions() if len(t)==2])

    #source.plot_char_input_statistics()
    #print(len(source.alphabet))
    #img_source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=20, grid_height=20, center_x=list(range(20)), center_y=20 / 2, degree=90, line_length=60, select_mode='random')
    #print(source.get_text_score('. parrot likes trees. wolf wolf wolf..'))

    SORN = Network()




    #retina = NeuronGroup(net=SORN, tag='retina', size=get_squared_dim(20*20), behaviour={
    #        2: SORN_init_neuron_vars(timescale=1),

            #9: SORN_external_input(strength=1.0, pattern_groups=[img_source]),

            #18: SORN_generate_output(init_TH='0.1;+-100%'),
            #19: SORN_buffer_variables(random_temporal_output_shift=False),

            #20: SORN_Refractory_Analog(factor='0.5;+-50%'),
        #})


    for layer, timescale in enumerate(attrs['TS']):

        e_ng = NeuronGroup(net=SORN, tag='PC_{},prediction_source'.format(timescale), size=get_squared_dim(int(attrs['N_e']/timescale)), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution='lognormal(0,[0.95#0])', normalize=True, partition_compensation=True),#0.89 uniform(0.1,0.11)#13%
            4: SORN_init_afferent_synapses(transmitter='GABA', density='full', distribution='lognormal(0,[0.4#1])', normalize=True),#0.80222 uniform(0.1,0.11)#45%

            12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
            13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]', so=False),
            17: SORN_fast_syn(transmitter='GABA', strength='-[0.1#4]', so=False),#0.11045
            18: SORN_generate_output(init_TH='0.1;+-100%'),
            19: SORN_buffer_variables(random_temporal_output_shift=False),

            #20: SORN_Refractory_Digital(factor='0.5;+-50%', threshold=0.1),
            20: SORN_Refractory_Analog(factor='0.5;+-50%'),
            21: SORN_STDP(eta_stdp='[0.00015#5]'),#, STDP_F={-4:-0.01,-3:0.01,-2:0.1,-1:0.5,0:0.2,1:-0.3,2:-0.1,3:-0.05}, plot=True),#{-2:0.1,-1:0.5,0:0.2,1:-0.3,2:-0.1}
            22: SORN_SN(syn_type='GLU', clip_max=None, behaviour_norm_factor=1.0),
            #22.1: SORN_SN(syn_type='GLU_same', clip_max=None, behaviour_norm_factor=0.6),
            #22.2: SORN_SN(syn_type='GLU_ff', clip_max=None, behaviour_norm_factor=0.25),
            #22.3: SORN_SN(syn_type='GLU_fb', clip_max=None, behaviour_norm_factor=0.25),7z

            23: SORN_IP_TI(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0006#8];+-50%', integration_length='[15#19];+-50%', clip_min=None),#30          #, gap_percent=10 #30;+-50% #0.0003 #np.mean(n.output_new)
            25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.5#9];+-50%'),
            26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#10], [0.2944#11])', eta_sc='[0.1#12];+-50%', integration_length='1'),#60;+-50% #0.05
            27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]')
        })

        i_ng = NeuronGroup(net=SORN, tag='Inter_{}'.format(timescale), size=get_squared_dim(int(0.2 * attrs['N_e']/timescale)), behaviour={
            2: SORN_init_neuron_vars(timescale=timescale),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,[0.87038#14])', normalize=True),  # 450
            4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),
            14: SORN_fast_syn(transmitter='GLU', strength='[1.5#17]', so=so),#1.5353
            15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#18]', so=False),#0.08
            18: SORN_generate_output(init_TH='0.1;+-0%'),
            19: SORN_buffer_variables(),

            #20: SORN_Refractory_Digital(factor='0.2;0.7', threshold=0.1),
            20: SORN_Refractory_Analog(factor='0.2;0.7'),

            #23: SORN_IP_TI(h_ip='lognormal_real_mean([0.08#6], [0.2944#7])', eta_ip='[0.0003#8];+-50%', integration_length='30;+-50%', clip_min=None),
        })

        i_ng['structure', 0].stretch_to_equal_size(e_ng)

        #SynapseGroup(net=SORN, src=retina, dst=e_ng, tag='GLU,GLU_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,GLU_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)#.partition([10, 10], [partition, partition])
        SynapseGroup(net=SORN, src=e_ng, dst=i_ng, tag='GLU', connectivity='in_box(10)', partition=True)#.partition([5, 5], [2, 2])
        SynapseGroup(net=SORN, src=i_ng, dst=e_ng, tag='GABA', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=i_ng, dst=i_ng, tag='GABA', connectivity='(s_id!=d_id)*in_box(10)', partition=True)



        if layer > 0:
            if attrs.get('ff', True):#forward synapses
                SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GLU,GLU_ff', connectivity='in_box(10)', partition=True)#.partition([10, 10], [partition, partition])
                #SynapseGroup(net=SORN, src=last_e_ng, dst=i_ng, tag='GABA', connectivity='in_box(10)', partition=True)#.partition([5, 5], [2, 2])
            if attrs.get('fb', False):#backward synapses
                SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GLU,GLU_fb', connectivity='in_box(10)', partition=True)#.partition([10, 10], [partition, partition])
                #SynapseGroup(net=SORN, src=e_ng, dst=last_i_ng, tag='GABA', connectivity='in_box(10)', partition=True)#.partition([5, 5], [2, 2])
        #else:
            # i_ng.add_behaviour(10, SORN_external_input(strength=1.0, pattern_groups=[source]))
        e_ng.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))

        last_e_ng = e_ng
        last_i_ng = i_ng

        if __name__ == '__main__' and attrs.get('UI', False):
            e_ng.color = get_color(0, timescale)
            i_ng.color = get_color(1, timescale)

    SORN.set_marked_variables(attrs['ind'], info=print_info, storage_manager=sm)
    SORN.initialize(info=False)

    ###################################################################################################################

    if __name__ == '__main__' and attrs.get('UI', False):
        Network_UI(SORN, label='SORN UI default setup', storage_manager=sm, group_display_count=2, reduced_layout=False).show()


    score = 0
    plastic_steps = attrs.get('plastic', 20000)

    for i in range(1):
        sm = StorageManager(attrs['name']+'[{:03d}]'.format(i+1), random_nr=True, print_msg=print_info)
        sm.save_param_dict(attrs)
        score += train_and_generate_text(SORN, plastic_steps, 5000, 1000, display=print_info, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=1000, storage_manager=sm)#5000, 3000 stdp_off=True

    #score += get_oscillation_score_hierarchical(SORN, 0, 5000)
    #print(predict_text_max_source_act(SORN, plastic_steps, 1000, 2000))
    #t = max_source_act_text(SORN, 2000)
    #print(t)
    return score


if __name__ == '__main__':

    #2 sentence grammar evolution
    #ind = [0.8696216017907924, 0.4054197902251851, 0.15908648909538786, 0.16151455753719493, 0.048518733002033534, 0.0001606965068387588, 0.04879157151210372, 0.24231706635277966, 0.00045610819523760965, 0.5253225640567556, 0.014480162857178793, 0.3081697797506037, 0.09954804863544643, 0.00010776187534473455, 0.8077440101913735, 0.7062739421354904, 2.4503147431937236, 3.040822590617692, 0.08547161769469239, 13.841327314728604]

    ind = []

    #ind = [0.6334443274716619, 0.5126409437649502, 0.15323295507273996, 0.1536422743166059, 0.10145192004366528, 0.00010586670718153889, 0.06228336679249316, 0.13136325800133292, 0.00040769621210919477, 0.5587032097852763, 0.015396068196825782, 0.26054188484930113, 0.08805620775871699, 8.025634802479273e-05, 1.5190991698821859, 0.9715267930705385, 3.9306527645012963, 1.1325207903028636, 0.08462568912522882, 18.21187538753475]

    #ind = []#[0.7276299449002248, 0.4259178231528062, 0.15041716281772968, 0.1624206959069482, 0.06937462068832563, 0.00012695752101168995, 0.055994137138549144, 0.1918235229704838, 0.0004487823289472987, 0.5859998358127545, 0.017645682015941022, 0.2618788932523037, 0.09574998261033661, 9.321737242246134e-05, 1.391058540337006, 1.0651470792109632, 3.0598888951412344, 1.1323592889033676, 0.08271775348263943, 15.080243774578744]

    #ind = []#[0.9150239636600058, 0.41444993786908246, 0.13078958866926443, 0.13714627712547764, 0.10630224681081862, 0.00015355740938283497, 0.0572896064024363, 0.17205724061775884, 0.00039571392172929647, 0.36313382202600764, 0.014006216457593942, 0.2853897955370888, 0.09556820236444917, 0.0001020117958079417, 1.2850520374240129, 0.9521124386241633, 2.8949553979288645, 1.4680181329908213, 0.07774755473801938, 13.999695490935174]

    #[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.00015, 0.04, 0.2944, 0.0006, 0.5, 0.015, 0.2944, 0.1, 0.0001, 0.87038, 0.82099, 0.1838, 1.5, 0.08, 15.0]
    #ind = []#[1.0029784264710608, 0.3788290207843384, 0.14392445474986193, 0.15848563208139504, 0.06461119780424836, 0.00018985428872687166, 0.06128522529961923, 0.28899820609814947, 0.0004285986393883749, 0.5521514051940992, 0.013741663128167885, 0.2432926836065868, 0.07900654931425338, 9.909181196675775e-05, 1.2187088459330422, 0.8231455657918816, 1.8422191338448057, 2.5956604699313264, 0.0810127114275404, 15.11313163118768]

    #ind = [1.1385839161773175, 0.4073146769613646, 0.13587912708168629, 0.1965291172296534, 0.07661149836598065, 0.00020840216060054014, 0.07123856635243955, 0.2384422002962631, 0.0004180627654563409, 0.4077163066752066, 0.014568544114246046, 0.28286016600695146, 0.10256707760821504, 8.728311353819638e-05, 0.834274750010592, 0.5473748796671416, 1.9849892656147436, 0.07268689716650815, 17.333978531296722]

    #ind = [0.783046250138997, 0.43558491916386505, 0.27221561385258014, 0.16964231336668145, 0.07919219556785047, 0.00017165173047783107, 0.06491120339899444, 0.24323564948178908, 0.0004506839958001859, 0.603570600116428, 0.010327904873102926, 0.27765418598000813, 0.09265882959260471, 0.00012054062555343568, 0.7752008835575164, 0.8265310969678688, 1.7787116863931238, 0.09004420081400137, 22.43755849738225]

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

    #print('x', run(attrs={'name': 'x', 'ind': [], 'N_e': 900, 'TS': [1, 2, 3], 'UI': False, 'ff': True, 'fb': True, 'plastic': 30000}

    #for i in range(1):
    #    print('score', run(attrs={'name': 'full_[1,4]_1600_10ksteps', 'ind': ind, 'N_e': 1600, 'TS': [1,4], 'UI': False, 'ff': True, 'fb': True, 'plastic': 10000}))#1600#2200

    print('score', run(attrs={'name': 'abc', 'ind': ind, 'N_e': 1400, 'TS': [1], 'UI': True, 'ff':True, 'fb':True,'plastic':30000}))

    #print('simu')

    '''
    plastic = 45000
    for i in range(10):
        print('score', run(attrs={'name': '900_1', 'ind': ind, 'N_e': 900, 'TS': [1], 'UI': False, 'ff':False, 'fb':False,'plastic':plastic}))
        print('score', run(attrs={'name': '900,1,2', 'ind': ind, 'N_e': 900, 'TS': [1, 2], 'UI': False, 'ff':False, 'fb':False,'plastic':plastic}))
        print('score', run(attrs={'name': '900,1,2,3', 'ind': ind, 'N_e': 900, 'TS': [1, 2, 3], 'UI': False, 'ff':False, 'fb':False,'plastic':plastic}))
        print('score', run(attrs={'name': '900_1,1,1', 'ind': ind, 'N_e': 900, 'TS': [1, 1, 1], 'UI': False, 'ff': False, 'fb': False, 'plastic': plastic}))
        
        #print('score', run(attrs={'name': 'ff_900_1', 'ind': ind, 'N_e': 900, 'TS': [1], 'UI': False, 'ff': True, 'fb': False,'plastic':plastic}))
        print('score', run(attrs={'name': 'ff_900,1,2', 'ind': ind, 'N_e': 900, 'TS': [1, 2], 'UI': False, 'ff': True, 'fb': False,'plastic':plastic}))
        print('score', run(attrs={'name': 'ff_900,1,2,3', 'ind': ind, 'N_e': 900, 'TS': [1, 2, 3], 'UI': False, 'ff': True, 'fb': False,'plastic':plastic}))
        print('score', run(attrs={'name': 'ff_900_1,1,1', 'ind': ind, 'N_e': 900, 'TS': [1, 1, 1], 'UI': False, 'ff': True, 'fb': False, 'plastic': plastic}))
        
        #print('score', run(attrs={'name': 'ff_fb_900_1', 'ind': ind, 'N_e': 900, 'TS': [1], 'UI': False, 'ff': True, 'fb': True,'plastic':plastic}))
        print('score', run(attrs={'name': 'ff_fb_900,1,2', 'ind': ind, 'N_e': 900, 'TS': [1, 2], 'UI': False, 'ff': True, 'fb': True,'plastic':plastic}))
        print('score', run(attrs={'name': 'ff_fb_900,1,2,3', 'ind': ind, 'N_e': 900, 'TS': [1, 2, 3], 'UI': False, 'ff': True, 'fb': True, 'plastic': plastic}))
        print('score', run(attrs={'name': 'ff_fb_900_1,1,1', 'ind': ind, 'N_e': 900, 'TS': [1, 1, 1], 'UI': False, 'ff': True, 'fb': True, 'plastic': plastic}))
    '''

    # 23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=0, gap_percent=10, clip_min=None),
    # 24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=0, gap_percent=0, clip_min=None),

