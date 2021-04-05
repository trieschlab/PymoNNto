from collections import Counter
from PymoNNto.NetworkBehaviour.Input.Old.TextActivator_old import *

import random

class NewGrammarActivator(TextActivator_old):

    def get_input_string(self):

        self.steps_plastic = self.kwargs.get('steps_plastic', 1000)
        n_sentences = self.kwargs.get('n_sentences', 1000)
        removed_sentences_perc = self.kwargs.get('removed_sentences_perc', 50)

        the = ['a',
               'the']

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

        where_animal = ['next to a forest',
                        'in the forest',
                        'in the park']

        self.valid_sentence_blocks=[]
        self.valid_sentence_blocks.append([the, human, eat, objects_eat, where_human])
        self.valid_sentence_blocks.append([the, human, drink, objects_drink, where_human])
        self.valid_sentence_blocks.append([the, animal, eat, objects_eat, where_animal])
        self.valid_sentence_blocks.append([the, animal, drink, objects_drink, where_animal])

        #def build_sentence():
        #    sentence = ''
        #    block = random.choice(self.valid_sentence_blocks)
        #    for block_elem in block:
        #        sentence += ' '+random.choice(block_elem)
        #    sentence += '.'
        #    return sentence

        self.all_sentences = []

        def build_sentences_recurrent(string, blocks):
            if len(blocks) > 0:
                for word in blocks.pop(0):
                    build_sentences_recurrent(string+' '+word, blocks.copy())
            else:
                return self.all_sentences.append(string+'.')

        for sentence in self.valid_sentence_blocks:
            build_sentences_recurrent('', sentence)
        random.shuffle(self.all_sentences)

        splitpos = int(len(self.all_sentences)/100*removed_sentences_perc)
        self.removed_sentences = self.all_sentences[0:splitpos]
        self.input_sentences = self.all_sentences[splitpos:]

        input_string = [random.choice(self.input_sentences) for _ in range(n_sentences)]
        return ''.join(input_string)

    def get_text_score(self, spont_output):
        result = super().get_text_score(spont_output)
        output_sentences = self.get_output_sentences(spont_output)
        # new output sentences
        new_dict = Counter([s for s in output_sentences if s in self.removed_sentences])
        result['n_new'] = sum(new_dict.values())
        # wrong output sentences
        wrong_dict = Counter([s for s in output_sentences if s not in self.all_sentences])
        result['n_wrong'] = sum(wrong_dict.values())
        return result


#ng = NewGrammarActivator()
#print(ng.get_input_string())
