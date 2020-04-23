import sys
sys.path.append('../../')

from NetworkCore.Network import *
from NetworkCore.Synapse_Group import *
from Testing.Common.Classifier_Helper import *
from NetworkBehaviour.Structure.Structure import *
from Exploration.StorageManager.StorageManager import *

from NetworkBehaviour.Logic.TREN.Neuron_Homeostais import *
from NetworkBehaviour.Logic.TREN.Neuron_Input import *
from NetworkBehaviour.Logic.TREN.Neuron_Learning import *

from NetworkBehaviour.Input.Images.Lines import *

display = False
so = True

def run(tag='hierarchical', ind=[], par={'N_e':900}):
    sm = StorageManager(tag, random_nr=True, print_msg=display)
    sm.save_param_dict(par)

    #source = FDTGrammarActivator_New(tag='grammar_act', random_blocks=True, input_density=10/par['N_e'])#.plot_char_input_statistics()#output_size=par['N_e']#15
    #source = LongDelayGrammar(tag='grammar_act', output_size=par['N_e'], random_blocks=True, mode=['very simple'], input_density=10/par['N_e'])#.print_test().plot_char_input_statistics()
    #print(source.get_text_score('. parrot likes trees. wolf wolf wolf..'))
    source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=30, grid_height=30, center_x=list(range(30)), center_y=30 / 2, degree=90, line_length=60)
    #source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=10, grid_height=10, center_x=10 / 2, center_y=list(range(10)), degree=0, line_length=20)
    #source = Line_Patterns(tag='image_act', group_possibility=1.0, grid_width=10, grid_height=10, center_x=10 / 2, center_y=10 / 2, degree=list(np.arange(0, 360, 20)), line_length=20)
    #source = MNIST_Patterns(tag='image_act', group_possibility=1.0, repeat_same_label_time=1)
    #source = TNAP_Image_Patches(tag='image_act', image_path='../../../Images/pexels-photo-275484.jpeg', grid_width=20, grid_height=20, dimensions=['on_center_white'], patch_norm=True)#'red', 'green', 'blue', 'gray', '255-red', '255-green', '255-blue', '255-gray',, 'rgbw', '255-rgbw''off_center_white',

    SORN = Network([], [], initialize=False)

    for timecale in [1]:#2

        e_ng = NeuronGroup(net=SORN, tag='main_exc_group,ts={}'.format(timecale), size=get_squared_dim(int(par['N_e'])), behaviour={

            1: STDP_simple(exponent='[3.0#1]', post_learn_value='[6.55#2]'),  # 8.92 #6.55
            2: TemporalWeightCache(decay=1, strength=1, GLU_density=0.5, set_weights=True),
            # 3: RandomWeightFluctuation(beta=4*0.2, gamma=3*0.2),
            3: GlutamateCacheConvergeAndNormalization(norm_value='0.1;0.6'),# ,#20.0 #(norm_value=0.001)#40
            5: InterGammaGlutamate(),#0.005
            6: IntraGammaGlutamate(),
            7: IntraGammaGABA(GABA_density=1.0, GABA_random_factor=10.0, GABA_Norm='[3.8#0]'),#3.4 #3.8
            8: ActivityBuffering(activity_multiplyer=0.0, firetreshold='0.1;+-0%'),#todo warning: relu deactivated
            9: HomeostaticMechanism(range_end='[550#3];+-30%', inc='[0.184#4];+-10%', dec='[0.492#5];+-10%', pattern_chance='[0.0086#6];+-30%'),#target_max=20.0#0.0086 #,'
            10: RandomLeakInput(random_strength='[0.5#7]'),

            11: additional(),

            100: NeuronRecorder(['n.output'], tag='exc_out_rec')
        })

        #i_ng['structure', 0].stretch_to_equal_size(e_ng)

        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GLU,e->e')#.partition([10, 10], [6, 6]) #, connectivity='(np.abs(sx-dx)<10)*(np.abs(sy-dy)<10)'
        SynapseGroup(net=SORN, src=e_ng, dst=e_ng, tag='GABA,e->e')#.partition([10, 10], [6, 6]) #, connectivity='(np.abs(sx-dx)<10)*(np.abs(sy-dy)<10)',

        #SynapseGroup(net=SORN, src=e_ng, dst=i_ng, connectivity='(np.abs(sx-dx)<10)*(np.abs(sy-dy)<10)', tag='GLU,e->i').partition([10, 10], [4, 4])
        #SynapseGroup(net=SORN, src=i_ng, dst=e_ng, connectivity='(np.abs(sx-dx)<10)*(np.abs(sy-dy)<10)', tag='GABA,i->e')
        #SynapseGroup(net=SORN, src=i_ng, dst=i_ng, connectivity='(np.abs(sx-dx)<10)*(np.abs(sy-dy)<10)', tag='GABA,i->i')

        e_ng.add_behaviour(4, TREN_external_input(strength=0.5, pattern_groups=[source]))
        # i_ng.add_behaviour(10, SORN_external_input(strength=0.3, pattern_groups=[source]))
        #if timecale == 1:
        e_ng.add_behaviour(101, NeuronRecorder(['n.pattern_index'], tag='inp_rec'))
        #else:
        #    #forward synapses
        #    SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GLU,e->e(+1)').partition([10, 10], [6, 6])
        #    SynapseGroup(net=SORN, src=last_e_ng, dst=e_ng, tag='GABA,e->i(+1)').partition([10, 10], [2, 2])
        #    #backward synapses
        #    SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GLU,e(+1)->e').partition([10, 10], [6, 6])
        #    SynapseGroup(net=SORN, src=e_ng, dst=last_e_ng, tag='GABA,e(+1)->i').partition([10, 10], [2, 2])

        #last_e_ng = e_ng
        #last_i_ng = i_ng

    SORN.set_marked_variables(ind, info=(ind == []))
    SORN.initialize(info=False)

    ############################################################################################################################################################

    score = 0

    #SORN.simulate_iterations(100, 100, measure_block_time=True, disable_recording=True)

    import Exploration.UI.Network_UI.Network_UI as SUI
    SUI.Network_UI(SORN, label='T', exc_group_name='main_exc_group', inh_group_name='main_inh_group', storage_manager=sm).show()

    score += get_evolution_score_words(SORN, 15000, 5000, 2000, display=False, stdp_off=True, same_timestep_without_feedback_loop=True, steps_recovery=15000)#, steps_recovery=15000
    #score += get_oscillation_score_hierarchical(SORN, 0, 5000)
    return score



if __name__ == '__main__':
    ind = []

    print('score', run(ind=ind, par={'N_e': 900}))#1400





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
