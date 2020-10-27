from SORNSim.NetworkBehaviour.Structure.Structure import *
from SORNSim.NetworkCore.Synapse_Group import *
from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkBehaviour.Input.Images.MNIST_Patterns import *

import os
import psutil

def print_mem(message=''):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)
    print(message, 'Memory:', mem)
    return mem

def split_connect(src_group, dst_group, x_blocks, y_blocks, receptive_field, network, syn_type):
    if x_blocks>1 or y_blocks>1:
        min_x=np.min(dst_group.x)
        max_x=np.max(dst_group.x)+0.0001
        x_steps = np.arange(x_blocks + 1) * ((max_x - min_x)/x_blocks)+min_x

        min_y=np.min(dst_group.y)
        max_y=np.max(dst_group.y)+0.0001
        y_steps = np.arange(y_blocks+1) * ((max_y - min_y)/y_blocks)+min_y

        #print(x_steps,y_steps)

        #block_mat = np.empty(shape=(y_blocks, x_blocks), dtype=object)
        for y in range(y_blocks):
            for x in range(x_blocks):
                dst = dst_group.subGroup((dst_group.x >= x_steps[x]) * (dst_group.x < x_steps[x+1]) * (dst_group.y >= y_steps[y]) * (dst_group.y < y_steps[y+1]))
                src = src_group.subGroup((src_group.x >= (x_steps[x]-receptive_field)) * (src_group.x < (x_steps[x+1]+receptive_field)) * (src_group.y >= (y_steps[y]-receptive_field)) * (src_group.y < (y_steps[y+1]+receptive_field)))

                sg=SynapseGroup(src, dst, receptive_field, net=network).add_tag(syn_type)
    else:
        sg=SynapseGroup(src_group, dst_group, receptive_field, net=None).add_tag(syn_type)
        network.SynapseGroups.append(sg)

    #return block_mat


#[behaviour, size, split, glu_rec_dst, gab_rec, glu_ff, gab_ff, glu_fb, gab_fb]
def create_Network_Structure(network, layer_param_dicts, subnetwork_optimization=True):

    inp_width = network.getNG('input')[0].width
    inp_height = network.getNG('input')[0].height

    input_group = network.getNG('input')[0]

    for i, l_dict in enumerate(layer_param_dicts):
        split=l_dict['split']
        #if subnetwork_optimization:
        #    split = int(l_dict['size'] / 10)
        #else:
        #    split = 1

        group = NeuronGroup(NeuronDimension(width=l_dict['size'], height=l_dict['size'], depth=1), l_dict['behaviour'], net=network).add_tag('Cortex').add_tag('V{}'.format(i))
        group.reconstruction_steps = i+1
        group[NeuronDimension].scale(inp_width / l_dict['size'], inp_height / l_dict['size'])#.move(10, 100)

        # recurrent
        if l_dict['glu_rec'] is not None: split_connect(group, group, split, split, l_dict['glu_rec'], network, 'GLU')
        if l_dict['gab_rec'] is not None: split_connect(group, group, split, split, l_dict['gab_rec'], network, 'GABA')

        # feed forward
        if l_dict['glu_ff'] is not None: split_connect(input_group, group, split, split, l_dict['glu_ff'], network, 'GLU')
        if l_dict['gab_ff'] is not None: split_connect(input_group, group, split, split, l_dict['gab_ff'], network, 'GABA')

        # feed back
        if l_dict['glu_fb'] is not None: split_connect(group, input_group, split, split, l_dict['glu_fb'], network, 'GLU')
        if l_dict['gab_fb'] is not None: split_connect(group, input_group, split, split, l_dict['gab_fb'], network, 'GABA')

        input_group = group


def get_neuron_group_blocks(block_width, block_height, block_group_width, block_group_height, behaviour, network, tag='Cortex_block', scale_x=1,scale_y=1):
    block_mat = np.empty(shape=(block_group_height, block_group_width), dtype=object)
    for y in range(block_group_height):
        for x in range(block_group_width):
            block_mat[y, x] = NeuronGroup(NeuronDimension(width=block_width, height=block_height, depth=1), behaviour, net=network).add_tag(tag + '(x:{},y:{})'.format(x, y))
            block_mat[y, x][NeuronDimension].move((x - (block_group_width - 1) / 2) * block_width, (y - (block_group_height - 1) / 2) * block_height)
            block_mat[y, x][NeuronDimension].scale(scale_x, scale_y)
    return block_mat



def get_evo_param(default, individual):
    if len(individual) > 0:
        param = individual[0]
        individual.pop(0)
        return param
    else:
        print(default)
        return default

def get_default_Input_Pattern_Neurons(input_width=1, input_height=1,input_depth=1, preprocessing_steps=-1, write_to='glu_inter_gamma_activity', patterns='cross', predefined_patterns=[]):
    if preprocessing_steps > 0:
        activator = NeuronPreprocessedActivator(write_to=write_to)
    else:
        activator = NeuronActivator(write_to=write_to)

    if 'cross' in patterns:
        lines1 = Line_Patterns(group_possibility=1.0, grid_width=input_width, grid_height=input_height, center_x=input_width / 2, center_y=list(range(input_height)), degree=0, line_length=input_width + input_height)
        lines2 = Line_Patterns(group_possibility=1.0, grid_width=input_width, grid_height=input_height, center_x=list(range(10)), center_y=input_height / 2, degree=90, line_length=input_width + input_height)
        activator.add_patternGroups([lines1, lines2])

    if 'rotate' in patterns:
        lines1 = Line_Patterns(individual_possibility=1 / 18, group_possibility=0.0, grid_width=input_width, grid_height=input_height, center_x=input_width / 2, center_y=input_height / 2, degree=np.array(range(18)) * 10, line_length=input_width + input_height)
        activator.add_patternGroups([lines1])

    if 'noise' in patterns:
        noise = Noise_Pattern(grid_width=input_width, grid_height=input_height, density=0.1)
        activator.add_patternGroups([noise])

    activator.add_patternGroups(predefined_patterns)

    #pat = np.random.rand(10, 10).flatten()
    #print(activator.get_pattern_differences(pat))

    behaviour = {
        1: activator,
        #2: TREN_input_weighting(),
        8: ActivityBuffering(store_input=False, min_buffersize=6),
        #8: HomeostaticMechanism(range_end=500, inc=0.5, dec=0.5, pattern_chance=0.01, target_max=1)
        #8: HomeostaticMechanism(range_end=550, inc=1.84, dec=4.92, pattern_chance=0.01, target_max=1)
    }

    input_neuron_group = NeuronGroup(NeuronDimension(width=input_width, height=input_height, input_pattern_groups=activator.TNAPatterns, depth=input_depth), behaviour).add_tag('input')  #

    if preprocessing_steps > 0:
        activator.preprocess(preprocessing_steps, input_neuron_group)

    return input_neuron_group

def format_array(x, format='{:.3f}'):
    return [format.format(i) for i in x]
