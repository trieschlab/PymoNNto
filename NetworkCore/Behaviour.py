from PymoNNto.NetworkCore.Base import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *

class Behaviour(NetworkObjectBase):
    #modificaton_reset_vars = []
    set_variables_on_init = False

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.used_attr_keys = []
        self.behaviour_enabled = self.get_init_attr('behaviour_enabled', True, None)
        super().__init__(tag=self.get_init_attr('tag', None, None))
        self.add_tag(self.__class__.__name__)

    def run_on_neuron_init(self):
        self.run_on_neuron_init_var = True
        return self

    def set_gene_variables(self):
        current_genome = {}
        for variable_key in self.init_kwargs:
            while type(self.init_kwargs[variable_key]) is str and '[' in self.init_kwargs[variable_key] and ']' in \
                    self.init_kwargs[variable_key]:
                s = self.init_kwargs[variable_key]

                start = s.index('[')
                end = s.index(']')
                internal = s[start + 1: end].split('#')
                default_value = float(internal[0])
                gene_key = internal[1]

                current_genome[gene_key] = get_gene(gene_key, default_value)

                self.init_kwargs[variable_key] = s[:start] + '{:.15f}'.format(current_genome[gene_key]).rstrip('0').rstrip('.') + s[end + 1:]
        return current_genome

    def diversity_string_to_vec2(self, ds, neurons):

        if 'same(' in ds and ds[-1] == ')':
            params=ds[5:-1].replace(' ', '').split(',')
            if len(params) == 2:
                #print('same', params)
                return getattr(neurons[params[0], 0], params[1])

        command = ds.split(';')
        if (not '(' in ds and not ')' in ds) and not command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
            return ds


        if len(command) == 1:
            if command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
                result = float(command[0])

            #else:
            #    result = self.get_random_nparray((neurons.size), rnd_code=command[0])
                #print(result, type(result))
                return result

        dist_cmd='uniform(low, high)'
        if len(command) > 2 and not 'plot' in command[2]:# problem: , also in command
            dist_cmd=command[2]

            if 'smooth' in command[2]:
                smoothing = float(command[2].replace('smooth', ''))
                dist_cmd = 'np.sum([uniform(low, high, size=dim) for _ in range(smoothing)], axis=0)/smoothing'.replace('smoothing', str(smoothing))


        if command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
            min_v = float(command[0])
            if '%' in command[1]:
                max_v = min_v
                if '-' in command[1]:
                    min_v -= min_v / 100 * float(command[1].replace('+', '').replace('-', '').replace('%', ''))
                if '+' in command[1]:
                    max_v += max_v / 100 * float(command[1].replace('+', '').replace('-', '').replace('%', ''))
            else:
                max_v = float(command[1])

            dist_cmd=dist_cmd.replace('low',str(min_v)).replace('high',str(max_v)).replace('min_v',str(min_v)).replace('max_v',str(max_v)).replace('min',str(min_v)).replace('max',str(max_v))
        else:
            dist_cmd=command[0]

        if 'lognormal_real_mean' in command[0]:
            parts = command[0].replace(')', '').replace(' ', '').split('(')
            arguments = parts[1].split(',')
            mean = float(arguments[0])
            sigma = float(arguments[1])
            mu = -np.power(sigma, 2) + np.log(mean)
            dist_cmd = 'lognormal({}, {})'.format(mu, sigma)

        result=self.get_random_nparray((neurons.size), rnd_code=dist_cmd)


        if 'plot' in command[-1]:
            import matplotlib.pyplot as plt
            #print(result)
            plt.hist(result, bins=30)
            plt.show()


        return result

    def diversity_string_to_vec(self, ds, neurons):

        if 'same(' in ds and ds[-1] == ')':
            params=ds[5:-1].replace(' ', '').split(',')
            if len(params) == 2:
                #print('same', params)
                return getattr(neurons[params[0], 0], params[1])

        command = ds.split(';')
        if (not '(' in ds and not ')' in ds) and not command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
            return ds


        if len(command) == 1:
            if command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
                result = float(command[0])

            #else:
            #    result = self.get_random_nparray((neurons.size), rnd_code=command[0])
                #print(result, type(result))
                return result

        dist_cmd='uniform(low, high)'
        if len(command) > 2 and not 'plot' in command[2]:# problem: , also in command
            dist_cmd=command[2]

            if 'smooth' in command[2]:
                smoothing = float(command[2].replace('smooth', ''))
                dist_cmd = 'np.sum([uniform(low, high, size=dim) for _ in range(smoothing)], axis=0)/smoothing'.replace('smoothing', str(smoothing))


        if command[0].replace('.', '').replace('+', '').replace('-', '').isdigit():
            min_v = float(command[0])
            if '%' in command[1]:
                max_v = min_v
                if '-' in command[1]:
                    min_v -= min_v / 100 * float(command[1].replace('+', '').replace('-', '').replace('%', ''))
                if '+' in command[1]:
                    max_v += max_v / 100 * float(command[1].replace('+', '').replace('-', '').replace('%', ''))
            else:
                max_v = float(command[1])

            dist_cmd=dist_cmd.replace('low',str(min_v)).replace('high',str(max_v)).replace('min_v',str(min_v)).replace('max_v',str(max_v)).replace('min',str(min_v)).replace('max',str(max_v))
        else:
            dist_cmd=command[0]

        if 'lognormal_real_mean' in command[0]:
            parts = command[0].replace(')', '').replace(' ', '').split('(')
            arguments = parts[1].split(',')
            mean = float(arguments[0])
            sigma = float(arguments[1])
            mu = -np.power(sigma, 2) + np.log(mean)
            dist_cmd = 'lognormal({}, {})'.format(mu, sigma)

        result=self.get_random_nparray((neurons.size), rnd_code=dist_cmd)


        if 'plot' in command[-1]:
            import matplotlib.pyplot as plt
            #print(result)
            plt.hist(result, bins=30)
            plt.show()


        return result

    def set_init_attrs_as_variables(self, object):
        for key in self.init_kwargs:
            setattr(object, key, self.get_init_attr(key, None, neurons=object))
            print('init', key)
            #get_init_attr

    def check_unused_attrs(self):
        for key in self.init_kwargs:
            if not key in self.used_attr_keys:
                print('Warning: "'+key+'" not used in set_variables of '+str(self)+' behaviour! Make sure that "'+key+'" is spelled correctly and get_init_attr('+key+',...) is called in set_variables. Valid attributes are:'+str(self.used_attr_keys))

    def get_init_attr(self, key, default, neurons=None, do_not_diversify=False, search_other_behaviours=False, required=False):

        if required and not key in self.init_kwargs:
            print('Warning:',key,'has to be specified for the behaviour to run properly.', self)

        self.used_attr_keys.append(key)

        result = self.init_kwargs.get(key, default)

        if key not in self.init_kwargs and neurons is not None and search_other_behaviours:
            for b in neurons.behaviours:
                if key in b.init_kwargs:
                    result = b.init_kwargs.get(key, result)

        if not do_not_diversify and type(result) is str and neurons is not None:
            result = self.diversity_string_to_vec(result, neurons)

        return result

    def set_variables(self, neurons):
        return

    def reset(self):
        return

    def new_iteration(self, neurons):
        return

    #def get_shared_variable(self, name):
    #    return None


    def visualize_module(self, vmi=None, vmo=None, vma=None):
        from Exploration.Visualization import Module_visualizer as drawer
        self.visualization_module_inputs = vmi
        self.visualization_module_outputs = vmo
        self.visualization_module_attributes = vma
        md = drawer.module_drawer()
        md.add_module(self)
        md.show()


    #def initialize_synapse_attr(self, target_attr, density, equal_range, random_range, neurons, synapse_type, all_neurons_same=False):
    #    for s in neurons.afferent_synapses[synapse_type]:
    #        s.enabled *= s.get_synapse_mat('uniform',density=density, clone_along_first_axis=all_neurons_same) > 0.0
    #        setattr(s, target_attr, s.enabled*(s.get_synapse_mat()+equal_range+s.get_synapse_mat('uniform',density=1.0, clone_along_first_axis=all_neurons_same)*random_range))#s.shape_mat*#neurons.GABA_strength+neurons.min_GABA_strength





