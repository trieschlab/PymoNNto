from PymoNNto import *
import copy
import pickle
import os
import marshal

compile_class = type(compile('1+1', '<string>', 'eval'))
base_obj_type = TaggableObjectBase#NetworkObjectBase

def add_to_compiled_save_list_and_get_save_str(obj, compiled, compiled_path):
    ct = len(compiled)+1
    s = '__compile#'+str(ct)+'.bin'
    compiled[s] = obj
    marshal.dump(obj, open(compiled_path + s, "wb"))
    return s

def clear_compiled_code(obj, visited=[], compiled={}, compiled_path=None):

    if isinstance(obj, base_obj_type) and (obj not in visited):
        visited.append(obj)
        d = obj.__dict__
        for key in d:
            if type(getattr(obj, key)) in [list, dict] or isinstance(getattr(obj, key), base_obj_type):
                clear_compiled_code(d[key], visited, compiled, compiled_path)

            if type(getattr(obj, key)) is compile_class:
                setattr(obj, key, add_to_compiled_save_list_and_get_save_str(getattr(obj, key), compiled, compiled_path))

    visited.append(obj)

    if type(obj) is list:
        for i in range(len(obj)):
            if type(obj[i]) in [list, dict] or isinstance(obj[i], base_obj_type):
                clear_compiled_code(obj[i], visited, compiled, compiled_path)

            if type(obj[i]) is compile_class:
                obj[i] = add_to_compiled_save_list_and_get_save_str(obj[i], compiled, compiled_path)

    if type(obj) is dict:
        for sub_obj_key in obj:
            if type(obj[sub_obj_key]) in [list, dict] or isinstance(obj[sub_obj_key], base_obj_type):
                clear_compiled_code(obj[sub_obj_key], visited, compiled, compiled_path)

            if type(obj[sub_obj_key]) is compile_class:
                obj[sub_obj_key] = add_to_compiled_save_list_and_get_save_str(obj[sub_obj_key], compiled, compiled_path)

    return compiled

def load_compiled_object(file, path):
    return marshal.load(open(path + file, "rb"))


def add_compiled_code(obj, visited=[], path=''):

    if isinstance(obj, base_obj_type) and (obj not in visited):
        visited.append(obj)
        d = obj.__dict__
        for key in d:
            if type(getattr(obj, key)) in [list, dict] or isinstance(getattr(obj, key), base_obj_type):
                add_compiled_code(d[key], visited, path)

            if type(getattr(obj, key)) is str and '__compile#' in getattr(obj, key):
                setattr(obj, key, load_compiled_object(getattr(obj, key), path))

    visited.append(obj)

    if type(obj) is list:
        for i in range(len(obj)):
            if type(obj[i]) in [list, dict] or isinstance(obj[i], base_obj_type):
                add_compiled_code(obj[i], visited, path)

            if type(obj[i]) is str and '__compile#' in obj[i]:
                obj[i] = load_compiled_object(obj[i], path)

    if type(obj) is dict:
        for sub_obj_key in obj:
            if type(obj[sub_obj_key]) in [list, dict] or isinstance(obj[sub_obj_key], base_obj_type):
                add_compiled_code(obj[sub_obj_key], visited, path)

            if type(obj[sub_obj_key]) is str and '__compile#' in obj[sub_obj_key]:
                obj[sub_obj_key] = load_compiled_object(obj[sub_obj_key], path)


def save_network(network, filename):
    folder = get_data_folder() + '/NetworkStates/'

    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except:
            print('was not able to create '+folder+' folder')

    folder +=  filename + '/'

    if not os.path.exists(folder):
        try:
            os.mkdir(folder)
        except:
            print('was not able to create '+folder+' folder')

    net = copy.deepcopy(network)
    clear_compiled_code(net, compiled_path=folder)

    file = folder + 'network.netstate'
    pickle.dump(net, open(file, 'wb'))
    print('networks saved as', file)



def load_network(filename):
    path=get_data_folder() + '/NetworkStates/'+filename+'/'
    file = path + 'network.netstate'
    network = pickle.load(open(file, 'rb'))
    add_compiled_code(network, path=path)
    return network
