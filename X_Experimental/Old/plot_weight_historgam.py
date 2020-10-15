import matplotlib.pylab as plt
from Exploration.StorageManager.StorageManager import *

sm = StorageManager('OneLayerSmallFSNWO_10_1930')#'CountingTest_10_7285' default_hist_10_9896 OneLayerSmallFSNW_10_4831

w_init = sm.load_np('ee_weights_init')
w = sm.load_np('ee_weights')

#print(type(w))
cut = 10
#for i in range(10):
syncount = []
for i in range(w_init.shape[0]):
    syncount.append(np.sum(w_init[i] > (np.max(w_init[i])/cut)))
print('before:', np.average(syncount))

syncount = []
for i in range(w.shape[0]):
    syncount.append(np.sum(w[i] > (np.max(w[i])/cut)))
print('after:', np.average(syncount))

i = 0

print(w_init[i][w_init[i] > 0])

plt.hist(w_init[i], bins=100)
plt.ylim([0., 10.0])
plt.show()

plt.hist(w[i], bins=100)
plt.ylim([0., 10.0])
plt.show()
