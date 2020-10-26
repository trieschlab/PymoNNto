from NetworkBehaviour.Input.Pattern_Basics import *
import random
import numpy as np
from collections import Counter
import pypianoroll as piano
import os
import re
from sklearn.feature_extraction.text import CountVectorizer
from scipy.stats import entropy
import csv
from scipy.stats import entropy
from itertools import groupby, count


#{' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'} #, 'MNAME':'Name', 'FNAME':'Name'
#CHILDES_activator = TextActivator_New(filename='CHILDES.txt', replace_dict={' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'})
#SPD_activator = TextActivator_New(filename='SPD.txt', replace_dict={'?': '.', ':': '.', ',': '.', '.': '. ', '  ': ' ', '-': ''})

class DrumBeatActivator(PatternGroup):

    def initialize(self): #
        self.last_iteration=-1
        self.nextone=None
        self.is_drum = True
        self.type = 'poly'

        self.offtoken = self.kwargs.get('offtoken', False)
        self.ontoken = self.kwargs.get('ontoken', False)
        self.include_inverse_alphabet = self.kwargs.get('include_inverse_alphabet', False)
        self.max_iterations = self.kwargs.get('max_iterations', None)
        self.filter_silence = self.kwargs.get('filter_silence', False) # false if no filter should be applied, integer for maximum allowed silent time steps


        self.beat_resolution = self.kwargs.get('beat_resolution', 4)

        self.current_index = -1
        self.seen = [] # part of corpus that has already been seen
        self.times_seen = 0 # times we have iterated through whole corpus

        self.which_tracks = self.kwargs.get('which_tracks', 'all') # read in all tracks in corpus, otherwise a list of indices
        self.distance_similar_tacks = self.kwargs.get('THR_similar_tracks', None) # define threshold for euclidean distance in 2D space to select similar tracks        

        if self.distance_similar_tacks is not None:
            assert len(self.which_tracks) == 1 # selecting similar tracks only implemented if one example track is given as input 
            
        self.path_to_music = self.kwargs.get('path_to_music', os.path.join(os.path.dirname(__file__),'..', '..','..','Data/midis/beats/'))
        self.alphabet = self.kwargs.get('instruments', [36,38,41,42,45,46,48,49,51,60,61,62,64,69]) # list of MIDI percussion indices

        self.instruments = self.get_instruments(self.path_to_music, self.alphabet) # dictionary of instruments
        self.corpus_blocks = self.get_beatmatrix(self.path_to_music, 'dataset.tsv', self.alphabet, self.which_tracks, self.max_iterations) # sequence of vectors with shape (128)

        if self.offtoken:
            self.alphabet.append(0) # STOP TOKEN
            self.instruments[0] = 'STOP'
        
        if self.ontoken:
            self.alphabet.append(1) # START TOKEN
            self.instruments[1] = 'START'

        self.corpus = self.create_corpus_from_tracks(self.corpus_blocks, self.offtoken, self.ontoken)
        #self.corpus_blocks.reshape((int(self.corpus_blocks.shape[0]*self.corpus_blocks.shape[1]), self.corpus_blocks.shape[2]))

        self.A = len(self.alphabet)
        if self.include_inverse_alphabet:
            self.A *= 2

    def create_corpus_from_tracks(self, tracks, offtoken, ontoken):
        corpus = tracks
        if offtoken:
            # we augment the corpus by a stop token 
            stop_row = np.zeros((tracks.shape[0], tracks.shape[1], 1))
            stop_row[:,-1,0] = 1
            corpus = np.concatenate((corpus, stop_row), axis=2)
        if ontoken: 
            # we augment the corpus by a start token
            start_row = np.zeros((tracks.shape[0], tracks.shape[1], 1))
            start_row[:,0,0] = 1
            corpus = np.concatenate((corpus, start_row), axis=2)

        corpus = corpus.reshape((int(corpus.shape[0]*corpus.shape[1]), corpus.shape[2])) # flatten beatmatrix

        return corpus

    def get_instruments(self, path, alphabet):
        all_instruments = {}
        with open(os.path.join(path, 'instruments.txt')) as f:
            for line in f:
                all_instruments[int(line[:2])] = line[3:-1]

        dict_instruments = {}
        for i in alphabet:
            dict_instruments[i] = all_instruments[i]

        return dict_instruments

    def get_beatmatrix(self, path, file, instruments, which_tracks='all', max_length=None):
        # creates polyphonic pianoroll of length max iterations
        dataset = []
        coordinates = []

        if which_tracks != 'all':

            # read tracks from list which_tracks
            with open(os.path.join(path, file)) as tsvfile:
                reader = csv.reader(tsvfile, delimiter='\t')
                dataset = [np.array(row[0].split(','),int) for idx, row in enumerate(reader) if idx in which_tracks]
            with open(os.path.join(path, file)) as tsvfile:
                reader = csv.reader(tsvfile, delimiter='\t')
                coordinates = [np.array(row[-1].split(','), float) for idx, row in enumerate(reader) if idx in which_tracks]

                # now choose similar tracks (with euclidian distance <= THR in 2D VAE projection)
                if self.distance_similar_tacks is not None: # select all tracks that are similar to the track in  self_which_tracks
                    with open(os.path.join(path, file)) as tsvfile:
                        reader = csv.reader(tsvfile, delimiter='\t')
                        for row in reader:
                            check = np.array(row[-1].split(','), float)
                            if np.linalg.norm(coordinates[0]-check) < self.distance_similar_tacks and np.linalg.norm(coordinates[0]-check)!=0:
                                coordinates.append(check)
                                dataset.append(np.array(row[0].split(','), int))
        else: # load all tracks 
            with open(os.path.join(path, file)) as tsvfile:
                reader = csv.reader(tsvfile, delimiter='\t')
                for row in reader:
                    dataset.append(np.array(row[0].split(','),int))
                    coordinates.append(np.array(row[-1].split(','), float))

        dataset = np.array(dataset)
        coordinates = np.array(coordinates)

        #if which_tracks is not 'all':
        #    dataset = dataset[which_tracks,:]

        if max_length is not None: 
            if max_length < dataset.shape[0]*dataset.shape[1]:
                n_rows = int(max_length/dataset.shape[1]) # we only take full tracks 
                dataset = dataset[:n_rows, :]

        if self.filter_silence: 
            # remove tracks that have longer silence than specified by self.filter_silence
            dataset = self.filter_tracks_by_max_silence(dataset, self.filter_silence)

        print(len(dataset), 'tracks')
        

        # now we create the matrix from the bit strings (each row in dataset is a matrix)
        beat_matrices = np.zeros((dataset.shape[0], dataset.shape[1], 14), bool)

        for i, row in enumerate(dataset):
            for j in range(len(row)):
                binary_string = np.binary_repr(dataset[i,j], width=len(instruments))
                # now populate the matrix
                for k, letter in enumerate(binary_string):
                    if int(letter):
                        beat_matrices[i, j, -k] = True

        return beat_matrices
        
    def get_instrument_input_statistics_list(self):
        stats = [len(np.nonzero(self.corpus[:,i])[0]) for i in range(len(self.alphabet))]
        stats = np.array(stats)
        if self.include_inverse_alphabet: # append the frequencies with which symbols do not occur
            inverse_symbols = np.repeat(len(self.corpus), len(stats)) - stats
            stats = np.concatenate((stats, inverse_symbols))        
        return stats


    #def get_alphabet_length(self):
    #    return len(self.alphabet)

    def generate_weights(self, neurons):
        if hasattr(neurons, 'input_density'):
            density = neurons.input_density
        else:
            density = self.kwargs.get('input_density', 1/60)#int(output_size / 60)

        output_size = neurons.size
        #output_size = self.kwargs.get('output_size', 600)
        # self.kwargs.get('activation_size', int(output_size / 60))

        A = self.A

        self.activation_size = int(output_size * density)

        neurons.Input_Weights = np.zeros((output_size, A))
        available = set(range(output_size))
        for a in range(A):
            temp = random.sample(available, self.activation_size)
            neurons.Input_Weights[temp, a] = 1
            available = set([n for n in available if n not in temp])
            assert len(available) > 0, 'Input alphabet too big for non-overlapping neurons'

        neurons.Input_Mask = (np.sum(neurons.Input_Weights, axis=1) > 0)
        neurons.mean_network_input_activity=self.activation_size/output_size

    def get_pattern(self, neurons): 
        if self.active:
            n_hot = self.get_next(next=neurons.iteration != self.last_iteration)
            self.last_iteration=neurons.iteration
            self.current_pattern_index = n_hot #for pattern activator   --> how does this work if my pattern is more than one symbol at a time?
            return self.get_activation(n_hot, neurons) #self.W[:, i]
        else:
            return None

    def initialize_neuron_group(self, neurons):
        #if not hasattr(neurons, 'Input_Weights'):
        self.generate_weights(neurons)

    
    def albphabet_index_to_note_symbol(self, index):
        """
        Convert an alphabet index (from the network) to the corresponding note string

        Arguments:
        index -- int, alphabet index

        Returns:
        symbol -- string corresponding to note
        """

        # first get the MIDI index
        midi = self.alphabet[index]
        return self.instruments[midi]

    
    def midi_index_to_alphabet_index(self, midi):
        '''
        looks for the MIDI index in the alphabet of the SORN and returns its index in the alphabet

        Arguments:
        midi -- int, a MIDI index

        Returns:
        index -- int, an index to index the networks alphabet
        '''
        return self.alphabet.index(midi)

    def convert_sequence_to_pianoroll(self, sequence):
        'conerts a sequence of MIDI indices to a pianoroll'
        pianoroll = np.zeros((len(sequence), 128)).astype(np.bool_)
        alphabet = self.alphabet
        if self.ontoken:
            alphabet = np.setdiff1d(alphabet, 1)
        if self.offtoken:
            alphabet = np.setdiff1d(alphabet, 0)
        pianoroll[:, alphabet] = sequence
        return pianoroll

    def set_nextone(self, vec):
        'sets next vector'
        self.nextone = vec


    def get_next(self, next=False):
        if next:
            self.current_index += 1

        # in case the sequence ends, restart it
        if self.current_index == len(self.corpus):
            self.current_index = 0
            self.times_seen+=1

        if self.nextone is not None:#outside activation
            self.corpus[self.current_index,:] = self.nextone

            self.nextone=None
        
        if next:
            self.seen.append(self.corpus[self.current_index,:].astype(bool))

            # corpus is already sequence of n-hot arrays, we do not need to convert it

        next_vector = self.corpus[self.current_index,:].astype(bool)

        if self.include_inverse_alphabet: 
            next_vector = np.concatenate((next_vector, np.invert(next_vector)))

        return next_vector
        #return self.corpus[self.current_index,:].astype(bool)

    def get_activation(self, n_hot, neurons):
        if not np.any(n_hot):
            return np.zeros(neurons.Input_Weights.shape[0]).astype(bool) # return a vector of zeros
        else:
            vector = np.zeros(neurons.Input_Weights.shape[0])
            indices = np.where(n_hot == 1)[0]
            for i in indices:
                vector += neurons.Input_Weights[:,i]
            return vector.astype(bool)
            #return neurons.Input_Weights[:,n_hot]
            #return neurons.Input_Weights * mask

    def get_music_score(self, spont_output, pianoroll, seen=None):
        result = {}

        output = spont_output[:-1]
        output=output.split(' ')

        print(set(np.nonzero(np.array(self.seen)[:len(self.seen)-len(output),:])[1]))

        if seen is None: # no network output sequence was given
            seen = self.seen[:len(self.seen)-len(output)] # the last n time steps it gets fed in the previous spontaneous output: that's not comparable between experiments

        seen_string = ''
        for i in range(len(seen)-len(output)): # the last n time steps it gets fed in the previous spontaneous output: that's not comparable between experiments
            if np.any(seen[i]): # vector is not all zeros
                indices = np.nonzero(seen[i])[0]
                if len(indices)==1: # predict only one note at this time step
                    note = self.albphabet_index_to_note_symbol(indices[0])
                    seen_string += note+' '
                else:
                    for j in indices:
                        note = self.albphabet_index_to_note_symbol(j)
                        seen_string += note
                    seen_string += ' '
            else:
                seen_string += '_ ' # silence

        seen_string = seen_string.split(' ')
        seen_string = seen_string[:-1]

        #result['seen_string']=seen_string
        result['times_seen'] = self.times_seen
        result['spont_output'] = spont_output
        result['output_beatmatrix'] = pianoroll

        # compute per track entropy and mean length
        if self.ontoken or self.offtoken:
            tracks = self.create_beat_matrix_from_results(pianoroll, self.offtoken, self.ontoken)
            result['track_length'] = self.compute_per_track_length(tracks)
            result['track_entropy'] = self.compute_per_track_entropy(tracks)
            print('mean per track entropy:', np.mean(result['track_entropy']), 'std:', np.std(result['track_entropy']))
            print('mean track length:', np.mean(result['track_length']), 'std:', np.std(result['track_length']))

        #result['seen_beatmatrix'] = seen
        result['alphabet'] = self.alphabet
        result['total_score']=0

        # compare frequencies of notes 

        # make a list of all possible notes 
        indices_non_zero = np.nonzero(pianoroll)
        number_note_played = {}
        number_note_seen = {}

        indices_non_zero_seen = np.nonzero(np.array(seen))

        for note in set(indices_non_zero_seen[1]): # can't take alphabet bc perhaps it has not seen all of corpus
            number_note_played[self.albphabet_index_to_note_symbol(note)] = len(indices_non_zero[0][np.where(indices_non_zero[1]==note)])
            number_note_seen[self.albphabet_index_to_note_symbol(note)] = len(indices_non_zero_seen[0][np.where(indices_non_zero_seen[1]==note)])

        number_note_seen['_'] = len(set(range(len(seen))) - set(indices_non_zero_seen[0]))
        number_note_played['_'] = len(set(range(len(pianoroll))) - set(indices_non_zero[0]))

        sorted_notes = [x[0] for x in sorted(number_note_seen.items(), key=lambda kv: kv[1], reverse=True)]
        freq_input = np.array([number_note_seen[x] for x in sorted_notes])
        freq_input = freq_input/freq_input.sum()

        result['input_frequencies'] = inp = dict(zip(sorted_notes, freq_input))
        result['sorted_symbols'] = sorted_notes

        freq_output = np.array([number_note_played[x] for x in sorted_notes])
        freq_output = freq_output/freq_output.sum()

        result['output_frequencies'] = out = dict(zip(sorted_notes, freq_output))

        result['diff_frequencies'] = diff = {x: abs(inp[x] - out[x]) for x in inp if x in out}

        result['sum_differences'] = sum_diff = sum(diff.values())

        result['total_score'] -= sum_diff

        # Now we look at the frequencies of chords

        times_seen_chords = {}
        notes_in_chords = {}
        for ts in range(len(seen_string)):
            if len(np.where(seen[ts])[0])>1: # only a chord if more than one note is played at the same time
                chord = seen_string[ts]
                if chord in times_seen_chords:
                    times_seen_chords[chord] +=1
                else:
                    notes_in_chords[chord] = np.where(seen[ts])[0] # how many notes are in this chord?
                    times_seen_chords[chord] = 1
          
        times_output_chords = {}

        for ts in range(len(pianoroll)):
            if len(np.where(pianoroll[ts])[0])>1:
                chord = output[ts]
                if chord in times_output_chords:
                    times_output_chords[chord] += 1
                else:
                    times_output_chords[chord] = 1
                if chord not in notes_in_chords:
                    notes_in_chords[chord] = np.where(pianoroll[ts][0])

        sorted_chords = [x[0] for x in sorted(times_seen_chords.items(), key=lambda kv: kv[1], reverse=True)]
        freq_input = np.array([times_seen_chords[x] for x in sorted_chords])
        freq_input = freq_input/freq_input.sum()

        result['input_frequencies_chords'] = inp = dict(zip(sorted_chords, freq_input))
        result['sorted_chords'] = sorted_chords

        freq_output = np.zeros(len(sorted_chords))
        for i, chord in enumerate(sorted_chords):
            if chord in times_output_chords:
                freq_output[i] = times_output_chords[chord]

        #freq_output = np.array([times_output_chords[x] for x in sorted_chords])
        freq_output = freq_output/freq_output.sum()

        result['output_frequencies_chords'] = out = dict(zip(sorted_chords, freq_output))
        result['midi_indices_per_chord'] = notes_in_chords
        result['n_notes_per_chord'] = len(notes_in_chords)

        # differences in frequencies
        # punish less if it gets frequencies of chords (compared to notes overall)
        result['diff_frequencies_chords'] = diff = {x: abs(inp[x] - out[x]) for x in inp if x in out}

        sum_diff = 0
        
        for key in diff: # punish less if it gets frequencies of higher n_grams wrong
            sum_diff += diff[key]/len(notes_in_chords[key]) # weighted by number of notes in a chord
        result['sum_differences_chords'] = sum_diff

        result['total_score'] -= sum_diff 

        #output frequencies for all output chords (also ones that do not appear in input)
        sorted_chords = [x[0] for x in sorted(times_output_chords.items(), key=lambda kv: kv[1], reverse=True)]
        freq_output = np.array([times_output_chords[x] for x in sorted_chords])
        freq_output = freq_output/freq_output.sum()

        result['sorted_chords_output_all'] = sorted_notes
        result['output_frequencies_chords_all'] = freq_output

        return result

    def get_entropy_of_track(self, pianoroll):
        alphabet = self.alphabet()
        indices_non_zero = pianoroll.nonzero()
        distribution = np.zeros(len(alphabet))
        for i in range(len(alphabet)):
            distribution[i] = sum(indices_non_zero[1] == alphabet[i])
        # add the silent time steps
        non_zero_indices = set(range(indices_non_zero[0]))
        all_indices = set(range(len(pianoroll)))
        silent_indices = all_indices - non_zero_indices
        distribution=np.append(distribution, len(silent_indices))
    
        return entropy(distribution)

    def create_beat_matrix_from_results(self, beat_matrix, offtoken=True, ontoken=False):
        #TODO: need to check that indexing is safe if start/stop tokens occur at first/last time step of output

        if offtoken and ontoken:
            # last row stands for start token, row before for stop token
            indices_start = np.nonzero(beat_matrix[:,-1])[0]
            indices_stop = np.nonzero(beat_matrix[:,-2])[0]

        elif offtoken and not ontoken: # we only have offtokens, but we start at first generated time step
            indices_stop = np.nonzero(beat_matrix[:,-1])[0]
            indices_start = indices_stop+1

        elif ontoken and not offtoken:
            indices_start = np.nonzero(beat_matrix[:,-1])[0]
            indices_stop = indices_start-1

        indices_start = indices_start[:-1] # remove last start token, it does not have a corresponding stop token
        indices_stop = indices_stop[1:] # remove first stop token, it does not have a corresponding start token

        tracks = []
        if len(indices_start) >0 and len(indices_stop)>0:
            assert [indices_stop[i] > indices_start[i] for i in range(len(indices_start))]

            for i in range(len(indices_start)):
                tracks.append(beat_matrix[indices_start[i]:indices_stop[i]+1,:14])
        
        else:# return whole matrix, we just have one track, it never predicted start/stop
            tracks.append(beat_matrix[:,:14])
        
        return np.array(tracks) 


    def get_percussion_track_entropy(self, track, len_alphabet=14, include_silence=False):
        distribution = np.zeros(len_alphabet)
        indices_non_zero = track.nonzero()
        for i in range(len_alphabet):
            distribution[i] = sum(indices_non_zero[1] == i)
        if include_silence:
        # add the silent time steps (when no note is played)
            non_zero_indices = set(indices_non_zero[0])
            all_indices = set(range(len(track)))
            silent_indices = all_indices - non_zero_indices
            distribution = np.append(distribution, len(silent_indices))

        return entropy(distribution)

    def compute_per_track_entropy(self, tracks, include_silence=False):
            '''
            return a list of per track entropies
            expects a beat matrix of shape (n_tracks, len_alphabet)
            '''
            entropy_generated_tracks = []

            if len(tracks)==1:
                entropy_generated_tracks = self.get_percussion_track_entropy(tracks, tracks.shape[1], include_silence = include_silence)

            else:
                for i in range(len(tracks)):
                    entropy_generated_tracks.append(self.get_percussion_track_entropy(tracks[i], tracks[i].shape[1], include_silence=include_silence))

            return entropy_generated_tracks

    def compute_per_track_length(self, tracks):
        '''
        returns a list of track lengths
        expects a beat matrix of shape (n_tracks, len_alphabet)
        '''
        return [len(i) for i in tracks]

    def find_length_longest_silence(self, track):
        '''
        given a beat_matrix (shape ts, instruments),
        returns the length of the longest silence,
        i.e. consecutive time steps where no instrument is played.
        '''
        silent_ts = [t for t in range(len(track)) if not np.any(track[t])]
        if silent_ts:
            c = count()
            val = max((list(g) for _, g in groupby(silent_ts, lambda x: x-next(c))), key=len)
            return len(val)
        else:
            return 0

    def filter_tracks_by_max_silence(self, corpus, max_silence=2):
        '''
        filters a corpus (of beatmatrices) by removing tracks that have
        more time steps of silence than specified by max_silence.
        '''
        filtered_corpus = [track for track in corpus if self.find_length_longest_silence(track)<=max_silence]
        return np.array(filtered_corpus)