from NetworkCore.Base import *

class PatternGroup(NetworkObjectBase):

    def __init__(self, **kwargs):
        super().__init__(kwargs.get('tag', None))
        self.kwargs=kwargs

        self.active = True
        self.current_pattern_index = -1

        if kwargs is not None:
            self.group_possibility = kwargs.get('group_possibility', 1.0)
            self.overlapping_with_other_groups = kwargs.get('overlapping_with_other_groups', False)
            self.has_overlapping_priority = kwargs.get('has_overlapping_priority', True)

        self.initialize()

    def initialize(self):
        return

    def initialize_neuron_group(self, neurons):
        return

    def get_pattern(self, neurons):
        return None

