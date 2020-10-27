import numpy as np
import matplotlib.pyplot as plt

#average_act = np.mean(np.array(e_ng['n.output'][0]), axis=1)

def inhibition_excitation_scatter(inh, exc):
    inh = np.mean(inh, axis=0)
    exc = np.mean(exc, axis=0)

    plt.scatter(exc, inh)
    plt.xlabel('excitation')
    plt.ylabel('inhibition')
    plt.show()

def get_t_vs_tp1_mat(average_activities_x, average_activities_y, resolution=100, flip=True, no_act_compensation=True):
    heatmap = np.zeros((resolution, resolution))
    max_act = np.maximum(np.max(average_activities_x), np.max(average_activities_y))

    if max_act > 0:
        for i in range(np.minimum(len(average_activities_x)-1, len(average_activities_y)-1)):
            x = int(np.trunc((resolution-1)/max_act*average_activities_x[i]))
            y = int(np.trunc((resolution-1)/max_act*average_activities_y[i+1]))
            heatmap[y, x] += 1

    if no_act_compensation:
        heatmap[0, 0] = 0

    if flip:
        heatmap = np.flip(heatmap, axis=0)

    return heatmap

def plot_t_vs_tp1(average_activities, resolution=100):
    heatmap=get_t_vs_tp1_mat(average_activities,average_activities, resolution)
    plt.imshow(heatmap)
    plt.xlabel('t')
    plt.ylabel('t+1')
    plt.xticks([])
    plt.yticks([])
    #plt.axis('off')
    plt.show()
