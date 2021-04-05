from collections import Counter

from PymoNNto.NetworkBehaviour.Input.Old.TextActivator_old import *


class FDTGrammarActivator(TextActivator_old):

    def get_input_string(self):

        self.steps_plastic=self.kwargs.get('steps_plastic', 1000)
        n_removed_sentences=self.kwargs.get('n_removed_sentences', 8)


        self.verbs = ['eats ',
                      'drinks ']

        self.subjects = ['man ',
                         'woman ',
                         'girl ',
                         'boy ',
                         'child ',
                         'cat ',
                         'dog ',
                         'fox ']

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
            partial_input_string.append(sub + ver + obj)

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
            self.removed_sentences.extend(['woman drinks milk.',
                                           'fox drinks tea.',
                                           'cat eats vegetables.',
                                           'girl eats meat.',
                                           'child eats fish.',
                                           'boy drinks juice.',
                                           'man drinks water.',
                                           'dog eats bread.'])
        if n_removed_sentences >= 16:
            self.removed_sentences.extend(['woman eats meat.',
                                           'fox eats bread.',
                                           'cat drinks tea.',
                                           'girl drinks juice.',
                                           'child drinks water.',
                                           'boy eats fish.',
                                           'man eats vegetables.',
                                           'dog drinks milk.'])
        if n_removed_sentences >= 24:
            self.removed_sentences.extend(['woman eats vegetables.',
                                           'fox eats fish.',
                                           'cat drinks juice.',
                                           'girl drinks tea.',
                                           'child drinks milk.',
                                           'boy eats bread.',
                                           'man eats meat.',
                                           'dog drinks water.'])
        if n_removed_sentences >= 32:
            self.removed_sentences.extend(['woman drinks water.',
                                           'fox drinks juice.',
                                           'cat eats bread.',
                                           'girl eats fish.',
                                           'child eats vegetables.',
                                           'boy drinks tea.',
                                           'man drinks milk.',
                                           'dog eats meat.'])
        if n_removed_sentences >= 40:
            self.removed_sentences.extend(['woman drinks tea.',
                                           'fox drinks milk.',
                                           'cat eats meat.',
                                           'girl eats vegetables.',
                                           'child eats bread.',
                                           'boy drinks water.',
                                           'man drinks juice.',
                                           'dog eats fish.'])
        if n_removed_sentences >= 48:
            self.removed_sentences.extend(['woman eats fish.',
                                           'fox eats meat.',
                                           'cat drinks milk.',
                                           'girl drinks water.',
                                           'child drinks juice.',
                                           'boy eats vegetables.',
                                           'man eats bread.',
                                           'dog drinks tea.'])
        if n_removed_sentences >= 56:
            self.removed_sentences.extend(['woman drinks juice.',
                                           'fox drinks water.',
                                           'cat eats fish.',
                                           'girl eats bread.',
                                           'child eats meat.',
                                           'boy drinks milk.',
                                           'man drinks tea.',
                                           'dog eats vegetables.'])

        input_string = [x for x in partial_input_string if x not in self.removed_sentences]
        self.used_sentences = np.unique(input_string)
        return ' '.join(input_string)

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


class eFDTGrammarActivator(TextActivator_old):

    def get_input_string(self):

        self.steps_plastic=self.kwargs.get('steps_plastic', 1000)
        n_removed_sentences=self.kwargs.get('n_removed_sentences', 8)

        self.verbs_singular = ['eats ',
                               'drinks ']

        self.verbs_plural = ['eat ',
                             'drink ']

        self.subjects_singular = ['man ',
                                  'woman ',
                                  'girl ',
                                  'boy ',
                                  'child ',
                                  'cat ',
                                  'dog ',
                                  'fox ']

        self.subjects_plural = ['men ',
                                'women ',
                                'girls ',
                                'boys ',
                                'children ',
                                'cats ',
                                'dogs ',
                                'foxes ']

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
            temp = random.choice(['sing', 'plur'])
            if temp == 'sing':
                sub = random.choice(self.subjects_singular)
                ver = random.choice(self.verbs_singular)
                if ver == self.verbs_singular[0]:
                    obj = random.choice(self.objects_eat)
                elif ver == self.verbs_singular[1]:
                    obj = random.choice(self.objects_drink)
            elif temp == 'plur':
                sub = random.choice(self.subjects_plural)
                ver = random.choice(self.verbs_plural)
                if ver == self.verbs_plural[0]:
                    obj = random.choice(self.objects_eat)
                elif ver == self.verbs_plural[1]:
                    obj = random.choice(self.objects_drink)

            partial_input_string.append(sub + ver + obj)

        # all unique input sentences
        self.all_sentences = np.unique(partial_input_string)
        input_string = [x for x in partial_input_string]
        self.used_sentences = np.unique(input_string)
        self.removed_sentences = []

        return ' '.join(input_string)

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


class SPGrammarActivator(TextActivator_old):

    def get_input_string(self):

        self.steps_plastic=self.kwargs.get('steps_plastic', 1000)
        n_removed_sentences=self.kwargs.get('n_removed_sentences', 8)

        self.subjects_singular = ['dog ',
                                  'cat ',
                                  'pig ',
                                  'bird ',
                                  'sun ',
                                  'fish ',
                                  'wind ',
                                  'monkey ',
                                  'horse ',
                                  'lion ',
                                  'elephant ',
                                  'duck ']

        self.subjects_plural = [s[:-1] + 's ' for s in self.subjects_singular]
        self.subjects = self.subjects_singular + self.subjects_plural
        self.subjects = np.array(self.subjects)

        self.verbs_plural = ['bark.',
                             'meow.',
                             'oink.',
                             'sing.',
                             'shine.',
                             'swim.',
                             'blow.',
                             'climb.',
                             'gallop.',
                             'hunt.',
                             'toot.',
                             'quack.']

        self.verbs_singular = [s[:-1] + 's.' for s in self.verbs_plural]
        self.verbs = self.verbs_singular + self.verbs_plural
        self.verbs = np.array(self.verbs)

        # create a huge list with all input sentences
        partial_input_string = []
        for _ in range(self.steps_plastic):
            # create a lot of sentences!
            sub = random.choice(self.subjects)
            ver = self.verbs[np.where(self.subjects == sub)][0]
            partial_input_string.append(sub + ver)

        # all unique input sentences
        self.all_sentences = [s + v for s, v in zip(self.subjects_singular, self.verbs_singular)] + \
                             [s + v for s, v in zip(self.subjects_plural, self.verbs_plural)]
        input_string = [x for x in partial_input_string]
        self.used_sentences = np.unique(input_string)
        self.removed_sentences = []

        # grammatical errors
        all_combinations = [s + v for s in self.subjects_singular for v in self.verbs_singular] + \
                           [s + v for s in self.subjects_plural for v in self.verbs_plural]
        all_wrong = [s + v for s in self.subjects_singular for v in self.verbs_plural] + \
                    [s + v for s in self.subjects_plural for v in self.verbs_singular]
        self.grammatical_errors = [s + v for s, v in zip(self.subjects_singular, self.verbs_plural)] + \
                                  [s + v for s, v in zip(self.subjects_plural, self.verbs_singular)]
        self.grammatical_errors += [s for s in all_wrong if s not in self.grammatical_errors]

        # semantic errors
        self.semantic_errors = [s for s in all_combinations if s not in self.all_sentences]
        sing_errors = [s + v for s, v in zip(self.subjects_singular, self.verbs_plural)]
        plur_errors = [s + v for s, v in zip(self.subjects_plural, self.verbs_singular)]
        self.semantic_errors += [s for s in all_wrong if s not in self.semantic_errors
                                 if s not in sing_errors
                                 if s not in plur_errors]

        return ' '.join(input_string)

    def get_text_score(self, spont_output):
        result = super().get_text_score(spont_output)
        output_sentences = self.get_output_sentences(spont_output)
        # new output sentences
        new_dict = Counter([s for s in output_sentences if s in self.removed_sentences])
        result['n_new'] = sum(new_dict.values())
        # wrong output sentences
        wrong_dict = Counter([s for s in output_sentences if s not in self.all_sentences])
        result['n_wrong'] = sum(wrong_dict.values())

        gram_dict = Counter([s for s in output_sentences if s in self.grammatical_errors])
        result['n_gram'] = sum(gram_dict.values())

        sema_dict = Counter([s for s in output_sentences if s in self.semantic_errors])
        result['n_sema'] = sum(sema_dict.values())

        others_dict = Counter([s for s in output_sentences \
                               if s not in self.all_sentences \
                               if s not in self.grammatical_errors \
                               if s not in self.semantic_errors])

        result['n_others'] = sum(others_dict.values())

        return result



class Delayed_FDTGrammarActivator(FDTGrammarActivator):

    def get_input_string(self):

        delay=self.kwargs.get('delay', 1)

        inp_str = super().get_input_string()

        inp_str_2 = ''
        for c in inp_str:
            for d in range(delay):
                inp_str_2 += c

        return inp_str_2[1:]

    #def get_pattern(self):
    #    temp = super().get_pattern()
    #    print(self.corpus[self.ind])
    #    return temp