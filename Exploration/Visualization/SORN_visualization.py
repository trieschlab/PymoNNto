#import sys
#sys.path.append('../../../TREN2')
#sys.path.append('../../../tren2')

#from X_Experimental.Functions import *

from Exploration.Visualization.Visualization_Helper import *

from Exploration.StorageManager.StorageManager import *
import matplotlib.pylab as plt
import matplotlib as mpl

mpl.rcParams["savefig.directory"] = '~/Desktop/'

from matplotlib.collections import PolyCollection
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import numpy as np
import os
import pickle
import configparser
from scipy.stats import entropy


def wrong_new_rigt_bar_comparison(tag, x,h,w,l,e,c):

    smg = StorageManagerGroup(tag)
    #smg.sort_by('score')
    #axis = smg.get_multi_param_list(['score', ''])

    def add_bar(lab, val, err, col):
        x.append(x[-1]+1)
        h.append(val)
        w.append(1.0)
        l.append(lab)
        e.append(err)#std
        c.append(col)
        return x[-1], val

    wrong_percentages = []
    right_percentages = []
    new_percentages = []

    for sm in smg.StorageManagerList:
        n_output_sentences = sm.load_param('n_output_sentences')
        n_wrong_sentences = sm.load_param('n_wrong_sentences')
        n_new_sentences = sm.load_param('n_new_sentences')
        n_right_sentences = sm.load_param('n_right_sentences')

        if n_output_sentences is not None and n_wrong_sentences is not None and n_new_sentences is not None and n_right_sentences is not None:
            wrong_percentages.append(n_wrong_sentences / n_output_sentences)
            right_percentages.append(n_new_sentences / n_output_sentences)
            new_percentages.append(n_right_sentences / n_output_sentences)

    _, yp1 = add_bar('w', np.average(wrong_percentages), np.std(wrong_percentages), 'red')
    xp, yp2 = add_bar('n', np.average(right_percentages), np.std(right_percentages), 'yellow')
    _, yp3 = add_bar('r', np.average(new_percentages), np.std(new_percentages), 'green')

    #plt.text(xp, np.max([wrong_percentages, right_percentages, new_percentages])+0.001, tag.replace('_layer_1l_exc_act', '').replace('_inpd', ''), fontsize=12, horizontalalignment='center', rotation=90)


def plot_wrong_new_right_bar(tags=[]):

    x = [0]
    h = [0]
    w = [0]
    l = ['']
    e = [0]
    c = ['white']

    for i, t in enumerate(tags):
        wrong_new_rigt_bar_comparison(t, x, h, w, l, e, c)

        for _ in range(2):
            x.append(x[-1]+1)
            h.append(0)
            w.append(0)
            l.append('')
            e.append(0)
            c.append('white')

    plt.bar(x, h, w, tick_label=l, yerr=e, color=c)

    plt.show()

if __name__ == '__main__':
    '''
    plot_wrong_new_right_bar(tags=[
        'bv_900_single_layer_1l_exc_act',
        'bv_1600_single_layer_1l_exc_act',
        'bv_1600_two_layer_1l_exc_act',
        'bv_3200_single_layer_1l_exc_act',

        'xps_900_single_layer_1l_exc_act',
        'xps_1600_single_layer_1l_exc_act',
        'xps_1600_two_layer_1l_exc_act',
        'xps_3200_single_layer_1l_exc_act',

        '900_single_layer_1l_exc_act',
        '1600_single_layer_1l_exc_act',
        '1600_two_layer_1l_exc_act',
        '3200_single_layer_1l_exc_act'
        
        'bv_900_single_layer_1l_exc_act',
        'xps_900_single_layer_1l_exc_act',
        '900_single_layer_1l_exc_act',

        'xps_1600_single_layer_1l_exc_act',
        'bv_1600_single_layer_1l_exc_act',
        '1600_single_layer_1l_exc_act',

        'xps_1600_two_layer_1l_exc_act',
        'bv_1600_two_layer_1l_exc_act',
        '1600_two_layer_1l_exc_act',

        'xps_3200_single_layer_1l_exc_act',
        'bv_3200_single_layer_1l_exc_act',
        '3200_single_layer_1l_exc_act',
    ])
    '''
    '''
    plot_wrong_new_right_bar(tags=[

        'bv_900_single_layer_1l_exc_act_0015_inpd',
        'xps_900_single_layer_1l_exc_act_0015_inpd',
        '900_single_layer_1l_exc_act_0015_inpd',

        'xps_1600_single_layer_1l_exc_act_0015_inpd',
        'bv_1600_single_layer_1l_exc_act_0015_inpd',
        '1600_single_layer_1l_exc_act_0015_inpd',

        'xps_1600_two_layer_1l_exc_act_0015_inpd',
        'bv_1600_two_layer_1l_exc_act_0015_inpd',
        '1600_two_layer_1l_exc_act_0015_inpd',

        'xps_3200_single_layer_1l_exc_act_0015_inpd',
        'bv_3200_single_layer_1l_exc_act_0015_inpd',
        '3200_single_layer_1l_exc_act_0015_inpd'
    ])
    '''

    plot_wrong_new_right_bar(tags=[
        '17_4_900_single',
        '17_4_900_double_ff_fb',
        '17_4_900_double_ff',
        '17_4_900_double_no_conn',
        '17_4_900_double_same_ff_fb'
    ])

def plot_netsize_vs_score():
    lookup_dict = {'n_wrong_sentences': 'wrong', 'IP_Test_diffuse': 'diffuse', 'n_new': 'new', 'n_wrong': 'wrong',
                   'folder_number': 'id', 'IP_Test_New': 'IP', 'IP_Test_New_and_diffuse': 'IP+diffuse'}

    def lookup(key):
        if key in lookup_dict:
            return lookup_dict[key]
        else:
            return key

    # Tags = ['SORN_One_layer', 'SORN_Two_layer', 'SORN_Three_layer']
    # Tags = ['SORN_One_layer', 'Adj_SORN_Two_layer', 'Adj_SORN_Three_layer']
    #Tags = ['SORN_Gram_train_time_50k', 'SORN_Gram_train_time_100k', 'SORN_Gram_train_time_200k',
    #        'SORN_Gram_train_time_300k']

    Tags = ['size_comp', 'bruno_size_comp', 'hierarchical_size_comp']

    params = ['N_e', 'n_output', 'n_wrong_sentences']  # , 'n_new' #, 'n_wrong_sentences'  #'n_wrong_sentences'

    print(params[1:])

    for tag in Tags:
        smg = StorageManagerGroup(tag)

        remove=[]
        for sm in smg.StorageManagerList:
            out=sm.load_param('n_output')
            wrong=sm.load_param('n_wrong_sentences')
            if out is None or wrong is None or 100/out*wrong>95:
                remove.append(sm)
        smg.StorageManagerList=[sm for sm in smg.StorageManagerList if sm not in remove]

        '''
        scores_old = []
        scores_new = []
        for sm in smg.StorageManagerList:
            source = FDTGrammarActivator_New(tag='grammar_act', output_size=sm.load_param('N_e'), random_blocks=True)

            text=sm.load_param('output')
            if text is not None:
                scores_old.append(source.get_text_score_old(text)['n_wrong'])
                scores_new.append(source.get_text_score(text)['n_wrong_sentences'])

        print(scores_old)
        print(scores_new)
        '''

        smg.sort_by(params[0])
        axis = smg.get_multi_param_list(params)  # axis[0]=N_e vec, axis[1]=n_output vec, ...
        #print(axis)

        # convert from number to percentage
        axis[2] = 100 / axis[1] * axis[2]
        # axis[3] = 100 / axis[1] * axis[3]

        for a, p in zip(axis[2:], params[2:]):  # remove first list (N_e)

            x, avg = smg.remove_duplicates_get_eval(axis[0], a, 'np.average(a)')
            x, std = smg.remove_duplicates_get_eval(axis[0], a, 'np.std(a)')

            #print(x, avg)

            plt.plot(x, avg, label=lookup(p) + ' ' + lookup(tag))
            plt.fill_between(x, avg - std, avg + std, alpha=0.2)

            plt.scatter(axis[0], a)

    # plt.axhline(1/540)

    fig_lettersize = 20
    plt.legend(loc='best', frameon=False, fontsize=fig_lettersize)
    plt.xlabel(lookup(params[0]), fontsize=fig_lettersize)
    plt.ylabel(r'sentences (%)', fontsize=fig_lettersize)

    if True:
        format = 'png'
        plot_sm = StorageManager('Plots', '_'.join(Tags) + '___' + '_'.join(params))
        plot_sm.save_param('Tags', str(Tags))
        plot_sm.save_param('params', str(params))
        plot_sm.save_param('lookup', str(lookup))
        plot_sm.save_param('fig_lettersize', fig_lettersize)
        plt.savefig(plot_sm.absolute_path + 'plot.' + format, format=format)

    plt.show()


def plot_netsize_vs_freq_spont_music(res_path, exp_sup_name, n_gram=1, remove_infrequent_ones=False, fig_path=None, title=None):
    first = True
    perf = []
    n = []
    for i in os.listdir(res_path):
        if i.startswith(exp_sup_name+'_'):
            perf.append(pickle.load(open(os.path.join(res_path,i, 'score_spontaneous.obj'), 'rb')))
            config = configparser.ConfigParser()
            config.read(os.path.join(res_path,i,'config.ini'))
            n.append(config['Parameters']['n_e'])

    if remove_infrequent_ones: 
        # clean the dictionaries such that they are the same (we delete occurences that have frequency below 10e-5)
        for i in range(len(perf)):
            for k, v in list(perf[i]['input_frequencies_{}'.format(n_gram)].items()):
                if v < 10e-4:
                    del perf[i]['input_frequencies_{}'.format(n_gram)][k]
                    del perf[i]['output_frequencies_{}'.format(n_gram)][k]
                    perf[i]['sorted_symbols_{}'.format(n_gram)].remove(k)
    # sort them
    n_int = [int(x) for x in n]
    indices = np.argsort(n_int)
    perf = [perf[x] for x in indices]
    n = [n[x] for x in indices]

    for i in range(len(perf)):
        if first: 
            freq_input = perf[i]['input_frequencies_{}'.format(n_gram)]
            sorted_notes = perf[i]['sorted_symbols_{}'.format(n_gram)]
            first = False
        freq_output = perf[i]['output_frequencies_{}'.format(n_gram)]
        assert list(freq_output.keys()) == list(freq_input.keys()), "input and output dictionaries are different"
        plt.plot(np.arange(len(freq_input)), list(freq_output.values()), linewidth='1', label='{}'.format(n[i]))

    plt.plot(np.arange(len(freq_input)), list(freq_input.values()), linewidth='3', color='k', label='MIDIS')
    leg = plt.legend(loc='best', frameon=False, fontsize=18)
    leg.set_title('Network size',prop={'size':18})
    plt.xticks(np.arange(len(sorted_notes)), sorted_notes, fontsize=10, rotation=90)
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
           ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%'], fontsize=18)
    plt.ylabel('frequency', fontsize=18)
    if title is not None:
        plt.title(title, fontsize=18)
    plt.tight_layout()
    plt.show()
    if fig_path is not None:
        save_path = fig_path+'n_params_spont_output_'+exp_sup_name+'_symbollength_'+str(n_gram)+'.pdf'
        plt.savefig(save_path, format='pdf')
    return


def plot_netsize_vs_freq_spont_music_polyphonic(res_path, exp_sup_name, remove_infrequent_ones=False, fig_path=None, title=None):
    first = True
    perf = []
    n = []
    for i in os.listdir(res_path):
        if i.startswith(exp_sup_name+'_'):
            perf.append(pickle.load(open(os.path.join(res_path,i, 'score_spontaneous.obj'), 'rb')))
            config = configparser.ConfigParser()
            config.read(os.path.join(res_path,i,'config.ini'))
            n.append(config['Parameters']['n_e'])

    if remove_infrequent_ones: 
        # clean the dictionaries such that they are the same (we delete occurences that have frequency below 10e-5)
        for i in range(len(perf)):
            for k, v in list(perf[i]['input_frequencies'].items()):
                if v < 10e-4:
                    del perf[i]['input_frequencies'][k]
                    del perf[i]['output_frequencies'][k]
                    perf[i]['sorted_symbols'].remove(k)
    # sort them
    n_int = [int(x) for x in n]
    indices = np.argsort(n_int)
    perf = [perf[x] for x in indices]
    n = [n[x] for x in indices]

    for i in range(len(perf)):
        if first: 
            freq_input = perf[i]['input_frequencies']
            sorted_notes = perf[i]['sorted_symbols']
            first = False
        freq_output = perf[i]['output_frequencies']
        assert list(freq_output.keys()) == list(freq_input.keys()), "input and output dictionaries are different"
        plt.plot(np.arange(len(freq_input)), list(freq_output.values()), linewidth='1', label='{}'.format(n[i]))

    plt.plot(np.arange(len(freq_input)), list(freq_input.values()), linewidth='3', color='k', label='MIDIS')
    leg = plt.legend(loc='best', frameon=False, fontsize=18)
    leg.set_title('Network size',prop={'size':18})
    plt.xticks(np.arange(len(sorted_notes)), sorted_notes, fontsize=10, rotation=90)
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
           ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%'], fontsize=18)
    plt.ylabel('frequency', fontsize=18)
    if title is not None:
        plt.title(title, fontsize=18)
    plt.tight_layout()
    plt.show()
    if fig_path is not None:
        save_path = fig_path+'n_params_spont_output_poly'+exp_sup_name+'.pdf'
        plt.savefig(save_path, format='pdf')
    return



def plot_netsize_vs_specific_performance_music(res_path, exp_sup_name, fig_path=None, title=None):

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

    return

def plot_specific_performance(spec_perf, path=None, title=None): 
    'spec freq: dictionary with specific frequency per symbol'
    fig = plt.figure(1, figsize=(15, 6))

    xticks = list(spec_perf.keys())
    plt.bar(np.arange(len(xticks)), [x for x in spec_perf.values()],alpha=0.7)

    plt.xticks(np.arange(len(xticks)), xticks, fontsize=15)
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0],
           ['0%', '20%', '40%', '60%', '80%', '100%',], fontsize=15)
    plt.ylim([0, 1])
    plt.ylabel('correct predictions', fontsize=15)
    if title is not None: 
        plt.title(str(title), fontsize=15)

    if path is not None:
        save_path = path+'specific_performance.pdf'
        print(save_path)
        plt.savefig(save_path, format='pdf')
    plt.show()



def plot_frequencies(score_dict, ngram=1, path=None, title=None):
    ''' compares frequencies of symbols occuring in corpus vs. in output, 
        parameter ngram stands for length of symbol sequence compared'''

    freq_output = score_dict['output_frequencies_{}'.format(ngram)]
    freq_input = score_dict['input_frequencies_{}'.format(ngram)]
    sorted_notes = score_dict['sorted_symbols_{}'.format(ngram)]

    plt.plot(np.arange(len(freq_input)), list(freq_output.values()), linewidth='1', label='output')
    plt.plot(np.arange(len(freq_input)), list(freq_input.values()), linewidth='3', color='k', label='input')

    leg = plt.legend(loc='best', frameon=False, fontsize=18)
    plt.xticks(np.arange(len(sorted_notes)), sorted_notes, fontsize=10, rotation=90)
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4],
           ['0%', '10%', '20%', '30%', '40%'], fontsize=18)
    #plt.ylim([0, 0.4])
    plt.ylabel('frequency', fontsize=18)
    plt.tight_layout()
    if title is not None: 
        plt.title(str(title), fontsize=18)

    if path is not None:
        save_path = path+'frequencies_symbollength{}.pdf'.format(ngram)
        print(save_path)
        plt.savefig(save_path, format='pdf')
    plt.show()   

    return

def plot_frequencies_poly(score_dict,path=None, title=None, show=False):
    ''' compares frequencies of symbols occuring in corpus vs. in output'''

    freq_output = score_dict['output_frequencies']
    freq_input = score_dict['input_frequencies']
    sorted_notes = score_dict['sorted_symbols']

    plt.plot(np.arange(len(freq_input)), list(freq_output.values()), linewidth='1', label='output')
    plt.plot(np.arange(len(freq_input)), list(freq_input.values()), linewidth='3', color='k', label='input')

    leg = plt.legend(loc='best', frameon=False, fontsize=18)
    plt.xticks(np.arange(len(sorted_notes)), sorted_notes, fontsize=10, rotation=90)
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
           ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%'], fontsize=18)
    #plt.ylim([0, 0.4])
    plt.ylabel('frequency', fontsize=18)
    if title is not None: 
        plt.title(str(title), fontsize=18)
    plt.tight_layout()

    if path is not None:
        save_path = path+'frequencies_polyphonic.pdf'
        print(save_path)
        plt.savefig(save_path, format='pdf')

    if show: 
        plt.show()   

    return


def plot_frequencies_chords_poly(score_dict,path=None, title=None):
    ''' compares frequencies of chords occuring in corpus vs. in output'''

    freq_output = score_dict['output_frequencies_chords']
    freq_input = score_dict['input_frequencies_chords']
    sorted_notes = score_dict['sorted_chords']

    plt.plot(np.arange(len(freq_input)), list(freq_output.values()), linewidth='1', label='output')
    plt.plot(np.arange(len(freq_input)), list(freq_input.values()), linewidth='3', color='k', label='input')

    leg = plt.legend(loc='best', frameon=False, fontsize=18)
    plt.xticks(np.arange(len(sorted_notes)), sorted_notes, fontsize=10, rotation=90)
    plt.yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
           ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%'], fontsize=18)
    #plt.ylim([0, 0.4])
    plt.ylabel('frequency', fontsize=18)
    plt.tight_layout()
    if title is not None: 
        plt.title(str(title))

    if path is not None:
        save_path = path+'frequencies_chords_polyphonic.pdf'
        print(save_path)
        plt.savefig(save_path, format='pdf')
    plt.show()   

    return


def plot_(tag, run_id):
    sm = StorageManager(tag, tag + '_{}'.format(run_id))
    #sm = StorageManager('weight_development', 'weight_development_3')  # 'CountingTest_10_7285' default_hist_10_9896 OneLayerSmallFSNW_10_4831
    # sm = StorageManager('just biggest syn test', 'just biggest syn test_40')
    y_values0 = []
    y_values1 = []
    y_values2 = []
    y_values3 = []
    x_values = []

    for i in range(100):
        synapses = sm.load_obj('syn{}'.format(i))

        y = np.average(np.sum(synapses.transpose() > (np.max(synapses, axis=1) * (1 / 2)), axis=0))
        y_values0.append(y)

        y = np.average(np.sum(synapses.transpose() > (np.max(synapses, axis=1) * (1 / 3)), axis=0))
        y_values1.append(y)

        y = np.average(np.sum(synapses.transpose() > (np.max(synapses, axis=1) * (1 / 4)), axis=0))
        y_values2.append(y)

        y = np.average(np.sum(synapses.transpose() > (np.max(synapses, axis=1) * (1 / 5)), axis=0))
        y_values3.append(y)

        x_values.append(i * 1000)

    plt.plot(x_values, y_values3, label='syn>max_syn*(1/5)')
    plt.plot(x_values, y_values2, label='syn>max_syn*(1/4)')
    plt.plot(x_values, y_values1, label='syn>max_syn*(1/3)')
    plt.plot(x_values, y_values0, label='syn>max_syn*(1/2)')

    plt.legend(loc='best', frameon=False, fontsize=20)
    plt.xlabel(r'plasticity iterations', fontsize=20)
    plt.ylabel(r'synapses', fontsize=20)

    plt.show()



def sdgsdfkkd():
    lookup_dict = {'n_wrong_sentences': 'wrong', 'IP_Test_diffuse': 'diffuse', 'n_new': 'new', 'n_wrong': 'wrong',
                   'folder_number': 'id', 'IP_Test_New': 'IP', 'IP_Test_New_and_diffuse': 'IP+diffuse'}

    def lookup(key):
        if key in lookup_dict:
            return lookup_dict[key]
        else:
            return key

    # Tags = ['SORN_One_layer', 'SORN_Two_layer', 'SORN_Three_layer']
    # Tags = ['SORN_One_layer', 'Adj_SORN_Two_layer', 'Adj_SORN_Three_layer']
    Tags = ['inh syn', 'random plasticity FDT train', 'random plasticity FDT train 2']
    # Tags = ['inh syn', 'just biggest syn']
    params = ['N_e', 'n_output', 'n_wrong_sentences']  # , 'n_new' #, 'n_wrong_sentences' 'n_wrong_words'

    print(params[1:])

    for tag in Tags:
        smg1 = StorageManagerGroup(tag)
        smg1.sort_by(params[0])
        axis = smg1.get_multi_param_list(params)  # axis[0]=N_e vec, axis[1]=n_output vec, ...
        print(axis)

        # convert from number to percentage
        axis[2] = 100 / axis[1] * axis[2]
        # axis[3] = 100 / axis[1] * axis[3]

        for a, p in zip(axis[2:], params[2:]):  # remove first list (N_e)

            x, avg = smg1.remove_duplicates_get_eval(axis[0], a, 'np.average(a)')
            x, std = smg1.remove_duplicates_get_eval(axis[0], a, 'np.std(a)')

            print(x, avg)

            plt.plot(x, avg, label=lookup(p) + ' ' + lookup(tag))
            plt.fill_between(x, avg - std, avg + std, alpha=0.2)

    # plt.axhline(1/540)

    fig_lettersize = 20
    plt.legend(loc='best', frameon=False, fontsize=fig_lettersize)
    plt.xlabel(lookup(params[0]), fontsize=fig_lettersize)
    plt.ylabel(r'sentences (%)', fontsize=fig_lettersize)

    if True:
        format = 'png'
        plot_sm = StorageManager('Plots', '_'.join(Tags) + '___' + '_'.join(params))
        plot_sm.save_param('Tags', str(Tags))
        plot_sm.save_param('params', str(params))
        plot_sm.save_param('lookup', str(lookup))
        plot_sm.save_param('fig_lettersize', fig_lettersize)
        plt.savefig(plot_sm.absolute_path + 'plot.' + format, format=format)

    plt.show()



def rgkdfjhgd(tag, run_id):
    sm = StorageManager(tag, tag + '_{}'.format(run_id))
    #sm = StorageManager('CHILDES_test', 'CHILDES_test_4')  # 'CountingTest_10_7285' default_hist_10_9896 OneLayerSmallFSNW_10_4831

    spec_perf = sm.load_obj('spec_perf')

    plt.bar(np.arange(len(spec_perf.keys())), spec_perf.values())
    plt.show()



def plot_average(tag, run_id):
    sm = StorageManager(tag, tag + '_{}'.format(run_id))
    #sm = StorageManager('osc_test_no_stdp', 'osc_test_no_stdp_0')
    avg = sm.load_obj('avg')
    avg = avg.reshape(-1, 10).mean(axis=-1)
    plt.plot(np.arange(len(avg)), avg, label='...')

    plt.legend(loc='best', frameon=False, fontsize=20)
    plt.xlabel('plasticity steps', fontsize=20)
    plt.ylabel('average excitatory neuron acticity', fontsize=20)
    plt.show()

#plot_average('reduced_oscillation_tests_default_200_syn_N_e_1000_TI_1000_and_100_and_IP_20perc',3)

def get_lognormal_overlay_plot():
    all = []
    # means=
    for i in range(10):
        logn = np.random.lognormal(mean=1 + (10 - i) / 5, size=1000)
        plt.hist(logn, range=(0, 100), bins=100, alpha=0.5)
        all.append(logn)

    plt.xlim(0, 100)
    plt.show()

    plt.hist(np.array(all).flatten(), range=(0, 100), bins=100)
    plt.xlim(0, 100)
    plt.show()


def get_ISI_plot():
    sm = StorageManager('distribution', 'distribution_0')
    avg = sm.load_obj('avg')
    x = sm.load_obj('x')

    isis = []
    for i in range(100):
        isis.append(SpikeTrain_ISI(x[:, i]))

    plt.hist(isis, bins=50, range=(0, 100))  # , stacked=True

    plt.xlim(0, 100)
    plt.show()





def ssdfasd(tag):
    temporal_avg=1000

    smg = StorageManagerGroup(tag)
    cut_off_freq = 0.1

    # def autocorr(x):
    #    result = np.correlate(x, x, mode='full')
    #    return result[result.size/2:]

    def autocorr(x, t=1):
        return np.corrcoef(np.array([x[:-t], x[t:]]))[0][1]

    for i, sm in enumerate(smg.StorageManagerList):
        c = np.random.rand(3)
        avg = sm.load_obj('avg')  # [0:10000]
        avg2 = avg.reshape(-1, temporal_avg).mean(axis=-1)
        Y = np.fft.fft(avg)
        freq = np.fft.fftfreq(len(avg), 1)

        print(autocorr(avg), autocorr(avg2))
        #print(np.var(np.abs(Y[freq > cut_off_freq])))

        #plt.plot(freq[freq > cut_off_freq], np.abs(Y[freq > cut_off_freq]), alpha=0.5, color=c)
        plt.plot(avg2)

    plt.show()

#temporal average + auto corellation

#ssdfasd('osc_test_no_stdp_big')
#ssdfasd('test')
#ssdfasd('reduced_oscillation_tests_default_100_syn_N_e_1000')


def polygon_under_graph(xlist, ylist):
    return [(xlist[0], 0.)] + list(zip(xlist, ylist)) + [(xlist[-1], 0.)]

#tags = ['reduced_oscillation_tests_default_50_syn', 'reduced_oscillation_tests_10perc_50_syn', 'reduced_oscillation_tests_20perc_50_syn', 'reduced_oscillation_tests_50perc_50_syn', 'reduced_oscillation_tests_80perc_50_syn']
#n=['default', '10%', '20%', '50%', '80%']
#tags = ['reduced_oscillation_tests_def_200_syn', 'reduced_oscillation_tests_10perc_200_syn', 'reduced_oscillation_tests_20perc_200_syn', 'reduced_oscillation_tests_50perc_200_syn']

#tags = ['reduced_oscillation_tests_diffIP_def_50_syn', 'reduced_oscillation_tests_diffIP_10perc_50_syn', 'reduced_oscillation_tests_diffIP_20perc_50_syn', 'reduced_oscillation_tests_diffIP_50perc_50_syn']
#tags = ['reduced_oscillation_tests_diffIP_def_200_syn', 'reduced_oscillation_tests_diffIP_10perc_200_syn', 'reduced_oscillation_tests_diffIP_20perc_200_syn', 'reduced_oscillation_tests_diffIP_50perc_200_syn']

#tags = ['osc_test_no_stdp', 'osc_test_stdp']
#tags = ['osc_test_no_stdp_big', 'osc_test_stdp_big']

def show_3D_oscillation_plot(tags, temporal_avg=10):


    for tn, tag in enumerate(tags):

        cc = 'rgbyrgbyrgbyrgbyrgbyrgbyrgbyrgbyrgbyrgby'

        smg = StorageManagerGroup(tag)
        cut_off_freq = 0.1
        c = np.random.rand(3)

        z = []
        colors = []
        verts = []
        fig = plt.figure(num=tag)
        ax = fig.gca(projection='3d')

        for i, sm in enumerate(smg.StorageManagerList):
            if sm.has_obj('avg'):
                z.append(i)
                colors.append(mcolors.to_rgba(cc[i], alpha=0.9))  # np.random.rand(3)
                avg = sm.load_obj('avg')  # [0:10000]
                avg = avg.reshape(-1, temporal_avg).mean(axis=-1)
                # Y = np.fft.fft(avg)
                # freq = np.fft.fftfreq(len(avg), 1)
                # plt.plot(freq[freq > cut_off_freq], np.abs(Y[freq > cut_off_freq]), alpha=0.5, color=c)
                # plt.plot(np.arange(len(avg)), avg, label='50 syn default')
                verts.append(polygon_under_graph(np.linspace(0., len(avg)*temporal_avg, len(avg)), avg))

        # plt.plot([], label=n[tn], color=c)

        poly = PolyCollection(verts, facecolors=colors)
        ax.add_collection3d(poly, zs=z, zdir='y')

        ax.set_xlim(0, len(avg)*temporal_avg)
        ax.set_ylim(-1, i)
        ax.set_zlim(0, 0.5)

        plt.show()

    #plt.legend(loc='best', frameon=False, fontsize=20)
    #plt.xlabel('freq', fontsize=20)
    #plt.ylabel('', fontsize=20)
    #plt.show()




def show_2D_oscillation_plot(tag, run_id, temporal_avg=10):
    sm = StorageManager(tag, tag+'_{}'.format(run_id))
    avg = sm.load_obj('avg')
    avg = avg.reshape(-1, temporal_avg).mean(axis=-1)
    plt.plot(np.arange(len(avg))*temporal_avg, avg, label='50 syn default')

    plt.legend(loc='best', frameon=False, fontsize=20)
    plt.xlabel('plasticity steps', fontsize=20)
    plt.ylabel('average excitatory neuron acticity', fontsize=20)
    plt.show()


def aagdsfgsdf(tag, run_id):
    sm = StorageManager(tag, tag+'_{}'.format(run_id))
    avg = sm.load_obj('avg')

    plt.plot(avg, label='net average')

    # plt.plot(x[:,1], label='neuron act')

    # x2 = x[:,1].reshape(-1, 10).mean(axis=-1)
    # plt.plot(np.arange(len(x2))*10, x2, label='10 step average')

    x2 = x[:, 4].reshape(-1, 100).mean(axis=-1)
    plt.plot(np.arange(len(x2)) * 100, x2, label='1 neuron 100 step average')

    # plt.plot(np.arange(len(x)), x[:,1], label='50 syn default')

    plt.legend(loc='best', frameon=False, fontsize=20)
    plt.xlabel('time', fontsize=20)
    plt.ylabel('', fontsize=20)

    plt.show()


def sdgsdfgdf():
    sm = StorageManager('syn_avg_act', 'syn_avg_act_2')
    avg = sm.load_obj('avg')
    plt.plot(np.arange(len(avg)), avg)
    plt.show()

    scale = 10
    for i in range(3):
        avg = avg.reshape(-1, scale).mean(axis=-1)
        plt.plot(np.arange(len(avg)) * np.power(scale, (i + 1)), avg)
    plt.show()



def bhbhjjb():
    cut_off_freq = 0.1

    sm = StorageManager('syn_avg_act_no_bug', 'syn_avg_act_no_bug_3')
    avg = sm.load_obj('avg')
    print(len(avg))
    Y = np.fft.fft(avg)
    freq = np.fft.fftfreq(len(avg), 1)
    plt.plot(freq[freq > cut_off_freq], np.abs(Y[freq > cut_off_freq]), label='150 synapses', alpha=0.5)
    # plt.plot(avg, label='150 synapses', alpha=0.5)

    sm = StorageManager('syn_avg_act_no_bug', 'syn_avg_act_no_bug_2')
    avg = sm.load_obj('avg')
    print(len(avg))
    Y = np.fft.fft(avg)
    freq = np.fft.fftfreq(len(avg), 1)
    plt.plot(freq[freq > cut_off_freq], np.abs(Y[freq > cut_off_freq]), label='100 synapses', alpha=0.5)
    # plt.plot(avg, label='100 synapses', alpha=0.5)

    sm = StorageManager('syn_avg_act_no_bug', 'syn_avg_act_no_bug_1')
    avg = sm.load_obj('avg')
    print(len(avg))
    Y = np.fft.fft(avg)
    freq = np.fft.fftfreq(len(avg), 1)
    plt.plot(freq[freq > cut_off_freq], np.abs(Y[freq > cut_off_freq]), label='50 synapses', alpha=0.5)
    # plt.plot(avg, label='50 synapses', alpha=0.5)

    sm = StorageManager('syn_avg_act_no_bug', 'syn_avg_act_no_bug_0')
    avg = sm.load_obj('avg')
    print(len(avg))
    Y = np.fft.fft(avg)
    freq = np.fft.fftfreq(len(avg), 1)
    plt.plot(freq[freq > cut_off_freq], np.abs(Y[freq > cut_off_freq]), label='10 synapses', alpha=0.5)
    # plt.plot(avg, label='10 synapses', alpha=0.5)

    fig_lettersize = 20
    plt.legend(loc='best', frameon=False, fontsize=fig_lettersize)
    plt.xlabel('frequency', fontsize=fig_lettersize)
    plt.ylabel('fourier transform y', fontsize=fig_lettersize)

    plt.show()


def create_beat_matrix_from_results(res_path, offtoken=True, ontoken=False):
    #TODO: need to check that indexing is safe if start/stop tokens occur at first/last time step of output
    perf = pickle.load(open(os.path.join(res_path, 'score_spontaneous.obj'), 'rb'))
    beat_matrix = perf['output_beatmatrix']

    if offtoken and ontoken:
        # last row stands for start token, row before for stop token
        indices_start = np.nonzero(beat_matrix[:,-1])[0]
        indices_stop = np.nonzero(beat_matrix[:,-2])[0]

    elif offtoken and not ontoken: # we only have offtokens, but we start at first generated time step
        indices_stop = np.nonzero(beat_matrix[:,-1])[0]
        indices_start = indices_stop+1

    elif ontoken and not offtoken:
        indices_start = np.nonzero(beat_matrix[:,-1])[0]
        indices_stop = indices_start-1

    indices_start = indices_start[:-1] # remove last start token, it does not have a corresponding stop token
    indices_stop = indices_stop[1:] # remove first stop token, it does not have a corresponding start token

    tracks = []
    if len(indices_start) >0 and len(indices_stop)>0:
        assert [indices_stop[i] > indices_start[i] for i in range(len(indices_start))]

        for i in range(len(indices_start)):
            tracks.append(beat_matrix[indices_start[i]:indices_stop[i]+1,:14])
        
    else:# return whole matrix, we just have one track, it never predicted start/stop
        tracks.append(beat_matrix[:,:14])

    return np.array(tracks)


def get_percussion_track_entropy(track, len_alphabet=14, include_silence=False):
    distribution = np.zeros(len_alphabet)
    indices_non_zero = track.nonzero()
    for i in range(len_alphabet):
        distribution[i] = sum(indices_non_zero[1] == i)
    if include_silence:
    # add the silent time steps (when no note is played)
        non_zero_indices = set(indices_non_zero[0])
        all_indices = set(range(len(track)))
        silent_indices = all_indices - non_zero_indices
        distribution = np.append(distribution, len(silent_indices))

    return entropy(distribution)

def compute_per_track_entropy(tracks):
        '''
        return a list of per track entropies
        expects a beat matrix of shape (n_tracks, len_alphabet)
        '''
        entropy_generated_tracks = []

        if len(tracks)==1:
            entropy_generated_tracks = self.get_percussion_track_entropy(tracks, tracks.shape[1], include_silence = include_silence)

        else:
            for i in range(len(tracks)):
                entropy_generated_tracks.append(get_percussion_track_entropy(tracks[i], tracks[i].shape[1]))

        return entropy_generated_tracks

def compute_per_track_length(tracks):
    '''
    returns a list of track lengths
    expects a beat matrix of shape (n_tracks, len_alphabet)
    '''
    return [len(i) for i in tracks]



