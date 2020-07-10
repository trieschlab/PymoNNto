import matplotlib.pylab as plt
import numpy as np
import os
import pickle
import configparser

res_path = '/Users/carolinscholl/Documents/PhD/rotations/2_triesch/tren2/Data/StorageManager/drum/'
exp_sup_name = '100Similar'
fig_path = '/Users/carolinscholl/Documents/PhD/rotations/2_triesch/tren2/Data/StorageManager/plots/'
#title = 'Alle meine Entchen'

title = None
perf = []
n = []
remove_infrequent_ones=False
first = True


exp_names = [
        'DrumBeats__drum_[1800]Ne_[1]_TrackID100_similarTHR0.5',
        'fastSTDPexc0.0015inh0.001_1800Ne_[1]_TrackID100_Similar0.5', 
        'DrumBeats__PV_SOM1800N_e_[1]_1800Ne_TrackID100_Similar0.5']

labels = [
         '1800 x S1',
         '1800 x S1, faster STDP', 
         '1800 x S1, different interneurons']

'''
new_labels = []

for i in os.listdir(res_path):
    if i.startswith(exp_sup_name+'_'):
        perf.append(pickle.load(open(os.path.join(res_path,i, 'score_spontaneous.obj'), 'rb')))
        config = configparser.ConfigParser()
        config.read(os.path.join(res_path,i,'config.ini'))
        n.append(config['Parameters']['n_e'])
        new_labels.append(labels[exp_names.index(i)])

for i in range(len(labels)):
    new_labels.append(labels[i][labels[i].find('drum')+4:labels[i].find('_Track')])
    if labels[i].find('Inverted') != -1:
        new_labels[i] = new_labels[i]+'+ inverted alphabet'

if remove_infrequent_ones: 
    # clean the dictionaries such that they are the same (we delete occurences that have frequency below 10e-5)
    for i in range(len(perf)):
        for k, v in list(perf[i]['input_frequencies'].items()):
            if v < 10e-4:
                del perf[i]['input_frequencies'][k]
                del perf[i]['output_frequencies'][k]
                perf[i]['sorted_symbols'].remove(k)

n_int = [int(x) for x in n]
indices = np.argsort(n_int)
perf = [perf[x] for x in indices]
n = [n[x] for x in indices]
'''


new_labels = labels

for i in exp_names:
    path = os.path.join(res_path, i)
    perf.append(pickle.load(open(os.path.join(path, 'score_spontaneous.obj'), 'rb')))
    config = configparser.ConfigParser()
    config.read(os.path.join(path,'config.ini'))
    n.append(config['Parameters']['n_e'])

for i in range(len(perf)):
    if first: 
        freq_input = perf[i]['input_frequencies']
        sorted_notes = perf[i]['sorted_symbols']
        first = False
    freq_output = perf[i]['output_frequencies']
    assert list(freq_output.keys()) == list(freq_input.keys()), "input and output dictionaries are different"
    plt.plot(np.arange(len(freq_input)), list(freq_output.values()), linewidth='1', label=new_labels[i])


plt.plot(np.arange(len(freq_input)), list(freq_input.values()), linewidth='3', color='k', label='Training Data')
leg = plt.legend(loc='best', frameon=False, fontsize=10)
leg.set_title('Network size',prop={'size':12})
plt.xticks(np.arange(len(sorted_notes)), sorted_notes, fontsize=10, rotation=90)
plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
    ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%'], fontsize=10)
#plt.ylim([0, 0.4])
plt.ylabel('frequency', fontsize=10)
if title is not None:
    plt.title(title, fontsize=12)
plt.tight_layout()
#plt.show()


random_title = int(np.random.randint(999999, size=1))

if fig_path is not None:
    save_path = fig_path+exp_sup_name+str(random_title)+'.pdf'
    plt.savefig(save_path, format='pdf')
