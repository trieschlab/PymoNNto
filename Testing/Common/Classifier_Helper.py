
import numpy as np
from sklearn import linear_model
import sys


def getXY(output_recorders, out_param_name, input_recorder, inp_param_name, start, end, XYshift=0, learn_shift=1):#todo XYshift -1 ...
    inputs = [rec[out_param_name, 0, 'np'][start+XYshift:end-learn_shift] for rec in output_recorders]
    X = np.concatenate(inputs, axis=1)
    Y = input_recorder[inp_param_name, 0, 'np'][learn_shift+start:end-XYshift].T.astype(int)
    #print(X.shape, Y.shape)
    return X, Y

def remove_lag(X, Y, lag):
    r = np.arange(len(Y))
    rx = X[(r % lag) == 0]#(lag - 1)
    ry = Y[(r % lag) == 0]#(lag - 1)
    return rx, ry

def train_same_step(output_recorders, out_param_name, input_recorders, inp_param_name, start, end):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorders, inp_param_name, start, end, XYshift=0, learn_shift=0)
    #X_train, Y_train= remove_lag(X_train, Y_train, lag)
    if sys.version_info[1]>5:#3.5...
        lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
    else:
        lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    return lg.fit(X_train, Y_train)

def train(output_recorders, out_param_name, input_recorder, inp_param_name, start, end, lag=1):
    X_train, Y_train = getXY(output_recorders, out_param_name, input_recorder, inp_param_name, start, end, XYshift=lag-1, learn_shift=lag)
    X_train, Y_train= remove_lag(X_train, Y_train, lag)
    if sys.version_info[1]>5:#3.5...
        lg = linear_model.LogisticRegression(solver='liblinear', multi_class='auto')
    else:
        lg = linear_model.LogisticRegression(solver='lbfgs', multi_class='ovr')#for older python version
    return lg.fit(X_train, Y_train)


def score(linear_model, input_recorders, inp_param_name, output_recorders, out_param_name, start, end):
    X_test, Y_test = getXY(input_recorders, inp_param_name, output_recorders, out_param_name, start, end)

    spec_perf = {}
    for symbol in np.unique(Y_test):
        symbol_pos = np.where(symbol == Y_test)
        spec_perf[symbol] = linear_model.score(X_test[symbol_pos], Y_test[symbol_pos])#source.index_to_symbol()

    print(spec_perf)
    s = 0
    for k in spec_perf:
        s += spec_perf[k]
    print('score:', s)
    return spec_perf


