from PymoNNto.Exploration.Network_UI.TabBase import *

class sidebar_activity_sub_module(TabBase):

    def __init__(self, add_color_dict={'output': (255, 255, 255), 'Input_Mask': (-100, -100, -100)}):
        self.add_color_dict = add_color_dict
        self.compiled={}
        for param in self.add_color_dict:
            self.compiled[param] = compile('n.'+param, '<string>', 'eval')

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI, index):

        def mce(event):
            Network_UI.neuron_select_group = event.currentItem.neuron_group_tag
            w = Network_UI.network[Network_UI.neuron_select_group, 0].width
            h = Network_UI.network[Network_UI.neuron_select_group, 0].height
            d = Network_UI.network[Network_UI.neuron_select_group, 0].depth
            y_temp = int((h*d - 1) - np.trunc(event.pos().y())) #np.clip(int((h - 1) - np.trunc(event.pos().y())), 0, h - 1)

            Network_UI.neuron_select_x = np.clip(int(np.trunc(event.pos().x())), 0, w - 1)
            Network_UI.neuron_select_y = np.clip(int(y_temp-np.trunc(y_temp/h)), 0, h - 1)
            Network_UI.neuron_select_z = np.clip(int(np.trunc(y_temp/h)), 0, d - 1)

            h_abs = np.clip(int(y_temp), 0, h * d - 1)
            Network_UI.neuron_select_id = (h_abs) * w + Network_UI.neuron_select_x

            #print(Network_UI.neuron_select_x, Network_UI.neuron_select_y, Network_UI.neuron_select_z, Network_UI.neuron_select_id, ' ', event.pos().x(), event.pos().y())
            Network_UI.static_update_func()

        group_select_box=QComboBox()
        Network_UI.Add_Sidebar_Element(group_select_box)

        self.image_item = Network_UI.Add_Image_Item(False, True, tooltip_message='white: active neurons\r\ndarker color: primary input neurons\r\ngreen: selected neuron')

        self.image_item.neuron_group_tag = Network_UI.group_tags[index]
        Network_UI.neuron_visible_groups.append(Network_UI.group_tags[index])
        self.image_item.mouseClickEvent = mce

        def group_changed(select_index):
            tag = Network_UI.group_tags[select_index]
            Network_UI.neuron_select_group = tag
            self.image_item.neuron_group_tag = tag
            Network_UI.neuron_visible_groups[index] = tag
            Network_UI.neuron_select_id = 0

        group_select_box.addItems(Network_UI.group_tags)
        group_select_box.setCurrentIndex(index)
        group_select_box.currentIndexChanged.connect(group_changed)



    def update(self, Network_UI):

        #for group_tag in Network_UI.group_tags:
        group_tag = self.image_item.neuron_group_tag
        if len(Network_UI.network[group_tag]) > 0:

            group = Network_UI.network[group_tag, 0]
            n=group #for eval operations

            alpha = group.color[3] / 255.0
            base_color = (group.color[0] * alpha, group.color[1] * alpha, group.color[2] * alpha)

            image=np.zeros((group.size,3))

            for i in range(3):
                image[:, i] += base_color[i]

            if Network_UI.neuron_select_group == group_tag:
                for i in range(3):
                    image[Network_UI.neuron_select_id, i] = Network_UI.neuron_select_color[i]

            for param, color in self.add_color_dict.items():
                try:
                #if True:#hasattr(group, param):
                    data=eval(self.compiled[param])

                    if (type(data) == np.ndarray and data.dtype == np.dtype('bool')) or (type(data) == bool):
                        for i in range(3):
                            image[data, i] += color[i]
                    else:
                        for i in range(3):
                            image[:, i] += color[i]*data
                except:
                    pass#print(param, "can not be evaluated")

            image=np.reshape(image, (group.height*group.depth, group.width, 3))#group.depth
            self.image_item.setImage(np.rot90(image, 3), levels=(0, 255))

class UI_sidebar_activity_module():

    def __init__(self, group_display_count=1, add_color_dict={'output': (255, 255, 255), 'Input_Mask': (-100, -100, -100)}):
        self.group_display_count=group_display_count
        self.add_color_dict=add_color_dict

    def add_recorder_variables(self, neuron_group, Network_UI):
        for module in self.sub_modules:
            module.add_recorder_variables(neuron_group, Network_UI)

    def initialize(self, Network_UI):

        if Network_UI.group_display_count is not None:
            self.group_display_count=Network_UI.group_display_count

        self.sub_modules = []
        for i in range(self.group_display_count):
            self.sub_modules.append(sidebar_activity_sub_module(add_color_dict=self.add_color_dict))
            self.sub_modules[-1].initialize(Network_UI, np.minimum(i, len(Network_UI.group_tags)))

    def update(self, Network_UI):
        for module in self.sub_modules:
            module.update(Network_UI)