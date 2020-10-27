import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
#from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *
from NetworkBehaviour.Input.Music.DrumBeatActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from Testing.Common.SORN_MusicHelper import *
from NetworkBehaviour.Structure.Structure import *
from Testing.Visualization.SORN_visualization import *


def get_color(type_index, layer):
    dim_value = max(layer * 0.7, 1.0)

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
so = True

def run(tag, ind=[], par={'N_e':1800, 'TS':[1]}):
    name = 'DrumBeats_'+'_'+tag+str(par['N_e'])+'N_e_'+str(par['TS'])

    sm = StorageManager(main_folder_name=tag, folder_name=name, random_nr=False, print_msg=display)
    sm.save_param_dict(par)

    source = DrumBeatActivator(tag='drum_act', which_tracks=[100], filter_silence=False, THR_similar_tracks=0.5, input_density=0.015, offtoken=True, ontoken=True, include_inverse_alphabet=False)#, include_inverse_alphabet= True)#output_size=par['N_e']

    SORN = Network()
    last_PC = None

    for i, timescale in enumerate(par['TS']):#
        PC = NeuronGroup(net=SORN, tag='Pyramidal Cell {},prediction_source'.format(timescale), size=get_squared_dim(int(par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timescale, init_TH='0.1;+-100%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='[50#0]%', distribution='uniform(0.1,0.11)', normalize=True, partition_compensation=True), #lognormal(0,0.6)
            4: SORN_init_afferent_synapses(transmitter='GABA_Dendrite', density='[30#1]%', distribution='uniform(0.1,0.11)', normalize=True),
            5: SORN_init_afferent_synapses(transmitter='GABA_Soma', density='[30#2]%', distribution='uniform(0.1,0.11)', normalize=True),
            6: SORN_init_afferent_synapses(transmitter='GABA_AIS', density='[30#3]%', distribution='uniform(0.1,0.11)', normalize=True),
            7: SORN_init_afferent_synapses(transmitter='GABA_NOX', density='full', distribution=None, normalize=True),

            12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#4]', so=so),
            13: SORN_slow_syn(transmitter='GABA_Dendrite', strength='-0.1', so=False),
            14: SORN_slow_input_collect(),

            17: SORN_fast_syn(transmitter='GABA_Soma', strength='-0.1', so=False),
            17.1: SORN_fast_syn(transmitter='GABA_AIS', strength='-0.1', so=False),
            #17.2: SORN_fast_syn(transmitter='GABA_NOX', strength='-0.1', so=False),
            19: SORN_input_collect(),

            20: SORN_Refractory(factor='[0.5#5];+-50%'),
            21: SORN_STDP_new(eta_stdp='[0.0015#6]', prune_stdp=False, excitation_punishment=0.0),#0.1#todo: test!!!
            22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

            23: SORN_IP_TI(mp='n.output_new/2.0+n.output_new_temp/2.0', h_ip='lognormal_real_mean([0.04#7], [0.2944#8])', eta_ip='[0.0006#9];+-50%', integration_length='[15#10];+-50%', clip_min=None),
            25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='0.5;+-50%', h_dh=0.0),#0.9#0.3
            26: SORN_SC_TI(h_sc='lognormal_real_mean([0.015#11], [0.2944#12])', eta_sc='[0.1#13];+-50%', integration_length='1'),
            #27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

            30: SORN_finish()

        })

        MT_SOM = NeuronGroup(net=SORN, tag='Martinotti Cell {},Somatostatin'.format(timescale), size=get_squared_dim(int(0.07 * par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timescale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            10: SORN_slow_syn(transmitter='GLU', strength='0.6', so=so),  # 1.5353
            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),

            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            19: SORN_input_collect(),
            #20: SORN_Refractory(factor='0.2;0.7'),
            30: SORN_finish()
        })

        '''
        EXP_NOX_CELL = NeuronGroup(net=SORN, tag='NOX Cell {}'.format(timescale), size=get_squared_dim(int(16)), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timescale, init_TH='0.04', activation_function='identity'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='full', distribution=None, normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            10: SORN_slow_syn(transmitter='GLU', strength='9.0', so=so),#1.5353
            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),

            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            19: SORN_input_collect(),
            #20: SORN_Refractory(factor='0.2;0.7'),
            30: SORN_finish()
        })
        '''

        BA_PV = NeuronGroup(net=SORN, tag='Basket Cell {},Parvalbumin'.format(timescale), size=get_squared_dim(int(0.07 * par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timescale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            10: SORN_slow_syn(transmitter='GLU', strength='0.6', so=so),  # 1.5353
            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),

            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08
            19: SORN_input_collect(),
            #20: SORN_Refractory(factor='0.2;0.7'),
            30: SORN_finish()
        })

        CH_PV = NeuronGroup(net=SORN, tag='Chandelier Cell {},Parvalbumin'.format(timescale), size=get_squared_dim(int(0.07 * par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=timescale, init_TH='0.1;+-0%'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,0.87038)', normalize=True),
            #4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),
            14: SORN_fast_syn(transmitter='GLU', strength='0.4', so=so),#1.5353
            #15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=False),#0.08

            19: SORN_input_collect(),
            #19: SORN_Refractory(factor='0.2;0.7'),
            30: SORN_finish()
        })

        MT_SOM['structure', 0].stretch_to_equal_size(PC)
        BA_PV['structure', 0].stretch_to_equal_size(PC)
        CH_PV['structure', 0].stretch_to_equal_size(PC)
        #EXP_NOX_CELL['structure', 0].stretch_to_equal_size(PC)

        SynapseGroup(net=SORN, src=PC, dst=PC, tag='GLU', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=PC, dst=MT_SOM, tag='GLU', connectivity='in_box(2)', partition=True)
        SynapseGroup(net=SORN, src=PC, dst=BA_PV, tag='GLU', connectivity='in_box(2)', partition=True)
        SynapseGroup(net=SORN, src=PC, dst=CH_PV, tag='GLU', connectivity='in_box(2)', partition=True)

        #SynapseGroup(net=SORN, src=PC, dst=EXP_NOX_CELL, tag='GLU', connectivity='in_box(3.75)', partition=True)

        SynapseGroup(net=SORN, src=MT_SOM, dst=PC, tag='GABA_Dendrite', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=BA_PV, dst=PC, tag='GABA_Soma', connectivity='in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=CH_PV, dst=PC, tag='GABA_AIS', connectivity='in_box(10)', partition=True)

        #SynapseGroup(net=SORN, src=EXP_NOX_CELL, dst=PC, tag='GABA_NOX', connectivity='in_box(3.75)', partition=True)

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

        PC.color = get_color(0, timescale)
        MT_SOM.color = get_color(1, timescale)
        BA_PV.color = get_color(2, timescale)
        CH_PV.color = get_color(3, timescale)
        EXP_NOX_CELL.color = get_color(4, timescale)
        #EXP_NOX_CELL.display_min_max_act = (0, 0.3)

    SORN.set_marked_variables(ind, info=(ind == []), storage_manager=sm)
    SORN.initialize(info=False)
    ############################################################################################################################################################

    score_spont = score_predict_train = score_predict_test = 0

    Network_UI(SORN, label='SORN UI PC PV SOM', storage_manager=sm, group_display_count=4, reduced_layout=False).show()

    SORN = run_plastic_phase(SORN, steps_plastic=1000000, display=True, storage_manager=sm)

    #print(set(np.nonzero(np.array(SORN['drum_act', 0].seen))[1]))

    readout, X_train, Y_train, X_test, Y_test = train_readout(SORN, steps_train=100000, steps_test=100, source = SORN['drum_act', 0], display=True, stdp_off=True, storage_manager=sm)
    
    score_predict_train = get_score_predict_next_step(SORN, SORN['drum_act', 0],readout, X_train, Y_train, display=True, stdp_off=True, storage_manager=sm)

    score_predict_test = get_score_predict_next_step(SORN, SORN['drum_act', 0],readout, X_test, Y_test, display=True, stdp_off=True, storage_manager=sm)
    
    score_spont = get_score_spontaneous_music(SORN, SORN['drum_act', 0], readout, split_tracks=False, steps_spont=2000, display=True, stdp_off=True, 
    same_timestep_without_feedback_loop=False, steps_recovery=0, create_MIDI=True, storage_manager=sm)#, steps_recovery=15000
    
    sm.save_obj('score_train', score_predict_train)
    sm.save_obj('score_test', score_predict_test)
    sm.save_obj('score_spontaneous', score_spont)

    plot_frequencies_poly(score_spont, path = sm.absolute_path+'frequencies', title='{} Ne, {} lag'.format(par['N_e'], par['TS']))

    return score_predict_train, score_predict_test, score_spont
    #return {'Prediction training set: ': score_predict_train, 'Prediction test set :': score_predict_test, 'Spontaneous:': score_spont}

if __name__ == '__main__':
    ind = []

    res_train, res_test, res_spont = run(tag='PV_SOM', ind=[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.0015, 0.04, 0.2944, 0.0006, 0.2, 0.015, 0.2944, 0.1, 0.001, 0.87038, 0.82099, 1.5, 0.08, 15.0])
    print('score', res_spont['total_score'])
