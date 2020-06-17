import numpy as np
from NetworkBehaviour.Recorder.Recorder import *
from Testing.Common.Classifier_Helper import *

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

    network['grammar_act', 0].active = True

    if stdp_off:
        network.activate_mechanisms('STDP')

    return text

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

def train_and_generate_text(SORN, steps_plastic, steps_train, steps_spont, steps_recovery=0, display=True, stdp_off=True, storage_manager=None, same_timestep_without_feedback_loop=False):
    #exc_neuron_tag, output_recorder_tag, input_recorder_tag
    #'main_exc_group', 'exc_out_rec', 'inp_rec'

    #SORN.clear_recorder()
    SORN.simulate_iterations(steps_plastic, 100, measure_block_time=display)#, disable_recording=True

    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    for ng in SORN['prediction_source']:
        SORN.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='prediction_rec')}, ng)
    for ng in SORN['text_input_group']:
        SORN.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)

    SORN.simulate_iterations(steps_train, 100, measure_block_time=display)

    if same_timestep_without_feedback_loop:
        readout_layer = train_same_step(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train)  # train
    else:
        readout_layer = train(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train, lag=1)  # steps_plastic, steps_plastic + steps_readout

    #SORN.clear_recorder(['prediction_rec', 'index_rec'])
    #SORN.deactivate_mechanisms(['prediction_rec', 'index_rec'])
    SORN.remove_behaviours_from_neuron_groups(SORN['prediction_source'], tags=['prediction_rec'])
    SORN.remove_behaviours_from_neuron_groups(SORN['text_input_group'], tags=['index_rec'])

    #SORN.recording_off()

    if same_timestep_without_feedback_loop:
        SORN['grammar_act', 0].active = False
        if steps_recovery > 0:
            SORN.simulate_iterations(steps_recovery, 100, measure_block_time=display, disable_recording=True)
        spont_output = get_simu_sequence(SORN, SORN['prediction_source'], 'n.output', readout_classifyer=readout_layer, seq_length=steps_spont, source=SORN['grammar_act', 0])#output generation
    else:
        spont_output = predict_sequence(readout_layer, SORN['prediction_source'], 'n.output', steps_spont, SORN, SORN['grammar_act', 0], lag=1)

    SORN['grammar_act', 0].active = True

    #if display:
    print(spont_output)
    SORN.recording_on()

    if stdp_off:
        SORN.activate_mechanisms('STDP')

    score_dict = SORN['grammar_act', 0].get_text_score(spont_output)

    if storage_manager is not None:
        storage_manager.save_param_dict(score_dict)

    return score_dict['total_score']
