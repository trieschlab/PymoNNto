import sys
sys.path.append('../../')

from SORNSim.NetworkBehaviour.Logic.SORN.SORN_advanced import *
#from NetworkBehaviour.Logic.SORN.SORN_advanced_buffer import *
from SORNSim.NetworkBehaviour.Input.Music.DrumBeatActivator import *
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Synapse_Group import *
from Testing.Common.SORN_MusicHelper import *
from SORNSim.NetworkBehaviour.Structure.Structure import *
from Testing.Visualization.SORN_visualization import *

display = False
so = True

def run(tag, ind=[], par={'N_e':[1800], 'TS':[1]}):
    name = 'DrumBeats_'+'_'+tag+str(par['N_e'])+'N_e_'+str(par['TS'])

    sm = StorageManager(main_folder_name=tag, folder_name=name, random_nr=False, print_msg=display)
    sm.save_param_dict(par)

    source = DrumBeatActivator(tag='drum_act', which_tracks=[100], filter_silence=False, THR_similar_tracks=0.5, input_density=0.015, offtoken=True, ontoken=True, include_inverse_alphabet=False)#, include_inverse_alphabet= True)#output_size=par['N_e']

    inh_thr = ['0.1;+-0%','0.1;+-0%', '0.1;+-0%']
    exc_thr = ['0.1;+-100%', '0.1;+-100%', '0.1;+-100%']

    SORN = Network()

    for i, lag in enumerate(par['TS']):#
        e_ng = NeuronGroup(net=SORN, tag='exc_cell_{},prediction_source,text_input_group'.format(lag), size=get_squared_dim(int(par['N_e'][i])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=lag, init_TH=exc_thr[i]),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='13%', distribution='lognormal(0,[0.89#0])', normalize=True, partition_compensation=True),
            4: SORN_init_afferent_synapses(transmitter='GABA', density='50%', distribution='lognormal(0,[0.80222#1])', normalize=True),

            12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', so=so),
            13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]', so=so),

            17: SORN_fast_syn(transmitter='GABA', strength='-[0.11045#4]', so=so),
            18: SORN_input_collect(),

            19: SORN_Refractory(factor='0.5;+-50%'),

            21: SORN_STDP(eta_stdp='[0.0001#5]', prune_stdp=False),
            22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),

            23: SORN_IP_TI(h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0006#8];+-50%', integration_length='[30#18];+-50%', clip_min=None),#, gap_percent=10 #30;+-50% #0.0003
            #24: SORN_NOX(mp='np.mean(n.output_new)', eta_nox='[0.3#9];+-50%', behaviour_enabled=False), #0.4
            25: SORN_NOX(mp='self.partition_sum(n)', eta_nox='[0.3#9];+-50%'),  # 0.4

            26: SORN_SC_TI(h_sc='lognormal_real_mean([0.01#10], [0.2944#11])', eta_sc='[0.1#12];+-50%', integration_length='1'), #60;+-50% #0.05
            27: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

            30: SORN_finish(),

            #99: SynapseRecorder(['[np.sum(s.slow_add)]'], tag='ex_glu_syn_rec'),
            #100: NeuronRecorder(['n.output'], tag='exc_out_rec')
        })

        i_ng = NeuronGroup(net=SORN, tag='inh_cell_{}'.format(lag), size=get_squared_dim(int(0.2 * (par['N_e'][i]))), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=lag, init_TH=inh_thr[i]),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='45%', distribution='lognormal(0,[0.87038#14])', normalize=True),  # 450
            4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            #11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]', so=so),
            14: SORN_fast_syn(transmitter='GLU', strength='[1.5#16]', so=so),#1.5353
            15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#17]', so=so),#0.08
            18: SORN_input_collect(),

            19: SORN_Refractory(factor='0.1;0.4'),

            #23: SORN_IP_TI(h_ip='lognormal_real_mean([0.08#6], [0.2944#7])', eta_ip='[0.0003#8];+-50%', integration_length='30;+-50%', clip_min=None),

            30: SORN_finish(),

            #100: NeuronRecorder(['n.output'], tag='inh_out_rec')
        })

        i_ng['structure', 0].stretch_to_equal_size(e_ng)


        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,ee', connectivity='(s_id!=d_id)*in_box(10)', partition=True)#.partition([10, 10], [4, 4])
        SynapseGroup(net=SORN, src=e_ng, dst=i_ng, tag='GLU,ie', connectivity='(s_id!=d_id)*in_box(10)', partition=True)#.partition([5, 5], [2, 2])
        SynapseGroup(net=SORN, src=i_ng, dst=e_ng, tag='GABA,ei', connectivity='(s_id!=d_id)*in_box(10)', partition=True)
        SynapseGroup(net=SORN, src=i_ng, dst=i_ng, tag='GABA,ii', connectivity='(s_id!=d_id)*in_box(10)', partition=True)

        if lag == 1:
            i_ng.add_behaviour(10, SORN_external_input(strength=1.0, pattern_groups=[source]))
            e_ng.add_behaviour(10, SORN_external_input(strength=1.0, pattern_groups=[source]))
            #e_ng.add_behaviour(101, NeuronRecorder(['n.pattern_index'], tag='inp_rec'))
        else:
            #forward synapses
            SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GLU,eeff')#.partition([10, 10], [4, 4])
            SynapseGroup(net=SORN, src=last_e_ng, dst=i_ng, tag='GABA,ieff')#.partition([5, 5], [2, 2])
            #backward synapses
            SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GLU,eebw')#.partition([10, 10], [4, 4])
            SynapseGroup(net=SORN, src=e_ng, dst=last_i_ng, tag='GABA,iebw')#.partition([5, 5], [2, 2])

        last_e_ng = e_ng # excitatory neuron group
        last_i_ng = i_ng # inhibitory neuron group
        e_ng.color = (0,0,255,255)
        i_ng.color = (255,0,255,255)
        e_ng.pattern_index=0
        i_ng.pattern_index=0

    SORN.set_marked_variables(ind, info=(ind == []))

    SORN.initialize(info=False)
    ############################################################################################################################################################

    score_spont = score_predict_train = score_predict_test = 0

    #import Exploration.UI.Network_UI.Network_UI as SUI
    #SUI.Network_UI(SORN, label='SORN UI default setup', storage_manager=sm, group_display_count=2, reduced_layout=False).show()

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

    #plot_frequencies_poly(score_spont, path = sm.absolute_path+'frequencies', title='{} Ne, {} lag'.format(par['N_e'], par['TS']))

    return score_predict_train, score_predict_test, score_spont
    #return {'Prediction training set: ': score_predict_train, 'Prediction test set :': score_predict_test, 'Spontaneous:': score_spont}

if __name__ == '__main__':
    ind = []

    res_train, res_test, res_spont = run(tag='drum', ind=[0.95, 0.4, 0.1383, 0.1698, 0.1, 0.0015, 0.04, 0.2944, 0.0006, 0.2, 0.015, 0.2944, 0.1, 0.001, 0.87038, 0.82099, 1.5, 0.08, 15.0])
    print('score', res_spont['total_score'])


    #res = run(ind=ind, par={'N_e':900})
    #for i in res: 
    #    print(i, res[i], '\n')

    







    # 23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=0, gap_percent=10, clip_min=None),
    # 24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=0, gap_percent=0, clip_min=None),

    #while True:
    #    for N_e in [300, 600, 900, 1200, 1500, 1800, 2100]:

    #import Exploration.Evolution.Distributed_Evolution as DistEvo
    #tag, ind = DistEvo.parse_sys(ind=ind)
    #score = run(tag, ind)
    #DistEvo.save_score(score, tag, ind)

# ind = [0.82595816313429, 0.7781756853872416, 0.1997858098991086, 0.13349801597979383, 0.10639055311698634, 0.000566173884684002, 0.02619084480461104, 0.39595248483787987, 0.0007719810261645456, 0.002418802021848068, 0.009578630957492154, 0.2782771896247201, 0.06311839742346288, 8.45109838208754e-05, 2.3294007949883344, 0.748120338752588, 0.18709794208310676, 1.7706595422790672, 0.08502206201400603]


#[0.6093440001479538, 0.6646333279025789, 0.0953427428598998, 0.1054391126030518, 0.21855080100129426, 0.00728797958091016, 0.02470102183549397, 0.3600451188525096, 0.0003334404915643689, 0.00024983606633075114, 0.008668195877663548, 0.2637360522306794, 0.07534380716443886, 0.00011833380544100796, 0.9123484575537191, 0.6715805262283047, 0.10484280187778258, 1.1026672210897053, 0.06792300099378663]

#ind = [0.13836856717331408, 0.16982974221677782, 0.11045406247494298, 0.1838996599635843, 1.5353184446420107, 0.08049924935792714, 0.2943968676418953, 0.0009456577980814013, 0.8900762238158484, 0.8022238912339718, 0.8703833239674005, 0.8209942320661112, 0.051296268342171394, 0.050399158855638226]

# ind = [0.7385370280470228, 0.8226723999377027, 0.11273843436441608, 0.1817644032593909, 0.109274620575415,
#       0.009975256314725341, 0.02778099081297295, 0.39756175082736167, 0.00039120709351901287,
#       0.00022072905217714855, 0.011438915209872046, 0.2931624407683382, 0.09948942825855073,
#       0.00010527804839371519, 0.7966525665779819, 0.8906946292176879, 0.18661541798990544, 1.177435046704275,
#       0.07324614476663155]

# ind = [0.7889235750016215, 0.7787296297295986, 0.11545489684529861, 0.14425136173265504, 0.1334078494022305, 0.010949423628177704, 0.02837490485493722, 0.39364605923691165, 0.00029810407779906487, 0.000272889327175645, 0.0094122950269217, 0.27969867617156896, 0.08719751512183936, 0.00010791317570951136, 0.7818341504591202, 0.9188187560763199, 0.11533496380851045, 1.0455233915758568, 0.07358930963812842]

# ind=[0.6951116983608534, 0.7316273333467899, 0.15824764725730692, 0.14100546078386125, 0.16227539842958205, 0.008549584240026881, 0.028703305399639067, 0.3925216279831653, 0.0003658913208852939, 0.00014818081437625505, 0.007653229058625494, 0.26990529201963115, 0.10502039531103616, 0.00011508666020354326, 0.7743735546648665, 0.6557455004591821, 0.1316552957712628, 0.9945206266724288, 0.0715909872901501]
