import sys
sys.path.append('../../')

display = False
tag = 'test'

def run(ind=[], thread_index=None):
    N_e = 900
    sm = StorageManager(tag, random_nr=thread_index, print_msg=display)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=N_e, random_blocks=True)

    e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(N_e),
                       behaviour={  # TRENNeuronDimension(width=30, height=30, depth=1)
                           1: NeuronActivator(write_to='input', pattern_groups=[source]),
                           2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.0;0.5'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density=100, distribution='lognormal(0,[0.8#8])', normalize=True),
                           4: SORN_init_afferent_synapses(transmitter='GABA', density=90, distribution='lognormal(0,[0.6#9])', normalize=True),

                           12: SORN_slow_syn(transmitter='GLU', strength='[0.63#0]', input_strength=1.0),
                           13: SORN_slow_syn(transmitter='GABA', strength='-[0.053#1]'),
                           ##16: SORN_intra_Gamma(transmitter='GLU', strength=1),
                           17: SORN_fast_syn(transmitter='GABA', strength='-[0.148#2]'),
                           20: SORN_input_collect(),

                           21: SORN_STDP(eta_stdp=0.04, prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None),
                           23: SORN_IP_TI(h_ip='l_norm_mean(0.03, [0.3#6])', eta_ip='0.001;+-50%', integration_length=9, gap_percent=0),  # TODO:0.04 0.005  #'0.06;+-[33#6]%'  [0.4#6] , clip_min=-0.001

                           24: SORN_diffuse_IP(h_dh='IPTI_h_ip', eta_dh='[0.001#7]', integration_length=1, gap_percent=10),#[0.1#7]

                           #25: SORN_iSTDP(h_ip='IPTI_h_ip', eta_istdp='0.0001'),

                           30: SORN_finish(),

                           100: TRENNeuronRecorder_eval(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='out_rec', max_length=1000),
                           101: TRENNeuronRecorder_eval(['n.pattern_index'], tag='inp_rec', max_length=1000)
                       })

    i_ng = NeuronGroup(tag='main_inh_group', size=get_squared_dim(int(0.2 * N_e)), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.082'),
        #3: SORN_init_afferent_synapses(transmitter='GLU', density=200, normalize=True),
        3: SORN_init_afferent_synapses(transmitter='GLU', density=450, distribution='lognormal(0,[0.6#10])', normalize=True),
        4: SORN_init_afferent_synapses(transmitter='GABA', density=40, distribution='lognormal(0,[0.8#11])', normalize=True),

        ##10: SORN_inter_Gamma(transmitter='GLU', strength=0.5, input_strength=1),
        11: SORN_slow_syn(transmitter='GABA', strength='-[0.001#3]'),
        14: SORN_fast_syn(transmitter='GLU', strength='[0.98#4]'),
        15: SORN_fast_syn(transmitter='GABA', strength='-[0.001#5]'),
        20: SORN_input_collect(),

        # 23: SORN_IP_TI(h_ip=0.04, eta_ip=0.005, integration_length=10, gap_percent=0),

        30: SORN_finish(),

        100: TRENNeuronRecorder_eval(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='out_rec', max_length=1000)
    })

    ee_syn = SynapseGroup(src=e_ng, dst=e_ng, connectivity='s_id!=d_id').add_tag('GLU')  # .add_tag('sparse')
    ie_syn = SynapseGroup(src=e_ng, dst=i_ng).add_tag('GLU')
    ei_syn = SynapseGroup(src=i_ng, dst=e_ng).add_tag('GABA')
    ii_syn = SynapseGroup(src=i_ng, dst=i_ng).add_tag('GABA')

    SORN_Global = Network([e_ng, i_ng], [ee_syn, ie_syn, ei_syn, ii_syn], initialize=False)

    SORN_Global.set_marked_variables(ind, info=(ind == []))
    SORN_Global.initialize(info=False)

    ####################################################
    ####################################################
    ####################################################

    print(get_evolution_score_words(SORN_Global, 'main_exc_group', 'out_rec', 'inp_rec', 5000, 2000, 2000, display=False))

    if thread_index is None:
        import Exploration.UI.Network_UI.Network_UI as SUI
        SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()


    #return get_evolution_score(SORN_Global, 5000, 3000, 0.2, e_ng, i_ng)#0.04
    return get_evolution_score_simple(SORN_Global, 5000, 4000, e_ng)

#ind = []
#ind = [0.5527127875577752, 0.04020901712213985, 0.12791981675797653, 0.0010099660654047625, 1.3087565011712985, 0.00137953057463504, 0.29265697193248, 0.0010576793743076345, 0.7588461190575841, 0.46991929277652644, 0.6479539971826234, 0.6917459314751938]
ind = [0.5588082981463739, 0.03810720001190248, 0.12146874750556602, 0.0010036198225645, 1.3501418629823916, 0.0013366155988339557, 0.2931147160912402, 0.0010275844953794905, 0.8093450035680635, 0.45799457377873565, 0.6801861426456063, 0.6725940225142736]

if __name__ == '__main__':
    if False:
        constraints = ['ind=np.clip(ind,0.001,None)']
        import Exploration.Evolution.Multithreaded_Evolution as Evo
        evolution = Evo.Multithreaded_Evolution(run, 32, thread_count=6, name="evo_simple_03", mutation=0.01, constraints=constraints)#0.05
        evolution.start([ind])
        # [0.5110424353387503, 0.03872423778139165, 0.11578232044182662, 0.001076839520800458, 1.1414563829081996, 0.001362577353310225, 0.302814681673642, 0.001063018854610935, 0.736743931898012, 0.4207765718078959, 0.6446226479571889, 0.7233048344617977]
        #[0.55, 0.04, 0.1149, 0.001139, 1.0, 0.001455, 0.3, 0.001, 0.736, 0.46168, 0.6052853, 0.746194]
        #evolution.continue_evo('Oscillation_evo_4922.txt')
    else:
        from Exploration.Evolution.Multithreaded_Evolution import *
        #[0.5110424353387503, 0.03872423778139165, 0.11578232044182662, 0.001076839520800458, 1.1414563829081996, 0.001362577353310225, 0.302814681673642, 0.001063018854610935, 0.736743931898012, 0.4207765718078959, 0.6446226479571889, 0.7233048344617977]
        #[0.55, 0.04, 0.1149, 0.001139, 1.0, 0.001455, 0.3, 0.001, 0.736, 0.46168, 0.6052853, 0.746194]
        run_multiple_times(run, -1, ind)















'''
            #[0.63, 0.053, 0.148, 0.001, 0.98, 0.001, 33.0, 0.00147, 0.8, 0.6, 0.6, 0.8]
        #evolution.start([[0.63, 0.053, 0.148, 0.001, 0.98, 0.001, 33.0, 0.00147, 0.8, 0.6, 0.6, 0.8]]) #[0.2, 0.2, 0.1, 30.0, 0.001, 30.0, 0.1, 1.2, 0.07]
        


                #ind=[0.09832983041253213, 0.2874567765364803, 0.170839193065773, 24.417996252470868, 0.0004722391171298246, 35.8125403737148, 0.15287089010831498, 1.1649878916717407, 0.09341651744072456]
        #ind=[0.18862899084667192, 0.23, 0.08, 27.884335370151334, 0.000569163502910996, 33.048366516603764, 0.08864024920977884, 1.3707954661269086, 0.07272552550636018]
        #[0.14567952470221007, 0.16914206624326053, 0.11247835215067827, 24.056172453931442, 0.00046049914847303374, 45.40697620667162, 0.15397702231647606, 1.4150837126257394, 0.08117645991991748]
        #ind=[0.6010343213539389, 0.05852350016620932, 0.1732677602783387, 0.001, 0.9832295232077173, 0.0010942685759959734, 27.120647531269814, 0.001616019194772113, 0.9526666843062752, 0.4841068231520772, 0.613898134768206, 0.7911986474263608]
        #ind=[0.6127500563975934, 0.03826681901135323, 0.1066143355314601, 0.0012136614660910262, 1.111525719959324, 0.0014383475279903855, 26.083595500637248, 0.001425181355772668, 0.7447956310982485, 0.45205189110989497, 0.6380705170677274, 0.8363033930828271]
        

        constraints = ['ind[0] = max(ind[0], 0.001)',
                       'ind[1] = max(ind[1], 0.001)',
                       'ind[2] = max(ind[2], 0.001)',
                       'ind[3] = max(ind[3], 0.001)',
                       'ind[4] = max(ind[4], 0.0001)',
                       'ind[5] = max(ind[5], 0.0001)',
                       'ind[6] = max(ind[6], 0.0001)',
                       'ind[7] = max(ind[7], 0.001)',
                       'ind[8] = max(ind[8], 0.001)',
                       'ind[9] = max(ind[9], 0.001)',
                       'ind[10] = max(ind[10], 0.001)',
                       'ind[11] = max(ind[11], 0.001)']

'''