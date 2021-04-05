from PymoNNto.NetworkBehaviour.Input.Pattern_Basics import *
import random
import numpy as np
from collections import Counter
import pypianoroll as piano
import os
import re
from scipy.stats import entropy
from sklearn.feature_extraction.text import CountVectorizer



#{' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'} #, 'MNAME':'Name', 'FNAME':'Name'
#CHILDES_activator = TextActivator_New(filename='CHILDES.txt', replace_dict={' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'})
#SPD_activator = TextActivator_New(filename='SPD.txt', replace_dict={'?': '.', ':': '.', ',': '.', '.': '. ', '  ': ' ', '-': ''})


class MusicActivator(PatternGroup):

    def initialize(self): #
        self.last_iteration=-1
        self.nextone=None

        self.notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'] # length of octave
        self.octaves = list(range(11))
        self.is_drum = False
        self.max_iterations = self.kwargs.get('max_iterations', None)

        self.beat_resolution = self.kwargs.get('beat_resolution', 24)
        self.instrument = self.kwargs.get('instrument', int(1))
        self.tempo = self.kwargs.get('tempo', int(120)) # BPM

        self.which_alphabet = self.kwargs.get('which_alphabet', 'train') 
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

        if self.type=='mono':
            for i in range(len(multitrack.tracks)):
                singletrack = multitrack.tracks[i].pianoroll

                if multitrack.beat_resolution != self.beat_resolution: # we downsample
                    # check if the shortest note is not shorter than our beat resolution
                    count = 0
                    legal = True
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
                        downsampled_track.append(singletrack[0]) # first time step always in
                        for ts in range(1,len(singletrack)-1):
                            if ts%int(multitrack.beat_resolution/self.beat_resolution)==0 or not np.any(singletrack[ts]) and np.any(singletrack[ts-1]) and np.any(singletrack[ts+1]):
                                downsampled_track.append(singletrack[ts])
                        if (len(singletrack)-1)%int(multitrack.beat_resolution/self.beat_resolution) ==0 :
                            downsampled_track.append(singletrack[len(singletrack)-1]) # also consider last time step 

                        single_tracks = np.append(single_tracks, np.array(downsampled_track), axis=0)
                    else:
                        print('skip track that is not representable by desired beat resolution', self.beat_resolution)


                elif self.beat_resolution == multitrack.beat_resolution:
                    # we don't downsample because beat resolution is the same as the track
                    single_tracks = np.append(single_tracks, np.array(singletrack), axis=0)

        if self.type=='poly':
            # merge the tracks of the same instrument
            instruments= {}
            instrument = -1
            for i in range(len(multitrack.tracks)):
                if instrument != multitrack.tracks[i].program:
                    instruments[multitrack.tracks[i].program] = [i] # append track IDs to instrument
                    instrument = multitrack.tracks[i].program
                elif instrument == multitrack.tracks[i].program:
                    instruments[instrument].append(i)

            merged_tracks_per_instrument = []

            for instrument in instruments:
                merged_tracks_per_instrument.append(multitrack[instruments[instrument]].get_merged_pianoroll())

            if multitrack.beat_resolution != self.beat_resolution:
                # we want to find out if we can downsample the track
                # we need to know the shortest and longest note
                merged = multitrack.get_merged_pianoroll() # all tracks merged together

                # make a list of all possible notes 
                indices_non_zero = np.where(merged)
                alphabet = list(np.arange(21,109))
                indices_per_note = {}
                min_per_note = {}
                max_per_note = {}            

                # get indices in track where each note is played
                for note in alphabet:
                    indices_per_note[note] = indices_non_zero[0][np.where(indices_non_zero[1]==note)]
                    if indices_per_note[note].size > 0: # else the note does not appear (length 0)
                        min_per_note[note] = len(indices_per_note)
                        max_per_note[note] = 1
                        count = 1
                        for i in range(len(indices_per_note[note])-1):
                            if indices_per_note[note][i+1] == indices_per_note[note][i]+1:
                                count+=1
                            else:
                                if count < min_per_note[note]:
                                    min_per_note[note] = count
                                if count > max_per_note[note]:
                                    max_per_note[note] = count
                                count = 1

                shortest_note = int(min(min_per_note.values()))
                longest_note = int(max(max_per_note.values()))

                # get shortest possible beat resolution
                #for i in reversed(range(shortest_note)):
                #    if beat_resolution%(i+1) == 0:
                #        beat_resolution = int(beat_resolution/(i+1))
                #        break       

                # is shortest note a divisor of beat_resolution?
                if shortest_note >= int(multitrack.beat_resolution/self.beat_resolution):
                #self.beat_resolution%shortest_note ==0 and shortest_note!=1:
                    # then we down-sample
                    for track in merged_tracks_per_instrument:
                        downsampled_track = []
                        downsampled_track.append(track[0]) # first time step always in
                        for ts in range(1,len(track)-1):
                            if ts%int(multitrack.beat_resolution/self.beat_resolution)==0 or not np.any(track[ts]) and np.any(track[ts-1]) and np.any(track[ts+1]):
                                downsampled_track.append(track[ts])
                        if (len(track)-1)%int(multitrack.beat_resolution/self.beat_resolution)==0:
                            downsampled_track.append(track[len(track)-1]) # also consider last time step 

                        single_tracks = np.append(single_tracks, np.array(downsampled_track), axis=0)


            if multitrack.beat_resolution == self.beat_resolution:
                for track in merged_tracks_per_instrument:
                    single_tracks = np.append(single_tracks, np.array(track), axis=0)
            
            # else we ignore the track because it is not representable by the chosen beat resolution
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
        self.path_to_music = self.kwargs.get('path_to_music', os.path.join(os.path.dirname(__file__),'..', '..','..','Data/midis/polyphonic'))
        self.input_midis = self.get_MIDIpianoroll() # sequence of vectors with shape (128)
        self.alphabet = self.get_alphabet()
        self.corpus = self.get_corpus()
        self.A = len(self.alphabet)
        self.lowest_pitch = min(self.alphabet)
        self.highest_pitch = max(self.alphabet) 
        self.dominant_key = self.get_dominant_key(self.convert_sequence_to_pianoroll(self.corpus))
        self.max_iterations = len(self.corpus)

    def get_note_input_statistics_list(self):
        return [len(np.nonzero(self.corpus[:,i])[0]) for i in range(len(self.alphabet))]

    def get_MIDIpianoroll(self):
        # creates polyphonic pianoroll of length max iterations
        corpus = np.empty((0, 128)).astype(bool)
        for i in os.listdir(self.path_to_music):
            if i.endswith('.mid') or i.endswith('.midi'):
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
         
        if next:
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



    def get_music_score(self, spont_output, pianoroll, seen=None):
        result = {}

        output = spont_output[:-1]
        output=output.split(' ')

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

        result['seen_string']=seen_string
        result['times_seen'] = self.times_seen
        result['spont_output'] = spont_output
        result['output_pianoroll'] = pianoroll
        result['seen_pianoroll'] = seen

        result['total_score']=0

        # compare frequencies of notes 

        # make a list of all possible notes 
        indices_non_zero = np.where(pianoroll)
        number_note_played = {}
        number_note_seen = {}

        indices_non_zero_seen = np.where(seen)

        # NEED TO MAKE SURE TO COMPARE STRINGS WITH STRINGS OR NUMBERS WITH NUBMERS HERE
        for note in set(indices_non_zero_seen[1]): # can't take alphabet bc perhaps it has not seen all of corpus
            number_note_played[self.albphabet_index_to_note_symbol(note)] = len(indices_non_zero[0][np.where(indices_non_zero[1]==self.alphabet[note])])
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
        alphabet = self.get_alphabet()
        indices_non_zero = pianoroll.nonzero()
        distribution = np.zeros(len(alphabet))
        for i in range(len(alphabet)):
            distribution[i] = sum(indices_non_zero[1] == alphabet[i])
        # add the silent time steps
        non_zero_indices = set(indices_non_zero[0])
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

    def get_note_input_statistics_list(self):
        result = np.zeros(self.get_alphabet_length())
        for ts in range(len(self.corpus)):
            for index in range(len(self.alphabet)):
                if self.corpus[ts] == self.alphabet[index]:
                    result[index] +=1
        return result

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

        if next:
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

        output = spont_output[:-1]
        output=output.split(' ')

        if seen is None: # no MIDI sequence was given
            seen = self.seen
        
        seen_string = []
        for i in range(len(seen)-len(output)): # the last n time steps it gets fed in the previous spontaneous output: that's not comparable between experiments
            seen_string.append(self.midi_index_to_notestring(seen[i]))

        #result['seen']=seen_string
        result['times_seen'] = self.times_seen
        result['spont_output'] = spont_output

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