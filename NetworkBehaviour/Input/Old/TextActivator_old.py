from PymoNNto.NetworkBehaviour.Input.Pattern_Basics import *
import random


class TextActivator_old(PatternGroup):

    def load_from_file(self, filename, replace_dict={}):
        data = open(filename, "r").readlines()
        data = data.replace('\r\n', '').replace('\r', '')
        for key in replace_dict:
            data = data.replace(key, replace_dict[key])
        return data

    def get_input_string(self):
        return ' '.join(['abcdef', ''])

    def initialize(self):

        N_e = self.kwargs.get('N_e', 1600)
        N_u = self.kwargs.get('N_u', int(N_e/60))

        self.corpus = self.get_input_string()
        self.corpus = self.corpus.lower()

        self.alphabet = ''.join(sorted(set(self.corpus)))
        self.A = len(self.alphabet)  # alphabet size
        self.N_e = N_e
        self.N_u = N_u

        # letter counter
        self.ind = -1  # index in the corpus

        self.W=self.generate_connection_e()

    def generate_connection_e(self):
        """
        Generate the W_eu connection matrix. TODO: params should not be passed
        as an argument again!

        Arguments:
        params -- bunch of simulation parameters from param.py

        Returns:
        W_eu -- FullSynapticMatrix of size (N_e, A), containing 1s and 0s
        """

        # choose random, non-overlapping input neuron pools
        W = np.zeros((self.N_e, self.A))
        available = set(range(self.N_e))
        for a in range(self.A):
            temp = random.sample(available, self.N_u)
            W[temp, a] = 1
            available = set([n for n in available if n not in temp])
            assert len(available) > 0, \
                'Input alphabet too big for non-overlapping neurons'

        # always use a full synaptic matrix
        #ans = synapses.FullSynapticMatrix(params, (self.N_e, self.A))
        #ans.W = W

        return W

    def sequence_ind(self):
        """
        Return the sequence index. The index is the current position in the
        input (here, the whole corpus is considered a sequence). TODO: the names
        'ind' and 'index' are confusing, improve their names.

        Returns:
        ind -- sequence (corpus) index of the current input
        """

        ind = self.ind
        return ind

    def index_to_symbol(self, index):
        """
        Convert an alphabet index (randing from 0 to A-1) to the corresponding
        symbol.

        Arguments:
        index -- int, alphabet index (NOT to sequence index ind)

        Returns:
        symbol -- char corresponding to the alphabet index
        """

        symbol = self.alphabet[index]
        return symbol

    def next(self):
        """
        Update current index and return next symbol of the corpus, in the form
        of a one-hot array (from Christoph's implementation). TODO: this is very
        ugly, there must be a better way to do implement this.

        Returns:
        one_hot -- one-hot array of size A containing the next input symbol
        """

        self.ind += 1

        # in case the sequence ends, restart it
        # this does not really affect FDT because the corpus is much bigger
        # than the number of simulation steps.
        if self.ind == len(self.corpus):
            self.ind = 0

        #print(self.ind,len(self.corpus))

        one_hot = np.zeros(self.A)
        one_hot[self.alphabet.find(self.corpus[self.ind])] = 1
        #print(self.corpus[self.ind])
        return one_hot

    def char_index_to_one_hot(self, char_indx):
        one_hot = np.zeros(self.A).astype(def_dtype)
        one_hot[char_indx] = 1
        return self.W.dot(one_hot)

    def get_pattern(self):
        n = self.next()
        self.current_pattern_index = self.alphabet.find(self.corpus[self.ind])
        return self.W.dot(n)

    def get_output_sentences(self, spont_output):
        # (exclude first and last sentences
        # and separate sentences by '.'. Also, remove extra spaces.
        return [s[1:] + '.' for s in spont_output.split('.')][1:-1]

    def get_text_score(self, spont_output):

        result = {}

        output_sentences =self.get_output_sentences(spont_output)

        # all output sentences
        # output_dict = Counter(output_sentences)
        n_output = len(output_sentences)
        unique, counts = np.unique(output_sentences, return_counts=True)

        result['n_output'] = n_output
        result['unique'] = unique
        result['counts'] = counts

        return result


class TestTextActivator(TextActivator_old):

    def get_input_string(self):

        load_from_file()

        text=' '.join(self.spd_party_programm)
        #text = 'VORWORT ZUM WAHL-PROGRAMM FÜR DIE EUROPA-WAHL. Wir müssen zusammenhalten. Damit sind die Länder von der Europäischen Union gemeint. Die Abkürzung dafür ist EU. In der EU machen viele Länder aus Europa zusammen Politik .Dadurch geht es Europa besser. Weil wir wissen, dass wir zusammen stärker sind. Wir erreichen mehr,wenn wir zusammenarbeiten. Und uns für die gleichen Ziele einsetzen.So kann Europa auch mehr in der Welt erreichen. Und die anderen Länder von der Welt hören besser auf die EU. Wir wollen zum Beispiel das erreichen: Alle Menschen sollen gute Arbeits-Plätze haben. Jeder Mensch soll die gleichen Chancen bekommen. Und alle Menschen sollen die gleichen Rechte haben. Auch das Klima und die Umwelt kennen keine Grenzen. Das heißt: Alle Länder von der EU müssen sich darum kümmern. Alle Länder müssen das Klima und die Umwelt schützen. Das Klima hat mit dem Wetter zu tun. Klima nennt man das Wetter in einem bestimmten Gebiet. Am 26. Mai 2019 wählen die Menschen in Deutschland. Sie wählen ein neues Europäisches Parlament. Das Europäische Parlament ist eine große Gruppe von Frauen und Männern. Sie heißen Abgeordnete. Ein Parlament ist so etwas wie eine Versammlung. In dem Parlament treffen sich viele Politiker und arbeiten zusammen. Die Politiker sind aus verschiedenen Ländern von Europa. Was machen diese Frauen und Männer im Europäischen Parlament? Sie machen die Gesetze. Gesetze sind Regeln. An diese Regeln müssen sich alle Menschen in der EU halten. EU ist die Abkürzung für Europäische Union. Das ist eine Gruppe von Ländern in Europa. Deutschland gehört auch dazu. Das Europäische Parlament hat einen Präsidenten. Der Präsident ist der Chef vom Parlament. Im Europäischen Parlament sitzen 750 andere Politiker. Sie nennt man Abgeordnete. Sie kommen aus verschiedenen Ländern von Europa. Die Menschen in den Ländern haben die Abgeordneten gewählt. Deshalb sind die Abgeordneten im Europäischen Parlament. Wie viele Abgeordnete darf jedes Land wählen? Das hängt von der Größe vom Land ab. Ein Land mit wenigen Einwohnern darf nur wenige Abgeordnete wählen. Das kleine Land Malta darf 6 Abgeordnete wählen. Ein Land mit vielen Einwohnern darf viele Abgeordnete wählen. Das große Land Deutschland darf 96 Abgeordnete wählen. Die Abgeordneten kontrollieren auch die Arbeit von der Regierung von der EU. Und sie achten auf das Geld von der EU. Die Menschen in Deutschland wählen das Europäische Parlament. Sie bestimmen damit: welche Parteien Abgeordnete in das EU Parlament schicken dürfen welche Parteien mit ihren Abgeordneten Gesetze machen können. Das ist eine wichtige Wahl für Deutschland. Und für die anderen Länder in der EU. Wer darf wählen? Bei der Europa-Wahl dürfen alle Menschen aus der EU wählen. Sie müssen mindestens 18 Jahre alt sein. Wo kann ich wählen? Sie können im Wahl-Lokal wählen. Das ist ein Raum in einem Haus. Die Adresse vom Wahl-Lokal steht in einem Brief. Dieser Brief heißt Wahl-Benachrichtigung. Wer wählen darf, bekommt eine Wahl-Benachrichtigung mit der Post. Sie bekommen diesen Brief vor dem Wahl-Tag'
        text = text.replace('?', '.').replace(':', '.').replace(',', '.').replace('.', '. ').replace('  ', ' ').replace('-', '')

        text = text.split('.')
        result = ''

        for i in range(10000):
            sentence = random.choice(text)
            if not ',' in sentence and len(sentence.split(' ')) <= 5:
                result += '.' + sentence

        return result

class Alphabet_Sequence_Activator(TextActivator_old):

    def get_input_string(self):

        alphabet_size = self.kwargs.get('A', 20)
        sequence_length = self.kwargs.get('L', 10000)

        alphabet_chars = [chr(i+97) for i in range(alphabet_size)]

        text = ''
        for i in range(sequence_length):
            text += random.choice(alphabet_chars)

        return text

