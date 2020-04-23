import sys
sys.path.append('../../')

from NetworkBehaviour.Logic.SORN.SORN_advanced import *
from NetworkBehaviour.Input.Text.TextActivator import *
from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *

display = False

def run(tag='hierarchical', ind=[], par={'N_e':900}):
    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    source = FDTGrammarActivator_New(tag='grammar_act', output_size=par['N_e'], random_blocks=True)
    #source = LongDelayGrammar(tag='grammar_act', output_size=par['N_e'], random_blocks=True, mode=['simple']).print_test()
    #print(source.get_text_score('. parrot likes trees. wolf wolf wolf..'))

    SORN_Global = Network([], [], initialize=False)

    for lag in [1, 2]:#

        e_ng = NeuronGroup(net=SORN_Global, tag='main_exc_group', size=get_squared_dim(par['N_e']), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=lag, init_TH='0.0;0.2'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='13%', distribution='lognormal(0,[0.89#0])', normalize=True, partition_compensation=True),  # 100
            4: SORN_init_afferent_synapses(transmitter='GABA', density='45%', distribution='lognormal(0,[0.80222#1])', normalize=True),  # 90

            12: SORN_slow_syn(transmitter='GLU', strength='[0.1383#2]', input_strength=1.0),
            13: SORN_slow_syn(transmitter='GABA', strength='-[0.1698#3]'),

            17: SORN_fast_syn(transmitter='GABA', strength='-[0.11045#4]'),
            18: SORN_input_collect(),

            19: SORN_Refractory(strength=1, factor='0.2;0.7'),

            21: SORN_STDP(eta_stdp='[0.0005#5]', prune_stdp=False),#0.01
            22: SORN_SN(syn_type='GLU', clip_max=None, init_norm_factor=1.0),
            #23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0004#8];+-45.4%', integration_length=0, gap_percent=10, clip_min=None),
            #24: SORN_diffuse_IP(mp='output_new', h_dh='same(IPTI, th)', eta_dh='[0.0002#9]', integration_length=0, gap_percent=0, clip_min=None),

            23: SORN_IP_TI(mp='output_new', h_ip='lognormal_real_mean([0.04#6], [0.2944#7])', eta_ip='[0.0006#8];+-45.4%', integration_length=0, clip_min=None),#, gap_percent=10 #'20;50'
            24: SORN_NOX(eta_nox='0.001;0.003'), #, target_clip_min=-0.01, target_clip_max=0.01

            25: SORN_SC_TI(mp='excitation', h_sc='lognormal_real_mean([0.01#10], [0.2944#11])', eta_sc='[0.1#12];+-30%', integration_length=0),#'50;150'
            26: SORN_iSTDP(h_ip='same(SCTI, th)', eta_istdp='[0.0001#13]'),

            30: SORN_finish(),

            100: NeuronRecorder(['n.output'], tag='exc_out_rec')
        })

        i_ng = NeuronGroup(net=SORN_Global, tag='main_inh_group', size=get_squared_dim(int(0.2 * par['N_e'])), behaviour={
            2: SORN_init_neuron_vars(iteration_lag=lag, init_TH='0.1'),
            3: SORN_init_afferent_synapses(transmitter='GLU', density='50%', distribution='lognormal(0,[0.87038#14])', normalize=True),  # 450
            4: SORN_init_afferent_synapses(transmitter='GABA', density='20%', distribution='lognormal(0,[0.82099#15])', normalize=True),  # 40

            11: SORN_slow_syn(transmitter='GABA', strength='-[0.1838#16]'),
            14: SORN_fast_syn(transmitter='GLU', strength='[1.5353#17]'),
            15: SORN_fast_syn(transmitter='GABA', strength='-[0.08#18]'),
            18: SORN_input_collect(),

            19: SORN_Refractory(strength=1, factor='0.2;0.7'),

            30: SORN_finish(),

            100: NeuronRecorder(['n.output'], tag='inh_out_rec')
        })

        ee_syn = SynapseGroup(net=SORN_Global, src=e_ng, dst=e_ng, connectivity='s_id!=d_id', tag='GLU,ee')
        ie_syn = SynapseGroup(net=SORN_Global, src=e_ng, dst=i_ng, tag='GLU,ie')
        ei_syn = SynapseGroup(net=SORN_Global, src=i_ng, dst=e_ng, tag='GABA,ei')
        ii_syn = SynapseGroup(net=SORN_Global, src=i_ng, dst=i_ng, tag='GABA,ii')

        if lag == 1:
            e_ng.add_behaviour(1, NeuronActivator(write_to='input', pattern_groups=[source]))  # ,source2
            e_ng.add_behaviour(101, NeuronRecorder(['n.pattern_index'], tag='inp_rec'))
        else:
            #forward synapses
            ee_ff_syn = SynapseGroup(net=SORN_Global, src=last_e_ng, dst=e_ng, tag='GLU,eeff')
            ie_ff_syn = SynapseGroup(net=SORN_Global, src=last_e_ng, dst=i_ng, tag='GABA,ieff')
            #backward synapses
            ee_bw_syn = SynapseGroup(net=SORN_Global, src=e_ng, dst=last_e_ng, tag='GLU,eebw')
            #ie_bw_syn = SynapseGroup(net=SORN_Global, src=e_ng, dst=last_i_ng, tag='GABA,iebw')

            SORN_Global.partition_Synapse_Group(ee_ff_syn, [10, 10], [4, 4])
            SORN_Global.partition_Synapse_Group(ee_bw_syn, [10, 10], [4, 4])

        SORN_Global.partition_Synapse_Group(ee_syn, [10, 10], [4, 4])
        SORN_Global.partition_Synapse_Group(ie_syn, [5, 5], [2, 2])
        ##SORN_Global.partition_Synapse_Group(ei_syn, [5, 5], [2, 2])

        last_e_ng = e_ng
        last_i_ng = i_ng

    SORN_Global.set_marked_variables(ind, info=(ind == []))

    SORN_Global.initialize(info=False)


    ####################################################
    ####################################################
    ####################################################

    import Exploration.UI.Network_UI.Network_UI as SUI
    SUI.Network_UI(SORN_Global, label='SORN UI', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    #return 100 + get_spontaneous_grammar_score(SORN_Global, 'main_exc_group', 'exc_out_rec', 'inp_rec', 20000, 5000, 0, 2000, display=True, stdp_off=True)

    #return get_evolution_score_words(SORN_Global, 'main_exc_group', 'out_rec', 'inp_rec', 15000, 5000, 2000, display=False, stdp_off=True)
    #return get_evolution_score_words(SORN_Global, 20000, 5000, 2000, display=True, stdp_off=True, same_timestep_without_feedback_loop=False, steps_recovery=0)#, storage_manager=sm
    #return get_evolution_score(SORN_Global, 5000, 3000, 0.2, e_ng, i_ng)#0.04
    return get_evolution_score_simple(SORN_Global, 5000, 4000, e_ng)


if __name__ == '__main__':
    #ind = [0.7385370280470228, 0.8226723999377027, 0.11273843436441608, 0.1817644032593909, 0.109274620575415,
    #       0.009975256314725341, 0.02778099081297295, 0.39756175082736167, 0.00039120709351901287,
    #       0.00022072905217714855, 0.011438915209872046, 0.2931624407683382, 0.09948942825855073,
    #       0.00010527804839371519, 0.7966525665779819, 0.8906946292176879, 0.18661541798990544, 1.177435046704275,
    #       0.07324614476663155]

    #ind = [0.7889235750016215, 0.7787296297295986, 0.11545489684529861, 0.14425136173265504, 0.1334078494022305, 0.010949423628177704, 0.02837490485493722, 0.39364605923691165, 0.00029810407779906487, 0.000272889327175645, 0.0094122950269217, 0.27969867617156896, 0.08719751512183936, 0.00010791317570951136, 0.7818341504591202, 0.9188187560763199, 0.11533496380851045, 1.0455233915758568, 0.07358930963812842]

    #ind=[0.6951116983608534, 0.7316273333467899, 0.15824764725730692, 0.14100546078386125, 0.16227539842958205, 0.008549584240026881, 0.028703305399639067, 0.3925216279831653, 0.0003658913208852939, 0.00014818081437625505, 0.007653229058625494, 0.26990529201963115, 0.10502039531103616, 0.00011508666020354326, 0.7743735546648665, 0.6557455004591821, 0.1316552957712628, 0.9945206266724288, 0.0715909872901501]
    ind = []#[0.6093440001479538, 0.6646333279025789, 0.0953427428598998, 0.1054391126030518, 0.21855080100129426, 0.00728797958091016, 0.02470102183549397, 0.3600451188525096, 0.0003334404915643689, 0.00024983606633075114, 0.008668195877663548, 0.2637360522306794, 0.07534380716443886, 0.00011833380544100796, 0.9123484575537191, 0.6715805262283047, 0.10484280187778258, 1.1026672210897053, 0.06792300099378663]


    #while True:
    #    for N_e in [300, 600, 900, 1200, 1500, 1800, 2100]:
    run(ind=ind, par={'N_e': 900})

    #import Exploration.Evolution.Distributed_Evolution as DistEvo
    #tag, ind = DistEvo.parse_sys(ind=ind)
    #score = run(tag, ind)
    #DistEvo.save_score(score, tag, ind)

#ind = [0.13836856717331408, 0.16982974221677782, 0.11045406247494298, 0.1838996599635843, 1.5353184446420107, 0.08049924935792714, 0.2943968676418953, 0.0009456577980814013, 0.8900762238158484, 0.8022238912339718, 0.8703833239674005, 0.8209942320661112, 0.051296268342171394, 0.050399158855638226]
