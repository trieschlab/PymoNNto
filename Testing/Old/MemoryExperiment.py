import sys; sys.path.append('.')

from Exploration.StorageManager.StorageManager import *
from Testing.Common.Classifier_Helper import *
from Testing.Old.SORN_simple_behaviour import *
from NetworkCore.Network import *
from NetworkCore.Neuron_Group import *
from NetworkCore.Synapse_Group import *

display = True

while True:

    for A in [10, 20, 30, 40, 100, 200]:#[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,17,18,19,20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 64, 128]:#:#[1, 2, 4, 8, 10, 16, 32, 64, 128]:

        for network_size_iteration in [1, 2, 16]:  # [2, 6, 10, 14, 16, 20]:#[16]:#[6, 8, 10, 12, 14, 16, 18, 20]:#[6, 8, 10, 12, 14, 16, 18, 20]:#:#[16] #1600
            N_e = network_size_iteration * 100

            L = 1000000

            sm = StorageManager('Test')
            sm.save_param('L', L)
            sm.save_param('A', A)
            sm.save_param('N_e', N_e)

            source = Alphabet_Sequence_Activator(N_e=N_e, A=A, L=L)#FDTGrammarActivator(N_e=N_e)

            SORN_layers_e = []
            SORN_layers_i = []
            ee_syns = []
            ie_syns = []
            ei_syns = []

            ee_forward_syns = []
            ee_backward_syns = []
            ie_forward_syns = []
            ie_backward_syns = []

            layers = 1
            for i in range(layers):

                print(N_e)

                #todo: sigma
                SORN_layers_e.append(NeuronGroup(size=N_e, behaviour={
                    1: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=10, iteration_lag=i + 1,fixed_synapse_count=False),
                    2: SORN_STDP(eta_stdp=0.005, prune_stdp=False),
                    3: SORN_SN(syn_type='GLU'),
                    5: SORN_IP_New(h_ip=0.1, eta_ip=0.001),  # '0.1,+-10%'
                    #6: SORN_diffuse_IP(h_ip=0.1, eta_ip=0.001, init_avg=0.1),
                    8: SORN_finish(),
                    9: NeuronRecorder(['np.sum(n.x)', 'n.x'])
                }))

                if i == 0:
                    SORN_layers_e[-1].add_behaviour(0, NeuronActivator(write_to='input', pattern_groups=[source]))
                    input_recorders = [SORN_layers_e[-1].add_behaviour(11, NeuronRecorder(['n.input', 'n.pattern_index']))]

                #todo: istdp
                SORN_layers_i.append(NeuronGroup(size=int(0.2 * N_e), behaviour={
                    10: SORN_Input_collect(T_min=0.0, T_max=0.5),
                    11: SORN_finish()
                }))

                ee_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_e[-1], connectivity='s_id!=d_id').add_tag('GLU').add_tag('sparse'))
                ie_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_i[-1]).add_tag('GLU'))
                ei_syns.append(SynapseGroup(src=SORN_layers_i[-1], dst=SORN_layers_e[-1]).add_tag('GABA'))

                if i > 0:  # connect to previous subsorn
                    ee_forward_syns.append(SynapseGroup(src=SORN_layers_e[-2], dst=SORN_layers_e[-1]).add_tag('GLU').add_tag('sparse'))
                    ee_backward_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_e[-2]).add_tag('GLU').add_tag('sparse'))

                    ie_forward_syns.append(SynapseGroup(src=SORN_layers_e[-2], dst=SORN_layers_i[-1]).add_tag('GLU'))
                    ie_backward_syns.append(SynapseGroup(src=SORN_layers_e[-1], dst=SORN_layers_i[-2]).add_tag('GLU'))

            SORN_Global = Network(SORN_layers_e + SORN_layers_i, ee_syns + ie_syns + ei_syns + ee_forward_syns + ee_backward_syns + ie_forward_syns + ie_backward_syns)

            steps_plastic = 100000#2000000  # sorn training time steps #100000
            steps_readout_train = 3*5000#np.maximum(10000, 3*L)  # readout train and test steps#10000
            steps_readout_test = 5000

            #input_recorder = SORN_layers_e[0][11]  # first layer/ 11. behaviour
            readout_recorders = [n[9] for n in SORN_layers_e]

            sm.save_obj('source', source)
            sm.save_obj('net_init', SORN_Global)

            # Step 1. Input with plasticity
            if display: print('Plasticity phase:')
            SORN_Global.recording_off()
            SORN_Global.simulate_iterations(steps_plastic, 100, measure_block_time=display)
            SORN_Global.recording_on()

            # Step 2. Input without plasticity: train (with STDP and IP off)
            if display: print('\nReadout training phase:')

            #sorn.params.par.eta_stdp = 'off'
            #sorn.params.par.eta_ip = 'off'
            #sorn.params.par.eta_istdp = 'off'
            #sorn.params.par.sp_init = 'off'
            # turn off noise
            #sorn.params.par.sigma = 0

            SORN_Global.learning_off()
            SORN_Global.simulate_iterations(steps_readout_train, 100, measure_block_time=display)



            # Step 3. Train readout layer with logistic regression
            #if display: print('\nTraining readout layer...')
            #readout_layer = train(readout_recorders, 'n.x', [input_recorder], 'n.pattern_index', 0, steps_readout)  # steps_plastic, steps_plastic + steps_readout
            #SORN_Global.clear_recorder()

            # Step 4. Input without plasticity: test (with STDP and IP off)
            if display: print('\nReadout testing phase:')
            # sorn.simulation(stats, phase='test')
            SORN_Global.simulate_iterations(steps_readout_test, 100, measure_block_time=display)

            # load stats to calculate the performance
            t_train = steps_readout_train
            t_test = steps_readout_test


            errors = []
            for t_past in range(20):

                X_train, y_train = getXY(readout_recorders, 'n.x', input_recorders, 'n.pattern_index', 0, t_train, t_past+1)
                #X_train = stats.raster_readout[t_past:t_train]
                #y_train = stats.input_readout[:t_train - t_past].T.astype(int)

                X_test, y_test = getXY(readout_recorders, 'n.x', input_recorders, 'n.pattern_index', t_train, t_train + t_test, t_past+1)
                #X_test = stats.raster_readout[t_train + t_past:t_train + t_test]
                #y_test = stats.input_readout[t_train:t_train + t_test - t_past].T.astype(int)

                readout = linear_model.LogisticRegression()#multi_class='auto', solver='lbfgs'
                output_weights = readout.fit(X_train, y_train)
                error = 1-output_weights.score(X_test, y_test)
                errors.append(error)
                sm.save_param('error_{}'.format(t_past), error)
                print('t_past', t_past, error)

            SORN_Global.clear_recorder()
            sm.copy_project_files()
            sm.save_obj('net', SORN_Global)

            #print(errors)
            #plt.plot(errors)
            #plt.show()

            if display: print('\ndone!')
