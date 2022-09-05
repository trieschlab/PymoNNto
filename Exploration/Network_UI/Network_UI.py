from PymoNNto.Exploration.UI_Base import *
from PymoNNto.NetworkBehaviour.Recorder.Recorder import *
from PymoNNto.Exploration.Network_UI.Neuron_Classification_Colorizer import *
from PymoNNto.NetworkBehaviour.Structure.Structure import *

class Network_UI(UI_Base):

    def __init__(self, network, modules=[], title='Network UI', group_tags=[], transmitters=[], storage_manager=None, group_display_count=None, reduced_layout=False):

        network.simulate_iteration()

        network.clear_recorder()

        self.render_every_x_frames = 1

        for ng in network.NeuronGroups:
            if ng['NeuronDimension', 0] is None:
                network.add_behaviours_to_object({0: get_squared_dim(ng.size)}, ng)

            if not hasattr(ng, 'color'):
                ng.color = (0, 0, 255, 255)
            ng.add_analysis_module(Neuron_Classification_Colorizer())

        if group_tags==[]:
            for ng in network.NeuronGroups:
                if ng.tags[0] not in group_tags:
                    group_tags.append(ng.tags[0])

        if transmitters==[]:
            for sg in network.SynapseGroups:
                if sg.tags[0] not in transmitters:
                    transmitters.append(sg.tags[0])

        self.reduced_layout=reduced_layout

        super().__init__(title=title)
        self.network = network

        self.event_list = []

        if group_display_count is None:
            group_display_count = len(network.NeuronGroups)

        self.group_display_count = group_display_count


        self.group_tags = group_tags
        self.transmitters=transmitters
        self.pause = False
        self.update_without_state_change = False
        self.storage_manager = storage_manager

        self.neuron_visible_groups = []

        self._neuron_select_group = network[group_tags[0], 0]
        self._neuron_select_mask = self._neuron_select_group.get_neuron_vec().astype(np.bool)#np.array([0])
        self._neuron_select_mask[0] = True

        self.neuron_select_x = 0
        self.neuron_select_y = 0

        self.neuron_select_color = (0, 255, 0, 255)

        self.modules = modules

        if type(self.modules) is dict:
            self.modules = self.modules.values()

        for beh in network.all_behaviours():
            for module in beh.get_UI_Tabs():
                self.modules.append(module)

        for module in self.modules:
            print('Initialize:', type(module).__name__)
            self.sidebar.set_parent_layout(root=True)
            module.initialize(self)

        for group_tag in group_tags:
            for group in network[group_tag]:

                group._rec_dict = {}

                for module in self.modules:
                    module.add_recorder_variables(group, self)

        self.init_recoders()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(40)

    def select_neuron_class(self, group, class_id, add_to_select_group=False):
        return self.select_neurons(group, group.classification == class_id, add_to_select_group)

    def select_neuron(self, group, id, add_to_select_group=False):
        return self.select_neurons(group, id, add_to_select_group)

    def select_neurons(self, group, mask, add_to_select_group=False):

        add_to_select_group = add_to_select_group or self.control_key_down

        group_changed = group != self._neuron_select_group
        self._neuron_select_group = group
        if group_changed or not add_to_select_group:
            self._neuron_select_mask = self._neuron_select_group.get_neuron_vec().astype(np.bool)
        self._neuron_select_mask[mask] = True

        print(np.where(self._neuron_select_mask>0)[0])

        for module in self.modules:
            module.on_selected_neuron_changed(self)

        self.static_update_func()


    def selected_class_ids(self):
        return np.unique(self._neuron_select_group.classification[self._neuron_select_mask])

    def selected_neuron_tag(self):
        return self._neuron_select_group.tags[0]

    def selected_neuron_group(self):
        return self._neuron_select_group

    def selected_neuron_mask(self):
        return self._neuron_select_mask

    def selected_neuron_id(self):
        return self._neuron_select_mask.argmax()#first "True" value in array

    def selected_neuron_ids(self):
        return np.where(self._neuron_select_mask)[0]



    def add_recording_variable(self, group, var, timesteps):

        try:
            n = group  # for eval
            eval(var) #produce error when not evaluable

            old_ts=0
            if var in group._rec_dict:
                old_ts=group._rec_dict[var]

            group._rec_dict[var] = max(timesteps,old_ts)
            #recorder.add_varable('n.output')
            return True
        except:
            return False

    def init_recoders(self):
        for group_tag in self.group_tags:
            for group in self.network[group_tag]:

                rec_time_dict={}
                for variable in group._rec_dict:
                    rec_length=group._rec_dict[variable]
                    if rec_length not in rec_time_dict:
                        rec_time_dict[rec_length]=[]
                    rec_time_dict[rec_length].append(variable)

                for rec_length in rec_time_dict:
                    rec = Recorder(rec_time_dict[rec_length] + ['n.iteration'], tag='UI_rec,rec_' + str(rec_length), max_length=rec_length)
                    self.network.add_behaviours_to_object({10000+rec_length: rec}, group)


    def static_update_func(self, event=None):
        if self.pause:
            self.update_without_state_change=True

    def get_selected_neuron_subgroup(self):
        syn_sgs = self.get_selected_synapses()
        if len(syn_sgs) > 0:
            return syn_sgs[0]
        else:
            return None

    def get_selected_synapses(self):
        result = []
        group = self.selected_neuron_group()
        synapse_groups = group.afferent_synapses['All']
        for i, s in enumerate(synapse_groups):
            if (type(s.dst.mask) == np.ndarray and s.dst.mask[self.selected_neuron_id()]) or (type(s.dst.mask) is bool and s.dst.mask == True):
                result.append(synapse_groups[i].dst)
        return result

    def on_timer(self):

        if not self.pause or self.step or self.update_without_state_change:
            self.step = False
            if not self.update_without_state_change:
                for i in range(self.render_every_x_frames):
                    self.network.simulate_iteration()

            self.it = self.network.iteration

            for module in self.modules:
                module.update(self)

            self.update_without_state_change = False

    def on_tab_change(self, i):
        self.static_update_func()

    def add_event(self, tag, duration=0):
        self.event_list.append(event(self.network.iteration, tag, self.network.iteration+duration))

def get_color(type_index, layer=1):
    dim_value = max(layer * 0.9, 1.0)

    if type_index == 0:
        return (0.0, 0.0, 255.0 / dim_value, 255.0)
    if type_index == 1:
        return (255.0 / dim_value, 0.0, 0.0, 255.0)
    if type_index == 2:
        return (255.0 / dim_value, 150.0 / dim_value, 0.0, 255.0)
    if type_index == 3:
        return (255.0 / dim_value, 80.0 / dim_value, 0.0, 255.0)
    if type_index == 4:
        return (255.0 / dim_value, 0.0 , 150.0/ dim_value, 255.0)


class event:

    def __init__(self, start_t, tag, end_t=None):
        self.start_t = start_t
        self.end_t = end_t
        self.tag = tag





class Analytics_Results_Select_ComboBox(QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def __init__(self, main_object, tag='classifier', first_entry=None, select_last=True, on_update_func=None):
        super().__init__()

        self.on_update_func = on_update_func

        self.first_entry = first_entry
        self.tag = tag

        self.current_results = {}
        self.current_modules = {}

        self.main_object = None
        self.change_main_object(main_object)

        if select_last and self.count() > 0:
            self.setCurrentIndex(self.count()-1)



    def change_main_object(self, main_object):
        if self.main_object is not None:
            self.remove_update_notifier()
        self.main_object = main_object
        self.update()
        self.set_update_notifier()

    def set_update_notifier(self):
        if isinstance(self.main_object, AnalysisModule):
            self.main_object.set_update_notifier(self.update)
        else:
            for obj in self.main_object[self.tag]:
                if isinstance(obj, AnalysisModule):
                    obj.set_update_notifier(self.update)

    def remove_update_notifier(self):
        if isinstance(self.main_object, AnalysisModule):
            self.main_object.remove_update_notifier(self.update)
        else:
            for obj in self.main_object[self.tag]:
                if isinstance(obj, AnalysisModule):
                    obj.remove_update_notifier(self.update)

    def get_selected_key(self):
        return self.currentText()

    def get_selected_module(self):
        key = self.get_selected_key()
        if key in self.current_modules:
            return self.current_modules[key]

    def get_selected_result(self):
        key = self.get_selected_key()
        if key in self.current_results:
            return self.current_results[key]

    def update(self, key=None):
        if key is None:
            current = self.currentText()
        else:
            current = key

        self.clear()

        if self.first_entry is not None:
            self.addItem(self.first_entry)

        if isinstance(self.main_object, AnalysisModule):
            self.current_results = self.main_object.get_results()
            for k in self.current_results:
                self.addItem(k)
            self.current_modules = {k: self.main_object for k in self.current_results}
        else:
            self.current_results, self.current_modules = self.main_object.get_all_analysis_module_results(self.tag, True)
            for k in self.current_results:
                self.addItem(k)

        for i in range(self.count()):
            if self.itemText(i) == current:
                self.setCurrentIndex(i)

        if self.on_update_func is not None:
            self.on_update_func(self.main_object, self.get_selected_module(), self.get_selected_key(), self.get_selected_result())



########################################################### Exception handling

#def except_hook(cls, exception, traceback):
#    sys.__excepthook__(cls, exception, traceback)

#sys.excepthook = except_hook


