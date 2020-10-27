import sys
sys.path.append('../../TREN2')
sys.path.append('../../tren2')

import matplotlib.pylab as plt

from SORNSim.NetworkBehaviour.Logic.TREN.Neuron_Learning import *

from SORNSim.NetworkCore.Network import *
from SORNSim.NetworkCore.Neuron_Group import *
from SORNSim.NetworkCore.Synapse_Group import *

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return np.array([x, y])


def get_next_step(p, center, sense_dist, input_ng, SORN_Global, output_ng):
    td = np.clip(-p[1]+center[1], 0, sense_dist)/sense_dist
    bd = np.clip(+p[1]-center[1], 0, sense_dist)/sense_dist
    ld = np.clip(+p[0]-center[0], 0, sense_dist)/sense_dist
    rd = np.clip(-p[0]+center[0], 0, sense_dist)/sense_dist

    inp = [td, bd, ld, rd]
    if np.sum(inp) > 0:
        inp = inp/np.sum(inp)

    input_ng[NeuronManualActivator].activate(inp)
    SORN_Global.simulate_iteration()
    out = output_ng.activity.copy()

    if np.sum(out) > 0:
        out = out/np.sum(out)*0.01

    #out=syns.GLU_Synapses.dot([td, bd, ld, rd])
    #print([td, bd, ld, rd],out)
    return [(-out[2] + out[3]) * 10, (+out[0] - out[1]) * 10]

def get_batch(input, output, batchsize=100, test=False):
    rnd = np.random.randint(0, input.shape[0] - batchsize * 2)
    if test:
        rnd = input.shape[0] - batchsize
    return input[rnd:rnd + batchsize], output[rnd:rnd + batchsize]

def update_Q_function(input, output, trainingsteps):

    with tf.variable_scope("network"):

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

def get_reward(center, position, predicted_position, reward_strength):
    dist = np.linalg.norm(position - center, 2)
    predicted_dist = np.linalg.norm(predicted_position - center, 2)
    dist_imp = predicted_dist-dist
    #print(dist_imp)

    #reward = ((dist_imp - last_reward) > 0) * 1.0
    #reward = np.clip(1-(dist_imp-last_reward)*100, 0, 1)
    reward = np.clip(dist_imp * reward_strength, 0, 1)

    #print(reward)

    return reward


def run_and_get_score(ind=[]):

    input_ng = NeuronGroup(size=4, behaviour = {
        5: NeuronManualActivator(write_to='glu_inter_gamma_activity'),
        7: ActivityBuffering(store_input=False, min_buffersize=6)#original:7
    }).add_tag('input')

    output_ng = NeuronGroup(size=4, behaviour={
        1: DopamineProcessing(source_weight_id=1, target_weight_id=0),
        2: TemporalWeightCache(decay=1, strength=1, GLU_density=1.0, set_weights=True,GLU_equal_factor=1,GLU_random_factor=0),
        3: RandomWeightFluctuation2(decay='[0.5#0]', strength='[1.0#1]', fluctuation='[0.001#2]', density='[0.05#3]'),
        4: GlutamateCacheConvergeAndNormalization(norm_value='0.05'),#todo output all same bug!!!!!!

        5: InterGammaGlutamate(GLU_density=1.0),#0.005
        8: ActivityBuffering(activity_multiplyer=0.0, firetreshold=0.1),

        # 7: RandomWeightFluctuation(beta=4*0.2, gamma=3*0.2),
        #8: HomeostaticMechanism(range_end='[550#3],+-30%', inc='[1.84#4],+-10%', dec='[4.92#5],+-10%',pattern_chance='[0.0086#6],+-30%'),
    })

    syns = SynapseGroup(src=input_ng, dst=output_ng).add_tag('GLU')

    SORN_Global = Network([input_ng, output_ng], [syns], initialize=False)
    SORN_Global.set_marked_variables(ind)
    SORN_Global.initialize()

    #syns.GLU_Synapse_Caches[0] = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])

    reward_strength = 1

    last_reward = 0
    last_dist = 0

    sense_dist = 5
    step_count = 100
    reset_count = 1000

    center = np.array([5.0, 5.0])

    spawn_dist = 0.1

    spawn_distances = []

    inc = 0.01
    dec = 0.01

    for runs in range(reset_count):

        #pos = np.array([9.0, 1.0])
        #pos = np.array(np.random.rand(2)*10)
        pos = pol2cart(spawn_dist, (2*np.pi)*np.random.rand())+center#/reset_count*runs

        predicted_pos = np.array(pos.copy())

        path = [pos.copy(), pos.copy()]
        steps = [[0, 0], [0, 0]]
        rewards = [0, 0]
        colors = [(0, 0, 0), (0, 0, 0)]

        #print(np.sum(syns.GLU_Synapse_Caches[0]),np.sum(syns.GLU_Synapse_Caches[1]))
        #print(syns.GLU_Synapses)

        for i in range(step_count):
            step = get_next_step(path[-1], center, sense_dist, input_ng, SORN_Global, output_ng)

            pos += step

            reward = get_reward(center, pos, predicted_pos, reward_strength)
            #output_ng.dopamine_level = reward

            SORN_Global.learning_off()
            #future_step = get_next_step(np.clip(pos, 0, 10), input_ng, SORN_Global, output_ng)
            predicted_pos = np.clip(pos, 0, 10)+step
            SORN_Global.learning_on()

            #print(out)
            #print([td, bd, ld, rd])

            path.append(np.clip(pos, 0, 10))
            steps.append(step)
            rewards.append(reward)
            colors.append((i/step_count, runs/reset_count, 0.0)) #reward

            if np.linalg.norm(path[-1] - center, 2) < 0.1:
                spawn_dist = np.clip(spawn_dist+inc, 0.1, 5)#make it harder
                output_ng.dopamine_level = 1
                if ind is []:
                    print(spawn_dist, 'reward', step)
                break

        if output_ng.dopamine_level == 0:
            spawn_dist = np.clip(spawn_dist-dec, 0.1, 5)#make it eayer
            if ind is []:
                print(spawn_dist, 'goal not found', step)

        SORN_Global.simulate_iteration()
        output_ng[RandomWeightFluctuation2].clear_weights(output_ng)

        spawn_distances.append(spawn_dist)

        path = np.array(path)
        plt.scatter(path[:, 0], path[:, 1], color=colors)#, color=colors)#, color=dop) #, edgecolor='black'

    if ind is []:
        plt.scatter(center[0], center[1], color='blue')
        plt.ylim([0, 10])
        plt.xlim([0, 10])
        plt.show()

        plt.plot(spawn_distances)
        plt.show()

    score = np.sum(spawn_distances)
    return score



if __name__ == '__main__':
    import Exploration.Evolution.Multithreaded_Evolution as Evo
    evolution = Evo.Multithreaded_Evolution(run_and_get_score, 60, thread_count=10, name="RL_EVO", mutation=0.05, death_rate=0.3)
    evolution.start([[0.5, 1.0, 0.001, 0.05]])
    #evolution.continue_evo('RL_Test.txt')

#run_and_get_score()
