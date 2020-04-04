import pypianoroll as piano
from Testing.Common.Classifier_Helper import *
from sklearn.multiclass import OneVsRestClassifier

def predict_note(linear_model, input_neuron_groups, inp_param_name):
    compiled_inp_param_name=compile(inp_param_name, '<string>', 'eval')
    inputs = [eval(compiled_inp_param_name) for n in input_neuron_groups]
    return int(linear_model.predict(np.concatenate(inputs).reshape(1, -1)))

def predict_vector(linear_model, input_neuron_groups, inp_param_name):
    compiled_inp_param_name=compile(inp_param_name, '<string>', 'eval')
    inputs = [eval(compiled_inp_param_name) for n in input_neuron_groups]
    return linear_model.predict(np.concatenate(inputs).reshape(1, -1))  

def predict_music_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1):

    if source.type=='mono':
        return predict_scalar_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1)
    else: # polyphonic
        return predict_vector_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1)


def predict_vector_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1):
    spont_output = ''
    symbol = None
    pianoroll = np.zeros((iterations, 128)).astype(np.bool_)

    for i in range(iterations):
        vector = predict_vector(linear_model, prediction_neuron_groups, inp_param_name)
        if np.any(vector): # vector is not all zeros
            indices = np.nonzero(vector)[1]
            if len(indices)==1: # predict only one note at this time step
                note = source.albphabet_index_to_note_symbol(indices[0])
                spont_output += note+' '
            else:
                for j in indices:
                    note = source.albphabet_index_to_note_symbol(j)
                    spont_output += note
                #spont_output -= '+'
                spont_output += ' '
        else:
            spont_output += '_ ' # silence

        if vector is not None:

            source.set_nextone(vector)

            pianoroll[i, source.alphabet] = vector

        SORN.simulate_iteration()

    return spont_output, pianoroll


def predict_scalar_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1):

    spont_output = ''
    symbol = None
    pianoroll = np.zeros((iterations, 128)).astype(np.bool_)

    for i in range(iterations):

        #if input_neuron_group.iteration % input_neuron_group.iteration_lag == input_neuron_group.iteration_lag-1: #last step
        symbol = predict_note(linear_model, prediction_neuron_groups, inp_param_name)
        note = source.albphabet_index_to_note_symbol(symbol)
        spont_output += note+' '

            #spont_output2 += source.index_to_symbol(simple_readout(input_neuron_group, 'n.x_without_input', source))

        #if input_neuron_groups.iteration % input_neuron_groups.iteration_lag == 0:
        if symbol is not None:
            #u = np.zeros(source.A)
            #u[symbol] = 1
            #input_neuron_group.input = source.W.dot(u)#applied in next step (0 without lag or 1 with lag)
            
            # symbol is the alphabet index, we need to convert it to a symbol of the alphabet
            source.set_nextone(source.alphabet[symbol])
            #input_neuron_group.input += input_neuron_group.Input_Weights[:, symbol]
            
            one_hot = np.zeros(128) # make one-hot vector
            one = source.alphabet[symbol] # translate SORN index to MIDI index
            if one != -1: # if network did not predict silence
                one_hot[one] = 1
            pianoroll[i] = one_hot

        SORN.simulate_iteration()

    return spont_output, pianoroll


def get_simu_music_sequence(SORN, prediction_neuron_groups, output_param_name, readout_classifyer, seq_length, source):
    # do not feed external input back in (predict current time step)
    result=''
    pianoroll = np.zeros((seq_length, 128)).astype(np.bool_)
    for _ in range(seq_length):
        SORN.simulate_iteration()
        symbol = predict_note(readout_classifyer, prediction_neuron_groups, output_param_name)
        result += source.albphabet_index_to_note_symbol(symbol)
        if symbol is not None: 
            one_hot = np.zeros(128) # make one-hot vector
            one = source.alphabet[symbol] # translate SORN index to MIDI index
            if one != -1: # if network did not predict silence
                one_hot[one] = 1
            pianoroll[i] = one_hot   
    return result, pianoroll


def run_plastic_phase(SORN, steps_plastic, display=True, storage_manager=None):
    if display:
        print("Plastic phase...")
    SORN.clear_recorder()
    SORN.activate_mechanisms('STDP')
    SORN.simulate_iterations(steps_plastic, 100, measure_block_time=display, disable_recording=True)

    SORN.deactivate_mechanisms('STDP')
    #SORN.clear_recorder()
    #SORN.recording_off()
    return SORN

def train_readout(SORN, steps_train, steps_test, display=True, stdp_off=True, storage_manager=None,same_timestep_without_feedback_loop=False):

    if display:
        print("\nRecord predictions...")

    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    for ng in SORN['prediction_source']:
        SORN.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='prediction_rec')}, ng)
    for ng in SORN['text_input_group']:
        SORN.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)

    SORN.simulate_iterations(int(steps_train+steps_test), 100, measure_block_time=display)

    if same_timestep_without_feedback_loop:
        readout_layer,X_train, Y_train, X_test, Y_test = \
        train_same_step_music(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train, steps_test)  # train
    else:
        readout_layer,X_train, Y_train, X_test, Y_test = \
        train_music(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train, steps_test, lag=1)  # steps_plastic, steps_plastic + steps_readout

    SORN.clear_recorder()
    SORN.recording_off()

    #if stdp_off:
    #    SORN.activate_mechanisms('STDP')
    if display:
        print('\nTrain readout')


    SORN.clear_recorder(['prediction_rec', 'index_rec'])
    SORN.deactivate_mechanisms(['prediction_rec', 'index_rec'])


    return readout_layer, X_train, Y_train, X_test, Y_test

def train_music(output_recorders, out_param_name, input_recorder, inp_param_name, start, n_train, n_test, lag=1):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorder, inp_param_name, start, n_train, XYshift=lag-1, learn_shift=lag)
    #X_train, Y_train= remove_lag(X_train, Y_train, lag)
    X_test, Y_test = getXY(output_recorders, out_param_name, input_recorder, inp_param_name, int(start+n_train), int(start+n_train+n_test), XYshift=lag-1, learn_shift=lag)
    #X_test, Y_test = remove_lag(X_test, Y_test, lag)
    
    if len(Y_train.shape) == 1: # monophonic input/output, we predict one note at a time
        if sys.version_info[1]>5:#3.5...
            lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
        else:
            lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    else: # multilabel classification for polyphonic music
        lg = OneVsRestClassifier(linear_model.LogisticRegression(solver='saga', multi_class='auto'))
        # ComplementNB classifier may be more suited for imbalanced classes, also deals with 0 counts (by Laplace smoothing)
    return lg.fit(X_train, Y_train.T), X_train, Y_train.T, X_test, Y_test.T


def train_same_step_music(output_recorders, out_param_name, input_recorders, inp_param_name, start, n_train, n_test):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorders, inp_param_name, start, n_train, XYshift=0, learn_shift=0)
    if n_test>0:
        X_test, Y_test = getXY(output_recorders, out_param_name, input_recorders, inp_param_name, int(start+n_train), int(n_train+n_test), XYshift=0, learn_shift=0)
    else:
        X_test, Y_test = None, None
    #X_train, Y_train= remove_lag(X_train, Y_train, lag)
    if sys.version_info[1]>5:#3.5...
        lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
    else:
        lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    return lg.fit(X_train, Y_train), X_train, Y_train, X_test, Y_test


def get_score_predict_next_step(SORN, readout_layer, X_test, Y_test, lag=1, display=True, stdp_off=True, storage_manager=None):
    # lag describes # time steps it is asked to predict in the future, from current state onwards
    if display:
        print("\nTesting prediction performance...")

    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    source = SORN['music_act', 0]

    #SORN.clear_recorder()
    #SORN.recording_on()
    if len(Y_test.shape)==1:
        spec_perf = {}
        for symbol in np.unique(Y_test):
            symbol_pos = np.where(symbol == Y_test)
            spec_perf[source.albphabet_index_to_note_symbol(symbol)]=readout_layer.score(X_test[symbol_pos],Y_test[symbol_pos])

    #SORN.clear_recorder()
    #SORN.recording_off()

        score = spec_perf

    else:
        score= readout_layer.score(X_test, Y_test)


    return score

def get_score_spontaneous_music(SORN, readout_layer, steps_spont, seen=None, steps_recovery=0, display=True, stdp_off=True, storage_manager=None, same_timestep_without_feedback_loop=False, create_MIDI=False):
    #exc_neuron_tag, output_recorder_tag, input_recorder_tag
    #'main_exc_group', 'exc_out_rec', 'inp_rec'
    
    if display:
        print('\nGenerate spontaneous output...')
    source = SORN['music_act', 0]
    
    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    for ng in SORN['prediction_source']:
        SORN.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='prediction_rec')}, ng)
    for ng in SORN['text_input_group']:
        SORN.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)


    SORN.clear_recorder()
    SORN.recording_on()

    if same_timestep_without_feedback_loop:
        SORN['music_act', 0].active = False
        if steps_recovery > 0:
            SORN.simulate_iterations(steps_recovery, 100, measure_block_time=display,disable_recording=True)
        spont_output, pianoroll = get_simu_music_sequence(SORN, SORN['prediction_source'], 'n.output', readout_classifyer=readout_layer, seq_length=steps_spont, source=SORN['music_act', 0])#output generation
    else:
        spont_output, pianoroll = predict_music_sequence(readout_layer, SORN['prediction_source'], 'n.output', steps_spont, SORN, SORN['music_act', 0], lag=1)

    SORN['music_act', 0].active = True

    if create_MIDI:
        track = piano.Track(pianoroll)
        track.program = source.instrument
        track.binarize()
        track.beat_resolution = source.beat_resolution
        track = piano.Multitrack(tracks=[track], beat_resolution=source.beat_resolution)
        if storage_manager is not None: 
            path = storage_manager.absolute_path
            track.write(path+'sample.mid')
        else:
            track.write('sample.mid')
            print('warning: no results path defined through storagemanager, MIDI will be saved in code repo')

    #if display:
    print(spont_output)
    SORN.recording_on()

    if stdp_off:
        SORN.activate_mechanisms('STDP') 

    
    score_dict = SORN['music_act', 0].get_music_score(spont_output, pianoroll, seen) 
    #print(score_dict)
    if storage_manager is not None:
        storage_manager.save_param_dict(score_dict)

    SORN.clear_recorder(['prediction_rec', 'index_rec'])
    SORN.deactivate_mechanisms(['prediction_rec', 'index_rec'])


    return score_dict








