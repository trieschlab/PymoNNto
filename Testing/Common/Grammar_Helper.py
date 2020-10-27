from SORNSim.NetworkBehaviour.Recorder.Recorder import *
from Testing.Common.Classifier_Helper import *

from SORNSim.Exploration.Analysis.PCA import *
from SORNSim.Exploration.Analysis.WiltingPriesemann import *

def max_source_act_text(network, steps):

    source = network['grammar_act', 0]
    alphabet = source.alphabet
    alphabet_length = len(alphabet)

    result_text = ''

    for i in range(steps):
        network.simulate_iteration()
        char_act = np.zeros(alphabet_length)

        for ng in network['prediction_source']:
            recon = ng.Input_Weights.transpose().dot(ng.output)
            char_act += recon

        char = source.index_to_char(np.argmax(char_act))
        result_text += char

    return result_text


def predict_text_max_source_act(network, steps_plastic, steps_recovery, steps_spont, display=True, stdp_off=True):
    network.simulate_iterations(steps_plastic, 100, measure_block_time=display)

    if stdp_off:
        network.deactivate_mechanisms('STDP')

    network['grammar_act', 0].active = False

    network.simulate_iterations(steps_recovery, 100, measure_block_time=display)

    text = max_source_act_text(network, steps_spont)

    print(text)

    #print('\x1b[6;30;42m' + 'Success!' + '\x1b[0m')

    network['grammar_act', 0].active = True

    if stdp_off:
        network.activate_mechanisms('STDP')

    return text

def get_max_text_score(network, steps_plastic, steps_recovery, steps_spont, display=True, stdp_off=True, return_key='total_score'):
    text = predict_text_max_source_act(network, steps_plastic, steps_recovery, steps_spont, display, stdp_off)
    scores = network['grammar_act', 0].get_text_score(text)
    return scores[return_key]

def predict_char(linear_model, input_neuron_groups, inp_param_name):
    compiled_inp_param_name=compile(inp_param_name, '<string>', 'eval')
    inputs = [eval(compiled_inp_param_name) for n in input_neuron_groups]
    return int(linear_model.predict(np.concatenate(inputs).reshape(1, -1)))


#def simple_readout(neuron_group, inp_param_name, source):
#    n=neuron_group
#    act = eval(inp_param_name)
#    u = source.W.transpose().dot(act)
#    return np.argmax(u)


def predict_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1):

    spont_output = ''

    symbol = None

    for i in range(iterations):

        #if input_neuron_group.iteration % input_neuron_group.iteration_lag == input_neuron_group.iteration_lag-1: #last step
        symbol = predict_char(linear_model, prediction_neuron_groups, inp_param_name)
        char = source.index_to_char(symbol)
        spont_output += char

            #spont_output2 += source.index_to_symbol(simple_readout(input_neuron_group, 'n.x_without_input', source))

        #if input_neuron_groups.iteration % input_neuron_groups.iteration_lag == 0:
        if symbol is not None:
            #u = np.zeros(source.A)
            #u[symbol] = 1
            #input_neuron_group.input = source.W.dot(u)#applied in next step (0 without lag or 1 with lag)

            source.set_next_char(char)
            #input_neuron_group.input += input_neuron_group.Input_Weights[:, symbol]

        SORN.simulate_iteration()

    return spont_output

def get_simu_sequence(SORN, prediction_neuron_groups, output_param_name, readout_classifyer, seq_length, source):
    result=''
    for _ in range(seq_length):
        SORN.simulate_iteration()
        symbol = predict_char(readout_classifyer, prediction_neuron_groups, output_param_name)
        result += source.index_to_char(symbol)
    return result

def train_and_generate_text(SORN, steps_plastic, steps_train, steps_spont, steps_recovery=0, display=True, stdp_off=True, storage_manager=None, same_timestep_without_feedback_loop=False, return_key='total_score'):
    #exc_neuron_tag, output_recorder_tag, input_recorder_tag
    #'main_exc_group', 'exc_out_rec', 'inp_rec'

    #SORN.clear_recorder()
    if steps_plastic>0:
        SORN.simulate_iterations(steps_plastic, 100, measure_block_time=display)#, disable_recording=True

    #for i, syn in enumerate(SORN['syn']):
    #    np.save('Data/E{}.npy'.format(i), syn.enabled)
    #    np.save('Data/W{}.npy'.format(i), syn.W)

    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    for ng in SORN['prediction_source']:
        SORN.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='prediction_rec')}, ng)
    for ng in SORN['text_input_group']:
        SORN.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)

    SORN.simulate_iterations(steps_train, 100, measure_block_time=display)

    print('test2')

    if same_timestep_without_feedback_loop:
        readout_layer = train_same_step(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train)  # train
    else:
        readout_layer = train(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train, lag=1)  # steps_plastic, steps_plastic + steps_readout

    #act = SORN['prediction_rec', 0]['n.output', 0, 'np']
    #transition_score = np.mean(np.abs(act[0:-2]-act[1:-1])/np.mean(act))

    ###########################################################
    ###########################################################
    ###########################################################

    additional_info=False

    if additional_info:
        act = SORN['prediction_rec', 0]['n.output', 0, 'np']

        mean_act_1 = np.mean(act, axis=1)

        print(mean_act_1.shape)

        group_mr_A = MR_estimation([mean_act_1], 1, 150)

        #storage_manager.save_np('act_inh', SORN['prediction_rec', 1]['n.output', 0, 'np'])

        storage_manager.save_np('r_k', group_mr_A['r_k'])
        storage_manager.save_param('branching_ratio', group_mr_A['branching_ratio'])

        singluar_values, components, explained_variance, explained_variance_ratio = get_activity_singular_values_and_components(act)

        storage_manager.save_np('singluar_values', singluar_values)
        storage_manager.save_np('components', components)
        storage_manager.save_np('explained_variance', explained_variance)
        storage_manager.save_np('explained_variance_ratio', explained_variance_ratio)

        #print(singluar_values)
        #print(components.shape, components)

    ###########################################################
    ###########################################################
    ###########################################################



    #SORN.recording_off()

    if same_timestep_without_feedback_loop:
        SORN['grammar_act', 0].active = False
        if steps_recovery > 0:
            SORN.simulate_iterations(steps_recovery, 100, measure_block_time=display, disable_recording=True)
        spont_output = get_simu_sequence(SORN, SORN['prediction_source'], 'n.output', readout_classifyer=readout_layer, seq_length=steps_spont, source=SORN['grammar_act', 0])#output generation
    else:
        spont_output = predict_sequence(readout_layer, SORN['prediction_source'], 'n.output', steps_spont, SORN, SORN['grammar_act', 0], lag=1)

    SORN['grammar_act', 0].active = True

    if additional_info:
        mean_act=np.mean(SORN['prediction_rec', 0]['n.output', 0, 'np'], axis=1)
        storage_manager.save_np('act_exc', mean_act)
    #SORN.clear_recorder(['prediction_rec', 'index_rec'])
    #SORN.deactivate_mechanisms(['prediction_rec', 'index_rec'])
    SORN.remove_behaviours_from_neuron_groups(SORN['prediction_source'], tags=['prediction_rec'])
    SORN.remove_behaviours_from_neuron_groups(SORN['text_input_group'], tags=['index_rec'])


    #if display:
    print(spont_output)
    SORN.recording_on()

    if stdp_off:
        SORN.activate_mechanisms('STDP')

    score_dict = SORN['grammar_act', 0].get_text_score(spont_output)


    if storage_manager is not None:
        storage_manager.save_param_dict(score_dict)

    result = score_dict[return_key]#-transition_score/10

    if result<0:
        return 0
    else:
        return result


#act = np.random.rand(10000)+1
#transition_error = np.mean(np.abs(act[0:-2]-act[1:-1])/np.mean(act))
#print(transition_error)