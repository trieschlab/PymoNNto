import sys
sys.path.append("..")

from SORNSim import *

from SORNSim.NetworkBehaviour.Logic.SORN.SORN_experimental import *
from SORNSim.NetworkBehaviour.Logic.SORN.SORN_WTA import *
from SORNSim.NetworkBehaviour.Input.Text.TextActivator import *

#from Testing.Common.Grammar_Helper import *

if __name__ == '__main__':
    from SORNSim.Exploration.Network_UI import *
    from Exploration.Network_UI.MyDefaultTabs import *
#    from SORNSim.Exploration.Network_UI.Network_UI import *
#    from SORNSim.Exploration.Network_UI.DefaultTabs import *




def run(attrs={'name': 'KWTA', 'ind': [], 'N_e': 900, 'plastic': 15000}):
    so = True

    print_info = attrs.get('print', True)

    if print_info:
        print(attrs)

    sm = StorageManager(attrs['name'], random_nr=True, print_msg=print_info)
    sm.save_param_dict(attrs)


    #source = NewGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015, frequency_adjustment=True)
    #source = FewSentencesContextGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015, frequency_adjustment=True)#
    source = FewSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015, frequency_adjustment=True)#21
    #source = FewLongSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015, frequency_adjustment=True)

    #txt='guin eats fish. parrot eats mets. pex eits box ests bea esfish. perrod eats mets. penguin eat. fish. pareod eats mets. bex ests brrod eats mets. box eats brx ests bryod eats mets. pey uin eats fish. parrot eats metd. penguin eats fish. parrot eats mets. pey uin eats fish. pareot eats muts. penguin eats fish. perrot eats mets. pey uingeany fiseanf fnx . ts buin eat. fish. parrot eats mets. bey eats brxod eats bets. beyguin eatf fish. parrot eats bets. penguin eats fish. parrot eats metd. box e ts brx ests bea . fox ests brx edts bgxin eatbefish. perrot eats mets. peyguin eats fish. parrot eats muts. beyguin eats fish. parrotneats mets. feyguin eats fish. parrot eats muts. beyguin eats fish. parrot eats mets. bay uingeanf ftshf sh. per ot  ats mets. box eins boe e ts box eats brxddy fnseingoin eath. fah. d  buinueats fish. parrot eats mets. pay uin uats fish. parrot eats mets. perguinguat eais . pen uin eats fish. perrot eats mets. boyguinsuin eat. boe d  box euin eat  fish. panrod eats metd. beyguins bnx eats brx t d. soxead. fox eats brx ests bradd eats mets. poy uin eatg fish. parrot eats mets. pey uin eats fish. parrot eats mets. pey uin eaes fish. parrot eats mets. ponguin eats fish. perrodneats meas. box eats brx d.ts mguin eats fish. paneod eats meas. payguin aat  fish. pareot eats mets. peyguin eats fish. panguineuat bfish. parrod eats mets. pox eits brx eats brx eats brx eats brx eats box eats brx eats bead. ponguineeats fish. pareot eats mets. pexguin eats fish. parrot eats mets. pedguin eats fish. porrot eats mets. box eits box eats bex d forrot eats muts. bey uin uins atsh. fh. od eatn eath.ffeh. parrot eats mets. box uin uing atshf sh. pargod eats mets. pan uin eats fish. perrod eats mets. box eats boa eats fguin eats fish. parrot eats mets. poyguin eats fish. porrot eats mets. box eits bre eats brx eats breot eats bet . box ein uins atsh. fh. pdnguin eat  fish. parrot eats meas. box eats breot eats mets. fesh. par ot eats metd. box eiss besufish. parrot eats mets. payguin  ans fish. parrot eats mets. poyguin eats fish. parrot eats mets. box eats brx eats brx eats breod eats meat. box dats brx eatsnfiin eat. fo h. pod.uin eats fish. parrot eats mets. penguin eats fish. perrot eats mets. penguin eats fish. porrot eats bets. penguin eats fish. parrot eats mets. parguin eats fish. parrot eats metd. box eats bea eatsnbuing ats fish. parrot eats mead. bon eits bead. box ein eats fish. pareot eats mets. peyguin eats fish. parrot eats bets. bey eass brx eats breod eats mets. poyguin aats fish. porrot eats mets. penguin eats fish. parroineeats fish. par ot eafs mets. box eats brx eats bre eats bgxin eats fish. parrot eats buts. panguin eats fish. poneoi. eat. box eats bre e. box eans ats fish. forrot eats mets. box eits brx eats breot  ats metd. box eats braot eats mets. perguin eats fish. parrot eats mets. poy ein eats fish. parrot eats mets. penguin eats fish. parrot eats mett. ead. box eats breod eats meas. box eats brx eats bread eats eats fish. perrot eats mead. box eats braod eats mets. poyguin eats fish. parrot eats beat. fox . ts fuin eats fish. parrot eats mets. penguin eats fish. barrot eats meas. box eats bread. fongod eaas mfish. parrot eats mets. pex eins mea . sa. uin eats fish. borroineeats fish. parrot eats mets. pey eits mea f bhn uinruin eats fish. parrot eats muts. peyguin eats fish. barrot eats mead. box eats brx eats brx eats brx eats breaeats me. . nguin eats fish. parrot eats mets. pey efn  inuinneats fish. panguin eats fish. perrot eats mets. penguin eats fish. parrod. fox eats bre eats bre eats mets. penguin eats fish. perrot eats mea . box eats bre eats uin eats fish. parrot eats meas. feygu n eats fish. parrod eats mets. poy uins brx eats box eats bre eats  ead. forrod eats muts. penguin eats fish. penrod. fat. fox eats brx d. eat. box eats bradd. bad  eat. fash. ngnguin eats fish. parrot eats mets. poy uins aeatfibo. eats bets. perguin uinseatshfish. p rrot eats mets. penguin eats fish. parrot eats mets. penguin eats fish. barrot eats mets. penguin eats fish. parrot eats mets. penguin eats fish. box eanh ata f fo. pansod eats mets. poyguin umea fish. parrot eats mets. payguineaa.  on uinseats fish. por ea e me seape buineats braad. erxutn. pe meas. penguin eats fish. parrot eats mets. box eats bre eats breod eats mead. por eats bre eats bre eats nuti. pat.ufng . p eguinfeat. fish. porrot eats mets. poy eats bea eats brx d eats aets. panguin eats fish. parrot eats mets. poy eats bread. box eats brx eats beat.  fog. ats uin eats fish. parrot eats mets. poy uan eins atsh. fh. od eats mets. box eits breod eats mets. pey ean aats fish. parrot eats mets. poy uin eats fish. parrot eats mets. box eats brx eatsnfeat  fish. parrot eats mets. pey eanseats fish. parrot eats bets. box eats braod eats meat. foxh. borgoineeas  uts. pox eins mea . panguin eats fish. parrot eats bets. boy eins ang ats fiah. b reoi. eats fish. parrot eats mets. peyguin eats fish. parrot eats mets. poy ed eats m'
    #html = source.mark_with_grammar(txt)
    #show_html(html)


    #source = SingleWordGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source = FewLongSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source.plot_char_frequency_histogram(20)

    SORN = Network()

    e_ng = NeuronGroup(net=SORN, tag='PC_{},prediction_source'.format(1), size=get_squared_dim(attrs['N_e']), behaviour={
                2: SORN_init_neuron_vars(timescale=1),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='90%', distribution='uniform(0.1,1.0)', normalize=True),#20%#lognormal(0,[0.95#1]) #[13#0]% #, partition_compensation=True , partition_compensation=True #lognormal(0,0.95)
                #4: SORN_init_afferent_synapses(transmitter='GABA', density='[30#1]%', distribution='uniform(0.0,1.0)', normalize=True),
                5: SORN_init_afferent_synapses(transmitter='GLU_cluster', density='90%', distribution='uniform(0.1,1.0)', normalize=True),

                10.0: SORN_slow_syn_simple(transmitter='GLU', strength='1.0', so=so), #todo: SORN_slow_syn_simple??????
                10.1: SORN_IP_WTA_apply(),
                10.15: WTA_refrac_apply(strengthfactor='[0.1#0]'),#0.1 #attrs['refrac']
                10.2: SORN_generate_output_K_WTA_partitioned(partition_size=7, K='[0.02#1]'),

                10.3: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                10.4: SORN_generate_output_K_WTA_partitioned(partition_size=7, K='[0.02#1]', filter_temporal_output=False),

                10.5: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                10.6: SORN_generate_output_K_WTA_partitioned(partition_size=7, K='[0.02#1]', filter_temporal_output=False),

                10.7: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                10.8: SORN_generate_output_K_WTA_partitioned(partition_size=7, K='[0.02#1]', filter_temporal_output=False),

                # 12.1: SORN_WTA_iSTDP(eta_iSTDP='[0.00015#2]'),
                # 12.2: SORN_SN(syn_type='GABA'),
                #13.4: SORN_generate_output_K_WTA_partitioned(K='[0.12#4]'),
                #13.5: SORN_WTA_fast_syn(transmitter='GABA', strength='-[0.5#5]', so=so),#[0.1383#2]SORN_fast_syn
                #14: WTA_refrac(),
                #, filter_temporal_output=True

                15: SORN_buffer_variables(random_temporal_output_shift=False),

                18: WTA_refrac(decayfactor=0.5),
                20: SORN_IP_WTA(h_ip='lognormal_real_mean([0.02#1], [0.2944#2])', eta_ip='[0.007#3]', target_clip_min=None, target_clip_max=None), #-1.0 #1.0 #0.007
                21.1: SORN_STDP(transmitter='GLU', eta_stdp='[0.00015#4]', STDP_F={-1: 0.2, 1: -1}),#, 0: 1 #[0.00015#7] #0.5, 0: 3.0
                21.2: SORN_STDP(transmitter='GLU_cluster', eta_stdp='[0.00015#5]', STDP_F={0: 2.0}),  #[0.00015#7]
                22: SORN_SN(syn_type='GLU', behaviour_norm_factor=1.0),
                23: SORN_SN(syn_type='GLU_cluster', behaviour_norm_factor='[0.3#6]')#0.1
            })


    # SynapseGroup(net=SORN, src=retina, dst=e_ng, tag='GLU,GLU_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

    receptive_field = 18
    #receptive_field = int(18*math.sqrt(attrs['N_e']/1400))
    print(receptive_field)

    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,syn', connectivity='(s_id!=d_id)*in_box({})'.format(receptive_field))#, partition=True)#14
    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU_cluster,syn', connectivity='(s_id!=d_id)*in_box({})'.format(receptive_field))#, partition=True)
    #SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GABA,GABA_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

    e_ng.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))

    if __name__ == '__main__' and attrs.get('UI', False):
        e_ng.color = get_color(0, 1)

    SORN.set_marked_variables(attrs['ind'], info=print_info, storage_manager=sm)
    SORN.initialize(info=False)

    #print(e_ng['GLU'])
    #print(SORN.SynapseGroups)

    ###################################################################################################################

    if __name__ == '__main__' and attrs.get('UI', False):
        my_modules = get_default_UI_modules()+get_my_default_UI_modules()
        my_modules[1] = multi_group_plot_tab(['output', 'exhaustion_value', 'weight_norm_factor'])  # , 'nox', 'refractory_counter'
        my_modules[18] = single_group_plot_tab({'activity': (0, 0, 0), 'excitation': (0, 0, 255), 'inhibition': (255, 0, 0), 'input_act': (255, 0, 255),'exhaustion_value': (0, 255, 0)})
        Network_UI(SORN, modules=my_modules, label='SORN UI K_WTA', storage_manager=sm, group_display_count=1, reduced_layout=False).show()

    score = 0
    plastic_steps = attrs.get('plastic', 20000)

    #for i in range(1):
    #    #sm = StorageManager(attrs['name'] + '[{:03d}]'.format(i + 1), random_nr=True, print_msg=print_info)
    #    #sm.save_param_dict(attrs)
    #    sm=None
    #    score += train_and_generate_text(SORN, plastic_steps, 5000, 1000, display=print_info, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=1000, storage_manager=sm, return_key='right_sentences_square_score')

    score = 0

    #print(train_and_generate_text(SORN, plastic_steps, 5000, 1000, display=print_info, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=5000, storage_manager=sm, return_key='right_sentences_square_score'))
    #print('Output:')
    #print(predict_text_max_source_act(SORN, plastic_steps, 5000, 5000, display=True, stdp_off=True))#plastic_steps, 5000, 1000

    #print('score=', score)

    return get_max_text_score(SORN, plastic_steps, 5000, 5000, display=True, stdp_off=True, return_key='right_word_square_score')


if __name__ == '__main__':
    #ind = [0.1024607932656874, 0.017593238652155188, 0.3082856525780059, 0.007677918919646546, 0.00015438098687883516, 0.0001579431193983243, 0.33978128099023547]
    ind = []

    print('score', run(attrs={'name': 'adsfdsfsdf', 'ind': ind, 'N_e': 1400, 'TS': [1], 'UI': True, 'plastic': 30000}))#30000 #50p log just exc 0.04






    #for refrac in [0.1, 0.5, 1.0]:
    #    print('score', run(attrs={'name': 'refrac_param{}'.format(refrac), 'ind': ind, 'N_e': 1400, 'TS': [1], 'UI': False, 'plastic': 30000, 'refrac': refrac}))


    #ind = []#[72.7255592339286, 29.458175070582683, 0.00015704485382051904, 0.006763629096129458, 0.11926664091843557, 0.5031562876644946, 0.035971677467027625, 0.00014754543834789394]#[]
    #ind = [91.28948124066251, 25.70311259727637, 0.00011958137352069863, 0.007103970516674569, 0.08764929945250621, 0.45626446218228583, 0.03506439143087593, 0.00012216591033475477]

    #[0.1, 0.02, 0.2944, 0.007, 0.00015, 0.00015, 0.3]
    # [0.020226353270632835, 0.9169259179752178, 1.1798519990521394, 0.94937075251603, 0.33040671196411336, 0.00664305122252098, 0.00012529660504072136, 0.0001550599521133631]

    #ind = [0.10942671202813736, 0.01969114446391008, 0.28822586745531886, 0.007612200554889048, 0.00015979023347970065, 0.00015715374718117852, 0.28771687148885944]

    #ind = [0.10584534961360437, 0.018824864124830556, 0.31792383056480966, 0.006868328437853531, 0.0001486108734181946, 0.00016336663822907974, 0.3097974393619824]#




# 17: SORN_IP_TI_WTA(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.006#6];+-50%', integration_length='[15#7];+-50%', clip_min=None),
# 17: SORN_IP_WTA(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.006#6]', clip_min=None),  # lognormal_real_mean([0.04#6], [0.2944#7]) #[0.0006#6];+-50% ;+-50%
#16: SORN_Neuron_Exhaustion(decay_factor='[0.9#3]', strength='[0.1#4]'),
#17: SORN_IP_TI_WTA(h_ip='[0.04#5]', eta_ip='[0.0006#6];+-50%', integration_length='[15#7];+-50%', clip_min=None),  # lognormal_real_mean([0.04#6], [0.2944#7])
#18: SORN_generate_output_K_WTA(K='[0.04#5]'),
#18: SORN_generate_output(init_TH='0.1;+-100%'),
#20: SORN_Refractory_Digital(factor='0.5;+-50%', threshold=0.1),
#20: SORN_Refractory_Analog(factor='0.5;+-50%'),