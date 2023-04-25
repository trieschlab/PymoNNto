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

    def __init__(self, tag, network, behavior):
        super().__init__(tag)

        self.network = network

        self.behavior = behavior
        if type(behavior) == list:
            self.behavior = dict(zip(range(len(self.behavior)), self.behavior))

        for b in self.behavior.values():
            for tag in b.tags:
                if not hasattr(self, tag):
                    setattr(self, tag, b)

        for k,b in self.behavior.items():
            self.network._add_behavior_to_sorted_execution_list(k, self, b)

        for k in sorted(list(self.behavior.keys())):
            if self.behavior[k].initialize_on_init:
                self.behavior[k].initialize(self)
                #behavior.check_unused_attrs()
                #network._initialize_check(self, k)

        #self.learning = True
        self.recording = True

        self.analysis_modules = []

    def add_behaviors(self, behavior_dict):
        for key in behavior_dict:
            self.add_behavior(key, behavior_dict[key])
        return behavior_dict



    def add_behavior(self, key, behavior, initialize=True):
        #check key already exists!!!
        if not key in self.behavior:
            self.behavior[key] = behavior
            self.network._add_behavior_to_sorted_execution_list(key, self, self.behavior[key])
            self.network._add_key_to_sorted_behavior_timesteps(key)#remove!!!
            self.network.clear_tag_cache()
            if initialize:
                #behavior.initialize_init(self)
                behavior.initialize(self)
                #behavior.initialize_last(self)
                behavior.check_unused_attrs()
            return behavior
        else:
            raise Exception('Error: Key already exists.'+str(key))

    def remove_behavior(self, key_tag_behavior_or_type):
        remove_keys=[]
        for key in self.behavior:
            b = self.behavior[key]
            if key_tag_behavior_or_type == key or key_tag_behavior_or_type in b.tags or key_tag_behavior_or_type == b or key_tag_behavior_or_type == type(b):
                remove_keys.append(key)
        for key in remove_keys:
            b=self.behavior.pop(key)
            self.network._remove_behavior_from_sorted_execution_list(self, b)

    def set_behaviors(self, tag, enabeled):
        if enabeled:
            print('activating', tag)
        else:
            print('deactivating', tag)
        for b in self[tag]:
            b.behavior_enabled = enabeled


    def deactivate_behaviors(self, tag):
        self.set_behaviors(tag, False)

    def activate_behaviors(self, tag):
        self.set_behaviors(tag, True)


    def find_objects(self, key):
        result = []

        if key in self.behavior:
            result.append(self.behavior[key])

        for bk in self.behavior:
            behavior = self.behavior[bk]
            result += behavior[key]

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

    def get_nparray(self, dim):
        return np.zeros(dim).astype(self.def_dtype)

    def get_buffer_mat(self, dim, size):
        return np.array([self.get_nparray(dim) for _ in range(size)])

    def buffer_roll(self, mat, new=None, counter=False):
        #return np.roll(mat, 1, axis=0)
        mat[1-counter : len(mat)-counter] = mat[0+counter : len(mat)-1+counter]

        if new is not None:
            mat[0-counter]=new

        return mat

    ################################################################################################
    #deprecated#####################################################################################
    ################################################################################################

    @deprecated_warning("set_mechanisms function will be removed in coming versions. Please use set_behaviors instead.")
    def set_mechanisms(self, tag):
        if tag is str:
            tag=[tag]
        for t in tag:
            set_behaviors(t)

    @deprecated_warning("deactivate_mechanisms function will be removed in coming versions. Please use deactivate_behaviors instead.")
    def deactivate_mechanisms(self, tag):
        self.set_behaviors(tag, False)

    @deprecated_warning("activate_mechanisms function will be removed in coming versions. Please use activate_behaviors instead.")
    def activate_mechanisms(self, tag):
        self.set_behaviors(tag, True)

    @deprecated_warning("add_behaviours function will be removed in coming versions. Please use add_behaviors instead.")
    def add_behaviours(self, behavior_dict):
        return self.add_behaviors(behavior_dict)

    @deprecated_warning("add_behaviour function will be removed in coming versions. Please use add_behavior instead.")
    def add_behaviour(self, key, behavior, initialize=True):
        return self.add_behavior(key, behavior, initialize)

    @deprecated_warning("remove_behaviour function will be removed in coming versions. Please use remove_behavior instead.")
    def remove_behaviour(self, key_tag_behavior_or_type):
        return self.remove_behavior(key_tag_behavior_or_type)

    @deprecated_warning("set_behaviours function will be removed in coming versions. Please use set_behaviors instead.")
    def set_behaviours(self, tag, enabeled):
        return self.set_behaviors(tag, enabeled)

    @deprecated_warning("deactivate_behaviours function will be removed in coming versions. Please use deactivate_behaviors instead.")
    def deactivate_behaviours(self, tag):
        return self.deactivate_behaviors(tag)

    @deprecated_warning("activate_behaviours function will be removed in coming versions. Please use activate_behaviors instead.")
    def activate_behaviours(self,tag):
        return self.activate_behaviors(tag)