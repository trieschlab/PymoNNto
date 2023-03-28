import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt

from PymoNNto.NetworkBehavior.Input.Activator import *
from PymoNNto.NetworkCore.Neuron_Group import *

import PymoNNto.Exploration.Evolution_Old.NetworkEvaluationFunctions as EvalF



class visualization_recorder(Behavior):
    def __init__(self):
        self.recorderlist = []
        self.neurons = None

    def initialize(self, neurons):
        self.neurons=neurons
        for recorder in self.recorderlist:
            recorder.initialize(neurons)

    def iteration(self, neurons):
        self.neurons = neurons
        for recorder in self.recorderlist:
            recorder.iteration(neurons)

class score_visualization_recorder(visualization_recorder):

    def __init__(self):
        super().__init__()
        self.neu_rec = Recorder(['norm_value', 'output_activity_history[0]', 'activity'], gapwidth=100)
        self.recorderlist.append(self.neu_rec)
        self.syn_rec = SynapseGroupRecorder(['GLU_Synapses'], gapwidth=1000)
        self.recorderlist.append(self.syn_rec)

    def visualize(self):
        print('rendering score visualization:')

        fig, axes = plt.subplots(2, 3)
        fig.canvas.set_window_title('score visualization')

        #image = get_whole_Network_weight_image(self.neurons, neuron_src_groups=None)
        #axes[0, 2].imshow(image, interpolation="nearest")
        #axes[0, 2].set_xlabel('weights')

        print('- activity diversity score...')
        axes[0, 0].plot(EvalF.get_diversity_score_sliding_window(np.array(self.neu_rec['activity'])))
        print('- activity sparseness score...')
        axes[0, 1].plot(EvalF.get_sparseness_score_sliding_window(np.array(self.neu_rec['activity'])))
        print('- weight diversity score...')
        axes[1, 0].plot(EvalF.get_diversity_score_timeline(np.array(self.syn_rec['GLU_Synapses']), self.neurons.get_combined_synapse_shape('GLU')))#(50,100)(400, 100)
        #axes[1, 1].get_TF_ANN_trining_accuracy_score

class activity_visualization_recorder(visualization_recorder):

    def __init__(self):
        super().__init__()
        self.neu_rec = Recorder(['n[8].avg', 'norm_value', 'output_activity_history[0]', 'activity'], gapwidth=100)
        self.recorderlist.append(self.neu_rec)

    def visualize(self):
        print('rendering activity visualization...')

        fig, axes = plt.subplots(2, 3)
        fig.canvas.set_window_title('activity visualization')

        axes[0, 0].plot(self.neu_rec['n[8].avg'],linewidth=2)
        axes[0, 0].axhline(y=np.average(self.neurons[HomeostaticMechanism].min))
        axes[0, 0].axhline(y=np.average(self.neurons[HomeostaticMechanism].max))
        axes[0, 0].set_xlabel('avg_act')

        axes[1, 0].plot(self.neu_rec['norm_value'],linewidth=2)
        axes[1, 0].set_xlabel('norm_value')

        axes[0, 1].plot(self.neu_rec['output_activity_history[0]'],linewidth=2)
        axes[0, 1].set_xlabel('norm_value')
        axes[1, 1].plot(self.neu_rec['activity'],linewidth=2)
        axes[1, 1].set_xlabel('activity')

        #axes[0, 2].plot(EvalF.get_diversity_score_sliding_window(np.array(self.neu_rec['n.activity'])))
        #axes[1, 2].plot(EvalF.get_sparseness_score_sliding_window(np.array(self.neu_rec['n.activity'])))

        # axes[0, 3].plot(np.array(syn_rec2['syn.GLU_Synapses'])[:, 0:20])#syn_rec.get_block(0, syn_rec.GLU_Synapses)

class input_visualization_recorder(visualization_recorder):

    def __init__(self):#todo: LGN n[8]
        super().__init__()
        self.neu_rec = Recorder(['n[8].avg', 'norm_value', 'output_activity_history[0]', 'activity'], gapwidth=100)
        self.recorderlist.append(self.neu_rec)

    def visualize(self):
        print('rendering input visualization...')

        fig, axes = plt.subplots(2, 4)
        fig.canvas.set_window_title('input visualization')

        axes[0, 0].plot(self.neu_rec['n[8].avg'])
        axes[0, 0].axhline(y=self.neurons[HomeostaticMechanism].min)
        axes[0, 0].axhline(y=self.neurons[HomeostaticMechanism].max)
        axes[0, 0].set_xlabel('avg_act')

        axes[1, 1].plot(self.neu_rec['n.norm_value'])
        axes[1, 1].set_xlabel('norm_value')

        axes[0, 1].plot(self.neu_rec['n.output_activity_history[0]'])
        axes[0, 1].set_xlabel('output_activity_history')
        axes[1, 1].plot(self.neu_rec['n.activity'])
        axes[1, 1].set_xlabel('activity')

        axes[0, 2].imshow(get_reconstruction_activations(np.array(self.neu_rec['activity'])[-10:-1], 10, 10), cmap=plt.cm.gist_gray, interpolation='nearest')

        axes[1, 2].matshow(np.array(self.neu_rec['norm_value'])[-1].reshape((10, 10)))
        axes[1, 2].set_xlabel('last norm_values')


        axes[0, 3].hist(np.array(self.neu_rec['activity'])[:, 0], bins=50)
        axes[0, 3].set_xlabel('first neuron activity distribution')

        axes[1, 3].hist(np.array(self.neu_rec['activity'])[:, 25], bins=50)
        axes[1, 3].set_xlabel('25. neuron activity distribution')

class weight_visualization_recorder(visualization_recorder):

    def __init__(self):
        super().__init__()
        self.syn_rec = SynapseGroupRecorder('GLU_Synapses', gapwidth=100)
        self.recorderlist.append(self.syn_rec)

    def visualize(self):
        print('rendering weight visualization...')

        #fig, axes = plt.subplots(2, 3)
        fig = plt.figure()
        fig.canvas.set_window_title('weight visualization')

        syns = self.neurons.afferent_synapses.get(self.syn_rec.transmitter,[])
        input_size = syns[0].get_src_size()

        data = np.array(self.syn_rec['GLU_Synapses'])

        fig.add_subplot(2, 3, 1).plot(data[:, 0:input_size])
        fig.add_subplot(2, 3, 2).matshow(data[:, 0:input_size].transpose())

        ax=fig.add_subplot(2, 3, 4)
        print(input_size, data.shape)
        ax.hist(data[0, 0:input_size], alpha=0.5, bins=50)
        ax.hist(data[-1, 0:input_size], alpha=0.5, bins=50)

        ax = fig.add_subplot(2, 3, 6, projection='3d')
        plot_3D_histogram(ax, data, 40, 10, x_label_caption='weights')

        #print(data.shape)
        while data.shape[0] < data.shape[1] and data.shape[1]%2 == 0:
            #x = data.shape[0]
            y = data.shape[1]

            data = np.concatenate((data[:, 0:int(y/2)], np.ones((5, int(y/2))), data[:, int(y/2):y]), axis=0)

        fig.add_subplot(2, 3, 3).matshow(data.transpose())




class firing_rate_visualization_recorder(visualization_recorder):

    def __init__(self):
        super().__init__()
        self.neu_rec = Recorder(['output_activity_history[0]', 'pre_inhibition_act', 'activity', 'norm_value'], gapwidth=1)
        self.recorderlist.append(self.neu_rec)

    def visualize(self):
        print('rendering firing rate visualization...')

        fig = plt.figure()
        fig.canvas.set_window_title('firing rate visualization')

        resolution = 100

        act = np.array(self.neu_rec['output_activity_history[0]'])[:, 0]
        act = act[act > 0]
        #plot_histogram(fig.add_subplot(2, 2, 1), act, resolution)
        plot_3D_histogram(fig.add_subplot(2, 2, 1, projection='3d'), act, resolution, 10, x_label_caption='output_activity_history')

        act = np.array(self.neu_rec['pre_inhibition_act'])[:, 0]
        act = act[act > 0]
        #plot_histogram(fig.add_subplot(2, 2, 2), np.array(self.neu_rec['n.pre_inhibition_act'])[:, 0], resolution)
        plot_3D_histogram(fig.add_subplot(2, 2, 2, projection='3d'), act, resolution, 10, x_label_caption='pre_inhibition_act')

        act = np.array(self.neu_rec['activity'])[:, 0]
        act = act[act > 0]
        #plot_histogram(fig.add_subplot(2, 2, 3), np.array(self.neu_rec['n.activity'])[:, 0], resolution)
        plot_3D_histogram(fig.add_subplot(2, 2, 3, projection='3d'), act, resolution, 10, x_label_caption='activity')

        fig.add_subplot(2, 2, 4).plot(self.neu_rec['norm_value'])
        #plot_3D_histogram(fig.add_subplot(2, 2, 4, projection='3d'), np.array(self.neu_rec['n.pre_inhibition_act'])[:, 0], resolution, 10, x_label_caption='pre_inhibition_act')


def visualize_layers(network, Cortex_PC_Neuron_Groups, LGN_PC_Neurons, v_split=False):
    num_groups = len(Cortex_PC_Neuron_Groups)
    fig, axes = plt.subplots(1, num_groups+(len(Cortex_PC_Neuron_Groups)==1))#int(num_groups/2), int(num_groups-num_groups/2))
    for i, group in enumerate(Cortex_PC_Neuron_Groups):
        #axes[i].imshow(get_group_block_mat_reconstruction_image(network, block, 'GLU_Synapses',3, individual_norm=True))

        image = EvalF.sum_cycles(EvalF.get_reconstruction(network, group))

        #image = EvalF.sum_temporal_abstraction_steps(network.get_reconstruction(group, None, LGN_PC_Neurons, 'GLU_Synapses', group.reconstruction_steps, individual_norm=True))
        axes[i].imshow(get_RGB_neuron_weight_image([image, None, None], [group.height*group.depth, group.width], [LGN_PC_Neurons.height*LGN_PC_Neurons.depth, LGN_PC_Neurons.width], v_split_first=v_split))#pattern_f
    plt.tight_layout()

def visualize_input_and_learned_patterns(network, Cortex_PC_Neurons, LGN_PC_Neurons, pattern=None, NN_eval=False, v_split=False):#, split_green_red_overlay=False
    print('rendering input and learned patterns visualization...')

    fig, axes = plt.subplots(2, 2)
    fig.canvas.set_window_title('input and learned patterns')

    image = get_whole_Network_weight_image(Cortex_PC_Neurons, neuron_src_groups=None, individual_norm=True)
    axes[1, 1].imshow(image, interpolation="nearest")

    #print('reconstruction')
    image = network.get_reconstruction(Cortex_PC_Neurons, list(range(Cortex_PC_Neurons.size)), LGN_PC_Neurons, 'GLU_Synapses', 3, individual_norm=True)
    #axes[0, 1].imshow(get_reconstruction_activations(image, 10, 10), cmap=plt.cm.gist_gray, interpolation='nearest')#, interpolation="nearest")

    axes[0, 1].imshow(get_RGB_neuron_weight_image([image, None, None], [Cortex_PC_Neurons.height*Cortex_PC_Neurons.depth, Cortex_PC_Neurons.width], [LGN_PC_Neurons.height*LGN_PC_Neurons.depth, LGN_PC_Neurons.width], v_split_first=v_split))#pattern_f

    #axes[0, 1].imshow(get_combined_RGB_Image(image, None, Cortex_PC_Neurons.width, Cortex_PC_Neurons.height*Cortex_PC_Neurons.depth, LGN_PC_Neurons.width, LGN_PC_Neurons.height*LGN_PC_Neurons.depth, transform_mat_func=pattern_f), interpolation='nearest')  # , interpolation="nearest")
    axes[0, 1].set_xlabel('weights')

    #print('reconstruction act')
    axes[0, 0].imshow(get_reconstruction_activations(np.clip(np.array(LGN_PC_Neurons[NeuronActivator].get_pattern_samples(10)), 0, 1), LGN_PC_Neurons.width, LGN_PC_Neurons.height * LGN_PC_Neurons.depth), cmap=plt.cm.gist_gray, interpolation='nearest')
    axes[0, 0].set_xlabel('input')

    if NN_eval:
        for i in range(3):
            axes[1, 1].plot(EvalF.get_TF_ANN_training_accuracy_score(network, [Cortex_PC_Neurons], [LGN_PC_Neurons[NeuronActivator].TNAPatterns[0]], 1000, 1000))

    #if not split_green_red_overlay:
    #    big_img = EvalF.get_pattern_response_image(network, LGN_PC_Neurons[TRENNeuronActivator].TNAPatterns[0], LGN_PC_Neurons, [Cortex_PC_Neurons])

        #big_img = EvalF.get_sorted_overview_image(network, [Cortex_PC_Neurons], [LGN_PC_Neurons[TRENNeuronActivator].TNAPatterns[0]],100, LGN=LGN_PC_Neurons)

        #axes[1, 0].matshow(big_img, cmap=plt.cm.gray)
        #axes[1, 0].set_xlabel('network resopnses')


def plot_network(network, blocks=None):
    fig = plt.figure()
    ax = fig.add_subplot(111)#, projection='3d'

    arrow_width=1
    arrow_lenth=1

    #img = mpimg.imread('../Data/Img/5.png')
    #ax.imshow(img)

    #x=[20, 100, 100, 110, 110, 100, 100, 80, 80, 60]
    #y=[0,  0,   10,  10,  30,  30,  40,  40, 45, 45]
    #z=[0,  0,   0,   0,   0,   0,   0,   0,  0,  0]
    #plt.plot(x,y,z)

    def pol2cart(rho, phi):
        x = rho * np.cos(phi)
        y = rho * np.sin(phi)
        return x, y

    for ng in network.NeuronGroups:
        ax.scatter(ng.x, ng.y)#, ng.z
        ax.text(np.min(ng.x), np.average(ng.y), ng.tags[0], color="blue")

    if blocks is not None:
        for ng in blocks:
            ax.scatter(ng.x, ng.y)#, ng.z
            ax.text(np.min(ng.x), np.average(ng.y), ng.tags[0])

    for sg in network.SynapseGroups:
        mul = 1
        color = 'green'
        if 'GABA' in sg.tags:#hasattr(sg, 'GABA_Synapses'):
            color = 'red'
            mul = -1

        if sg.src is not sg.dst:
            a_x = np.average(sg.src.x)+mul
            a_y = np.average(sg.src.y)
            d_x = np.average(sg.dst.x)+mul
            d_y = np.average(sg.dst.y)

            plt.plot([a_x, d_x], [a_y, d_y], color=color)#[np.average(sg.src.z), np.average(sg.dst.z)]
            plt.arrow(a_x, a_y, d_x-a_x, d_y-a_y, color=color, head_width=arrow_width, head_length=arrow_lenth)
        else:

            vec = np.array([sg.src.x, sg.src.y, sg.src.z])
            av = np.average(vec, axis=1)

            m = np.max(vec, axis=1)

            if 'GABA' in sg.tags:
                m[1] = np.min(vec[1])

            center = (av + m) / 2

            dist = np.linalg.norm(center-m, ord=2)

            xps = []
            yps = []
            zps = []

            for i in range(140):
                x, y = pol2cart(dist*0.7, np.deg2rad((i-10)*mul))
                xps.append(x+center[0])
                yps.append(y+center[1])
                zps.append(center[2])

            plt.plot(xps, yps, color=color)#, z
            plt.arrow(xps[-2], yps[-2], xps[-1]-xps[-2], yps[-1]-yps[-2], color=color, head_width=arrow_width, head_length=arrow_lenth)


    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    #ax.set_zlabel('Z Label')

    #ax.set_xlim(-5, 5)
    #ax.set_ylim(-2, 12)
    #ax.set_zlim(0, 100)

    plt.show()

def plot(data):
    plt.plot(data)

def matshow(data):
    plt.matshow(data)

def imshow(data):
    plt.imshow(data, cmap=plt.cm.gist_gray, interpolation='nearest')

def run_and_visualize(behaviors, network, Cortex_PC_Neurons, iterations):
    network.add_behaviors_to_neuron_group(behaviors, Cortex_PC_Neurons)
    network.simulate_iterations(100, iterations / 100, True)
    for b in behaviors:
        b.visualize()


def show():
    plt.show()
