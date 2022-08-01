from PymoNNto.NetworkCore.Base import *
import inspect

#This class can be used to add tag-searchable functions to the neurongroups, synapsegroups and the network object.
#It has a main execute funtion which can be called with module(...) or module.exec(...)
#Other "normal" functions can be added as well.
#Via the add_tag function, the modules can be categorized into groups

class AnalysisModule(NetworkObjectBase):

    def __init__(self, parent=None, **kwargs):
        self.init_kwargs = kwargs
        super().__init__(tag=self.get_init_attr('tag', None))

        self.used_attr_keys = []

        self.add_tag(self.__class__.__name__)

        self.execution_arguments = self._get_default_args_(self.execute)

        self.result_storage = {}#key=arguments value=result from run
        self.current_result = None
        self.save_results = True

        self.update_notifier_functions = []

        self.progress_update_function = None

        if parent is not None:
            self._attach_and_initialize_(parent)


    def add_progress_update_function(self, function):
        self.progress_update_function = function

    def update_progress(self, percent):
        if self.progress_update_function is not None:
            self.progress_update_function(percent)

    def _attach_and_initialize_(self, parent):
        self.parent = parent  # NeuronGroup SynapseGroup or Network
        parent.analysis_modules.append(self)
        setattr(parent, self.__class__.__name__, self) #ng1.AnalysisModule(...)
        self.initialize(parent)

    def initialize(self, neurons): #override
        #access arguments via get_init_attr(key, default)
        #self.add_tag('classifier')
        #self.add_execution_argument(...)
        #execute does not have to be used. You can just add all kinds of easy access convenience funtions to the class
        return

    def execute(self, neurons, **kwargs): #override (do not call directly with instance.execute(...). Use instance(...))
        #self.parent
        return


    def is_executable(self):
        return type(self).execute != AnalysisModule.execute
        #return self.execute is super(AnalysisModule, self).execute

    def get_init_attr(self, key, default):
        if key in self.init_kwargs:
            return self.init_kwargs[key]
        else:
            return default

    def _update_notification_(self, key=None):
        for function in self.update_notifier_functions:
            function(key)

    def remove_update_notifier(self, function):
        if function in self.update_notifier_functions:
            self.update_notifier_functions.remove(function)

    def set_update_notifier(self, function):
        self.update_notifier_functions.append(function)

    #def add_execution_argument(self, key, default):
    #    self.execution_arguments[key] = default

    def __call__(self, **kwargs):
        self.update_progress(0)
        self.current_key = self.generate_current_key(kwargs)
        return self.save_result(self.current_key,self.execute(self.parent, **kwargs))

    def exec(self, **kwargs):
        self.update_progress(0)
        self.current_key = self.generate_current_key(kwargs)
        return self.save_result(self.current_key,self.execute(self.parent, **kwargs))


    def _get_base_name_(self):
        return self.__class__.__name__

    def generate_current_key(self, args_key, add_args=True):
        key = self._get_base_name_()
        if len(args_key) > 0 and add_args:
            key += ' ' + str(args_key)
        return key

    def save_result(self, key, result):
        self.update_progress(100)
        if self.save_results and result is not None:
            self.current_result = result
            self.result_storage[key] = result
        self._update_notification_(key)
        return result

    def last_call_result(self):
        return self.current_result

    def get_results(self):
        return self.result_storage

    def remove_result(self, key):
        if key in self.result_storage:
            return self.result_storage.pop(key)
        else:
            print('cannot remove result', key, 'not found.')
        self._update_notification_()

    def clear_results(self):
        self.result_storage = {}
        self._update_notification_()

    def _get_default_args_(self, func, exclude=['self', 'args', 'kwargs'], exclude_first=True):
        result = {}
        signature = inspect.signature(func)
        i=0
        for k, v in signature.parameters.items():
            if i>0 or not exclude_first:
                if k not in exclude:
                    if v.default is not inspect.Parameter.empty:
                        result[k] = v.default
                    else:
                        result[k] = ''
            i += 1
        return result


