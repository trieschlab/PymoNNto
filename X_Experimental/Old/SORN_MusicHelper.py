import pypianoroll as piano
from SORNSim.NetworkBehaviour.Recorder.Recorder import *
from Testing.Common.Classifier_Helper import *
from sklearn.multiclass import OneVsRestClassifier
from sklearn.naive_bayes import ComplementNB

def predict_note(linear_model, input_neuron_groups, inp_param_name):
    compiled_inp_param_name=compile(inp_param_name, '<string>', 'eval')
    inputs = [eval(compiled_inp_param_name) for n in input_neuron_groups]
    inputs = np.concatenate(inputs).reshape(1, -1)
    #inputs = add_bias_neuron(inputs)
    return int(linear_model.predict(inputs))

def predict_vector(linear_model, input_neuron_groups, inp_param_name):
    compiled_inp_param_name=compile(inp_param_name, '<string>', 'eval')
    inputs = [eval(compiled_inp_param_name) for n in input_neuron_groups]
    inputs = np.concatenate(inputs).reshape(1, -1)
    #inputs = add_bias_neuron(inputs)
    return linear_model.predict(inputs)  

def predict_music_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1):

    if source.type=='mono':
        return predict_scalar_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1)
    else: # polyphonic
        return predict_vector_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1)


def add_bias_neuron(X):
    return np.concatenate((X, np.ones((X.shape[0], 1))), axis=1) # add a bias neuron

def predict_vector_sequence(linear_model, prediction_neuron_groups, inp_param_name, iterations, SORN, source, lag=1):
    spont_output = ''
    symbol = None

    if source.is_drum:
        pianoroll = np.zeros((iterations, len(source.alphabet))).astype(np.bool_) # we work with the drum beat matrix
    else:
        pianoroll = np.zeros((iterations, 128)).astype(np.bool_) # we have just one instrument, directly create MIDI pianoroll 

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

            if source.is_drum: 
                pianoroll[i,:] = vector
            else:
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

def train_readout(SORN, steps_train, steps_test, source, display=True, stdp_off=True, storage_manager=None,same_timestep_without_feedback_loop=False):

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
        train_music(SORN['prediction_rec'], 'n.output', SORN['index_rec', 0], 'n.pattern_index', 0, steps_train, steps_test, source, lag=1)  # steps_plastic, steps_plastic + steps_readout

    SORN.clear_recorder()
    SORN.recording_off()

    #if stdp_off:
    #    SORN.activate_mechanisms('STDP')
    if display:
        print('\nTrain readout')


    SORN.clear_recorder(['prediction_rec', 'index_rec'])
    SORN.deactivate_mechanisms(['prediction_rec', 'index_rec'])


    return readout_layer, X_train, Y_train, X_test, Y_test

def train_music(output_recorders, out_param_name, input_recorder, inp_param_name, start, n_train, n_test, source, lag=1):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorder, inp_param_name, start, n_train, XYshift=lag-1, learn_shift=lag)
    #X_train, Y_train= remove_lag(X_train, Y_train, lag)
    #X_train = add_bias_neuron(X_train)

    X_test, Y_test = getXY(output_recorders, out_param_name, input_recorder, inp_param_name, int(start+n_train), int(start+n_train+n_test), XYshift=lag-1, learn_shift=lag)
    #X_test, Y_test = remove_lag(X_test, Y_test, lag)
    #X_test = add_bias_neuron(X_test)

    if len(Y_train.shape) == 1: # monophonic input/output, we predict one note at a time
        if sys.version_info[1]>5:#3.5...
            lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
        else:
            lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    else: # multilabel classification for polyphonic music
        if source.A > len(source.alphabet): # we have inverted alphabet as additional input (activate set of neurons when symbol is absent)
            Y_train = Y_train[:len(source.alphabet), :] # however, we only want to predict if note is present (0 vs 1)
            Y_test = Y_test[:len(source.alphabet), :]
        
        lg = OneVsRestClassifier(linear_model.LogisticRegression(solver='saga', multi_class='auto', n_jobs=-1))
        # ComplementNB classifier may be more suited for imbalanced classes, also deals with 0 counts (by Laplace smoothing)
        #lg = OneVsRestClassifier(ComplementNB())
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


def get_score_predict_next_step(SORN, source, readout_layer, X_test, Y_test, lag=1, display=True, stdp_off=True, storage_manager=None):
    # lag describes # time steps it is asked to predict in the future, from current state onwards
    if display:
        print("\nTesting prediction performance...")

    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    #SORN.clear_recorder()
    #SORN.recording_on()

    # we have monotonic input/output
    if len(Y_test.shape)==1:
        spec_perf = {}
        for symbol in np.unique(Y_test):
            symbol_pos = np.where(symbol == Y_test)
            spec_perf[source.albphabet_index_to_note_symbol(symbol)]=readout_layer.score(X_test[symbol_pos],Y_test[symbol_pos])

    #SORN.clear_recorder()
    #SORN.recording_off()
        score = spec_perf

    else: # polyphony
        score = {}
        score['accuracy'] = readout_layer.score(X_test, Y_test) # this is the accuracy, probably not a good measure for polyphonic music
        
        Y_output = readout_layer.predict(X_test)

        # compute expected frame-level accuracy (ACC)
        TP = 0
        FP = 0
        FN = 0
        for ts in range(len(Y_output)):
            for note in range(Y_output.shape[1]):
                if Y_output[ts,note] and Y_test[ts, note]:
                    TP+=1
                if Y_output[ts,note] and not Y_test[ts, note]:
                    FP+=1
                if not Y_output[ts,note] and Y_test[ts, note]:
                    FN+=1
        
        score['FP'] = FP
        score['TP'] = TP
        score['FN'] = FN
        score['ACC'] = TP / float(TP+FP+FN) #ACC: sum(TP) / (sum(TP)+ sum(FN)+ sum(FP))

    return score


def get_score_spontaneous_music(SORN, source, readout_layer, steps_spont, split_tracks=False, seen=None, steps_recovery=0, display=True, stdp_off=True, storage_manager=None, same_timestep_without_feedback_loop=False, create_MIDI=False):
    #exc_neuron_tag, output_recorder_tag, input_recorder_tag
    #'main_exc_group', 'exc_out_rec', 'inp_rec'
    
    if display:
        print('\nGenerate spontaneous output...')
    
    if stdp_off:
        SORN.deactivate_mechanisms('STDP')

    for ng in SORN['prediction_source']:
        SORN.add_behaviours_to_neuron_group({100: NeuronRecorder(['n.output'], tag='prediction_rec')}, ng)
    for ng in SORN['text_input_group']:
        SORN.add_behaviours_to_neuron_group({101: NeuronRecorder(['n.pattern_index'], tag='index_rec')}, ng)


    SORN.clear_recorder()
    SORN.recording_on()

    if same_timestep_without_feedback_loop:
        source.active = False
        if steps_recovery > 0:
            SORN.simulate_iterations(steps_recovery, 100, measure_block_time=display,disable_recording=True)
        spont_output, pianoroll = get_simu_music_sequence(SORN, SORN['prediction_source'], 'n.output', readout_classifyer=readout_layer, seq_length=steps_spont, source=source)#output generation
    else:
        spont_output, pianoroll = predict_music_sequence(readout_layer, SORN['prediction_source'], 'n.output', steps_spont, SORN, source, lag=1)

    source.active = True

    if create_MIDI and source.is_drum: # create a percussion track!
        # in this case pianoroll is a sequence of vectors of length alphabet, each letter in the alphabet stands for one instrument

        if split_tracks == False and source.offtoken == False: # create one long track
            instruments_non_zero = np.nonzero(pianoroll)
            instruments_non_zero = list(set(instruments_non_zero[1])) # for them we have to create tracks          

            tracks = []

            for i in range(len(instruments_non_zero)):
                track = np.zeros((len(pianoroll), 128))
                track[:,source.alphabet[instruments_non_zero[i]]] = pianoroll[:,instruments_non_zero[i]]
                track = piano.Track(track)
                #track.program = source.alphabet[instruments_non_zero[i]]
                track.binarize()
                track.beat_resolution=4
                track.is_drum  = True
                tracks.append(track)

            multitrack = piano.Multitrack(tracks=tracks, beat_resolution=4)

            if storage_manager is not None: 
                path = storage_manager.absolute_path
                multitrack.write(path+'sample.mid')
            else:
                multitrack.write('sample.mid')
                print('warning: no results path defined through storagemanager, MIDI will be saved in code repo')
            
        else: # create n tracks of length of input tracks (or diverse length if stop token is active)

            if source.offtoken and not source.ontoken:
                stop_tokens = np.nonzero(pianoroll[:,-1])[0] # time steps when track is finished
                if stop_tokens.size==0: # if it never predicted a stop token
                    start_tokens = [len(pianoroll)] # we just generate one long track
                else:
                    start_tokens = stop_tokens + 1 # so that indexing works

                n_tracks = int(len(start_tokens))-1
                #start_tokens = np.insert(start_tokens, 0, 0) # add first start token
                # note that we do not generate a track from the time steps potentially generated after the last stop token and before first stop token

            elif source.ontoken and not source.offtoken:
                start_tokens = np.nonzero(pianoroll[:,-1])[0] # time steps when track starts
                n_tracks = int(len(start_tokens))-1

            elif source.ontoken and source.offtoken:
                n_tracks=0
                start_tokens = []
                stop_tokens = []
                start = False
                stop = False
                for i in range(len(pianoroll)):
                    if pianoroll[i, -1]: # we have a start token
                        start=i # we also overwrite start token if two appear without a stop token in between
                        stop = False
                    if pianoroll[i, -2]: # we have a stop token
                        stop =i 

                    if stop and not start: 
                        stop = False

                    if start and stop and stop > start: 
                        start_tokens.append(start)
                        stop_tokens.append(stop)
                        n_tracks+=1 
                        start = False
                        stop = False
                    
                    if start and stop and stop <= start: 
                        start = False
                        stop = False 
                #print(start_tokens)
                #print(stop_tokens)
                # we ignore parts when two stop tokens or two start tokens occur after another

            else:  # else we split the generated output after 32 time steps each (length of one track in the corpus)
                len_track = len(source.corpus_blocks[0])
                n_tracks = int(len(pianoroll)/len_track)

            for j in range(n_tracks):
                if source.offtoken and source.ontoken: 
                    curr_pianoroll = pianoroll[start_tokens[j]:stop_tokens[j], :int(source.A-2)] # ignore last two tokens in alphabet 
                elif source.offtoken or source.ontoken:
                    curr_pianoroll = pianoroll[start_tokens[j]:start_tokens[j+1], :int(source.A-1)] # ignore last token in alphabet (stop token)
                else:    
                    curr_pianoroll = pianoroll[j*len_track:(j*len_track)+len_track,:]
                if np.any(curr_pianoroll): # only proceed if it would not be all silence
                    instruments_non_zero = np.nonzero(curr_pianoroll)
                    instruments_non_zero = list(set(instruments_non_zero[1])) # for them we have to create tracks          

                    tracks = []
                    for i in range(len(instruments_non_zero)):
                        track = np.zeros((len(curr_pianoroll), 128))
                        track[:,source.alphabet[instruments_non_zero[i]]] = curr_pianoroll[:,i]
                        track = piano.Track(track)
                        track.program = source.alphabet[instruments_non_zero[i]]
                        track.binarize()
                        track.beat_resolution=4
                        track.is_drum  = True
                        tracks.append(track)   

                    multitrack = piano.Multitrack(tracks=tracks, beat_resolution=4)
                    if storage_manager is not None: 
                        path = storage_manager.absolute_path
                        multitrack.write(path+'sample{}.mid'.format(j+1))
                    else:
                        multitrack.write('sample{}.mid'.format(j+1))
                        print('warning: no results path defined through storagemanager, MIDI will be saved in code repo')
                    
    elif create_MIDI: # we create just one MIDI track of one instrument (if we have a MusicActivator)
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

    score_dict = source.get_music_score(spont_output, pianoroll) 
    #print(score_dict)
    if storage_manager is not None:
        storage_manager.save_param_dict(score_dict)

    SORN.clear_recorder(['prediction_rec', 'index_rec'])
    SORN.deactivate_mechanisms(['prediction_rec', 'index_rec'])


    return score_dict








