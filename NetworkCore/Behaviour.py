from PymoNNto.NetworkCore.Base import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *

class Behaviour(NetworkObjectBase):
    set_variables_on_init = False
    attached_UI_Tabs = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.used_attr_keys = []
        self.behaviour_enabled = self.get_init_attr('behaviour_enabled', True, None)
        super().__init__(tag=self.get_init_attr('tag', None, None))


    def set_variables(self, neurons):
        return

    def new_iteration(self, neurons):
        return

    def set_gene_variables(self):
        current_genome = {}

        #for k,v in self._caller_module.__dict__.items():
        #    if k not in locals():
        #        print(k)
        #        locals()[k]=v

        for variable_key in self.init_kwargs:
            while type(self.init_kwargs[variable_key]) is str and '[' in self.init_kwargs[variable_key] and ']' in self.init_kwargs[variable_key]:
                s = self.init_kwargs[variable_key]

                start = s.index('[')
                end = s.index(']')

                content = s[start + 1: end]

                if '#' in content:
                    parts = content.split('#')
                    default_value = eval(parts[0])#float(parts[0])
                    gene_key = parts[1]
                else:
                    gene_key = content
                    default_value = None

                current_genome[gene_key] = get_gene(gene_key, default_value)

                self.init_kwargs[variable_key] = s[:start] + '{:.15f}'.format(current_genome[gene_key]).rstrip('0').rstrip('.') + s[end + 1:]
        return current_genome

    def __str__(self):
        result = self.__class__.__name__+'('
        for k in self.init_kwargs:
            result += str(k) + '=' + str(self.init_kwargs[k])+','
        result += ')'
        return result

    def evaluate_diversity_string(self, ds, neurons_or_synapses):

        if 'same(' in ds and ds[-1] == ')':
            params = ds[5:-1].replace(' ', '').split(',')
            if len(params) == 2:
                return getattr(neurons_or_synapses[params[0], 0], params[1])

        plot = False
        if ';plot' in ds:
            ds = ds.replace(';plot', '')
            plot = True

        result = ds

        if '(' in ds and ')' in ds:#is function
            if type(neurons_or_synapses).__name__ == "NeuronGroup":
                result = neurons_or_synapses.get_neuron_vec(ds)

            if type(neurons_or_synapses).__name__ == "SynapseGroup":
                result = neurons_or_synapses.get_synapse_mat(ds)

        if plot:
            if type(result) == np.ndarray:
                import matplotlib.pyplot as plt
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
            result = self.evaluate_diversity_string(result, neurons)

        if type(result) is str and default is not None:
            if '%' in result and is_number(result.replace('%', '')):
                result = str(float(result.replace('%', '')) / 100.0)

            result = type(default)(result)#cast


        return result



    def visualize_module(self, vmi=None, vmo=None, vma=None):
        from PymoNNto.Exploration.Visualization import Module_visualizer as drawer
        self.visualization_module_inputs = vmi
        self.visualization_module_outputs = vmo
        self.visualization_module_attributes = vma
        md = drawer.module_drawer()
        md.add_module(self)
        md.show()

    #helper function for UI

    def get_UI_Tabs(self):
        return []

    def get_UI_Preview_Plots(self):
        #Examples:
        #[[np.sin(x) for x in range(100)]] # only y
        #[[list(range(100)),[np.sin(x) for x in range(100)]]] x and y
        #[[np.sin(x) for x in range(100)],[np.sin(x) for x in range(100)]] # two plots only y
        #[np.random.rand(291, 291, 3)] image
        #[np.random.rand(291, 291, 3), [np.sin(x) for x in range(100)]] image and plot
        return None
    
    