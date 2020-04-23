""" LanguageTask experiment

This script contains the experimental instructions for the LanguageTask
experiment.
"""
import sys; sys.path.append('.')

from sklearn import linear_model

from Testing.Old.SORN_simple_behaviour import *
from NetworkBehaviour.Input.Old.GrammarTaskActivator_old import *
from NetworkCore.Network import *
from NetworkCore.Neuron_Group import *
from NetworkCore.Synapse_Group import *

source = GrammarActivator(N_e=1600)

SORN_1_e = NeuronGroup(size=1600, behaviour={
    0: NeuronActivator(write_to='input', pattern_groups=[source]),
    1: SORN_Input_collect(T_min=0.0, T_max=0.5, lamb=10),
    2: SORN_STDP(eta_stdp=0.005, prune_stdp=False),
    3: SORN_SN(syn_type='GLU'),
    #4: SORN_iSTDP(eta_istdp=0.001, h_ip=0.1),
    #5: SORN_SN(syn_type='GABA'),
    6: SORN_IP(h_ip=0.1, eta_ip=0.001),
    #7: SORN_SP(sp_prob=0.1, sp_init=0.001, syn_type='GLU'),
    8: SORN_finish(),
    9: NeuronRecorder(['np.sum(n.x)', 'n.x', 'n.input', 'n.pattern_index'])
})

SORN_1_i = NeuronGroup(size=int(0.2 * 1600), behaviour={
    10: SORN_Input_collect(T_min=0.0, T_max=0.5), #10,11
    11: SORN_finish()
})

ee = SynapseGroup(src=SORN_1_e, dst=SORN_1_e, connectivity='s_id!=d_id').add_tag('GLU').add_tag('sparse')
ie = SynapseGroup(src=SORN_1_e, dst=SORN_1_i).add_tag('GLU')
ei = SynapseGroup(src=SORN_1_i, dst=SORN_1_e).add_tag('GABA')


SORN_Global = Network([SORN_1_e, SORN_1_i], [ee, ie, ei])

steps_plastic = 100000  # sorn training time steps
steps_readout = 10000  # readout train and test steps
steps_spont = 10000  # steps of spontaneous generation

#steps_plastic = 1000  # sorn training time steps
#steps_readout = 100  # readout train and test steps
#steps_spont = 10000  # steps of spontaneous generation
display = True

recorder = SORN_1_e[NeuronRecorder]






# Step 1. Input with plasticity
if display: print('Plasticity phase:')
# sorn.simulation(stats, phase='plastic')
SORN_Global.simulate_iterations(100, int(steps_plastic/100), True)



# Step 2. Input without plasticity: train (with STDP and IP off)
if display: print('\nReadout training phase:')
# sorn.params.par.eta_stdp = 'off'
SORN_Global.learning_off()
# sorn.simulation(stats, phase='train')
SORN_Global.simulate_iterations(steps_readout)



# Step 3. Train readout layer with logistic regression
if display: print('\nTraining readout layer...')
t_train = steps_readout
X_train = recorder['n.x'][:t_train - 1]  # stats.raster_readout[:t_train-1] #
y_train = recorder['n.pattern_index'][1:t_train].T  # stats.input_readout[1:t_train].T.astype(int) #
n_symbols = source.A  #
lg = linear_model.LogisticRegression()
readout_layer = lg.fit(X_train, y_train)



# Step 4. Input without plasticity: test (with STDP and IP off)
if display: print('\nReadout testing phase:')
# sorn.simulation(stats, phase='test')
SORN_Global.simulate_iterations(steps_readout)



# Step 5. Estimate SORN performance
if display: print('\nTesting readout layer...')
t_test = steps_readout
X_test = recorder['n.x'][t_train:t_train + t_test - 1]
y_test = recorder['n.pattern_index'][1 + t_train:t_train + t_test].T  # .T.astype(int)
# store the performance for each letter in a dictionary
spec_perf = {}
for symbol in np.unique(y_test):
    symbol_pos = np.where(symbol == y_test)
    spec_perf[source.index_to_symbol(symbol)] = readout_layer.score(X_test[symbol_pos], y_test[symbol_pos])
print(spec_perf)





# Step 6. Generative SORN with spont_activity (retro feed input)
if display: print('\nSpontaneous phase:')

# begin with the prediction from the last step
symbol = readout_layer.predict(X_test[-1].reshape(1, -1))
u = np.zeros(n_symbols)
u[symbol] = 1

SORN_1_e[0].active = False

# update sorn and predict next input
spont_output = ''
for _ in range(steps_spont):
    SORN_1_e.input = source.W.dot(u)
    SORN_Global.simulate_iteration()

    #sorn.step(u)
    symbol = int(readout_layer.predict(SORN_1_e.x.reshape(1, -1)))
    spont_output += source.index_to_symbol(symbol)
    u = np.zeros(n_symbols)
    u[symbol] = 1

# Step 7. Calculate parameters to save (exclude first and last sentences
# and separate sentences by '.'. Also, remove extra spaces.
output_sentences = [s[1:]+'.' for s in spont_output.split('.')][1:-1]

print(spont_output)



# all output sentences
output_dict = Counter(output_sentences)
n_output = len(output_sentences)
unique, counts = np.unique(output_sentences, return_counts=True)


# new output sentences
new_dict = Counter([s for s in output_sentences if s in source.removed_sentences])#todo ???
n_new = sum(new_dict.values())

# wrong output sentences
wrong_dict = Counter([s for s in output_sentences if s not in source.all_sentences])
n_wrong = sum(wrong_dict.values())

print('sentences:', n_output, 'unique:', len(unique), counts, 'new???removed!', n_new, 'wrong', n_wrong)

if source.dict == 'SP':
    gram_dict = Counter([s for s in output_sentences if s in source.grammatical_errors])
    n_gram = sum(gram_dict.values())

    sema_dict = Counter([s for s in output_sentences if s in source.semantic_errors])
    n_sema = sum(sema_dict.values())

    others_dict = Counter([s for s in output_sentences \
                          if s not in source.all_sentences \
                          if s not in source.grammatical_errors \
                          if s not in source.semantic_errors])
    n_others = sum(others_dict.values())



if display: print('\ndone!')
