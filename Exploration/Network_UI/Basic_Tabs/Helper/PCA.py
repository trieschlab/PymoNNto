import numpy as np
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

#X = np.array([np.random.rand(1000) for i in range(1000)])

def get_PCA(act, num_sv=100):
    num_sv = min([num_sv, len(act)])
    pca = PCA(n_components=num_sv)
    pca.fit(act)

    return pca

def get_activity_singular_values(act, num_sv=100):
    num_sv = min([num_sv, len(act)])
    pca = PCA(n_components=num_sv)
    pca.fit(act)

    return pca.singular_values_

def get_activity_singular_values_and_components(act, num_sv=100):
    num_sv = min([num_sv, len(act)])
    pca = PCA(n_components=num_sv)
    pca.fit(act)

    return pca.singular_values_, pca.components_, pca.explained_variance_, pca.explained_variance_ratio_


#pca.explained_variance_ !!!

