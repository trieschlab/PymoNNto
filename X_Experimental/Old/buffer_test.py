from NetworkBehaviour.Input.Old.GrammarTaskActivator_old import *
from Exploration.StorageManager.StorageManager import *
from Testing.Common.Classifier_Helper import *

#from NetworkBehaviour.Logic_SORN.TextActivator import *
#source = TestTextActivator(N_e=1600)





def train_from_buffer(source, iterations, buffer_length):

    #inputs = np.array([source.get_pattern() for i in range(iterations + 1)])
    inputs = np.array([source.next() for i in range(iterations+1)])
    buffer_states = []
    labels = []
    for i in range(iterations-buffer_length):
        buffer_states.append(inputs[i:i+buffer_length].flatten())
        #labels.append(np.argmax(source.W.transpose().dot(inputs[i + buffer_length])))
        labels.append(np.argmax(inputs[i+buffer_length]))

    buffer_states = np.array(buffer_states)
    labels = np.array(labels)
    lg = linear_model.LogisticRegression()
    reg = lg.fit(buffer_states, labels.T.astype(int))

    spont_out = ''
    buf = buffer_states[-1]

    for i in range(10000):
        prediction = int(reg.predict(buf.reshape(1, -1)))
        spont_out += source.index_to_symbol(prediction)
        one_hot = np.zeros(source.A)
        one_hot[prediction] = 1
        #one_hot = source.W.dot(one_hot)
        buf = np.roll(buf, len(source.alphabet)*-1)
        buf[len(buf)-len(one_hot):len(buf)] = one_hot

    print(spont_out)
    return reg, spont_out
















for i in range(10):
    for s in [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]:
        size = s*100
        source = FDTGrammarActivator(N_e=size)
        readout_layer, spont_output = train_from_buffer(source, 10000, int(size / (size / 60)))

        score_dict = source.get_text_score(spont_output)

        sm = StorageManager('buffer_{}_{}'.format(size, int(np.random.rand() * 10000)))
        sm.save_param('N_e', size)
        sm.save_param('spont_output', spont_output)
        sm.save_param_dict(score_dict)
