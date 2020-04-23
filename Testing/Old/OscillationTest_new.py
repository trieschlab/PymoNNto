display = False
tag = 'test'

def run(ind=[], thread_index=None):
    N_e = 900
    sm = StorageManager(tag, random_nr=thread_index, print_msg=display)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=N_e, random_blocks=True)

    e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(N_e),
                       behaviour={  # TRENNeuronDimension(width=30, height=30, depth=1)
                           1: NeuronActivator(write_to='input', pattern_groups=[source]),
                           2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.0;0.2'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density=100, distribution='lognormal(0,0.8)', normalize=True),
                           4: SORN_init_afferent_synapses(transmitter='GABA', density=90, distribution='lognormal(0,0.8)', normalize=True),

                           12: SORN_slow_syn(transmitter='GLU', strength='[0.2#0]', input_strength=1.0),
                           13: SORN_slow_syn(transmitter='GABA', strength='-[0.2#1]'),
                           ##16: SORN_intra_Gamma(transmitter='GLU', strength=1),
                           17: SORN_fast_syn(transmitter='GABA', strength='-[0.1#2]'),
                           20: SORN_input_collect(),

                           21: SORN_STDP(eta_stdp=0.001, prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None),
                           23: SORN_IP_TI(h_ip='0.05;+-[30#3]%', eta_ip='[0.001#4];+-[30#5]%', integration_length='7', gap_percent=10, clip_min=-0.001),  # TODO:0.04 0.005

                           # 24: SORN_iSTDP(eta_istdp='0.0001', h_ip='IPTI_h_ip'),

                           30: SORN_finish(),

                           100: TRENNeuronRecorder_eval(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='out_rec', max_length=1000),
                           101: TRENNeuronRecorder_eval(['n.pattern_index'], tag='inp_rec', max_length=1000)
                       })

    i_ng = NeuronGroup(tag='main_inh_group', size=get_squared_dim(int(0.2 * N_e)), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.1'),
        3: SORN_init_afferent_synapses(transmitter='GLU', density=450, distribution='lognormal(0,0.8)', normalize=True),
        4: SORN_init_afferent_synapses(transmitter='GABA', density=40, distribution='lognormal(0,0.8)', normalize=True),

        ##10: SORN_inter_Gamma(transmitter='GLU', strength=0.5, input_strength=1),
        11: SORN_slow_syn(transmitter='GABA', strength='-[0.1#6]'),
        14: SORN_fast_syn(transmitter='GLU', strength='[1.2#7]'),
        15: SORN_fast_syn(transmitter='GABA', strength='-[0.07#8]'),
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

    #simulate_train_test_and_evaluate(SORN_Global, 'main_exc_group', 'out_rec', 'inp_rec', sm, 10000, 10000, 1000, display=True)

    import Exploration.UI.Network_UI.Network_UI as SUI
    SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    return get_evolution_score(SORN_Global, 5000, 2000, None, e_ng, i_ng)#0.04



if __name__ == '__main__':
    if False:
        constraints =['ind[0] = max(ind[0], 0.001)',
                       'ind[1] = max(ind[1], 0.001)',
                       'ind[2] = max(ind[2], 0.001)',
                       'ind[3] = max(ind[3], 0)', 'ind[3] = min(ind[3], 50)',
                       'ind[4] = max(ind[4], 0.0001)',
                       'ind[5] = max(ind[5], 0)', 'ind[5] = min(ind[5], 50)',
                       'ind[6] = max(ind[6], 0.001)',
                       'ind[7] = max(ind[7], 0.001)',
                       'ind[8] = max(ind[8], 0.001)']

        import Exploration.Evolution.Multithreaded_Evolution as Evo
        evolution = Evo.Multithreaded_Evolution(run, 32, thread_count=6, name="Oscillation_evo", mutation=0.05, constraints=constraints)#0.05

        evolution.start([[0.2, 0.2, 0.1, 30.0, 0.001, 30.0, 0.1, 1.2, 0.07]])
        #evolution.continue_evo('Oscillation_evo_1006_2.txt')
    else:
        from Exploration.Evolution.Multithreaded_Evolution import *
        #ind=[0.09832983041253213, 0.2874567765364803, 0.170839193065773, 24.417996252470868, 0.0004722391171298246, 35.8125403737148, 0.15287089010831498, 1.1649878916717407, 0.09341651744072456]
        #ind=[0.18862899084667192, 0.23, 0.08, 27.884335370151334, 0.000569163502910996, 33.048366516603764, 0.08864024920977884, 1.3707954661269086, 0.07272552550636018]
        ind=[0.14567952470221007, 0.16914206624326053, 0.11247835215067827, 24.056172453931442, 0.00046049914847303374, 45.40697620667162, 0.15397702231647606, 1.4150837126257394, 0.08117645991991748]
        run_multiple_times(run, -1, ind)
