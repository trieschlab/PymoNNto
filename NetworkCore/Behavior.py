from PymoNNto.NetworkCore.Base_Tagable_Object import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *



class Behavior(TaggableObjectBase):

    initialize_on_init = False
    initialize_last = False
    attached_UI_Tabs = []


    def initialize(self, neurons):
        return

    def iteration(self, neurons):
        return


    def __init__(self, *args, **kwargs):
        self.init_kwargs = kwargs
        for i, arg in enumerate(args):
           self.init_kwargs['arg_'+str(i)]=arg
        self.used_attr_keys = []
        self.behavior_enabled = self.parameter('behavior_enabled', True, None)
        super().__init__(tag=self.parameter('tag', None, None))
        self.empty_iteration_function = self.is_empty_iteration_function()

        if hasattr(self, 'set_variables'):
            raise Exception('"set_variables" is deprecated. Please rename function to "initialize"')
        if hasattr(self, 'new_iteration'):
            raise Exception('"new_iteration" is deprecated. Please rename function to "iteration"')


    def set_gene_variables(self):

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

                gene_value = get_gene(gene_key, default_value)

                self.init_kwargs[variable_key] = s[:start] + '{:.15f}'.format(gene_value).rstrip('0').rstrip('.') + s[end + 1:]

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
                result = neurons_or_synapses.vector(ds)

            if type(neurons_or_synapses).__name__ == "SynapseGroup":
                result = neurons_or_synapses.matrix(ds)

        if plot:
            if type(result) == np.ndarray:
                import matplotlib.pyplot as plt
                plt.hist(result, bins=30)
                plt.show()

        return result


    def set_parameters_as_variables(self, object):
        for key in self.init_kwargs:
            setattr(object, key, self.parameter(key, None, neurons=object))

    set_init_attrs_as_variables = set_parameters_as_variables

    def check_unused_attrs(self):
        for key in self.init_kwargs:
            if not key in self.used_attr_keys:
                print('Warning: "'+key+'" not used in initialize of '+str(self)+' behavior! Make sure that "'+key+'" is spelled correctly and parameter('+key+',...) is called in initialize. Valid attributes are:'+str(self.used_attr_keys))

    def parameter(self, key, default=None, neurons=None, do_not_diversify=False, search_other_behaviors=False, required=False):

        if required and not key in self.init_kwargs:
            print('Warning:',key,'has to be specified for the behavior to run properly.', self)

        self.used_attr_keys.append(key)

        result = self.init_kwargs.get(key, default)

        if key not in self.init_kwargs and neurons is not None and search_other_behaviors:
            for b in neurons.behaviors:
                if key in b.init_kwargs:
                    result = b.init_kwargs.get(key, result)

        if not do_not_diversify and type(result) is str and neurons is not None:
            result = self.evaluate_diversity_string(result, neurons)

        if type(result) is str and default is not None:
            if '%' in result and is_number(result.replace('%', '')):
                result = str(float(result.replace('%', '')) / 100.0)

            try:
                result = type(default)(result)#cast
            except:
                result = float(result)#to prevent int error during evolution


        return result

    get_init_attr = parameter
    kwargs = parameter
    args = parameter
    parameter = parameter
    argument = parameter

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

    def is_empty_iteration_function(self):
        f = self.iteration

        #Returns true if f is an empty function.
        def empty_func():
            pass

        def empty_func_with_docstring():
            #Empty function with docstring.
            pass

        def constants(f):
            #Return a tuple containing all the constants of a function without: * docstring
            return tuple(x for x in f.__code__.co_consts if x != f.__doc__)

        return (f.__code__.co_code == empty_func.__code__.co_code and constants(f) == constants(empty_func)) or \
               (f.__code__.co_code == empty_func_with_docstring.__code__.co_code and constants(f) == constants(empty_func_with_docstring))


class Behaviour(Behavior):
    def __init__(self, *args, **kwargs):
        raise Exception("Warning: 'Behaviour' is depreciated. Please use 'Behavior' instead!")

