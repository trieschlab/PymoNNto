#import sys
#sys.path.append('../../TREN2')
#sys.path.append('../../tren2')
from Testing.TREN.Helper import *
import Exploration.Evolution.NetworkEvaluationFunctions as EvalF
input_width = 15
input_height = 15
import gc

MNIST_patterns = MNIST_Patterns(group_possibility=1.0, repeat_same_label_time=1)

def create_run_and_evaluate(ind=[], evolution=True):
    gc.collect()

    LGN_PC_Neurons = get_default_Input_Pattern_Neurons(input_width=input_width, input_height=input_height, patterns='', predefined_patterns=[MNIST_patterns])  #rotate cross noise rotateimg_patches #input_width=input_width, input_height=input_height, input_depth=1,

    behaviour1 = {

        1: STDP_simple(exponent='[8.92#1]', post_learn_value='[6.55#2]'),  # 8.92 #6.55
        2: TemporalWeightCache(decay=1, strength=1, GLU_density=0.5, set_weights=True),
        # 3: RandomWeightFluctuation(beta=4*0.2, gamma=3*0.2),
        4: GlutamateCacheConvergeAndNormalization(norm_value='0.1,0.6'),# ,#20.0 #(norm_value=0.001)#40
        5: InterGammaGlutamate(),#0.005
        6: IntraGammaGlutamate(),
        7: IntraGammaGABA(GABA_density=1.0, GABA_random_factor=10.0, GABA_Norm='[3.8#0]'),#3.4 #3.8
        8: ActivityBuffering(activity_multiplyer=0.0, firetreshold=0.1),#todo warning: relu deactivated
        9: HomeostaticMechanism(range_end='[550#3],+-30%', inc='[1.84#4],+-10%', dec='[4.92#5],+-10%', pattern_chance='[0.0086#6],+-30%'),#target_max=20.0#0.0086 #,'
        10: RandomLeakInput(random_strength='[0.5#7]')
    }

    tren = Network(NeuronGroups=[LGN_PC_Neurons], SynapseGroups=[], initialize=False)#TRENet([LGN_PC_Neurons, Cortex_V1, Cortex_V2], [LGN_to_V1, V1_inh, V1_rec, V1_to_V2, V2_inh])

    create_Network_Structure(tren, [
        #{'behaviour': behaviour1, 'size': 10, 'split': 1, 'glu_rec': None, 'gab_rec': None, 'glu_ff': 5, 'gab_ff': None, 'glu_fb': None, 'gab_fb': None}
        {'behaviour': behaviour1, 'size': 40, 'split': 4, 'glu_rec': None, 'gab_rec': 10, 'glu_ff': 10, 'gab_ff': None, 'glu_fb': None, 'gab_fb': None},
        {'behaviour': behaviour1, 'size': 5, 'split': 1, 'glu_rec': None, 'gab_rec': 28, 'glu_ff': 28, 'gab_ff': None, 'glu_fb': None, 'gab_fb': None}
        #{'behaviour':behaviour1, 'size':15, 'split':1, 'glu_rec':None, 'gab_rec':15, 'glu_ff':10, 'gab_ff':None, 'glu_fb':None, 'gab_fb':None},
        #{'behaviour':behaviour1, 'size':4,  'split':1, 'glu_rec':None, 'gab_rec':28, 'glu_ff':28, 'gab_ff':None, 'glu_fb':None, 'gab_fb':None}
    ])

    tren.set_marked_variables(ind, info=not evolution)
    tren.initialize(info=not evolution)

    tren.simulate_iterations(5000, 100, not evolution)

    #import Exploration.UI.Realtime_UI as RUI
    #RUI.TREN_Realtime_UI(tren, tren.getNG('Cortex')[1], LGN_PC_Neurons,reconstruction_groups=tren.getNG('Cortex')).show()


    if evolution:
        return EvalF.get_Autoencoder_Score(tren, [tren.getNG('Cortex')[1]], 100)

    import Exploration.Visualization.Pyplot_visualizer as pv
    pv.visualize_layers(tren, tren.getNG('Cortex'), LGN_PC_Neurons, v_split=True)#, Cortex_V2, Cortex_V3
    pv.show()

#########
#Execute
#########

evolution = True

if evolution:
    constraints = []#['ind[0] = max(ind[0], 2.0)', 'ind[1] = max(ind[1], 4.0)', 'ind[2] = min(ind[2], 0.05)']
    if __name__ == '__main__':
        import Exploration.Evolution.Multithreaded_Evolution as Evo
        evolution = Evo.Multithreaded_Evolution(create_run_and_evaluate, 32, thread_count=4, name="MNIST_Autoencoder_Two_Layer variable_noise", mutation=0.05, constraints=constraints)
        evolution.start([[4.966167839019163, 4.192809910257579, 0.05657743987433898, 509.9871338378249, 0.29406266265897296, 0.3193893363111231, 0.08284412870417605, 0.1],
                         [4.043698551048355, 3.835397053462794, 0.05898891800853792, 500.00413618178493, 0.39230184764178344, 0.3872451423904377, 0.0085004067564455, 0.1],
                         [5.149667888459877, 3.647104781266361, 0.05577893866456646, 516.6488500033189, 0.3730157017562895, 0.33395409245171803, 0.1910232632129247, 0.1],
                         [4.927035088393434, 3.7367935873351286, 0.05624089440369129, 517.2745509108091, 0.2778324660024919, 0.31365870423822634, 0.20007795972547548, 0.1],
                         [5.213319729968475, 3.67107928026228, 0.05719733486309294, 480.45186463501204, 0.30700077270387927, 0.3757832982778819, 0.16686407094144645, 0.1],
                         [4.053218219088883, 3.7971014438199484, 0.0581834462373688, 495.50077898333393, 0.39026624066991544, 0.33653432167437575, 0.21333445748279323, 0.1],
                         [4.754844493066912, 3.455791609235984, 0.0548866820340498, 537.4536797901111, 0.2835518576654149, 0.39108763517452994, 0.1726233253382668, 0.1],
                         [4.316029399788208, 3.679450888156755, 0.05808537362794965, 475.9535568882848, 0.422946503784775, 0.4194006172562603, 0.18999819743033577, 0.1],
                         [4.650782261800137, 3.818050785225562, 0.053082431524396054, 452.6293931549344, 0.33028325006419534, 0.29189461738851097, 0.1862615164511844, 0.1],
                         [3.8951019192903464, 3.1214461204398245, 0.060459347180681834, 476.39790755738477, 0.3763434301549741, 0.3409724082782067, 0.13839550135067452, 0.1],
                         [4.4744940648255325, 3.677044688173778, 0.055431902428742214, 444.89303080051894, 0.3458400871889963, 0.29351008425967334, 0.17372919115909274, 0.1],
                         [3.713217885154617, 2.94764862156013, 0.06117167308606408, 397.6598655582083, 0.368142736999896, 0.39461102220875405, 0.1922598750785935, 0.1],
                         [4.894429998201307, 3.534093895430462, 0.05839010890817238, 556.335571790876, 0.3811365413272615, 0.3536913724035742, 0.21316714639758746, 0.1],
                         [4.745592604869098, 3.575529018376033, 0.058732523339435766, 489.31626167696953, 0.39375448632387033, 0.3816970147413976, 0.17402671095474734, 0.1],
                         [4.721294024500002, 3.810306828263033, 0.06190626270543924, 561.2153226209489, 0.37445071096199767, 0.3467378913565452, 0.16102507174433892, 0.1],
                         [4.959355696654529, 3.466961186123369, 0.05223103442624812, 455.23429104322116, 0.41866211799929937, 0.30095055802447307, 0.18315185507921028, 0.1]])#, [3.4, 8.9, 6.5, 550, 1.8, 4.9, 0.008]
        #evolution.continue_evo('MNIST_Autoencoder_Two_Layer variable noise_5585.txt')
else:
    create_run_and_evaluate([2.5, 4.0, 0.5, 573.0, 0.3, 0.3, 0.09], evolution=False)

