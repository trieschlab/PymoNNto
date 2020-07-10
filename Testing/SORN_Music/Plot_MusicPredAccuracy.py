import matplotlib.pylab as plt
import numpy as np
import os
import pickle
import configparser


res_path = '/Users/carolinscholl/Documents/PhD/rotations/2_triesch/tren2/Data/StorageManager/mono/'
exp_sup_name = 'Entchen'
fig_path = '/Users/carolinscholl/Documents/PhD/rotations/2_triesch/tren2/Data/StorageManager/plots/'
title = 'Alle meine Entchen'

perf_train = []
perf_test = []
n = []
for i in os.listdir(res_path):
    if i.startswith(exp_sup_name+'_'):
        perf_train.append(pickle.load(open(os.path.join(res_path,i, 'score_train.obj'), 'rb')))
        perf_test.append(pickle.load(open(os.path.join(res_path,i, 'score_test.obj'), 'rb')))
        config = configparser.ConfigParser()
        config.read(os.path.join(res_path,i,'config.ini'))
        n.append(config['Parameters']['n_e'])
width = 0.2

n_int = [int(x) for x in n]
indices = np.argsort(n_int)
sorted_perf_train = [perf_train[x] for x in indices]
sorted_perf_test = [perf_test[x] for x in indices]
xticks = list(sorted_perf_train[0].keys())
n = [n[x] for x in indices]

fig=plt.figure(figsize=(10,5))
if title is not None: 
    plt.suptitle(title, fontsize=15)
plt.subplot(121)
plt.title('Training set', fontsize=15)
for i in range(len(sorted_perf_train)):
    plt.bar(np.arange(len(xticks))+ (i-1)*width, [x for x in sorted_perf_train[i].values()], width=width, alpha=0.7)

plt.ylabel('correct predictions', fontsize=15)
plt.ylim([0, 1])

plt.xticks(np.arange(len(xticks)), xticks, fontsize=15)
plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0],
           ['0%', '20%', '40%', '60%', '80%', '100%',], fontsize=15)

plt.subplot(122)
xticks = list(sorted_perf_test[0].keys())

plt.title('Test set', fontsize=15)
for i in range(len(sorted_perf_train)):
    plt.bar(np.arange(len(xticks))+ (i-1)*width, [x for x in sorted_perf_test[i].values()], width=width, alpha=0.7, label='{}'.format(n[i]))

leg = fig.legend(loc='lower center', fontsize=15, ncol=len(n),bbox_to_anchor=(0.5, -0.03))
leg.set_title('Network size', prop={'size':15})
plt.xticks(np.arange(len(xticks)), xticks, fontsize=15)
plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0],
           ['0%', '20%', '40%', '60%', '80%', '100%',], fontsize=15)
plt.ylim([0, 1])
fig.subplots_adjust(bottom=0.2)


if fig_path is not None:
    save_path = fig_path+'spec_perf_'+exp_sup_name+'.pdf'
    plt.savefig(save_path, format='pdf')

