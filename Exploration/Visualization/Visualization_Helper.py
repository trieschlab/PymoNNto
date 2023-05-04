import numpy as np
from math import *

#ms_per_step=2

#def step_ms(x):
#    return x*ms_per_step

def SpikeTrain_ISI(x):
    result = []
    last = -1
    for i, x in enumerate(x):
        if x > 0:
            if last!=-1:
                result.append(i-last)
            last=i

    return result

def get_bins(number, xrightlim):
    #xrightlim = max_neuron_frequency()
    binwidth = xrightlim / number
    return np.arange(0, xrightlim, binwidth)

def get_distribution_markers(data):
    mean = np.mean(data)
    std = np.std(data)
    return mean-std, mean, mean+std

def plot_histogram(axis, data, bins, mean=True, std=True):
    axis.hist(data, bins=bins)
    for x,c in zip(get_distribution_markers(data), ['green', 'red', 'green']):
        axis.axvline(x=x, color=c)


def plot_3D_histogram(axis, data, bins, time_steps, mean=True, std=True, x_label_caption='Spike Rate Hz'):

    for i in range(time_steps):
        z = i * 10

        step = int(len(data) / time_steps)
        ys = data[i * step:(i + 1) * step]
        hist, bins = np.histogram(ys, bins=bins)
        xs = (bins[:-1] + bins[1:]) / 2
        width = bins[1] - bins[0]

        c = np.random.rand(3)
        axis.bar(xs, hist, color=c, ec=c, alpha=0.8, width=width, zdir='y', zs=z)

    axis.set_xlabel(x_label_caption)
    axis.set_zlabel('Nr')
    axis.set_ylabel('Recording Blocks')

    axis.set_yticklabels([])

#def plot_3D_hist(act):
#    fig = plt.figure()
#    ax = fig.add_subplot(111, projection='3d')
#    plot_3D_histogram(ax, act, 40, 10)
#    plt.show()



def get_reconstruction_activations(origin_activations, input_grid_width, input_grid_height):
    dim = int(floor(sqrt(len(origin_activations))))
    result_pic_width = (dim + 1) * (input_grid_width + 1)
    result_pic_height = (dim + 1) * (input_grid_height + 1)

    # print(dim)
    # print(result_pic_width)
    # print(result_pic_height)

    border_value = np.max(origin_activations)

    x = 0
    y = 0

    result = np.ones((result_pic_height, result_pic_width)) * border_value

    # print(origin_activations)

    for activations in origin_activations:
        inp_syn = activations[0:input_grid_width * input_grid_height].reshape((input_grid_height, input_grid_width))
        result[y * (input_grid_height + 1):y * (input_grid_height + 1) + input_grid_height, x * (input_grid_width + 1):x * (input_grid_width + 1) + input_grid_width] = inp_syn
        x += 1
        if x > dim:
            y += 1
            x = 0

    return result



#def plot_reconstruction_activations(origin_activations, input_grid_width, input_grid_height, ax=None):
#    result=get_reconstruction_activations(origin_activations, input_grid_width, input_grid_height)

    # colormap = matplotlib.cm.gist_gray
#    colormap = plt.cm.gist_gray

    # colormap.set_bad(color='red')
    # result = np.ma.array(result, mask=(result == np.array(0)))

#    if ax is not None:
#        ax.imshow(result, cmap=colormap, interpolation='nearest')
#    else:
#        plt.imshow(result, cmap=colormap, interpolation='nearest')


# def get_whole_Network_reconstruction_image(self, neuron_dst_group, input_source, x_elements, y_elements, element_rows=-1, element_cols=-1, add_activity=True, include_GABA=True):
#    if element_rows == -1: element_rows = input_source.width
#    if element_cols == -1: element_cols = input_source.height
#
#    reconstructions=self.get_reconstruction(, source_group_neuron_indexes, input_source, synapse_weight_attribute_name, recostruction_steps)
#
#    return self.get_combined_RGB_Image(elements_g=weights, elements_r=inh_synapses, element_rows=element_rows, element_cols=element_cols, x_elements=x_elements, y_elements=y_elements)

# rec=network.get_reconstruction(Cortex_PC_Neurons, list(range(10)), LGN_PC_Neurons, 'GLU_Synapses', 1)#{'GLU_Synapses':1,'GABA_Synapses':-1}, just_nuerons=[] just_synapses=[]
# network.plot_reconstruction_activations(rec, 10, 10)
# plt.show()


def dif_width_vstack(matrixes, reshapes, max_width):
    #print(reshapes, max_width)

    for i in range(len(matrixes)):
        if reshapes[i][0] < max_width:
            t = []
            for e in range(len(matrixes[i])):
                t.append(np.hstack([matrixes[i][e].reshape(reshapes[i][0], reshapes[i][1]), np.zeros((max_width-reshapes[i][0], reshapes[i][1]))]).flatten())
            matrixes[i] = np.array(t)

    return np.hstack(matrixes)

def upscale(img,factor):
    h = img.shape[0]
    w = img.shape[1]
    r = img[:,:,0].repeat(factor).reshape((h, w*factor)).repeat(factor, axis=0).reshape((h*factor, w*factor))
    g = img[:,:,1].repeat(factor).reshape((h, w*factor)).repeat(factor, axis=0).reshape((h*factor, w*factor))
    b = img[:,:,2].repeat(factor).reshape((h, w*factor)).repeat(factor, axis=0).reshape((h*factor, w*factor))
    return np.stack([r, g, b],axis=-1)

def get_whole_Network_weight_image(neuron_dst_group, plot_inh_synapses=False, neuron_src_groups=None, add_activity=False, individual_norm=False, exc_weight_attr='GLU_Synapses', inh_weight_attr='GABA_Synapses', activations=None):

    exc_synapses = []
    inh_synapses = []

    shapes = []

    temp_inh_syns = neuron_dst_group.synapses(afferent, 'GABA')

    for syn in neuron_dst_group.synapses(afferent, 'GLU'):
        if neuron_src_groups is None or syn.src in neuron_src_groups:

            found = None
            for inh_syn in temp_inh_syns:
                if syn.src == inh_syn.src and syn.dst == inh_syn.dst:
                    found = inh_syn

            if found is not None:
                inh_synapses.append(getattr(found, inh_weight_attr).copy())
                #inh_synapses.append(found.GABA_Synapses.copy())
            else:
                inh_synapses.append(np.zeros(getattr(syn, exc_weight_attr).shape))
                #inh_synapses.append(np.zeros(syn.GLU_Synapses.shape))

            #print(syn.src.width, syn.src.height)

            exc_synapses.append(getattr(syn, exc_weight_attr).copy())
            shapes.append(np.array([syn.src.width, syn.src.height*syn.src.depth]))

    shapes = np.array(shapes)

    #print(shapes, shapes[:, 0])
    max_cols = np.max(shapes[:, 0])
    row_sum = np.sum(shapes[:, 1])

    weights = dif_width_vstack(exc_synapses, shapes, max_cols)
    inh_weights = dif_width_vstack(inh_synapses, shapes, max_cols)

    #print(weights.shape, inh_weights.shape, row_sum, max_cols)

    if individual_norm:
        weights = weights/np.max(weights, axis=1)[:, None]

    #print(neuron_dst_group.depth)

    return get_RGB_neuron_weight_image([inh_weights, weights], weight_dim=[row_sum, max_cols], neuron_dim=[neuron_dst_group.height*neuron_dst_group.depth, neuron_dst_group.width], activities=activations)
    #return get_combined_RGB_Image(g_weight_mat=weights, r_weight_mat=inh_weights, element_rows=max_cols, element_cols=row_sum, x_elements=neuron_dst_group.width, y_elements=neuron_dst_group.height*neuron_dst_group.depth)


def get_group_block_mat_reconstruction_image(network, source_block, synapse_weight_attribute_name, recostruction_steps, individual_norm=False, print_status=False):

    if type(source_block) == np.ndarray:
        source_block=list(source_block.flatten())
    elif not type(source_block) == list:
        source_block=[source_block]

    #reconstructions=
    #for neuron_group in source_block:


    #image = network.get_reconstruction(group, None, LGN_PC_Neurons, 'GLU_Synapses', 3, individual_norm=True)
    # axes[i].imshow(get_RGB_neuron_weight_image([image, None, None], [group.height*group.depth, group.width], [LGN_PC_Neurons.height*LGN_PC_Neurons.depth, LGN_PC_Neurons.width], v_split_first=v_split))#pattern_f




def get_RGB_neuron_weight_image_pattern(rgb_weights, neuron_dim, pattern):
    return get_RGB_neuron_weight_image(rgb_weights, neuron_dim, pattern.get_pattern_dimension(), pattern.reconstruct_pattern)


def get_RGB_neuron_weight_image(rgb_weights, neuron_dim, weight_dim, weight_transform_func=None, v_split_first=False, activities=None):

    if weight_transform_func is None:
        temp=weight_dim.copy()
        weight_transform_func = lambda mat: mat.reshape(temp[0], temp[1])
    #else:


    if v_split_first:
        weight_dim[0]=int(weight_dim[0]/2)

    for w in rgb_weights:
        if w is not None:
            scale = 1
            w_max = np.max(w)
            if w_max > 0:
                scale = 1 / w_max
            w *= scale

    result_height = neuron_dim[0] * weight_dim[0] + neuron_dim[0] + 1
    result_width = neuron_dim[1] * weight_dim[1] + neuron_dim[1] + 1

    result = np.ones((result_height, result_width, 3))

    for y in range(neuron_dim[0]):
        for x in range(neuron_dim[1]):

            element_id = x + y * neuron_dim[0]

            ymin = (1 + y) + y * weight_dim[0]
            ymax = (1 + y) + (y + 1) * weight_dim[0]
            xmin = (1 + x) + x * weight_dim[1]
            xmax = (1 + x) + (x + 1) * weight_dim[1]

            result[ymin:ymax, xmin:xmax, :] *= 0

            if v_split_first:
                result[ymin:ymax, xmin:xmax, 0:2] = vsplit(weight_transform_func(rgb_weights[0][element_id]))
            else:
                for i, w in enumerate(rgb_weights):
                    if w is not None:
                        transformed = weight_transform_func(w[element_id])
                        result[ymin:ymax, xmin:xmax, i] = transformed

            if activities is not None:
                result[ymin:ymax, xmin:xmax, 2] += activities[element_id]

    return result

def vsplit(weight_mat):
    result = np.zeros((int(weight_mat.shape[0]/2), weight_mat.shape[1], 2))
    result[:, :, 0]=weight_mat[0:int(weight_mat.shape[0] / 2), :]
    result[:, :, 1]=weight_mat[int(weight_mat.shape[0] / 2):, :]
    return result

#def v_split_top(weight_mat):
#    return weight_mat[0:int(weight_mat.shape[0] / 2), :]

#def v_split_bottom(weight_mat):
#    return weight_mat[int(weight_mat.shape[1] / 2):, :]

#reconstruct_pattern
'''
def get_combined_RGB_Image(r_weight_mat=None, g_weight_mat=None, x_elements=0, y_elements=0, element_rows=0, element_cols=0, activities=None, h_split_rmat=False, transform_mat_func=None):

    if h_split_rmat:
        #r_weight_mat = v_split_top(r_weight_mat)
        #g_weight_mat = v_split_bottom(r_weight_mat)
        element_cols = int(element_cols / 2)

    if transform_mat_func is None:
        print('tmf')
        def default_transform_mat_func(mat):
            return mat.reshape(element_cols, element_rows)
        transform_mat_func = default_transform_mat_func
    else:
        dim = transform_mat_func(None)
        element_cols = dim[0]
        element_rows = dim[1]


    result_width = x_elements * element_rows + x_elements + 1
    result_height = y_elements * element_cols + y_elements + 1

    result = np.ones((result_height, result_width, 3))

    if r_weight_mat is not None:
        r_scale = 1
        r_max = np.max(r_weight_mat)
        if r_max > 0:
            r_scale = 1 / r_max

    if g_weight_mat is not None:
        g_scale = 1
        g_max = np.max(g_weight_mat)
        if g_max > 0:
            g_scale = 1 / g_max

    for y in range(y_elements):
        for x in range(x_elements):

            element_id = x + y * x_elements

            xmin = (1 + x) + x * element_rows
            xmax = (1 + x) + (x + 1) * element_rows
            ymin = (1 + y) + y * element_cols
            ymax = (1 + y) + (y + 1) * element_cols

            if r_weight_mat is not None:
                if h_split_rmat:
                    result[ymin:ymax, xmin:xmax, 0] = v_split_top(transform_mat_func(r_weight_mat[element_id])) * r_scale
                else:
                    result[ymin:ymax, xmin:xmax, 0] = transform_mat_func(r_weight_mat[element_id]) * r_scale
            else:
                result[ymin:ymax, xmin:xmax, 0] *= 0

            if g_weight_mat is not None:
                if h_split_rmat:
                    result[ymin:ymax, xmin:xmax, 0] = v_split_bottom(transform_mat_func(r_weight_mat[element_id])) * r_scale
                else:
                    result[ymin:ymax, xmin:xmax, 1] = transform_mat_func(g_weight_mat[element_id]) * g_scale
            else:
                result[ymin:ymax, xmin:xmax, 1] *= 0

            result[ymin:ymax, xmin:xmax, 2] *= 0
            if activities is not None:
                result[ymin:ymax, xmin:xmax, 2] += activities[element_id]

    return result



'''