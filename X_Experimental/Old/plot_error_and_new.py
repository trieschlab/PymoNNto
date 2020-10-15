import sys; sys.path.append('.')
import matplotlib.pylab as plt
from Exploration.StorageManager.StorageManager import *

# parameters to include in the plot
SAVE_PLOT = True

################################################################################
#                             Make plot                                        #
################################################################################

# 0. build figures
fig = plt.figure(1, figsize=(7, 6))

experiment_path = '../../Data/StorageManager/'

experiment_n = len(os.listdir(experiment_path))

folders = ['IP_Test_New', 'IP_Test_New_and_diffuse', 'IP_Test_diffuse']#['OneLayerSmallNS', 'TwoLayerSmallNS']#'OneLayerSmallASNiefixblub', 'OneLayerSmallFSNiefix']#['OneLayerSmall', 'OneLayerSmallFSS']#,'OneLayerSmallNoSTDPFSC'# #CountingTest
colors_wrong = ['blue', 'red', 'black']
colors_new = ['green', 'yellow', 'purple']
captions = ['new', 'new+diff', 'diff']#['one', 'two']#'average syn', 'same syn']

for tag_i, Tag in enumerate(folders):#, 'OneLayerSmallNoSTDP'['buffer', 'OneLayer', 'TwoLayer']:#, 'TwoLayerOneWayForward', 'TwoLayerOneWay'

    percent_new = np.zeros(experiment_n)
    percent_error = np.zeros(experiment_n)
    net_size = np.zeros(experiment_n)

    for exp, exp_name in enumerate(os.listdir(experiment_path)):
        if exp_name.split('_')[0] == Tag or Tag == '':
            exp_n = int(exp_name.split('_')[1])
            print(exp_name)
            sm = StorageManager(experiment_path + exp_name + '/')

            n_output=sm.load_param('n_output')
            n_new=sm.load_param('n_new')
            n_wrong=sm.load_param('n_wrong')

            if n_output is not None and n_new is not None and n_wrong is not None:
                #print(sm.load_param('n_new'), float(sm.load_param('n_output')))
                percent_new[exp] = np.maximum(float(sm.load_param('n_new')),1) / np.maximum(float(sm.load_param('n_output')),1)
                percent_error[exp] = np.maximum(float(sm.load_param('n_wrong')),1) / np.maximum(float(sm.load_param('n_output')),1)
                net_size[exp] = exp_n
            else:
                print('not found', exp_name)

    #print(percent_new, percent_error, net_size)

    N_e = np.unique(net_size)
    #N_e = np.delete(N_e , 0)

    print(N_e)
    new = []
    new_std = []
    new_up = []
    new_down = []
    wrong = []
    wrong_std = []
    wrong_up = []
    wrong_down = []
    for i, n in enumerate(N_e):
        net = np.where(n == net_size)
        new.append(percent_new[net].mean())
        new_std.append(percent_new[net].std())
        new_up.append(np.percentile(percent_new[net], 75))
        new_down.append(np.percentile(percent_new[net], 25))
        wrong.append(percent_error[net].mean())
        wrong_std.append(percent_error[net].std())
        wrong_up.append(np.percentile(percent_error[net], 75))
        wrong_down.append(np.percentile(percent_error[net], 25))
        # print n, percent_new[net], percent_error[net]

    new_color = colors_new[tag_i]#np.random.rand(3)#np.power(np.random.rand(3), 2)#'blue'
    wrong_color = colors_wrong[tag_i]#np.random.rand(3)#np.power(np.random.rand(3), 2)#'red'

    plt.plot(N_e*100, new, '-o', color=new_color, alpha=0.5, label='new '+captions[tag_i], linestyle='dashed')
    plt.plot(N_e*100, wrong, '-o', color=wrong_color, alpha=0.5, label='wrong '+captions[tag_i])

    plt.fill_between(N_e*100, np.array(new) - np.array(new_std), np.array(new) + np.array(new_std), color=new_color, alpha=0.2)
    plt.fill_between(N_e*100, np.array(wrong) - np.array(wrong_std), np.array(wrong) + np.array(wrong_std), color=wrong_color, alpha=0.2)

plt.axhline(1/540)

# 4. adjust figure parameters and save
fig_lettersize = 20
# plt.title('Plasticity effects')
plt.legend(loc='best', frameon=False, fontsize=fig_lettersize)
plt.xlabel('SORN sizes', fontsize=fig_lettersize)#r'$N^{\rm E}$'  #synapses/neuron
plt.ylabel(r'sentences (%)', fontsize=fig_lettersize)
#plt.ylim([0., 0.06])
if SAVE_PLOT:
    plots_dir = '../../Data/plots/GrammarTask/'
    if not os.path.exists(plots_dir):
        os.makedirs(plots_dir)
    plt.savefig('{}error_and_new.pdf'.format(plots_dir), format='pdf')
plt.show()
