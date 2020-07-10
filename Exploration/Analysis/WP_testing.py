import numpy as np
import mrestimator as mre

def h_offset(exp_fit: mre.FitResult, expoffset_fit: mre.FitResult) -> bool:
    """
    Test the H_offset hypothesis as described in (Wilting&Priesemann 2018; Supplemental Note 5)
    :return: if True, then the data set should be rejected for m estimation
    """

    return 2*expoffset_fit.ssres < exp_fit.ssres


def h_tau(exp_fit: mre.FitResult, expoffset_fit: mre.FitResult) -> bool:
    """
    Test the H_tau hypothesis as described in (Wilting&Priesemann 2018; Supplemental Note 5)
    :return: if True, then the data set should be rejected for m estimation
    """
    tau_exp, tau_offset = exp_fit.tau, expoffset_fit.tau

    return (np.abs(tau_exp - tau_offset) / np.min((tau_exp, tau_offset))) > 2


def h_lin(rk: mre.CoefficientResult, exp_fit: mre.FitResult) -> bool:
    """
    Test the H_lin hypothesis as described in (Wilting&Priesemann 2018; Supplemental Note 5)
    :return: if True, then the data set should be rejected for m estimation
    """
    lin_fit = mre.fit(rk, fitfunc=mre.f_linear)

    return lin_fit.ssres < exp_fit.ssres

#import matplotlib as plt

def branching_ratio(spikes, bin_w):
    GExc_spks = spikes

    #with open(bpath + '/raw/gexc_spks.p', 'rb') as pfile:
    #    GExc_spks = pickle.load(pfile)
    # with open(bpath+'/raw/ginh_spks.p', 'rb') as pfile:
    #     GInh_spks = pickle.load(pfile)

    #ts = GExc_spks['t'] / ms
    #ts = ts[ts > (nsp['T1'] + nsp['T2'] + nsp['T3'] + nsp['T4']) / ms]
    #ts = ts - (nsp['T1'] + nsp['T2'] + nsp['T3'] + nsp['T4']) / ms

    #assert (np.min(ts) >= 0)

    bins = np.arange(0, (len(spikes) + bin_w), bin_w)
    counts, bins = np.histogram(GExc_spks, bins=bins)

    print(np.shape(counts))
    # counts = np.reshape(counts, (len(counts),1))
    # print(np.shape(counts))

    rk = mre.coefficients(counts, dt=bin_w, dtunit='ms')#, desc=''
    ft = mre.fit(rk)

    return rk, ft, (counts, bins)