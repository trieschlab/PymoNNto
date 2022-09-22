from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *

class sidebar_neuron_grid_submodule(TabBase):

    def __init__(self, add_color_dict):
        self.add_color_dict = add_color_dict

        self.compiled = {}
        for param in self.add_color_dict:
            self.compiled[param] = compile('n.'+param, '<string>', 'eval')

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def on_selected_neuron_changed(self, Network_UI):
        tag = self.image_item.neuron_group_tag
        self.color_select_box.change_main_object(Network_UI.network[tag, 0])

    def get_clicked_neuron_id(self, Network_UI, event):
        group_tag = event.currentItem.neuron_group_tag
        w = Network_UI.network[group_tag, 0].width
        h = Network_UI.network[group_tag, 0].height
        d = Network_UI.network[group_tag, 0].depth
        y_temp = int(
            (h * d - 1) - np.trunc(event.pos().y()))

        neuron_select_x = np.clip(int(np.trunc(event.pos().x())), 0, w - 1)
        neuron_select_y = np.clip(int(y_temp - np.trunc(y_temp / h)), 0, h - 1)
        neuron_select_z = np.clip(int(np.trunc(y_temp / h)), 0, d - 1)

        h_abs = np.clip(int(y_temp), 0, h * d - 1)
        return (h_abs) * w + neuron_select_x

    def initialize(self, Network_UI, index):
        #just store for mcde event bug ('QGraphicsSceneMouseEvent' object has no attribute 'currentItem')
        self.last_id = 0
        self.last_group = None

        def mce(event):
            self.last_id = self.get_clicked_neuron_id(Network_UI, event)
            self.last_group = Network_UI.network[event.currentItem.neuron_group_tag, 0]
            Network_UI.select_neuron(self.last_group, self.last_id)

        def mdce(event):
            if self.last_group.classification is not None:
                selected_class = self.last_group.classification[self.last_id]
                Network_UI.select_neuron_class(self.last_group, selected_class)

        group_select_box = QComboBox()
        self.color_select_box = Analytics_Results_Select_ComboBox(Network_UI.network[Network_UI.group_tags[index], 0] ,'classifier', first_entry='group color')

        #Network_UI.sidebar.add_row()
        #Network_UI.sidebar.add_widget(group_select_box, stretch=0)
        #Network_UI.sidebar.add_widget(self.color_select_box, stretch=0)
        #Network_UI.sidebar.set_parent_layout()

        Network_UI.sidebar.add_row()
        Network_UI.sidebar.add_widget([group_select_box, self.color_select_box])
        Network_UI.sidebar.set_parent_layout()

        self.image_item = Network_UI.sidebar.add_plot(tooltip_message='white: active neurons\r\ncolor: neuron classification or base color\r\ngreen: selected neuron', stretch=100).add_image()

        self.image_item.neuron_group_tag = Network_UI.group_tags[index]
        Network_UI.neuron_visible_groups.append(Network_UI.group_tags[index])
        self.image_item.mouseClickEvent = mce

        self.image_item.mouseDoubleClickEvent = mdce


        def group_changed(select_index):
            tag = Network_UI.group_tags[select_index]
            Network_UI.select_neuron(Network_UI.network[tag, 0], 0)
            self.color_select_box.change_main_object(Network_UI.network[tag, 0])
            self.image_item.neuron_group_tag = tag
            Network_UI.neuron_visible_groups[index] = tag

        group_select_box.addItems(Network_UI.group_tags)
        group_select_box.setCurrentIndex(index)
        group_select_box.currentIndexChanged.connect(group_changed)



    def update(self, Network_UI):
        group_tag = self.image_item.neuron_group_tag
        if len(Network_UI.network[group_tag]) > 0:

            group = Network_UI.network[group_tag, 0]
            n = group #for eval operations

            group.classification = self.color_select_box.get_selected_result()
            if group.classification is None:
                group.classification = group.get_neuron_vec()
            image = np.array(group['Neuron_Classification_Colorizer', 0].get_color_list(group.classification, format='[r,g,b]'))

            #selected
            if Network_UI.selected_neuron_group().tags[0] == group_tag:
                for i in range(3):
                    image[Network_UI.selected_neuron_mask(), i] = Network_UI.neuron_select_color[i]

            #parameter
            for param, color in self.add_color_dict.items():
                try:
                    data=eval(self.compiled[param])

                    if (type(data) == np.ndarray and data.dtype == np.dtype('bool')) or (type(data) == bool):
                        for i in range(3):
                            image[data, i] += color[i]
                    else:
                        for i in range(3):
                            image[:, i] += color[i]*data
                except:
                    pass



            image=np.reshape(image, (group.height*group.depth, group.width, 3))#group.depth
            self.image_item.setImage(np.rot90(image, 3), levels=(0, 255))

class UI_sidebar_neuron_grid_module():

    def __init__(self, group_display_count=1, add_color_dict={'output': (255, 255, 255)}):
        self.group_display_count = group_display_count
        if type(add_color_dict) is str:
            add_color_dict={add_color_dict:(255,255,255)}
        self.add_color_dict = add_color_dict

    def add_recorder_variables(self, neuron_group, Network_UI):
        for module in self.sub_modules:
            module.add_recorder_variables(neuron_group, Network_UI)

    def on_selected_neuron_changed(self, NetworkUI):
        for module in self.sub_modules:
            module.on_selected_neuron_changed(NetworkUI)

    def initialize(self, Network_UI):

        if Network_UI.group_display_count is not None:
            self.group_display_count=Network_UI.group_display_count

        self.sub_modules = []
        for i in range(self.group_display_count):
            self.sub_modules.append(sidebar_neuron_grid_submodule(self.add_color_dict))
            self.sub_modules[-1].initialize(Network_UI, np.minimum(i, len(Network_UI.group_tags)))

    def update(self, Network_UI):
        for module in self.sub_modules:
            module.update(Network_UI)