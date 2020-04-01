from collections import Counter
import numpy as np
from sklearn import linear_model
import sys
from NetworkBehaviour.Recorder.Recorder import *

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

def get_oscillation_score_hierarchical(SORN_Global, simulation_steps, evaluation_steps):
    result = 0
    parts = 0

    for mode in ['grammar input', 'free activity without learning', 'free activity with learning']:

        if mode is 'free activity without learning':
            SORN_Global['activator', 0].active = False
            SORN_Global.deactivate_mechanisms('STDP')

        if mode is 'free activity with learning':
            SORN_Global['activator', 0].active = False
            SORN_Global.activate_mechanisms('STDP')

        SORN_Global.simulate_iterations(simulation_steps+evaluation_steps, 100, measure_block_time=True)

        for group in SORN_Global['main_exc_group']:
            target = np.mean((group['IPTI'][0].min_th + group['IPTI'][0].max_th) / 2)
            activity = np.mean(np.array(group['n.output', 0])[-evaluation_steps:], axis=1)
            result += 1 - np.sum(np.abs(activity - target)) / evaluation_steps
            parts += 1

        for group in SORN_Global['main_inh_group']:
            activity = np.mean(np.array(group['n.output', 0])[-evaluation_steps:], axis=1)
            bad_count = (np.sum(activity < 0.0001) + np.sum(activity > 0.5))
            result += 1 - bad_count / evaluation_steps
            parts += 1

    return result/parts

def get_evolution_score_simple(SORN_Global, simulation_steps, evaluation_steps, e_ng):
    SORN_Global.simulate_iterations(simulation_steps, 100, measure_block_time=False)
    exc_avg_tar = np.mean((e_ng['IPTI'][0].min_th + e_ng['IPTI'][0].max_th) / 2)
    exc_avg = np.mean(np.array(e_ng['n.output', 0])[-evaluation_steps:], axis=1)
    exc_score = np.power(np.sum(np.abs(exc_avg - exc_avg_tar)), 2)
    return -exc_score

def get_evolution_score(SORN_Global, simulation_steps, evaluation_steps, inh_target_act, e_ng, i_ng):
    SORN_Global.simulate_iterations(simulation_steps, 100, measure_block_time=False)
    exc_avg_tar = np.mean((e_ng['IPTI'][0].min_th + e_ng['IPTI'][0].max_th) / 2)
    inh_avg_tar = inh_target_act#exc_avg_tar*2#inh_target_act  # 0.017
    exc_avg = np.mean(np.array(e_ng['n.output', 0])[-evaluation_steps:], axis=1)
    inh_avg = np.mean(np.array(i_ng['n.output', 0])[-evaluation_steps:], axis=1)
    exc_score = np.power(np.sum(np.abs(exc_avg - exc_avg_tar)), 2)
    inh_score = np.power(np.sum(np.abs(inh_avg - inh_avg_tar)), 2)

    print(exc_score, inh_score/20)
    score1 = -(exc_score + inh_score/20)

    SORN_Global.deactivate_mechanisms('STDP')

    SORN_Global.simulate_iterations(simulation_steps, 100, measure_block_time=False)
    exc_avg_tar = np.mean((e_ng['IPTI'][0].min_th + e_ng['IPTI'][0].max_th) / 2)
    inh_avg_tar = exc_avg_tar#inh_target_act  # 0.017
    exc_avg = np.mean(np.array(e_ng['n.output', 0])[-evaluation_steps:], axis=1)
    inh_avg = np.mean(np.array(i_ng['n.output', 0])[-evaluation_steps:], axis=1)
    exc_score = np.power(np.sum(np.abs(exc_avg - exc_avg_tar)), 2)
    inh_score = np.power(np.sum(np.abs(inh_avg - inh_avg_tar)), 2)

    score2 = -(exc_score + inh_score)

    return score1+score2



def getXY(output_recorders, out_param_name, input_recorder, inp_param_name, start, end, XYshift=0, learn_shift=1):#todo XYshift -1 ...
    inputs = [rec[out_param_name, 0, 'np'][start+XYshift:end-learn_shift] for rec in output_recorders]
    X = np.concatenate(inputs, axis=1)
    Y = input_recorder[inp_param_name, 0, 'np'][learn_shift+start:end-XYshift].T.astype(int)
    #print(X.shape, Y.shape)
    return X, Y

def remove_lag(X, Y, lag):
    r = np.arange(len(Y))
    rx = X[(r % lag) == 0]#(lag - 1)
    ry = Y[(r % lag) == 0]#(lag - 1)
    return rx, ry

def train_same_step(output_recorders, out_param_name, input_recorders, inp_param_name, start, end):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorders, inp_param_name, start, end, XYshift=0, learn_shift=0)
    #X_train, Y_train= remove_lag(X_train, Y_train, lag)
    if sys.version_info[1]>5:#3.5...
        lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
    else:
        lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    return lg.fit(X_train, Y_train)

def train(output_recorders, out_param_name, input_recorder, inp_param_name, start, end, lag=1):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorder, inp_param_name, start, end, XYshift=lag-1, learn_shift=lag)
    X_train, Y_train= remove_lag(X_train, Y_train, lag)
    if sys.version_info[1]>5:#3.5...
        lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
    else:
        lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    return lg.fit(X_train, Y_train)


def score(linear_model, input_recorders, inp_param_name, output_recorders, out_param_name, start, end):
    X_test, Y_test = getXY(input_recorders, inp_param_name, output_recorders, out_param_name, start, end)

    spec_perf = {}
    for symbol in np.unique(Y_test):
        symbol_pos = np.where(symbol == Y_test)
        spec_perf[symbol] = linear_model.score(X_test[symbol_pos], Y_test[symbol_pos])#source.index_to_symbol()

    print(spec_perf)
    s = 0
    for k in spec_perf:
        s += spec_perf[k]
    print('score:', s)
    return spec_perf


def predict_char(linear_model, input_neuron_groups, inp_param_name):
    compiled_inp_param_name=compile(inp_param_name, '<string>', 'eval')
    inputs = [eval(compiled_inp_param_name) for n in input_neuron_groups]
    return int(linear_model.predict(np.concatenate(inputs).reshape(1, -1)))


def simple_readout(neuron_group, inp_param_name, source):
    n=neuron_group
    act = eval(inp_param_name)
    u = source.W.transpose().dot(act)
    return np.argmax(u)


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

def get_evolution_score_words(SORN, steps_plastic, steps_train, steps_spont, steps_recovery=0, display=True, stdp_off=True, storage_manager=None, same_timestep_without_feedback_loop=False):
    #exc_neuron_tag, output_recorder_tag, input_recorder_tag
    #'main_exc_group', 'exc_out_rec', 'inp_rec'

    #SORN.clear_recorder()
    SORN.simulate_iterations(steps_plastic, 100, measure_block_time=display)#, disable_recording=True

    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    for ng in SORN['prediction_source']:
        SORN.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='pediction_rec')}, ng)
    for ng in SORN['text_input_group']:
        SORN.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)

    SORN.simulate_iterations(steps_train, 100, measure_block_time=display)

    if same_timestep_without_feedback_loop:
        readout_layer = train_same_step(SORN['pediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train)  # train
    else:
        readout_layer = train(SORN['pediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train, lag=1)  # steps_plastic, steps_plastic + steps_readout

    SORN.clear_recorder(['pediction_rec', 'index_rec'])
    SORN.deactivate_mechanisms(['pediction_rec', 'index_rec'])
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




'''
def get_spontaneous_grammar_score(SORN, exc_neuron_tag, output_recorder_tag, input_recorder_tag, steps_plastic, steps_train, steps_recovery, steps_spont, display=True, stdp_off=True):

    #print('plastic')
    SORN.clear_recorder()
    SORN.simulate_iterations(steps_plastic, 100, measure_block_time=display, disable_recording=True)#plastic

    if stdp_off:
        SORN.learning_off()

    #print('train')
    SORN.simulate_iterations(steps_train, 100, measure_block_time=display)
    simu_readout_classifyer = train_same_step(SORN[output_recorder_tag], 'n.output', SORN[input_recorder_tag, 0], 'n.pattern_index', 0, steps_train) #train

    #print('recovery')
    SORN['activator', 0].active = False
    SORN.simulate_iterations(steps_recovery, 100, measure_block_time=display, disable_recording=True)#activity recovery

    #print('spont')
    spont_output = get_simu_sequence(SORN, exc_neuron_tag, 'n.output', readout_classifyer=simu_readout_classifyer, seq_length=steps_spont, source=SORN['grammar_act', 0])#output generation
    SORN['activator', 0].active = True

    if stdp_off:
        SORN.learning_on()

    print(spont_output.replace(' ', '_'))
    score_dict = SORN['grammar_act', 0].get_text_score(spont_output)

    single_char_redundancy = 0
    for i in range(len(spont_output)-1):
        if spont_output[i]==spont_output[i+1]:
            single_char_redundancy+=1

    return score_dict['total_score']-(single_char_redundancy)/1000
'''


    # Step 7. Calculate parameters to save
    #score_dict = source.get_text_score(spont_output)
    #if display: print(score_dict)

    # Step 8. Save
    #storage_manager.save_param('spont_output', spont_output)
    #storage_manager.save_param_dict(score_dict)


    # Step 4. Input without plasticity: test (with STDP and IP off)
    #if display: print('\nReadout testing phase:')
    #SORN.simulate_iterations(steps_readout, 100, measure_block_time=display)

    # Step 5. Estimate SORN performance
    # if display: print('\nTesting readout layer...')
    # spec_perf = score(readout_layer, readout_recorders, 'n.x', input_recorders, 'n.pattern_index', 0, steps_readout)  # steps_plastic + steps_readout, steps_plastic + steps_readout * 2
    # SORN_Global.clear_recorder()

    #storage_manager.save_obj('avg', readout_recorders[0]['np.average(n.activity)'])
    #storage_manager.save_obj('x', readout_recorders[0]['n.output'])
