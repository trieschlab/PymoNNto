# WiltingPriesemann toolbox for MR estimation
# Authors: Jens Wilting & Viola Priesemann
# Max-Planck-Institute for Dynamics and Self-Organization
# Am Fassberg 17
# D-37077 Goettingen
# Germany
#
# Minimal toolbox for MR estimation according to
# Wilting & Priesemann, 2018

import numpy as np
import scipy.stats
import scipy.interpolate


# ============================================================================
# Simulation of branching processes with immigration
# Ref: C. Heathcote, J R Stat Soc Ser B, 1965
# All variable names according to Wilting & Priesemann, 2018
# ============================================================================
def simulate_branching(length=10000, m=0.9, activity=100):
    
    h = activity * (1 - m)
    
    A_t = np.zeros(length, dtype=int)
    A_t[0] = np.random.poisson(lam=activity)
    
    print('Generating branching process with ' + str(length )+ ' time steps, m=' + str(m) + ', and drive rate' + str(h))
    
    for idx in range(1, length):
        if not idx % 1000:
            print(str(idx) + " loops completed")
        tmp = 0
        tmp += np.random.poisson(lam=h)
        if m > 0:
            #for idx2 in range(A_t[idx - 1]):
            tmp += np.random.poisson(lam=m, size=A_t[idx - 1]).sum()      
            
        A_t[idx] = tmp
        
    print("Branching process created with mean activity " + str(A_t.mean()))

    return A_t



# ============================================================================
# Emulation of binomial subsampling for given time series
# Ref: Wilting & Priesemann, 2018
# All variable names according to Wilting & Priesemann, 2018
# ============================================================================
def simulate_binomial_subsampling(A_t, alpha):
    a_t = np.zeros(len(A_t))
    for idx, item in enumerate(A_t):
        a_t[idx] = scipy.stats.binom.rvs(A_t[idx], alpha)

    return a_t



# ============================================================================
# Helper routine to handle different input formats
# for possible input formats, see below
# ============================================================================
def input_handler(items):
    situation = -1
    if isinstance(items, np.ndarray):
        if items.dtype.kind == 'i' or items.dtype.kind == 'f' or items.dtype.kind == 'u' :
            items = [items]
            situation = 0
        elif items.dtype.kind == 'S':
            situation = 1
        else:
            raise Exception('Invalid input: numpy.ndarray which is neither data nor file name.')
    elif isinstance(items, list):
        if all(isinstance(item,str) for item in items):
            situation = 1
        elif all(isinstance(item,np.ndarray) for item in items):
            situation = 0
        else:
            raise Exception('Invalid input: input type not recognized')
    elif isinstance(items, basestring):
        items = [items]
        situation = 1
    else:
        raise Exception('Invalid input: input type not recognized')
    

    if situation == 0:
        return items
    elif situation == 1:
        data = []
        for idx, item in enumerate(items):
            data.append(np.load(item))
        return data
    else:
        raise Exception('Unknown situation!')
    
    
    
# ============================================================================
# Helper routine to compute linear regression slopes $r_k$
# ============================================================================
def get_slopes(all_counts, k_min, k_max, scatterpoints):
        
    k = np.arange(k_min, k_max)#original:1
    r_k = np.zeros(len(k))
    intercepts = np.zeros(len(k))
    r_values = np.zeros(len(k))
    p_values = np.zeros(len(k))
    std_errs = np.zeros(len(k))

    xs = []
    ys = []

    #print(all_counts[0].shape)

    for idx, step in enumerate(k):
        x = np.empty(0)
        y = np.empty(0)
        for counts in all_counts:
            x = np.concatenate((x, counts[0:-step]))
            y = np.concatenate((y, counts[step:]))
            
        slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x,y)
        r_k[idx] = slope
        intercepts[idx] = intercept
        r_values[idx] = r_value
        p_values[idx] = p_value
        std_errs[idx] = std_err
        
        if idx == 0:
            data_length = len(x) + 1
            mean_activity = x.mean()
        
        if scatterpoints:
            if scatterpoints == True:
                xs.append(x)
                ys.append(y)  
            else:
                x = x[0::len(x) / scatterpoints]
                y = y[0::len(y) / scatterpoints]
                xs.append(x)
                ys.append(y)
                
    return k, r_k, intercepts, r_values, p_values, std_errs, data_length, mean_activity, xs, ys



# ============================================================================
# Helper routine for exponential model
# ============================================================================
def func(x, a, b, string=False):
    if string:
        return (r'$r_k = ' + str(round(a, 3))
                + '\cdot' + str(round(b, 3)) + '^k$')
    else:
        return np.abs(a)*np.abs(b)**x
    
    
    
# ============================================================================
# MR estimation routine
# Ref: Wilting & Priesemann, 2018
# All variable names according to Wilting & Priesemann, 2018
#
# Required input: time series (see below for possible formats), k_max
#
# Returns: dict with information from MR estimation
#
# Possible data formats (will be expanded in the future):
# 1) single time series as numpy.array
# 2) multiple time series as list [numpy.array, numpy.array, ...]
# 3) path to a .npy file with time series
# 4) list of paths to multiple .npy files with time series
# ============================================================================
def MR_estimation(all_counts, minslopes=1, maxslopes=40, scatterpoints=False, fractions=1):
    
    # scatterpoints: if scatterpoints of all regressions shall be returned. Can consume a lot of memory if True

    #print(np.array(all_counts).shape)

    return_dict = dict()
    
    all_counts = np.array(input_handler(all_counts))

    fraction_block_size=int(np.floor(len(all_counts[0])/fractions))

    k = []
    r_k = []
    #intercepts = []
    #r_values = []
    #p_values = []
    std_errs = []
    data_length = []
    #mean_activity = []
    #xs = []
    #ys = []

    for f in range(fractions):
        spike_fraction = all_counts[:, fraction_block_size*f:fraction_block_size*(f+1)]
        #print(f, len(spike_fraction[0]))
        # Get all slopes r_k
        _k, _r_k, _intercepts, _r_values, _p_values, _std_errs, _data_length, _mean_activity, _xs, _ys = get_slopes(spike_fraction, minslopes, maxslopes, scatterpoints)

        k.append(_k)
        r_k.append(_r_k)
        #intercepts.append(_intercepts)
        #r_values.append(_r_values)
        #p_values.append(_p_values)
        std_errs.append(_std_errs)
        data_length.append(_data_length)
        #mean_activity.append(_mean_activity)
        #xs.append(_xs)
        #ys.append(_ys)

    k = k[0]
    r_k = np.mean(r_k, axis=0)
    #intercepts=intercepts[0]
    #r_values=np.mean(r_values, axis=0)
    #p_values=np.mean(p_values, axis=0)
    std_errs=np.mean(std_errs, axis=0)
    data_length=data_length[0]
    #mean_activity=np.mean(mean_activity, axis=0)
    #xs=xs[0]
    #ys=ys[0]

    
    # Fit m, b (here as p_opt = [b, m]) according to exponential model        
    fitfunc = func
    p0 = [r_k[0], 1.0]

    p_opt, pcov = scipy.optimize.curve_fit(fitfunc, k, r_k, p0=p0, maxfev=100000, sigma=std_errs * np.linspace(1, 10, len(std_errs)))

    return_dict['branching_ratio'] = p_opt[1]
    return_dict['autocorrelationtime'] = - 1.0 / np.log(p_opt[1])
    return_dict['naive_branching_ratio'] = r_k[0]
    return_dict['k'] = k
    return_dict['r_k'] = r_k
    return_dict['fitfunc'] = fitfunc
    #if scatterpoints:
    #    if onlytwoscatterpoints:
    #        return_dict['xs'] = [xs[0], xs[-1]]
    #        return_dict['ys'] = [ys[0], ys[-1]]
    #    else:
    #        return_dict['xs'] = xs
    #        return_dict['ys'] = ys
    return_dict['data_length'] = data_length
    return_dict['p_opt'] = p_opt

    return return_dict

#import matplotlib.pyplot as plt
#act=np.random.rand(10000)
#data = MR_estimation(act, 1, 100, fractions=4)
#plt.scatter(data['k'], data['r_k'])
#plt.show()