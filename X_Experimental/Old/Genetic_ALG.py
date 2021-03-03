import sys
sys.path.append('../../TREN2')
sys.path.append('../../tren2')

import Exploration.Evolution.NetworkEvaluationFunctions as EvalF
from Testing.TREN.Helper import *
from Exploration.Evolution.Evo_Plots import *

def eval_func(ind, visualize=False):
    ind = ind.copy()

    print(format_array(ind))

    LGN_PC_Neurons = get_default_Input_Pattern_Neurons(input_width=10, input_height=10, patterns='rotate')  #,cross,noise

    behaviour = {
        0: NeuronDimension(10, 10, 1),
        1: InterGammaGlutamate(),
        # 2: TREN2NeuronIntraGammaGLU(),
        3: IntraGammaGABA(GABA_density=1.0, GABA_random_factor=0.0, GABA_Norm=get_evo_param(4.3, ind)),
        4: ActivityBuffering(activity_multiplyer=0.0, firetreshold=0.1),
        5: STDP(exponent=get_evo_param(4.0, ind), post_learn_value=get_evo_param(0.08, ind)),
        6: TemporalWeightCache(decay=1, strength=1),
        8: HomeostaticMechanism(range_end=get_evo_param(500, ind), inc=get_evo_param(0.5, ind), dec=get_evo_param(0.5, ind), pattern_chance=get_evo_param(0.01, ind)),  # speed:inc,dec #range_end=500
        9: GlutamateCacheConvergeAndNormalization(norm_value=6.0)
    }

    Cortex_PC_Neurons = NeuronGroup(-1, behaviour)

    feed_forward_syn = SynapseGroup(LGN_PC_Neurons, Cortex_PC_Neurons).add_tag('GLU')
    #recurrent_syn = TRENSynapseGroup(Cortex_PC_Neurons, Cortex_PC_Neurons, 's!=d').add_tag('GLU')
    inh_syn = SynapseGroup(Cortex_PC_Neurons, Cortex_PC_Neurons, 's!=d').add_tag('GABA')
    #inh_syn.shape_mat = inh_syn.get_ring_mat(10, 4.0)

    network = Network([LGN_PC_Neurons, Cortex_PC_Neurons], [feed_forward_syn, inh_syn])#recurrent_syn

    #rec=network.add_behaviours_to_neuron_group([TRENRecorder_eval(['n[10].avg'], gapwidth=100)], Cortex_PC_Neurons)[0]
    #network.simulate_iterations(100, 400, False)

    scores=[]
    for i in range(10):
        network.simulate_iterations(100, 40, False)
        score = EvalF.get_pattern_response_score(network, LGN_PC_Neurons[NeuronActivator].TNAPatterns[0], LGN_PC_Neurons, [Cortex_PC_Neurons], combinations=False) * (18 * 18)  # **2
        score += EvalF.get_pattern_response_score(network, LGN_PC_Neurons[NeuronActivator].TNAPatterns[0], LGN_PC_Neurons, [Cortex_PC_Neurons], combinations=True)

        scores.append(score)

    #import Exploration.Pyplot_visualizer as pv
    #pv.plot(scores)
    #pv.plot([np.average(np.array(scores)) for _ in scores])
    #score = EvalF.get_diversity_score(feed_forward_syn.GLU_Synapses.reshape((50, 100)))

    score = np.average(np.array(scores))

    print(score)

    if visualize:
        import Testing.Visualization.Pyplot_visualizer as pv
        #pv.matshow(inh_syn.GABA_Synapses[55].reshape(10, 10))
        #pv.plot(rec['n[10].avg'])
        pv.visualize_input_and_learned_patterns(network, Cortex_PC_Neurons, LGN_PC_Neurons, NN_eval=False)
        pv.show()

    return score

#22x22 Net test_1558547816.1330419.txt
#visualize_evolution_run('22x22 Net test_1558547816.1330419.txt', ['GABA_min', 'GABE_rnd', 'th', 'exp', 'learn speed','inc','dec','pattern chance','norm','---'])


#eval_func([4.727207749959612, 7.869339491307885, 9, 1152.046957812022, 3.078347860574453, 2.005965766084856, 0.0035233099163080816], True)
eval_func([3.0, 7.0, 6.0, 500, 2.0, 6.0, 0.01], True) #presentation line

#eval_func([4.5, 8.0, 11, 700.0, 4.0, 20.0, 0.01], True) #presentation cross



#if __name__ == '__main__':
#    evolution = Multithreaded_Evolution(eval_func, 32, thread_count=2, name="10x10 new score 2 simple lower mutation", mutation=0.05)
#    evolution.start([[3.4, 8.9, 6.5, 550, 1.8, 4.9, 0.008]])#[3.0, 7.0, 6.0, 500, 2.0, 6.0, 0.01]#[4.5, 8.0, 11, 700.0, 4.0, 20.0, 0.01]







#evolution = Evolution(eval_func, 32, name="10x10 new evo short")
#evolution.continue_evo('22x22 Net test_1558547816.1330419.txt')

#def eval_func_2(ind):
#    return np.sum(np.array(ind))

#evolution = Evolution(eval_func_2, 32, name="10x10 new evo short")
#evolution.start([[3.0, 7.0, 6.0, 500, 2.0, 6.0, 0.01]])