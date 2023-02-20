from PymoNNto.NetworkCore.Base_Tagable_Object import *
import numpy as np
from numpy.random import *
from numpy import *
from functools import wraps

def lognormal_real_mean(mean=1.0, sigma=1.0, size=1):
    mu = -np.power(sigma, 2) + np.log(mean)
    return lognormal(mu, sigma, size=size)

def lognormal_rm(mean=1.0, sigma=1.0, size=1):
    return lognormal_real_mean(mean,sigma,size)

def uniform_gap(mean=1.0, gap_percent=10, size=1):
    return uniform(low=mean-mean*gap_percent, high=mean+-mean*gap_percent, size=size)

def is_number(s):
    """ Returns True if string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False

def deprecated_warning(message):
    def inner_function(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            #raise Exception(message)
            print(message)
            return function(*args, **kwargs)
        return wrapper
    return inner_function

class NetworkObjectBase(TaggableObjectBase):

    def __init__(self, tag, network, behaviour):
        super().__init__(tag)

        self.network = network

        self.behaviour = behaviour
        if type(behaviour) == list:
            self.behaviour = dict(zip(range(len(self.behaviour)), self.behaviour))

        for b in self.behaviour.values():
            for tag in b.tags:
                if not hasattr(self, tag):
                    setattr(self, tag, b)

        for k in sorted(list(self.behaviour.keys())):
            if self.behaviour[k].set_variables_on_init:
                network._set_variables_check(self, k)

        self.analysis_modules = []

    def add_behaviour(self, key, behaviour, initialize=True):
        self.behaviour[key] = behaviour
        self.network._add_key_to_sorted_behaviour_timesteps(key)
        self.network.clear_tag_cache()
        if initialize:
            behaviour.set_variables(self)
            behaviour.check_unused_attrs()
        return behaviour

    def add_behaviours(self, behaviour_dict):
        for key in behaviour_dict:
            self.add_behaviour(key, behaviour_dict[key])
        return behaviour_dict

    def remove_behaviour(self, key_tag_behaviour_or_type):
        remove_keys=[]
        for key in self.behaviour:
            b = self.behaviour[key]
            if key_tag_behaviour_or_type == key or key_tag_behaviour_or_type in b.tags or key_tag_behaviour_or_type == b or key_tag_behaviour_or_type == type(b):
                remove_keys.append(key)
        for key in remove_keys:
            self.behaviour.pop(key)



    def set_behaviours(self, tag, enabeled):
        if enabeled:
            print('activating', tag)
        else:
            print('deactivating', tag)
        for b in self[tag]:
            b.behaviour_enabled = enabeled


    def deactivate_behaviours(self, tag):
        self.set_behaviours(tag, False)

    def activate_behaviours(self, tag):
        self.set_behaviours(tag, True)


    def find_objects(self, key):
        result = []

        if key in self.behaviour:
            result.append(self.behaviour[key])

        for bk in self.behaviour:
            behaviour = self.behaviour[bk]
            result += behaviour[key]

        for am in self.analysis_modules:
            result += am[key]

        return result

    def add_analysis_module(self, module):
        module._attach_and_initialize_(self)

    def get_all_analysis_module_results(self, tag, return_modules=False): #...get_analysis_module_results('Classification')
        result = {}
        modules = {}
        for module in self[tag]:
            module_results = module.get_results()
            for k in module_results:
                result[k] = module_results[k]
                modules[k] = module
        if return_modules:
            return result, modules
        else:
            return result

    def buffer_roll(self, mat, new=None):
        #return np.roll(mat, 1, axis=0)
        mat[1:len(mat)] = mat[0:len(mat) - 1]

        if new is not None:
            mat[0]=new

        return mat

    def get_nparray(self, dim):
        return np.zeros(dim).astype(def_dtype)

    def _get_mat(self, mode, dim, density=None, scale=None, plot=False):
        if mode not in self._mat_eval_dict:
            ev_str = mode

            cast = True

            if ev_str == bool or ev_str == 'bool':
                cast = False
                ev_str = 'zeros(dtype=bool)'

            if ev_str == int or ev_str == 'int':
                cast = False
                ev_str = 'zeros(dtype=int)'

            if ev_str == 'random' or ev_str == 'rand' or ev_str == 'rnd':
                ev_str = 'uniform'

            if type(ev_str) == int or type(ev_str) == float:
                ev_str = str(ev_str)+'*ones()'

            if '(' not in ev_str and ')' not in ev_str:
                ev_str += '()'

            if 'zeros' in ev_str or 'ones' in ev_str:
                a1 = 'shape=dim'
            else:
                a1 = 'size=dim'

            ev_str = ev_str.replace(')', ',' + a1 + ')')
            ev_str = ev_str.replace('(,', '(')

            if cast:
                ev_str += '.astype(self.def_dtype)'

            self._mat_eval_dict[mode] = compile(ev_str, '<string>', 'eval')

        result = eval(self._mat_eval_dict[mode])

        if density is not None:
            if type(density) == int or type(density) == float:
                result = (result * (random_sample(dim) <= density))
            elif type(density) is np.ndarray:
                result = (result * (random_sample(dim) <= density[:, None]))

        if scale is not None:
            result *= scale

        if plot:
            import matplotlib.pyplot as plt
            plt.hist(result.flatten(), bins=50)
            plt.show()

        return result

    '''
    def _get_mat(self, mode, dim, scale=None, density=None, plot=False, kwargs={}, args=[]): # mode in ['zeros', 'zeros()', 'ones', 'ones()', 'uniform(...)', 'lognormal(...)', 'normal(...)']

        if mode == 'random' or mode == 'rand' or mode == 'rnd':
            mode = 'uniform'

        if type(mode) == int or type(mode) == float:
            mode = 'ones()*'+str(mode)

        if '(' not in mode and ')' not in mode:
            mode += '()'

        if mode not in self._mat_eval_dict:
            if 'zeros' in mode or 'ones' in mode:
                a1 = 'shape=dim'
            else:
                a1 = 'size=dim'
            if '()' in mode:#no arguments => no comma
                ev_str = mode.replace(')', '*args,'+a1+',**kwargs)')
            else:
                if args!=[]:
                    print('Warning: args cannot be used when arguments are passed as strings')
                ev_str = mode.replace(')', ','+a1+',**kwargs)')

            self._mat_eval_dict[mode] = compile(ev_str, '<string>', 'eval')

        result = eval(self._mat_eval_dict[mode])

        if density is not None:
            if type(density) == int or type(density) == float:
                result = (result * (random_sample(dim) <= density))
            elif type(density) is np.ndarray:
                result = (result * (random_sample(dim) <= density[:, None]))

        if scale is not None:
            result *= scale

        if plot:
            import matplotlib.pyplot as plt
            plt.hist(result.flatten(), bins=30)
            plt.show()

        return result.astype(def_dtype)
    '''

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

    ################################################################################################
    #deprecated#####################################################################################
    ################################################################################################

    @deprecated_warning("set_mechanisms function will be removed in coming versions. Please use set_behaviours instead.")
    def set_mechanisms(self, tag):
        if tag is str:
            tag=[tag]
        for t in tag:
            set_behaviours(t)

    @deprecated_warning("deactivate_mechanisms function will be removed in coming versions. Please use deactivate_behaviours instead.")
    def deactivate_mechanisms(self, tag):
        self.set_behaviours(tag, False)

    @deprecated_warning("activate_mechanisms function will be removed in coming versions. Please use activate_behaviours instead.")
    def activate_mechanisms(self, tag):
        self.set_behaviours(tag, True)