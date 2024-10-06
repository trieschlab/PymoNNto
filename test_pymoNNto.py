import numpy as np
from PymoNNto.NetworkCore.Network import *
from PymoNNto.NetworkCore.Behavior import *
from PymoNNto.NetworkCore.Neuron_Group import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.NetworkCore.Analysis_Module import *

from PymoNNto.Exploration.HelperFunctions import *
from PymoNNto.Exploration.StorageManager.StorageManager import *

from PymoNNto.Exploration.Evolution.Evolution import *

import os
import shutil

from PymoNNto.Exploration.Network_UI import *

import pytest

#from PyQt5.QtCore import QLibraryInfo
#os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = QLibraryInfo.location(
#    QLibraryInfo.PluginsPath
#)


folder = get_data_folder()+'/StorageManager/'
def clear_folder(f):
    if os.path.isdir(folder+f+'/'):
        shutil.rmtree(folder+f+'/')


class Counter(Behavior):
    def initialize(self, neurons):
        self.inc = self.parameter('inc', 1)
        neurons.count = neurons.vector()
    def iteration(self, neurons):
        neurons.count += self.inc

def get_sample_network():
    My_Network = Network()
    My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behavior={
        1: Counter(inc='[2#I]'),
        2: Recorder('count')
    })
    My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')
    sm = StorageManager('test', random_nr=False, print_msg=False)
    My_Network.initialize(storage_manager=sm)

    return My_Network, My_Neurons, My_Synapses, sm

def get_sample_network_list():
    My_Network = Network()
    My_Neurons = NeuronGroup(net=My_Network, tag='my_neurons', size=100, behavior=[
        Counter(inc='[2#I]'),
        Recorder('count')
    ])
    My_Synapses = SynapseGroup(net=My_Network, src=My_Neurons, dst=My_Neurons, tag='GLUTAMATE')
    sm = StorageManager('test', random_nr=False, print_msg=False)
    My_Network.initialize(storage_manager=sm)

    return My_Network, My_Neurons, My_Synapses, sm

def test_basics():
    net = Network()
    NeuronGroup(net=net, tag='neurons', size=100, behavior={})
    NeuronGroup(net=net, tag='neurons2', size=50, behavior={})
    SynapseGroup(net=net, tag='syn', src='neurons', dst='neurons2', behavior={})

    net.initialize()

    zero_vec = net.neurons.vector()

    one_vec = net.neurons.vector(1)
    m10_vec = net.neurons.vector(-10)

    bool_vec = net.neurons.vector(bool)
    int_vec = net.neurons.vector(int)

    uni_vec = net.neurons.vector('uniform')#, plot=True
    rnd_vec = net.neurons.vector('random')#, plot=True
    log_vec = net.neurons.vector('lognormal(mean=1, sigma=1)')#, plot=True
    norm_vec = net.neurons.vector('normal(loc=1,scale=1)')#, plot=True

    assert len(zero_vec) == 100 and zero_vec[0] == 0
    assert len(one_vec) == 100 and one_vec[0] == 1
    assert len(m10_vec) == 100 and m10_vec[0] == -10

    assert bool_vec[0] == False and bool_vec.dtype == bool
    assert int_vec[0] == 0 and int_vec.dtype == int

    assert len(uni_vec) == 100 and uni_vec[0]>=0 and uni_vec[0]<=1
    assert len(rnd_vec) == 100 and rnd_vec[0]>=0 and rnd_vec[0]<=1
    assert len(log_vec) == 100
    assert len(norm_vec) == 100


    zero_mat = net.syn.matrix()

    one_mat = net.syn.matrix(1)
    m10_mat = net.syn.matrix(-10)

    bool_mat = net.syn.matrix(bool)
    int_mat = net.syn.matrix(int)

    uni_mat = net.syn.matrix('uniform')#, plot=True
    rnd_mat = net.syn.matrix('random')#, plot=True
    log_mat = net.syn.matrix('lognormal(mean=1, sigma=1)')#, plot=True
    norm_mat = net.syn.matrix('normal(loc=1,scale=1)')#, plot=True

    assert zero_mat.shape[0] == 50 and zero_mat.shape[1] == 100 and zero_mat[0, 0] == 0
    assert one_mat.shape[0] == 50 and one_mat.shape[1] == 100 and one_mat[0, 0] == 1
    assert m10_mat.shape[0] == 50 and m10_mat.shape[1] == 100 and m10_mat[0, 0] == -10

    assert bool_mat[0, 0] == False and bool_mat.dtype == bool
    assert int_mat[0, 0] == 0 and int_mat.dtype == int

    assert uni_mat.shape[0] == 50 and uni_mat.shape[1] == 100 and uni_mat[0, 0]>=0 and uni_mat[0, 0]<=1
    assert rnd_mat.shape[0] == 50 and rnd_mat.shape[1] == 100 and rnd_mat[0, 0]>=0 and rnd_mat[0, 0]<=1
    assert log_mat.shape[0] == 50 and log_mat.shape[1] == 100
    assert norm_mat.shape[0] == 50 and norm_mat.shape[1] == 100

def test_behavior_and_tagging():
    print()

    # basic network
    set_genome({'I': 1})
    for My_Network, My_Neurons, My_Synapses, sm in [get_sample_network(), get_sample_network_list()]:

        My_Network.simulate_iterations(1000)

        My_Network.deactivate_behaviors('Counter')
        My_Network.simulate_iterations(10)

        My_Network.activate_behaviors('Counter')
        My_Network.simulate_iterations(20)

        My_Network.recording_off()
        My_Network.simulate_iterations(30)

        assert My_Network.iteration == 1000+10+20+30
        assert np.mean(My_Neurons.count) == 1000+20+30

        assert My_Synapses.src == My_Neurons
        assert My_Synapses.dst == My_Neurons

        assert My_Neurons.synapses(afferent, 'GLUTAMATE') == [My_Synapses]

        assert len(My_Network.all_objects()) == 3

        #tagging system
        assert My_Network['my_neurons'] == [My_Neurons]
        assert len(My_Network['count', 0]) == My_Network.iteration-30

        My_Network.clear_recorder()
        assert len(My_Neurons['count', 0]) == 0

        assert My_Network.tag_shortcuts['my_neurons'] == My_Network['my_neurons']

        if os.path.isdir(folder+'test/'):
            shutil.rmtree(folder+'test/')



def test_storage_manager():
    print()

    clear_folder('test')

    sm = StorageManager('test', print_msg=False)
    assert os.path.isfile('Data/StorageManager/test/test/config.ini')

    sm.save_param('k', 0)
    assert sm.load_param('k') == 0

    sm.save_param_dict({'k1': 1, 'k2': 2, 'k3': 3})
    assert sm.load_param('k1') == 1
    assert sm.load_param('k2') == 2
    assert sm.load_param('k3') == 3

    sm2 = StorageManager('test', print_msg=False)
    sm2.save_param('k', 101)
    sm2.save_param('k1', 102)

    smg = StorageManagerGroup('test')

    smg.sort_by('k')

    k_pl = smg.get_param_list('k')
    assert k_pl == [0, 101]

    m_pl = smg.get_multi_param_list(['#SM#','k','k1'])
    assert m_pl[0, 0].load_param('k') == 0
    assert m_pl[0, 1].load_param('k') == 101

    assert m_pl[1, 0] == 0
    assert m_pl[1, 1] == 101

    assert m_pl[2, 0] == 1
    assert m_pl[2, 1] == 102

    clear_folder('test')


def test_add_remove_behaviors():
    print()

    set_genome({'I': 1})
    My_Network, My_Neurons, My_Synapses, sm = get_sample_network()

    My_Neurons.count *= 0
    My_Neurons.remove_behavior('Counter')
    My_Network.simulate_iterations(10)
    assert np.mean(My_Neurons.count) == 0

    My_Neurons.add_behavior(0.5, Counter(inc='2'), initialize=True)
    My_Network.simulate_iterations(10)
    assert np.mean(My_Neurons.count) == 2*10

    My_Neurons.remove_behavior('Counter')
    My_Neurons.add_behavior(4, Counter(inc='2'), initialize=False)
    assert np.mean(My_Neurons.count) == 2*10

    if os.path.isdir(folder+'test/'):
        shutil.rmtree(folder+'test/')

##########################UI

#pip install pytest-qt

'''
@pytest.fixture
def app(qtbot):
    My_Network, My_Neurons, My_Synapses, sm = get_sample_network()
    My_Network.simulate_iteration()

    ui_app = Network_UI(My_Network, modules=get_default_UI_modules(), title='test', storage_manager=sm, group_display_count=1, reduced_layout=False)
    ui_app.pause = True

    qtbot.addWidget(ui_app.main_window)

    return ui_app


def test_label(app):

    assert app.width == 1200

    def visible():
        return True

    for i in range(app.tabs.count()):
        app.tabs.widget(i).isVisible=visible

    for _ in range(10):
        for module in app.modules:
            module.update(app)

    if os.path.isdir(folder+'test/'):
        shutil.rmtree(folder+'test/')


############# Evolution


def test_evolution():
    print()

    #clear storage manager
    clear_folder('pytest_evo')

    genome = {'a': 1, 'b': 2, 'c': 2, 'd': 2, 'e':3}

    evo = Evolution(name='pytest_evo',
                    slave_file='Exploration/Evolution/example_slave.py',
                    individual_count=2,
                    mutation=0.04,
                    death_rate=0.5,
                    constraints=['b>=a', 'a<=1', 'b>= 2'],
                    inactive_genome_info={'info': 'my_info'},
                    start_genomes=[genome],
                    devices={'single_thread': 1,
                             #'multi_thread': 4,
                             #'ssh user@host.de': 0,
                             }
                    )


    for device in evo.devices:
        device.start()

    #run 10 full generations
    for _ in range(3):
        for device in evo.devices:
            device.main_loop_update()

    first_run_score = evo.scored_individuals[0].score

    #continue
    evo.load_state()

    #run to full generations
    for _ in range(3):
        for device in evo.devices:
            device.main_loop_update()

    second_run_score = evo.scored_individuals[0].score

    clear_folder('pytest_evo')

    start_score = 7
    assert first_run_score >= start_score
    assert second_run_score >= first_run_score
    assert evo.Breed_And_Select.generation == 3
    
'''