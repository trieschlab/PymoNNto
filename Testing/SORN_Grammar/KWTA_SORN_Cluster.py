import sys

sys.path.append('../../')

from NetworkCore.Network import *
from NetworkCore.Neuron_Group import *
from NetworkCore.Synapse_Group import *
from Testing.Common.Grammar_Helper import *
from NetworkBehaviour.Logic.SORN.SORN_experimental import *
from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *
from NetworkBehaviour.Logic.SORN.SORN_WTA import *
from NetworkBehaviour.Input.Text.TextActivator import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *


if __name__ == '__main__':
    from Exploration.UI.Network_UI.Network_UI import *



def run(attrs={'name': 'KWTA', 'ind': [], 'N_e': 900, 'plastic': 15000, 'refrac':0.1}):
    so = True

    print_info = attrs.get('print', True)

    if print_info:
        print(attrs)

    sm = None#StorageManager(attrs['name'], random_nr=True, print_msg=print_info)
    #sm.save_param_dict(attrs)

    #source = FewSentencesContextGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=21)#0.015
    source = FewSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=31)#0.015
    #source = SingleWordGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source = FewLongSentencesGrammar(tag='grammar_act', output_size=attrs['N_e'], random_blocks=True, input_density=0.015)
    #source.plot_char_frequency_histogram(20)

    SORN = Network()

    e_ng = NeuronGroup(net=SORN, tag='PC_{},prediction_source'.format(1), size=get_squared_dim(attrs['N_e']), behaviour={
                2: SORN_init_neuron_vars(timescale=1),
                3: SORN_init_afferent_synapses(transmitter='GLU', density='90%', distribution='uniform(0.1,1.0)', normalize=True),#20%#lognormal(0,[0.95#1]) #[13#0]% #, partition_compensation=True , partition_compensation=True #lognormal(0,0.95)
                #4: SORN_init_afferent_synapses(transmitter='GABA', density='[30#1]%', distribution='uniform(0.0,1.0)', normalize=True),
                5: SORN_init_afferent_synapses(transmitter='GLU_cluster', density='90%', distribution='uniform(0.1,1.0)', normalize=True),

                10.0: SORN_slow_syn(transmitter='GLU', strength='1.0', so=so),
                10.1: SORN_IP_WTA_apply(),
                10.15: WTA_refrac_apply(strengthfactor='[0.1#0]'),#0.1 #attrs['refrac']
                10.2: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]'),

                10.3: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                10.4: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]', filter_temporal_output=False),

                10.5: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                10.6: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]', filter_temporal_output=False),

                10.7: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                10.8: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]', filter_temporal_output=False),


                #11.3: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                #11.4: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]', filter_temporal_output=False),

                #11.5: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                #11.6: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]', filter_temporal_output=False),

                #11.7: SORN_slow_syn_simple(transmitter='GLU_cluster', strength='1.0'),
                #11.8: SORN_generate_output_K_WTA_partitioned(K='[0.02#1]', filter_temporal_output=False),


                # 12.1: SORN_WTA_iSTDP(eta_iSTDP='[0.00015#2]'),
                # 12.2: SORN_SN(syn_type='GABA'),
                #13.4: SORN_generate_output_K_WTA_partitioned(K='[0.12#4]'),
                #13.5: SORN_WTA_fast_syn(transmitter='GABA', strength='-[0.5#5]', so=so),#[0.1383#2]SORN_fast_syn
                #14: WTA_refrac(),
                #, filter_temporal_output=True

                15: SORN_buffer_variables(random_temporal_output_shift=False),

                18: WTA_refrac(),
                20: SORN_IP_WTA(h_ip='lognormal_real_mean([0.02#1], [0.2944#2])', eta_ip='[0.007#3]', clip_min=None),
                21.1: SORN_STDP(transmitter='GLU', eta_stdp='[0.00015#4]', STDP_F={-1: 1, 1: -1}),#, 0: 1 #[0.00015#7]
                21.2: SORN_STDP(transmitter='GLU_cluster', eta_stdp='[0.00015#5]', STDP_F={0: 0.5}),  #[0.00015#7]
                22: SORN_SN(syn_type='GLU', behaviour_norm_factor=1.0),
                23: SORN_SN(syn_type='GLU_cluster', behaviour_norm_factor='[0.3#6]')#0.1
            })

    # SynapseGroup(net=SORN, src=retina, dst=e_ng, tag='GLU,GLU_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,syn', connectivity='(s_id!=d_id)*in_box(20)', partition=True)
    SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU_cluster,syn', connectivity='(s_id!=d_id)*in_box(20)', partition=True)
    #SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GABA,GABA_same', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

    e_ng.add_behaviour(9, SORN_external_input(strength=1.0, pattern_groups=[source]))

    if __name__ == '__main__' and attrs.get('UI', False):
        e_ng.color = get_color(0, 1)

    SORN.set_marked_variables(attrs['ind'], info=print_info, storage_manager=sm)
    SORN.initialize(info=False)


    ###################################################################################################################

    if __name__ == '__main__' and attrs.get('UI', False):
        Network_UI(SORN, label='SORN UI K_WTA', storage_manager=sm, group_display_count=1, reduced_layout=False).show()

    score = 0
    plastic_steps = attrs.get('plastic', 20000)

    #for i in range(1):
    #    #sm = StorageManager(attrs['name'] + '[{:03d}]'.format(i + 1), random_nr=True, print_msg=print_info)
    #    #sm.save_param_dict(attrs)
    #    sm=None
    #    score += train_and_generate_text(SORN, plastic_steps, 5000, 1000, display=print_info, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=1000, storage_manager=sm, return_key='right_sentences_square_score')

    score = 0
    print(predict_text_max_source_act(SORN, plastic_steps, 5000, 1000, display=True, stdp_off=True))

    print('score=', score)

    return score


if __name__ == '__main__':
    #ind = []#[72.7255592339286, 29.458175070582683, 0.00015704485382051904, 0.006763629096129458, 0.11926664091843557, 0.5031562876644946, 0.035971677467027625, 0.00014754543834789394]#[]
    #ind = [91.28948124066251, 25.70311259727637, 0.00011958137352069863, 0.007103970516674569, 0.08764929945250621, 0.45626446218228583, 0.03506439143087593, 0.00012216591033475477]
    ind = []

    #[0.020226353270632835, 0.9169259179752178, 1.1798519990521394, 0.94937075251603, 0.33040671196411336, 0.00664305122252098, 0.00012529660504072136, 0.0001550599521133631]

    default_modules[1] = multi_group_plot_tab(['output', 'exhaustion_value', 'weight_norm_factor'])#, 'nox', 'refractory_counter'
    default_modules[18] = single_group_plot_tab({'activity': (0, 0, 0), 'excitation': (0, 0, 255), 'inhibition': (255, 0, 0), 'input_act': (255, 0, 255), 'exhaustion_value': (0, 255, 0)})

    print('score', run(attrs={'name': 'adsfdsfsdf', 'ind': ind, 'N_e': 800, 'TS': [1], 'UI': True, 'ff': True, 'fb': False, 'plastic': 30000}))#30000 #50p log just exc 0.04


    #for refrac in [0.1, 0.5, 1.0]:
    #    print('score', run(attrs={'name': 'refrac_param{}'.format(refrac), 'ind': ind, 'N_e': 1400, 'TS': [1], 'UI': False, 'plastic': 30000, 'refrac': refrac}))


# 17: SORN_IP_TI_WTA(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.006#6];+-50%', integration_length='[15#7];+-50%', clip_min=None),
# 17: SORN_IP_WTA(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.006#6]', clip_min=None),  # lognormal_real_mean([0.04#6], [0.2944#7]) #[0.0006#6];+-50% ;+-50%
#16: SORN_Neuron_Exhaustion(decay_factor='[0.9#3]', strength='[0.1#4]'),
#17: SORN_IP_TI_WTA(h_ip='[0.04#5]', eta_ip='[0.0006#6];+-50%', integration_length='[15#7];+-50%', clip_min=None),  # lognormal_real_mean([0.04#6], [0.2944#7])
#18: SORN_generate_output_K_WTA(K='[0.04#5]'),
#18: SORN_generate_output(init_TH='0.1;+-100%'),
#20: SORN_Refractory_Digital(factor='0.5;+-50%', threshold=0.1),
#20: SORN_Refractory_Analog(factor='0.5;+-50%'),