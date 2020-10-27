from SORNSim.NetworkBehaviour.Input.Old.CountingTaskActivator import *
from Testing.Old.SORN_simple_behaviour import *
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Neuron_Group import *
from SORNSim.NetworkCore.Synapse_Group import *

from SORNSim.Exploration.StorageManager.StorageManager import *
from Testing.Common.Classifier_Helper import *


if True:
    Tag = 'CountingTest'

    N_e = 200
    syn = 10

    sm = StorageManager(Tag + '_{}_{}'.format(syn, int(np.random.rand() * 10000)))

    source = CountingActivator(N_e=N_e, N_u=10)

    SORN_layers_e = []
    SORN_layers_i = []
    ee_syns = []
    ie_syns = []
    ei_syns = []

    ee_forward_syns = []
    ee_backward_syns = []

    layers = 1
    for i in range(layers):

        SORN_layers_e.append(NeuronGroup(size=N_e, behaviour={
            1: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=syn, iteration_lag=i + 1, fixed_synapse_count=False),
            2: SORN_STDP(eta_stdp=0.001, prune_stdp=True),  # 0.005 False other exp
            3: SORN_SN(syn_type='GLU'), 6: SORN_IP(h_ip=0.1, eta_ip=0.001), 8: SORN_finish(),
            9: NeuronRecorder(['np.sum(n.x)', 'n.x'])}))

        if i == 0:
            SORN_layers_e[-1].add_behaviour(0, NeuronActivator(write_to='input', pattern_groups=[source]))
            SORN_layers_e[-1].add_behaviour(11, NeuronRecorder(['n.input', 'n.pattern_index']))

        SORN_layers_i.append(NeuronGroup(size=int(0.2 * N_e),
                                         behaviour={10: SORN_Input_collect(T_min=0.0, T_max=0.5), 11: SORN_finish()}))

        ee_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_e[-1], connectivity='s_id!=d_id').add_tag(
            'GLU').add_tag('sparse'))
        ie_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_i[-1]).add_tag('GLU'))
        ei_syns.append(SynapseGroup(src=SORN_layers_i[-1], dst=SORN_layers_e[-1]).add_tag('GABA'))

        if i > 0:  # connect to previous subsorn
            ee_forward_syns.append(
                SynapseGroup(src=SORN_layers_e[-2], dst=SORN_layers_e[-1]).add_tag('GLU').add_tag('sparse'))
            ee_backward_syns.append(
                SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_e[-2]).add_tag('GLU').add_tag('sparse'))

    SORN_Global = Network(SORN_layers_e + SORN_layers_i,
                          ee_syns + ie_syns + ei_syns + ee_forward_syns + ee_backward_syns)

    # SORN_1_e = NeuronGroup(size=200, behaviour={
    #    0: TRENNeuronActivator(write_to='input', pattern_groups=[source]),
    #    1: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=10),
    #    2: SORN_STDP(eta_stdp=0.001, prune_stdp=True),
    #    3: SORN_SN(syn_type='GLU'),
    #    #4: SORN_iSTDP(eta_istdp=0.001, h_ip=0.1),
    #    #5: SORN_SN(syn_type='GABA'),
    #    6: SORN_IP(h_ip=0.1, eta_ip=0.001),
    #    #7: SORN_SP(sp_prob=0.1, sp_init=0.001, syn_type='GLU'),
    #    8: SORN_finish(),
    #    9: TRENNeuronRecorder_eval(['np.sum(n.x)', 'n.x', 'n.input', 'n.pattern_index'])
    # })

    # SORN_1_i = NeuronGroup(size=int(0.2 * 200), behaviour={
    #    10: SORN_Input_collect(T_min=0.0, T_max=0.5),
    #    11: SORN_finish()
    # })

    # ee = SynapseGroup(src=SORN_1_e, dst=SORN_1_e, connectivity='s_id!=d_id').add_tag('GLU').add_tag('sparse')
    # ie = SynapseGroup(src=SORN_1_e, dst=SORN_1_i).add_tag('GLU')
    # ei = SynapseGroup(src=SORN_1_i, dst=SORN_1_e).add_tag('GABA')

    # SORN_Global = Network([SORN_1_e, SORN_1_i], [ee, ie, ei])

    # recorder = SORN_layers_e[0][TRENNeuronRecorder_eval]

    sm.save_np('ee_weights_init', np.array(ee_syns[0].W.toarray()))

    input_recorder = SORN_layers_e[0][11]  # first layer/ 11. behaviour
    readout_recorders = [n[9] for n in SORN_layers_e]

    steps_plastic = 50000  # sorn training time steps
    steps_readout = 5000  # readout train and test steps

    display = True

    # 1. input with plasticity
    if display: print('Plasticity phase:')
    SORN_Global.simulate_iterations(steps_plastic, 100, True)

    # 2. input without plasticity - train (STDP and IP off)
    if display: print('\nReadout training phase:')
    SORN_Global.learning_off()
    for n in SORN_layers_e: n[6].eta_ip = 0.0
    SORN_Global.simulate_iterations(steps_readout, 100, True)

    # 3. input without plasticity - test performance (STDP and IP off)
    if display: print('\nReadout testing phase:')
    SORN_Global.simulate_iterations(steps_readout, 100, True)

    # 4. calculate performance
    if display: print('\nCalculating performance... ', end='')

    X_train, y_train_ind = getXY(readout_recorders, 'n.x', [input_recorder], 'n.pattern_index', steps_plastic,
                                 steps_plastic + steps_readout)
    X_test, y_test_ind = getXY(readout_recorders, 'n.x', [input_recorder], 'n.pattern_index',
                               steps_plastic + steps_readout, steps_plastic + steps_readout + steps_readout)

    # Logistic Regression
    readout = linear_model.LogisticRegression(multi_class='multinomial', solver='lbfgs')
    output_weights = readout.fit(X_train, y_train_ind)
    performance = output_weights.score(X_test, y_test_ind)

    sm.save_param('N_e', N_e)
    sm.save_param('syn', syn)
    sm.save_param('performance', performance)
    sm.save_np('ee_weights', np.array(ee_syns[0].W.toarray()))



    print('Performance:', performance)
    if display: print('done')


