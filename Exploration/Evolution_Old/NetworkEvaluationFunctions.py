import numpy as np

#import matplotlib.pyplot as plt

class Evaluator:

    def __init__(self, activator):
        self.activator = activator

    def get_pattern_differences(self, learned_pattern):
        result = []
        slp=np.sum(learned_pattern)
        for pattern_group in self.activator.TNAPatterns:
            for pattern in pattern_group.patterns:
                if slp == 0:
                    result.append(len(learned_pattern))
                else:
                    normed = learned_pattern*(np.sum(pattern)/slp)
                    result.append(np.sum(np.abs(pattern-normed)))
        return np.array(result)

    def get_pattern_differences_score(self, learned_pattern):
        differences = self.get_pattern_differences(learned_pattern)
        return np.sum(differences)

    def get_pattern_count_score(self, learned_pattern, threshold=0.5):
        differences = self.get_pattern_differences(learned_pattern)
        return np.sum(differences > (np.max(differences)*threshold))

def get_Autoencoder_Score(network, NeuronGroups, cycles):

    network.learning_off()

    input=network.getNG('input')[0]
    pattern_group=input[1].TNAPatterns[0]

    delay = 0
    for ng in NeuronGroups:
        delay = max(delay, ng.reconstruction_steps)

    input_id_buffer = np.ones(delay)*-1

    result_score=0

    for i in range(cycles+delay):
        network.simulate_iteration()
        if input_id_buffer[-1] != -1:
            reconstruction = np.sum(network.get_network_activity_reconstruction(input, 'GLU_Synapses', delay), axis=0).flatten()
            input_pattern = np.array(pattern_group.patterns[int(input_id_buffer[-1])]).copy().flatten()

            reconstruction = reconstruction/np.sum(reconstruction)
            input_pattern = input_pattern/np.sum(input_pattern)

            result_score += np.sum(np.abs(reconstruction-input_pattern))

            #plt.matshow(reconstruction.reshape(2*28, 28))
            #plt.matshow(input_pattern.reshape(2*28, 28))
            #plt.show()

        input_id_buffer = np.roll(input_id_buffer, 1)
        input_id_buffer[0] = pattern_group.current_pattern_index

    result_score = result_score/cycles/2

    network.learning_on()

    return 1-result_score


#####################
#Diversity
#####################


def flatten_cycles(reconstruction): #[neuron_id, gamma_cycle, recon_t] => [neuron_id, flattened_recon]
    return reconstruction.reshape((reconstruction.shape[0], reconstruction.shape[1]*reconstruction.shape[2]))

def sum_cycles(reconstruction, norm=True): #[neuron_id, recon_timestep, recon_t] => [neuron_id, sumed_recon]
    s=np.sum(reconstruction, axis=1)
    if norm:
        s = s / np.max(s, axis=1)[:, None]
    return s

def get_reconstruction(network, NeuronGroup):
    return network.get_reconstruction(NeuronGroup, None, network.getNG('input')[0], 'GLU_Synapses', NeuronGroup.reconstruction_steps, individual_norm=True)


#def get_Group_Weighted_total_neuron_diversity_metric(network, NeuronGroups, reconstruction=False):
#    results = get_neuron_weight_diversity_metric(network, NeuronGroups, reconstruction)
#    return np.sum(np.array([np.array(score)/ng.size for ng, score in zip(NeuronGroups, results)]))

def get_variance_score(matrix, max, exponent=5):
    vars = np.std(matrix/np.sum(matrix, axis=1)[:, None], axis=1)
    score = 1 - vars
    score = np.power(score, exponent)
    score = np.clip(score, 0, max)
    return np.sum(score)/len(score)

#print(get_variance_score(np.array([[12, 0, 0, 0, 0, 0], [1, 2, 1, 1, 3, 4], [2, 2, 2, 2, 2, 2], [4, 4, 4, 0, 0, 0]]), 1.9))

#def get_neuron_weight_diversity_metric(network, NeuronGroups, reconstruction=False):
#    result = []
#    for neuron_group in NeuronGroups:
#        if reconstruction:
#            rec=network.get_reconstruction(neuron_group, None, network.getNG('input')[0], 'GLU_Synapses', neuron_group.reconstruction_steps, individual_norm=True)
#            #Todo: better function
#            var_score=get_variance_score(rec, 1.0)
#            print(var_score)
#            result.append(get_diversity_score(rec) * var_score)
#        else:
#            group_metrics = []
#            for s in neuron_group.afferent_synapses['GLU']:
#                group_metrics.append(get_diversity_score(s.GLU_Synapses))
#
#            result.append(group_metrics)
#    return result

def get_diversity_score_sliding_window(mat_timeline, block_size=100):
    sw=timeline_to_sliding_window(mat_timeline, block_size)
    return get_diversity_score_timeline(sw)

def get_diversity_score_timeline(mat_timeline, reshape=None):
    return np.array([get_diversity_score(m, reshape) for m in mat_timeline])


def get_diversity_score(matrix, reshape=None):
    if reshape is not None:
        mat = matrix.reshape(reshape)
    else:
        mat = matrix

    d = np.sum(mat, axis=1)
    d[d == 0] = 1
    mat = mat/d[:, None]

    metric = 0
    for i in range(mat.shape[0]):
        #cells_with_content = np.sum(matrix[i] > 0.0)

        metric += np.sum(np.linalg.norm(mat-mat[i], axis=1))

        #difference=0
        #for j in range(mat.shape[0]):
        #    difference += np.linalg.norm(mat[i] - mat[j])
        #metric += difference #np.sum(mat[i])*

    return metric/(mat.shape[0])#d

#####################
#Sparseness
#####################

def get_sparseness_score_sliding_window(mat_timeline, block_size=100):
    sw = timeline_to_sliding_window(mat_timeline, block_size)
    return get_sparseness_score_timeline(sw)

def get_sparseness_score_timeline(activity_trace_timeline):
    return np.array([get_sparseness_score(m) for m in activity_trace_timeline])

def get_sparseness_score(activity_trace):
    d = np.sum(activity_trace)
    if d == 0:
        return 0
    else:
        activity_trace = activity_trace/d
        return np.sum(np.power(activity_trace, 2.0))


#####################
#ANN evaluation
#####################

def get_TF_ANN_training_accuracy_score(network, NeuronGroups, PatternGroups, network_iterations, trainingsteps, max_gamma_cycles_for_pattern = 2):
    activity, labels = network.get_random_network_responses(network_iterations + max_gamma_cycles_for_pattern + 1, NeuronGroups, PatternGroups)

    activity_blocks = activity_trace_to_time_blocks(np.array(activity), max_gamma_cycles_for_pattern)
    one_hot_ids = id_vec_to_one_hot_vec(labels)

    scores = get_training_score(activity_blocks, one_hot_ids, trainingsteps)

    return scores


def get_batch(input, output, batchsize=100, test=False):
    rnd = np.random.randint(0, input.shape[0] - batchsize * 2)
    if test:
        rnd = input.shape[0] - batchsize
    return input[rnd:rnd + batchsize], output[rnd:rnd + batchsize]

def get_training_score(input, output, trainingsteps):
    import tensorflow as tf

    with tf.variable_scope("network"):
        # mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

        x = tf.placeholder(tf.float32, shape=[None, input.shape[1]])
        W = tf.get_variable("weights", shape=[input.shape[1], output.shape[1]], initializer=tf.glorot_uniform_initializer())
        b = tf.get_variable("bias", shape=[output.shape[1]], initializer=tf.constant_initializer(0.1))
        y = tf.nn.relu(tf.matmul(x, W) + b)
        y_ = tf.placeholder(tf.float32, [None, output.shape[1]])

        cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=y, labels=y_)
        train_step = tf.train.GradientDescentOptimizer(0.001).minimize(cross_entropy)

        correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        sess = tf.InteractiveSession()
        tf.global_variables_initializer().run()

        tx, ty = get_batch(input, output, test=True)

        accuracies = []

        for step in range(trainingsteps):
            batch_xs, batch_ys = get_batch(input, output)  # mnist.train.next_batch(100)
            sess.run(train_step, feed_dict={x: batch_xs, y_: batch_ys})

            acc = sess.run(accuracy, feed_dict={x: tx, y_: ty})
            accuracies.append(acc)

            if step % 200 == 0:
                print("training step: {} | model accuracy: {}".format(step, acc))

        sess.close()#???????

    tf.reset_default_graph()

    return accuracies

#####################
#Activity Trace Image generation
#####################

def get_pattern_response(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = 0, pattern_repeat=1, combinations=False, return_labels=False):
    activity, labels = network.get_network_responses(pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern=3+max_gamma_cycles_for_pattern, pattern_repeat=pattern_repeat, combinations=combinations)
    activity=remove_trace_delay(activity, 2)
    activity=activity_trace_to_time_blocks(np.array(activity), max_gamma_cycles_for_pattern)
    if return_labels:
        return activity, labels
    else:
        return activity

def get_pattern_response_score(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = 0, pattern_repeat=1, combinations=False):
    activity=get_pattern_response(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = max_gamma_cycles_for_pattern, pattern_repeat=pattern_repeat, combinations=combinations)
    return get_diversity_score(activity)

def get_pattern_response_image(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = 0, pattern_repeat=1, combinations=False):
    activity, labels=get_pattern_response(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = max_gamma_cycles_for_pattern, pattern_repeat=pattern_repeat, combinations=combinations, return_labels=True)

    s = sorted(zip(labels, activity), key=lambda i: i[0], reverse=True)
    ids = [l for (l, a) in s]
    activity = [a for (l, a) in s]

    one_hot_ids = id_vec_to_one_hot_vec(ids)

    #print(np.array(one_hot_ids),np.zeros((np.array(activity).shape[0], 5)).shape, np.array(activity).shape)

    return np.concatenate((np.array(one_hot_ids) * 0.4, np.zeros((np.array(activity).shape[0], 5)) + 0.2, np.array(activity)), axis=1)



#def get_pattern_response_score(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = 0, combinations=False):
#    activity, labels = network.get_network_responses(pattern_group, target_activation_neurons, target_recording_neuron_groups, 3+max_gamma_cycles_for_pattern, combinations=combinations)
#    activity=remove_trace_delay(activity, 2)

#    activity = activity_trace_to_time_blocks(np.array(activity), max_gamma_cycles_for_pattern)

#    return get_diversity_score(activity)

#def get_pattern_response_image(network, pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern = 0, pattern_repeat=1, combinations=False):
#    activity, labels = network.get_network_responses(pattern_group, target_activation_neurons, target_recording_neuron_groups, max_gamma_cycles_for_pattern=3+max_gamma_cycles_for_pattern, pattern_repeat=pattern_repeat, combinations=combinations)

#    activity = remove_trace_delay(activity, 2)
#    activity = activity_trace_to_time_blocks(np.array(activity), max_gamma_cycles_for_pattern)

    #print(get_diversity_score(activity))

#    s = sorted(zip(labels, activity), key=lambda i: i[0], reverse=True)
#    ids = [l for (l, a) in s]
#    activity = [a for (l, a) in s]

#    one_hot_ids = id_vec_to_one_hot_vec(ids)

#    return np.concatenate((np.array(one_hot_ids) * 0.4, np.zeros((np.array(activity).shape[0], 5)) + 0.2, np.array(activity)), axis=1)


def get_sorted_overview_image(network, NeuronGroups, PatternGroups, iterations, max_gamma_cycles_for_pattern = 4, LGN=None):

    activity, labels = network.get_network_responses(PatternGroups[0], LGN, NeuronGroups, max_gamma_cycles_for_pattern)
    #activity, labels = network.get_random_network_responses(iterations + max_gamma_cycles_for_pattern + 1, NeuronGroups, PatternGroups)

    activity = activity_trace_to_time_blocks(np.array(activity), max_gamma_cycles_for_pattern)

    s = sorted(zip(labels, activity), key=lambda i: i[0], reverse=True)
    ids = [l for (l, a) in s]
    activity = [a for (l, a) in s]

    one_hot_ids = id_vec_to_one_hot_vec(ids)

    return np.concatenate((np.array(one_hot_ids) * 0.4, np.zeros((np.array(activity).shape[0], 5)) + 0.2, np.array(activity)), axis=1)


#####################
#Helper
#####################

def remove_trace_delay(trace, delay):
    return trace[delay:trace.shape[0]]

def activity_trace_to_time_blocks(trace, cycles):
    result = []

    for i in range(trace.shape[0] - cycles - 1):
        result.append(trace[i:i + 1 + cycles].copy().flatten())

    return np.array(result)


def id_vec_to_one_hot_vec(ids):
    id_list = []
    for id in ids:
        if not id in id_list:
            id_list.append(id)

    result = np.zeros((len(ids), len(id_list)))

    for i in range(len(ids)):
        id_pos = id_list.index(ids[i])
        result[i, id_pos] = 1

    return result

def timeline_to_sliding_window(timeline, block_size=100):
    mat = []
    for i in range(timeline.shape[0] - block_size):
        mat.append(timeline[i:i + block_size])
    return np.array(mat)






















#patricks code:
'''
def norm(data):
    maxval = np.amax(data)
    minval = np.amin(data)

    if(maxval < -1*minval):
        maxval = -1*minval

    if (maxval == 0):
        return data
    else:
        return data / maxval

def discrimination(matrix):

    oldmatrix = matrix
    matrix = norm(matrix)

    def discriminate(line):
        maxi = np.argmax(line)

        sum = 0
        for i, val in enumerate(line):
            if (i == maxi):
                sum += val
            else:
                sum -= val

        return sum

    row_sums = list(map(discriminate, matrix))
    col_sums = list(map(discriminate, np.transpose(matrix)))


    return (np.sum(row_sums) + np.sum(col_sums)) / (len(row_sums) + len(col_sums))
'''