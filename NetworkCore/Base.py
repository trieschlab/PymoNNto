import numpy as np

from numpy.random import *


def_dtype = np.float64

class NetworkObjectBase:

    def __init__(self, tag):
        self.tags = []
        self.clear_cache()
        if tag is not None:
            self.add_tag(tag)

    def find_objects(self, key):#override for deeper search
        return []

    def clear_cache(self):
        self.tag_shortcuts = {}

    def set_tag_attrs(self, tag, attr, value):
        for obj in self[tag]:
            setattr(obj, attr, value)

    def call_tag_functions(self, tag, attr, **args):#todo: test
        for obj in self[tag]:
            getattr(obj, attr)(args)

    def __getitem__(self, key):

        np_array_conversion = isinstance(key, tuple) and 'np' in key

        if key in self.tag_shortcuts and type(self.tag_shortcuts[key]) is not np.ndarray:
            if np_array_conversion:
                return np.array(self.tag_shortcuts[key])
            else:
                return self.tag_shortcuts[key]

        if isinstance(key, tuple):
            k = key[0]
            index = key[1]
        else:
            k = key
            index = None

        result = []
        if k in self.tags or (k is type and isinstance(self, k)):
            result = [self]

        result += self.find_objects(k)

        if index is not None:
            if len(result)>0:
                result = result[index]
            else:
                result=None

        if not key in self.tag_shortcuts:
            self.tag_shortcuts[key] = result

        if np_array_conversion:# only used for [key,index,'np'] not for [key, 'np']
            return np.array(result)
        else:
            return result


    def add_tag(self, tag):
        for subtag in tag.split(','):
            self.tags.append(subtag)
        return self

    def buffer_roll(self, mat, new=None):
        #return np.roll(mat, 1, axis=0)
        mat[1:len(mat)] = mat[0:len(mat) - 1]

        if new is not None:
            mat[0]=new

        return mat

    def get_nparray(self, dim):
        return np.zeros(dim).astype(def_dtype)

    def get_random_nparray(self, dim, density=None, clone_along_first_axis=False, rnd_code=None):#rnd_code=random_sample(dim)
        if rnd_code is None:
            result = random_sample(dim)
        else:
            if 'dim' not in rnd_code:
                if rnd_code[-1] == ')':
                    rnd_code = rnd_code[:-1]+',size=dim)'
                else:
                    rnd_code = rnd_code+'(size=dim)'
            result = eval(rnd_code)

        if density is None:
            result = result.astype(def_dtype)
        elif type(density) == int or type(density) == float:
            result = (result * (random_sample(dim) <= density)).astype(def_dtype)
        elif type(density) is np.ndarray:
            result = (result * (random_sample(dim) <= density[:, None])).astype(def_dtype)


        if not clone_along_first_axis:
            return result
        else:
            return np.array([result[0] for _ in range(dim[0])])


    def get_buffer_mat(self, dim, size):
        return np.array([self.get_nparray(dim) for _ in range(size)])
