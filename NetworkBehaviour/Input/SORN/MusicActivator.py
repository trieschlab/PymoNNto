from NetworkBehaviour.Input.Pattern_Basics import *
import random
import numpy as np
from collections import Counter
import pypianoroll as piano
import os
import re
from sklearn.feature_extraction.text import CountVectorizer
from scipy.stats import entropy


#{' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'} #, 'MNAME':'Name', 'FNAME':'Name'
#CHILDES_activator = TextActivator_New(filename='CHILDES.txt', replace_dict={' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'})
#SPD_activator = TextActivator_New(filename='SPD.txt', replace_dict={'?': '.', ':': '.', ',': '.', '.': '. ', '  ': ' ', '-': ''})


class MusicActivator(PatternGroup):

    def initialize(self): #
        self.last_iteration=-1
        self.nextone=None

        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] # length of octave
        self.octaves = list(range(11))

        self.max_iterations = self.kwargs.get('max_iterations', None)

        self.beat_resolution = self.kwargs.get('beat_resolution', 4)
        self.instrument = self.kwargs.get('instrument', int(1))
        self.tempo = self.kwargs.get('tempo', int(120)) # BPM

        self.which_alphabet = self.kwargs.get('which_alphabet', 'all') 
        assert self.which_alphabet in ['train', 'minmax', 'all']
        self.current_index = -1

        self.seen = [] # part of corpus that has already been seen
        self.times_seen = 0 # times we have iterated through whole corpus
        
    def midi_index_to_notestring(self, index):
        '''
        Convert MIDI index to a string of the note

        Arguments:
        index -- int, MIDI index from 0-127 or -1 for silence

        Returns:
        string -- string corresponding to a note
        '''
        if index == -1:
            note_as_string = '_'
        else:
            octave = (index // len(self.notes))-1
            assert octave in self.octaves, 'Illegal MIDI index'
            assert 0 <= index <= 127, 'Illegal MIDI index'
            note = self.notes[index % len(self.notes)]

            note_as_string = note + str(octave)

        return note_as_string

    def load_MIDI(self, path):
        multitrack = piano.parse(path)
        multitrack.trim_trailing_silence()
        multitrack.binarize()

        single_tracks = np.empty((0, 128))
        for i in range(len(multitrack.tracks)):
            singletrack = multitrack.tracks[i].pianoroll

            legal=True
            if self.type=='mono':
                # check if the shortest note is not shorter than our beat resolution
                count = 0
                for i in range(len(singletrack)-1):
                    if np.any(singletrack[i]) and not np.any(singletrack[i+1]) and count < int(multitrack.beat_resolution/self.beat_resolution):
                        legal = False
                        break
                    if np.any(singletrack[i]) and np.array_equal(singletrack[i],singletrack[i+1]) :
                        count+=1
                    else:
                        count = 0

            if legal: # shortest pitch in track is representable by our beat resolution
                downsampled_track = []
                for ts in range(0,len(singletrack)):
                    if ts%int(multitrack.beat_resolution/self.beat_resolution)==0 or not np.any(singletrack[ts]):
                        downsampled_track.append(singletrack[ts])

                '''
                # we have to find the silent time steps between two consecutive same pitches
                ts_zeros = np.squeeze(np.where(~singletrack.any(axis=1)))
                # do not consider first or last time step
                ts_zeros = ts_zeros[(ts_zeros!=0) & (ts_zeros!=len(singletrack))]
                for j in range(len(ts_zeros)):
                    # if pitch before and after silence is the same and this time step will be swallowed by downsampling
                    if np.array_equal(singletrack[ts_zeros[j]-1,:],singletrack[ts_zeros[j]+1,:]) and ts_zeros[j]%int(multitrack.beat_resolution/self.beat_resolution) and not np.any(singletrack[ts_zeros[j]]):
                        # insert silence at the corresponding position such that in downsampled array silence will occur
                        singletrack = np.insert(singletrack, int(np.round(ts_zeros[j]/int(multitrack.beat_resolution/self.beat_resolution),0)), np.zeros(128), axis=1)
                        ts_zeros+=1

                # now we downsample
                singletrack = singletrack[::int(multitrack.beat_resolution/self.beat_resolution)]
                single_tracks = np.append(single_tracks, singletrack, axis=0)
                '''
                single_tracks = np.append(single_tracks, np.array(downsampled_track), axis=0)

        #multitrack.downsample(int(multitrack.beat_resolution/self.beat_resolution)) # sample down to self_beat_resolution time steps per beat
        #multitrack.tempo = self.tempo

        #for i in range(len(multitrack.tracks)):
        #    singletrack = multitrack.tracks[i]
        #    single_tracks = np.append(single_tracks, singletrack.pianoroll, axis=0)

        # singletrack = multitrack.tracks[0]
        # return singletrack.pianoroll
        return single_tracks

    def get_alphabet_length(self):
        return len(self.alphabet)


    def generate_weights(self, neurons):

        if hasattr(neurons, 'input_density'):
            density = neurons.input_density
        else:
            density = self.kwargs.get('input_density', 1/60)#int(output_size / 60)

        output_size = neurons.size
        #output_size = self.kwargs.get('output_size', 600)
        # self.kwargs.get('activation_size', int(output_size / 60))

        A = self.get_alphabet_length()

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

    def get_dominant_key(self, pianoroll):
        assert pianoroll.shape[1] == 128
        kind = ['minor', 'major']
        max_perc = 0
        key = np.zeros(3) # base tone, minor(0)/major(1), percent
        for i in range(12):
            for j in range(2):
                curr_perc = piano.metrics.in_scale_rate(pianoroll, key=i, kind=kind[j])
                if curr_perc > max_perc:
                    max_perc = curr_perc
                    key[0] = i
                    key[1] = j
                    key[2] = curr_perc
        return {'key': [key[0], kind[int(key[1])]], 'percentage': key[2]}

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
        return self.midi_index_to_notestring(midi)


    def midi_index_to_alphabet_index(self, midi):
        '''
        looks for the MIDI index in the alphabet of the SORN and returns its index in the alphabet

        Arguments:
        midi -- int, a MIDI index

        Returns:
        index -- int, an index to index the networks alphabet
        '''
        return self.alphabet.index(midi)



class PolyphonicActivator(MusicActivator):

    def initialize(self):
        super().initialize()
        self.type = 'poly'
        self.beat_resolution = 24
        print('NO DOWNSAMPLING, NOT YET IMPLEMENTED FOR POLYPHONIC MUSIC')
        self.path_to_music = self.kwargs.get('path_to_music', os.path.join(os.path.dirname(__file__),'..', '..','..','Data/midis/polyphonic'))
        self.input_midis = self.get_MIDIpianoroll() # sequence of vectors with shape (128)
        self.alphabet = self.get_alphabet()
        self.corpus = self.get_corpus()
        self.A = len(self.alphabet)
        self.lowest_pitch = min(self.alphabet)
        self.highest_pitch = max(self.alphabet) 
        self.dominant_key = self.get_dominant_key(self.convert_sequence_to_pianoroll(self.corpus))
        self.max_iterations = len(self.corpus)

    def get_MIDIpianoroll(self):
        # creates polyphonic pianoroll of length max iterations
        corpus = np.empty((0, 128)).astype(bool)
        for i in os.listdir(self.path_to_music):
            if i.endswith('.mid') or i.endswith('.midi'):
                print(i)
                corpus = np.append(corpus, self.load_MIDI(os.path.join(self.path_to_music, i)), axis=0)
                if self.max_iterations is not None and len(corpus) > self.max_iterations:
                    corpus = corpus[:self.max_iterations]
                    # stop reading in MIDIs if max corpus size is reached
                    break
        assert np.any(corpus), 'empty corpus'
        return corpus

    def get_alphabet(self):
        if self.which_alphabet == 'minmax':
            indices_non_zero = self.input_midis.nonzero()
            alphabet = list(range(indices_non_zero[1].min(), indices_non_zero[1].max()))
            return alphabet
        elif self.which_alphabet == 'train':
            indices_non_zero = self.input_midis.nonzero()
            alphabet = sorted(set(indices_non_zero[1])) 
            return alphabet         
        elif self.which_alphabet == 'all': # use all notes on a grand piano
            return list(range(21,109)) 

    def get_corpus(self):
        return self.input_midis[:, self.alphabet]

    def convert_sequence_to_pianoroll(self, sequence):
            'conerts a sequence of MIDI indices to a pianoroll'
            pianoroll = np.zeros((len(sequence), 128)).astype(np.bool_)
            pianoroll[:, self.alphabet] = sequence
            return pianoroll

    '''
    def get_dominant_key(self, sequence=None):
        # get dominant key in corpus 
        pianoroll = self.convert_sequence_to_pianoroll(sequence)
        return super.get_dominant_key(pianoroll)
    '''
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
         
        self.seen.append(self.corpus[self.current_index,:])
        # corpus is already sequence of n-hot arrays, we do not need to convert it
        return self.corpus[self.current_index,:].astype(bool)


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

    def get_music_score(self, spont_output, pianoroll, Y_train):
        # TODO: not yet implemented
        result = {}
        result['output_text'] = spont_output
        result['total_score']=0

        return result

    def get_entropy_of_track(self, pianoroll):
        alphabet = self.get_alphabet()
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

class MonophonicActivator(MusicActivator): # convert Pianoroll from MIDI to monophonic sequence of pitches

    def initialize(self):
        super().initialize()
        self.type = 'mono'
        self.path_to_music = self.kwargs.get('path_to_music', os.path.join(os.path.dirname(__file__),'..', '..','..','Data/midis/monophonic'))
        self.input_midis = self.get_MIDIpianoroll()
        self.corpus = self.get_corpus()
        self.alphabet = self.get_alphabet()
        self.A = len(self.alphabet)
        self.lowest_pitch = min(self.alphabet)
        self.highest_pitch = max(self.alphabet)   
        print("Alphabet:", self.alphabet)
        self.dominant_key = self.get_dominant_key(self.convert_sequence_to_pianoroll(self.corpus))
        self.max_iterations = len(self.corpus)
        print(self.get_entropy_of_track(self.corpus))

    def get_MIDIpianoroll(self):
        # creates polyphonic pianoroll of length max iterations
        full_roll = np.empty((0, 128)).astype(bool)
        for i in os.listdir(self.path_to_music):
            if i.endswith('.mid') or i.endswith('.midi'):
                p_roll = self.load_MIDI(os.path.join(self.path_to_music, i))
                if np.any(p_roll) and piano.metrics.polyphonic_rate(p_roll,threshold=1) > 0: # we only work with monophonic input when we have symbolic alphabet
                    print("skip polyphonic track")
                    pass
                else:
                    full_roll = np.append(full_roll, p_roll, axis=0)
                    if self.max_iterations is not None and len(full_roll) > self.max_iterations:
                        full_roll = full_roll[:self.max_iterations]
                        # stop reading in MIDIs if max corpus size is reached
                        break
        assert np.any(full_roll), 'empty corpus'
        return full_roll                        

    def get_alphabet(self):
        if self.which_alphabet == 'train': # only the notes that also appear in training data
            return sorted(set(self.corpus))

        elif self.which_alphabet == 'minmax': # all notes between lowest and highest pitch in training data
            min_pitch = self.corpus[np.where(self.corpus > 0, self.corpus, np.inf).argmin()] # need to ignore -1
            max_pitch = self.corpus.max()
            alphabet = list(range(min_pitch, max_pitch+1))
            alphabet.append(-1) # add this for silence
            return alphabet

        elif self.which_alphabet == 'all': # all possible notes on a grand piano (MIDI IDs 21-108)
            alphabet = list(range(21,109))
            alphabet.append(-1) # add this for silence (all zeros)
            return alphabet

    def get_corpus(self):
        self.input_midis = self.input_midis[:self.max_iterations]
        sym_sequence = np.full(self.input_midis.shape[0], -1).astype(np.int8) # make a sequence of -1 (stands for silence)
        indices_non_zero = self.input_midis.nonzero() # find all time steps where a tone is played
        sym_sequence[indices_non_zero[0]] = indices_non_zero[1] # set non_zero time steps with the current index for pitch played
        corpus = np.array(sym_sequence).flatten().astype(np.int8)
        return corpus

    def set_nextone(self, midi):
        'sets next index'
        self.nextone = midi

    def get_next(self, next=False):

        if next:
            self.current_index += 1

        if self.max_iterations is not None and self.current_index % self.max_iterations == 0:
            self.current_index = 0
            self.times_seen+=1

        if self.nextone is not None:#outside activation (spontaneous phase: we feed output back in)
            self.corpus[self.current_index] = self.nextone
            self.nextone=None

        self.seen.append(self.corpus[self.current_index])

        return self.corpus[self.current_index]

    def print_test(self, length=1000):
        temp = self.current_index
        t = ''
        for i in range(length):
            c = self.corpus[i]
            t += self.index_to_symbol(c)
        print(t)
        self.current_index = temp
        return self

    def convert_sequence_to_pianoroll(self, sequence):
        '''
        converts sequence of MIDI indices to a pianoroll
        '''
        pianoroll = np.empty((len(sequence), 128)).astype(bool)
        for i in range(len(sequence)):
            index = sequence[i]
            one_hot = np.zeros(128) # make one-hot vector
            if index != -1:
                one_hot[index] = True
            pianoroll[i] = one_hot
        return pianoroll

    '''
    def get_dominant_key(self, pianoroll=None):
        if pianoroll == None:
            pianoroll = self.corpus
        proll = self.convert_sequence_to_pianoroll(pianoroll)
        return super.get_dominant_key(pianoroll=proll)
    '''
    def initialize_neuron_group(self, neurons):
        #if not hasattr(neurons, 'Input_Weights'):
        self.generate_weights(neurons)

    def get_activation(self, pitch_index, neurons):
        return neurons.Input_Weights[:, pitch_index]

    def get_pattern(self, neurons):
        if self.active:
            c = self.get_next(next=neurons.iteration != self.last_iteration)
            self.last_iteration=neurons.iteration
            i = self.midi_index_to_alphabet_index(c)
            self.current_pattern_index = i #for pattern activator
            return self.get_activation(i, neurons) #self.W[:, i]
        else:
            return None

    def get_entropy_of_track(self, sequence):
        alphabet = self.get_alphabet()
        distribution = np.zeros(len(alphabet))
        for i in range(len(alphabet)):
            distribution[i] = len(np.where(sequence ==alphabet[i])[0])
        return entropy(distribution)

    def get_music_score(self, spont_output, pianoroll, seen=None):
        result={}
        if seen is None: # no MIDI sequence was given
            seen = self.seen
        
        seen_string = []
        for i in range(len(seen)):
            seen_string.append(self.midi_index_to_notestring(seen[i]))

        result['seen']=seen_string
        result['times_seen'] = self.times_seen
        output = spont_output[:-1]
        output=output.split(' ')
        
        # n-gram frequencies
        result['total_score']=0 # this is the best possible score if there are no differences in frequencies

        for i in range(1, 4):
            input_igrams = [seen_string[j:j+i] for j in range(len(seen_string)-i+1)]  
            input_igrams = [' '.join([elem for elem in input_igrams[x]]) for x in range(len(input_igrams))]
            notes_input = Counter(input_igrams)
            sorted_notes = [x[0] for x in sorted(notes_input.items(), key=lambda kv: kv[1], reverse=True)]
            freq_input = np.array([notes_input[x] for x in sorted_notes])
            freq_input = freq_input/freq_input.sum()
            result['input_frequencies_{}'.format(i)] = inp = dict(zip(sorted_notes, freq_input))     
            result['sorted_symbols_{}'.format(i)] = sorted_notes

            output_igrams = [output[j:j+i] for j in range(len(output))]
            output_igrams = [' '.join([elem for elem in output_igrams[x]]) for x in range(len(output_igrams))]
            output_counter = Counter(output_igrams)
            freq_output = np.array([output_counter[x] for x in sorted_notes])
            freq_output = freq_output/freq_output.sum()
            result['output_frequencies_{}'.format(i)] = out = dict(zip(sorted_notes, freq_output))

            result['diff_frequencies_{}'.format(i)] = diff = {x: abs(inp[x] - out[x]) for x in inp if x in out}

            result['sum_differences_{}'.format(i)] = sum_diff = sum(diff.values())

            result['total_score'] -= sum_diff/i # punish less if it gets frequencies of higher n_grams wrong

        #store pitch transitions
        result['n_different_transitions'] = 0
        for i in range(len(spont_output) - 1):
            if spont_output[i] != spont_output[i + 1]:
                result['n_different_transitions'] += 1

        if (len(spont_output) - 1)>0:
            result['%_different_transitions'] = result['n_different_transitions']/(len(spont_output) - 1)
        else:
            result['%_different_transitions'] = 0.0
        
        result['dominant_key_output'] = self.get_dominant_key(pianoroll)

        result['dominant_key_input'] = self.get_dominant_key(self.convert_sequence_to_pianoroll(seen))
    
        return result

