import numpy as np



def relu2(x, param):
    return np.clip((x > param)*(1 / (1 - param) * (x - param)), 0, 1)

def relu3(x ,param, stepheight):
    return np.clip((x > param) * (stepheight + (1-stepheight) / (1 - param) * (x - param)), 0, 1)

def roll(mat):
    #return np.roll(mat, 1)
    mat[1:len(mat)]=mat[0:len(mat)-1]
    return mat


#print(GammaBlock_to_Hz(0.5))

#import matplotlib.pyplot as plt
#plt.plot([relu3(x/100, 0.1, 0) for x in range(100)])
#plt.show()