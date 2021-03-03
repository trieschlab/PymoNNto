import sys
sys.path.append('../../')

display = False
tag = "test"
if len(sys.argv) > 1:
    tag = sys.argv[1]


def run(ind=[], thread_index=None):
    N_e = 900
    sm = StorageManager(tag, random_nr=thread_index, print_msg=display)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=N_e, random_blocks=True)

    e_ng = NeuronGroup(tag='main_exc_group', size=get_squared_dim(N_e),
                       behaviour={
                           1: NeuronActivator(write_to='input', pattern_groups=[source]),
                           2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.0;0.5'),
                           3: SORN_init_afferent_synapses(transmitter='GLU', density=100, distribution='lognormal(0,0.8)', normalize=True),
                           4: SORN_init_afferent_synapses(transmitter='GABA', density=90, distribution='lognormal(0,0.6)', normalize=True),

                           12: SORN_slow_syn(transmitter='GLU', strength='0.63', input_strength=1.0),
                           13: SORN_slow_syn(transmitter='GABA', strength='-0.053'),
                           17: SORN_fast_syn(transmitter='GABA', strength='-0.148'),
                           20: SORN_input_collect(),

                           21: SORN_STDP(eta_stdp='0.005', prune_stdp=False),
                           22: SORN_SN(syn_type='GLU', clip_max=None),
                           23: SORN_IP_TI(h_ip='0.07;+-33%', eta_ip='0.00147;+-95%', integration_length=9, gap_percent=10, clip_min=None),  # TODO:0.04 0.005  #'0.06;+-[33#6]%'  [0.4#6] , clip_min=-0.001


                           30: SORN_finish(),

                           100: TRENRecorder_eval(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='out_rec', max_length=1000),
                           101: TRENRecorder_eval(['n.pattern_index'], tag='inp_rec', max_length=1000)
                       })

    i_ng = NeuronGroup(tag='main_inh_group', size=get_squared_dim(int(0.2 * N_e)), behaviour={
        2: SORN_init_neuron_vars(iteration_lag=1, init_TH='0.082'),

        3: SORN_init_afferent_synapses(transmitter='GLU', density=450, distribution='lognormal(0,0.6)', normalize=True),
        4: SORN_init_afferent_synapses(transmitter='GABA', density=40, distribution='lognormal(0,0.8)', normalize=True),

        11: SORN_slow_syn(transmitter='GABA', strength='-0.001'),
        14: SORN_fast_syn(transmitter='GLU', strength='0.98'),
        15: SORN_fast_syn(transmitter='GABA', strength='-0.001'),
        20: SORN_input_collect(),

        30: SORN_finish(),

        100: TRENRecorder_eval(['np.mean(n.output)', 'np.mean(n.TH)', 'n.output', 'n.TH', 'n.excitation', 'n.inhibition', 'n.input_act'], tag='out_rec', max_length=1000)
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

    if thread_index is None:
        import Exploration.Network_UI.Network_UI as SUI
        SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    #return get_evolution_score_words(SORN_Global, 'main_exc_group', 'out_rec', 'inp_rec', 5000, 3000, 2000, display=False, stdp_off=True)
    #return get_evolution_score(SORN_Global, 5000, 3000, 0.2, e_ng, i_ng)#0.04
    #return get_evolution_score_simple(SORN_Global, 5000, 4000, e_ng)


ind = []

if __name__ == '__main__':
    if False:
        constraints = ['ind=np.clip(ind,0.001,None)']
        import Exploration.Evolution.Multithreaded_Evolution as Evo
        evolution = Evo.Multithreaded_Evolution(run, 32, thread_count=6, name=tag, mutation=0.01, constraints=constraints)#0.05
        evolution.start([ind])
    else:
        from Exploration.Evolution.Multithreaded_Evolution import *
        run_multiple_times(run, -1, ind)


