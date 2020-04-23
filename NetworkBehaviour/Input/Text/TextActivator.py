from NetworkBehaviour.Input.Pattern_Basics import *
import random
import numpy as np
from collections import Counter

#{' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'} #, 'MNAME':'Name', 'FNAME':'Name'
#CHILDES_activator = TextActivator_New(filename='CHILDES.txt', replace_dict={' PERIOD': '.', ' COMMA': '.', ' QUESTION': '.'})
#SPD_activator = TextActivator_New(filename='SPD.txt', replace_dict={'?': '.', ':': '.', ',': '.', '.': '. ', '  ': ' ', '-': ''})




class TextActivator_New(PatternGroup):

    def get_unique_block_text(self):
        return ' '.join(self.corpus_blocks)

    def build_sentences_recurrent(self, string, blocks, result):
        if len(blocks) > 0:
            words = blocks.pop(0)
            if len(words) is 0:
                self.build_sentences_recurrent(string, blocks.copy(), result)
            else:
                for word in words:
                    if word == '':
                        self.build_sentences_recurrent(string, blocks.copy(), result)
                    else:
                        self.build_sentences_recurrent(string + ' ' + word, blocks.copy(), result)
        else:
            return result.append(string)

    def get_char_input_statistics_dict(self):
        result = {}
        for sentence in self.corpus_blocks:
            for c in sentence:
                result[c] += 1
        return result

    def get_char_input_statistics_list(self):
        result = np.zeros(self.get_alphabet_length())
        for sentence in self.corpus_blocks:
            for c in sentence:
                result[self.char_to_index(c)] += 1
        return result

    def plot_char_input_statistics(self):
        import matplotlib.pyplot as plt

        result = self.get_char_input_statistics_list()

        objects = list(self.alphabet)
        y_pos = np.arange(len(objects))

        plt.barh(y_pos, result, align='center', alpha=0.5)
        plt.yticks(y_pos, objects)
        plt.show()
        return self

    #def get_activation_list(self):
    #    return dict([(char, source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])

    def build_sentences_from_sentence_bilding_blocks(self, blocks):
        result=[]
        for sentence in blocks:
            self.build_sentences_recurrent('', sentence, result)
        return result

    def initialize(self):
        self.last_iteration=-1
        self.nextchar=None

        self.max_iterations = self.kwargs.get('max_iterations', None)
        self.random_blocks = self.kwargs.get('random_blocks', True)

        self.corpus = self.get_input_string()
        self.corpus = self.corpus.lower()

        self.corpus_blocks = self.get_text_blocks()

        ut = self.get_unique_block_text()
        self.alphabet = ''.join(sorted(set(ut)))
        self.words = list(sorted(set(self.split_text_into_words(ut))))

        self.current_index = -1
        self.blockcount = -1
        #self.W = self.generate_connection_e()
        #self.Input_Weight_Dict={}
        #self.input_mask=(np.sum(self.W, axis=1)>0)

        if self.kwargs.get('random_blocks', True):
            self.corpus = []

    def load_from_file(self, filename, replace_dict={}):
        data = open(filename, "r").read()
        data = data.replace('\r\n', '').replace('\r', '').replace('\n', '')
        for key in replace_dict:
            data = data.replace(key, replace_dict[key])
        return data

    def get_input_string(self):#overrride
        filename = self.kwargs.get('filename', None)
        replace_dict = self.kwargs.get('replace_dict', {})
        if filename is not None:
            return self.load_from_file(filename, replace_dict)[0:self.max_iterations]
        else:
            return self.kwargs.get('input_string', '')[0:self.max_iterations]

    def get_text_blocks(self):#override
        return self.split_text_into_sentences(self.corpus)#np.unique()#list(sorted(set()))

    def split_text_into_sentences(self, text):
        return [sentence + '.' for sentence in text.split('.')]

    def split_text_into_words(self, sentence):
        return [word for word in sentence.replace('.', ' ').replace(',', ' ').replace('?', ' ').replace('!', ' ').split(' ') if word!='']


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
        neurons.add_tag('text_input_group')

    def index_to_char(self, index):
        return self.alphabet[index]

    def char_to_index(self, char):
        return self.alphabet.find(char)

    def get_next_block(self):
        self.blockcount += 1
        if self.blockcount == len(self.corpus_blocks):
            self.blockcount = 0

        if self.random_blocks:
            return random.choice(self.corpus_blocks)
        else:
            return self.corpus_blocks[self.blockcount]

    def set_next_char(self, char):
        self.nextchar=char

    def get_char(self, next=False):

        if next:
            self.current_index += 1

        if self.max_iterations is not None and self.current_index % self.max_iterations == 0:
            self.current_index = 0

        if self.current_index >= len(self.corpus):
            self.corpus += self.get_next_block()

        if self.nextchar is not None:#outside activation
            self.corpus[self.current_index] = self.nextchar
            self.nextchar=None

        return self.corpus[self.current_index]

    def get_alphabet_length(self):
        return len(self.alphabet)

    def initialize_neuron_group(self, neurons):
        #if not hasattr(neurons, 'Input_Weights'):
        self.generate_weights(neurons)

    def get_activation(self, char_indx, neurons):
        return neurons.Input_Weights[:, char_indx]

    def get_pattern(self, neurons):
        if self.active:
            c = self.get_char(next=neurons.iteration != self.last_iteration)
            self.last_iteration=neurons.iteration
            i = self.char_to_index(c)
            self.current_pattern_index = i #for pattern activator
            return self.get_activation(i, neurons) #self.W[:, i]
        else:
            return None

    def get_text_score(self, spont_output):
        result = {}
        result['output_text'] = spont_output

        #store char transitions
        result['n_different_transitions'] = 0
        for i in range(len(spont_output) - 1):
            if spont_output[i] != spont_output[i + 1]:
                result['n_different_transitions'] += 1

        if (len(spont_output) - 1)>0:
            result['%_different_transitions'] = result['n_different_transitions']/(len(spont_output) - 1)
        else:
            result['%_different_transitions'] = 0.0

        #words and sentences
        output_sentences = self.split_text_into_sentences(spont_output)
        if len(output_sentences)>2:
            output_sentences=output_sentences[1:-1]

        result['n_output_sentences'] = len(output_sentences)
        result['n_wrong_sentences'] = 0
        result['n_new_sentences'] = 0
        result['n_right_sentences'] = 0
        result['n_words'] = 0
        result['n_wrong_words'] = 0

        result['right_words'] = {}
        result['right_sentences'] = {}
        result['new_sentences'] = {}
        result['unique_sentences'] = {}
        result['wrong_sentences'] = {}

        def add_to_dict(d, key):
            if key not in d:
                d[key] = 1
            else:
                d[key] += 1

        for sentence in output_sentences:

            add_to_dict(result['unique_sentences'], sentence)

            words_in_sentence = self.split_text_into_words(sentence)
            result['n_words'] += len(words_in_sentence)

            wrong = False
            for word in words_in_sentence:
                if word not in self.words:
                    wrong = True
                    result['n_wrong_words'] += 1
                else:
                    add_to_dict(result['right_words'], word)

            if sentence not in self.corpus_blocks:
                if not wrong:
                    result['n_new_sentences'] += 1
                    add_to_dict(result['new_sentences'], sentence)
                else:
                    result['n_wrong_sentences'] += 1
                    add_to_dict(result['wrong_sentences'], sentence)
            else:
                result['n_right_sentences'] += 1
                add_to_dict(result['right_sentences'], sentence)

        result['n_right_words'] = result['n_words'] - result['n_wrong_words']

        if result['n_words'] > 0:
            result['%_right_words'] = result['n_right_words'] / result['n_words']
            result['%_wrong_words'] = result['n_wrong_words'] / result['n_words']
        else:
            result['%_right_words'] = 0.0
            result['%_wrong_words'] = 1.0

        def square_score(count_list):
            count_list=np.array(count_list)
            np.sum(np.sqrt(w_counts)) / len(self.words) / 10

        w_counts = np.array(list(result['right_words'].values()))
        result['right_word_square_score'] = np.sum(np.sqrt(w_counts))/len(self.words)/10

        rs_counts = np.array(list(result['right_sentences'].values()))
        result['right_sentences_square_score'] = np.sum(np.sqrt(rs_counts))/len(self.corpus_blocks)/10

        ns_count = np.array(list(result['new_sentences'].values()))
        result['new_sentences_square_score'] = np.sum(np.sqrt(ns_count))/len(self.corpus_blocks)/10

        result['total_score'] = (result['%_different_transitions'] + result['right_word_square_score'] + result['right_sentences_square_score'])/3

        #with open('obj/'+ name + '.pkl', 'wb') as f:
        #    pickle.dump(result, f, pickle.HIGHEST_PROTOCOL)

        return result


    def print_test(self, length=1000):
        temp = self.current_index
        t = ''
        for i in range(length):
            t += self.get_char(True)
        print(t)
        self.current_index = temp
        return self



class FDTGrammarActivator_New(TextActivator_New):

    def get_text_blocks(self):

        self.steps_plastic=self.kwargs.get('steps_plastic', 1000)
        n_removed_sentences=self.kwargs.get('n_removed_sentences', 8)


        self.verbs = ['eats ',
                      'drinks ']

        self.subjects = [' man ',
                         ' woman ',
                         ' girl ',
                         ' boy ',
                         ' child ',
                         ' cat ',
                         ' dog ',
                         ' fox ']

        self.objects_eat = ['meat.',
                            'bread.',
                            'fish.',
                            'vegetables.']

        self.objects_drink = ['milk.',
                              'water.',
                              'juice.',
                              'tea.']

        self.objects = [self.objects_eat, self.objects_drink]

        # create a huge list with all input sentences
        partial_input_string = []
        for _ in range(self.steps_plastic):
            # create a lot of sentences!
            sub = random.choice(self.subjects)
            ver = random.choice(self.verbs)
            if ver == self.verbs[0]:
                obj = random.choice(self.objects_eat)
            elif ver == self.verbs[1]:
                obj = random.choice(self.objects_drink)
            partial_input_string.append((sub + ver + obj).lower())

        # all unique input sentences
        self.all_sentences = np.unique(partial_input_string)

        # remove random sentences
        shuffled_unique_sentences = np.unique(partial_input_string)
        np.random.shuffle(shuffled_unique_sentences)

        # TODO: make sure all words appear at least once
        # TODO: sentences must be removed at random, but this was done in
        # the original work
        self.removed_sentences = []
        if n_removed_sentences >= 8:
            self.removed_sentences.extend([' woman drinks milk.',
                                           ' fox drinks tea.',
                                           ' cat eats vegetables.',
                                           ' girl eats meat.',
                                           ' child eats fish.',
                                           ' boy drinks juice.',
                                           ' man drinks water.',
                                           ' dog eats bread.'])
        if n_removed_sentences >= 16:
            self.removed_sentences.extend([' woman eats meat.',
                                           ' fox eats bread.',
                                           ' cat drinks tea.',
                                           ' girl drinks juice.',
                                           ' child drinks water.',
                                           ' boy eats fish.',
                                           ' man eats vegetables.',
                                           ' dog drinks milk.'])
        if n_removed_sentences >= 24:
            self.removed_sentences.extend([' woman eats vegetables.',
                                           ' fox eats fish.',
                                           ' cat drinks juice.',
                                           ' girl drinks tea.',
                                           ' child drinks milk.',
                                           ' boy eats bread.',
                                           ' man eats meat.',
                                           ' dog drinks water.'])
        if n_removed_sentences >= 32:
            self.removed_sentences.extend([' woman drinks water.',
                                           ' fox drinks juice.',
                                           ' cat eats bread.',
                                           ' girl eats fish.',
                                           ' child eats vegetables.',
                                           ' boy drinks tea.',
                                           ' man drinks milk.',
                                           ' dog eats meat.'])
        if n_removed_sentences >= 40:
            self.removed_sentences.extend([' woman drinks tea.',
                                           ' fox drinks milk.',
                                           ' cat eats meat.',
                                           ' girl eats vegetables.',
                                           ' child eats bread.',
                                           ' boy drinks water.',
                                           ' man drinks juice.',
                                           ' dog eats fish.'])
        if n_removed_sentences >= 48:
            self.removed_sentences.extend([' woman eats fish.',
                                           ' fox eats meat.',
                                           ' cat drinks milk.',
                                           ' girl drinks water.',
                                           ' child drinks juice.',
                                           ' boy eats vegetables.',
                                           ' man eats bread.',
                                           ' dog drinks tea.'])
        if n_removed_sentences >= 56:
            self.removed_sentences.extend([' woman drinks juice.',
                                           ' fox drinks water.',
                                           ' cat eats fish.',
                                           ' girl eats bread.',
                                           ' child eats meat.',
                                           ' boy drinks milk.',
                                           ' man drinks tea.',
                                           ' dog eats vegetables.'])

        input_string = [x for x in partial_input_string if x not in self.removed_sentences]
        #self.used_sentences = np.unique(input_string)
        return list(sorted(set(input_string)))

    def get_text_score_old(self, spont_output):
        result = {}
        output_sentences = self.split_text_into_sentences(spont_output)
        if len(output_sentences)>2:
            output_sentences=output_sentences[1:-1]
        # new output sentences
        new_dict = Counter([s for s in output_sentences if s in self.removed_sentences])
        result['n_new'] = sum(new_dict.values())
        # wrong output sentences
        wrong_dict = Counter([s for s in output_sentences if s not in self.all_sentences])
        result['n_wrong'] = sum(wrong_dict.values())
        return result


class LongDelayGrammar(TextActivator_New):

    def get_text_blocks(self):
        modes = self.kwargs.get('mode', ['simple'])#'a/the', 'where'

        if type(modes) is not list:
            modes = [modes]

        self.valid_sentence_blocks = []

        if 'a/the' in modes:
            start = ['a', 'the']
        else:
            start = []

        subject_forest = ['deer', 'fox', 'wolf', 'reindeer']
        subject_air = ['bird', 'raven', 'parrot']
        subject_water = ['fish', 'whale', 'dolphin']
        subject_ice = ['penguin', 'polar bear']

        if 'very simple' in modes or 'likes' in modes:
            center = ['likes']

            forest = ['forest.']
            air = ['trees.']
            water = ['sea.']
            ice = ['the ice.']

            self.valid_sentence_blocks.append([start, subject_forest, center, forest])
            self.valid_sentence_blocks.append([start, subject_air, center, air])
            self.valid_sentence_blocks.append([start, subject_water, center, water])
            self.valid_sentence_blocks.append([start, subject_ice, center, ice])

        if 'simple' in modes:
            center = ['likes', 'lives in', 'prefers']

            forest = ['forest.']
            air = ['trees.']
            water = ['sea.']
            ice = ['the ice.']

            self.valid_sentence_blocks.append([start, subject_forest, center, forest])
            self.valid_sentence_blocks.append([start, subject_air, center, air])
            self.valid_sentence_blocks.append([start, subject_water, center, water])
            self.valid_sentence_blocks.append([start, subject_ice, center, ice])

        if 'level31' in modes or 'where' in modes:
            where_center = ['is an animal that lives in the']

            where_forest = ['forest.']
            where_air = ['trees.']
            where_water = ['sea.']
            where_ice = ['ice.']

            self.valid_sentence_blocks.append([start, subject_forest, where_center, where_forest])
            self.valid_sentence_blocks.append([start, subject_air, where_center, where_air])
            self.valid_sentence_blocks.append([start, subject_water, where_center, where_water])
            self.valid_sentence_blocks.append([start, subject_ice, where_center, where_ice])

        if 'level17' in modes or 'what' in modes:
            what_center = ['is an animal that']

            what_forest = ['is well camouflaged.']
            what_air = ['flies to the air.']
            what_water = ['swims to the sea.']
            what_ice = ['likes cold weather.']

            self.valid_sentence_blocks.append([start, subject_forest, what_center, what_forest])
            self.valid_sentence_blocks.append([start, subject_air, what_center, what_air])
            self.valid_sentence_blocks.append([start, subject_water, what_center, what_water])
            self.valid_sentence_blocks.append([start, subject_ice, what_center, what_ice])

        if 'level17' in modes or 'what' in modes:
            what_center = ['is an animal that']

            what_forest = ['camouflages.']
            what_air = ['flies.']
            what_water = ['swims.']
            what_ice = ['likes cold weather.']

            self.valid_sentence_blocks.append([start, subject_forest, what_center, what_forest])
            self.valid_sentence_blocks.append([start, subject_air, what_center, what_air])
            self.valid_sentence_blocks.append([start, subject_water, what_center, what_water])
            self.valid_sentence_blocks.append([start, subject_ice, what_center, what_ice])

        all_sentences = self.build_sentences_from_sentence_bilding_blocks(self.valid_sentence_blocks)
        return all_sentences

class ComplexGrammarActivator(TextActivator_New):

    def get_text_blocks(self):

        the = ['a',
               'the',
               'a young',
               'the young',
               'some',
               '']

        human = ['man',
                 'woman',
                 'girl',
                 'boy',
                 'child']

        animal = ['cat',
                  'dog',
                  'fox']

        eat = ['eats']

        drink = ['drinks']

        sits = ['sits']

        objects_eat = ['meat',
                       'bread',
                       'fish',
                       'vegetables']

        objects_drink = ['milk',
                         'water',
                         'juice',
                         'tea']

        where_human = ['at the table',
                       'in the park',
                       'in a park',
                       'next to a park',
                       'in the kitchen',
                       'at the desk',
                       'on the desk']

        where_animal = ['next to forest',
                        'in the forest',
                        'in the park']

        additional = ['while the sun is shining',
                        'while its raining',
                        'and looks into the sky',
                        '']

        self.valid_sentence_blocks=[]


        self.valid_sentence_blocks.append([the, human, sits, where_human, additional])

        self.valid_sentence_blocks.append([the, animal, sits, where_human, additional])

        self.valid_sentence_blocks.append([the, human, eat, objects_eat, additional])
        self.valid_sentence_blocks.append([the, human, drink, objects_drink, additional])
        self.valid_sentence_blocks.append([the, animal, eat, objects_eat, additional])
        self.valid_sentence_blocks.append([the, animal, drink, objects_drink, additional])

        self.valid_sentence_blocks.append([the, human, eat, objects_eat, where_human, additional])
        self.valid_sentence_blocks.append([the, human, drink, objects_drink, where_human, additional])
        self.valid_sentence_blocks.append([the, animal, eat, objects_eat, where_animal, additional])
        self.valid_sentence_blocks.append([the, animal, drink, objects_drink, where_animal, additional])

        all_sentences = []

        self.build_sentences_from_sentence_bilding_blocks(self.valid_sentence_blocks, all_sentences)

        return all_sentences




class FDTGrammarActivator_New_shuffle(FDTGrammarActivator_New):

    def get_next_block(self):
        block=super().get_next_block()
        l = list(block)
        random.shuffle(l)
        result = ''.join(l)
        return result

class Random_Text_Activator(TextActivator_New):

    def initialize(self):
        self.alph = self.kwargs.get('alph', '. abcdefghijklmnopqrstuvwxyz')
        super().initialize()


    def get_random_char(self):
        rnd=np.random.randint(0, 25)
        return self.alph[rnd]

    def get_input_string(self):
        return self.alph

    def get_next_block(self):
        return self.get_random_char()

    #def get_text_blocks(self):

