from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *




class UI_sidebar_network_selector():

    def __init__(self, add_color_dict={'output': (255, 255, 255)}):
        if type(add_color_dict) is str:
            add_color_dict={add_color_dict:(255,255,255)}
        self.add_color_dict = add_color_dict

        self.compiled = {}
        for param in self.add_color_dict:
            self.compiled[param] = compile('n.'+param, '<string>', 'eval')

    #def add_recorder_variables(self, neuron_group, Network_UI):
    #    for module in self.sub_modules:
    #        module.add_recorder_variables(neuron_group, Network_UI)

    #def on_selected_neuron_changed(self, NetworkUI):
    #    for module in self.sub_modules:
    #        module.on_selected_neuron_changed(NetworkUI)

    def get_clicked_neuron_id(self, Network_UI, event):
        group = event.currentItem.neuron_group
        w = group.width
        h = group.height
        d = group.depth
        y_temp = int(
            (h * d - 1) - np.trunc(event.pos().y()))

        neuron_select_x = np.clip(int(np.trunc(event.pos().x())), 0, w - 1)
        neuron_select_y = np.clip(int(y_temp - np.trunc(y_temp / h)), 0, h - 1)
        neuron_select_z = np.clip(int(np.trunc(y_temp / h)), 0, d - 1)

        h_abs = np.clip(int(y_temp), 0, h * d - 1)
        return (h_abs) * w + neuron_select_x


    def addRow(self, Network_UI, layout, ng):
        row = QHBoxLayout()
        layout.addLayout(row, stretch=1)

        ng.visible_cb = QCheckBox()
        ng.uilabel = QLabel(ng.tag)
        ng.color_select_box = Analytics_Results_Select_ComboBox(ng, 'classifier', first_entry='group color')
        ng.slider = QSlider(1)

        ng.slider.setMinimum(0)
        ng.slider.setMaximum(100)
        ng.slider.setMaximumWidth(100)
        ng.slider.setSliderPosition(100)
        ng.slider.mouseReleaseEvent = Network_UI.static_update_func
        ng.slider.setToolTip('scale neuron-group plots up and down (only visualization)')

        row.addWidget(ng.visible_cb, stretch=1)
        row.addWidget(ng.uilabel, stretch=10)
        row.addWidget(ng.color_select_box, stretch=10)
        row.addWidget(ng.slider, stretch=10)

        ng.visible_cb.setChecked(True)
        ng.visible_cb.group = ng

        def visible_cb_changed(event):
            ng.visible_cb.group.is_visible = ng.visible_cb.isChecked()

        ng.visible_cb.stateChanged.connect(visible_cb_changed)

    def initialize(self, Network_UI):

        self.config_dlg = QDialog()
        self.config_dlg.setWindowTitle('config')
        layout = QVBoxLayout()
        self.config_dlg.setLayout(layout)
        self.config_dlg.resize(600, 100)

        #self.config_dlg
        #dlg.exec()

        self.selected_label = Network_UI.sidebar.add_widget(QLabel(), stretch=1)
        link_font = QFont()
        link_font.setUnderline(True)
        self.selected_label.setFont(link_font)
        self.selected_label.setStyleSheet("color: rgb(0,0,200)")

        def show_dlg(event):
            self.config_dlg.exec()
        self.selected_label.mouseReleaseEvent = show_dlg


        for ng in Network_UI.network.NeuronGroups:
            #layout = Network_UI.sidebar.add_row()

            self.addRow(Network_UI, layout, ng)

            # Network_UI.sidebar.add_widget(, stretch=0)

            #Network_UI.sidebar.add_widget(ng.color_select_box, stretch=0)

            #self.add_cb(Network_UI, ng)

            #ng.color_select_box.hide()
            #ng.uilabel.hide()
            #ng.hide_cb.hide()

            #layout.removeWidget(ng.color_select_box)
            #layout.removeWidget(ng.uilabel)

            #ng.color_select_box.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
            #ng.uilabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

            #ng.color_select_box.adjustSize()
            #ng.uilabel.adjustSize()
            #layout.adjustSize()

            #Network_UI.sidebar.set_parent_layout()

        self.plt = Network_UI.sidebar.add_plot(tooltip_message='white: active neurons\r\ncolor: neuron classification or base color\r\ngreen: selected neuron', stretch=100)



        #selected...
        self.sel_rect = QGraphicsRectItem()#

        self.plt.addItem(self.sel_rect)
        self.sel_rect.setPen(QPen(QColor(0, 255, 0), 3))


        #self.sel_rect.setParentItem()

        y = 0
        x = 0
        for i, ng in enumerate(Network_UI.network.NeuronGroups):

            ng.image_item = self.plt.add_image()
            ng.image_item.neuron_group=ng
            ng.classification = ng.vector()
            image = np.array(ng['Neuron_Classification_Colorizer', 0].get_color_list(ng.classification, format='[r,g,b]'))
            image = np.reshape(image, (ng.height * ng.depth, ng.width, 3))
            ng.image_item.setImage(np.rot90(image, 3), levels=(0, 255))

            ng.image_item.setPos(x, y)
            y += ng.height + 5

            def mce(event):
                self.last_id = self.get_clicked_neuron_id(Network_UI, event)
                self.last_group = event.currentItem.neuron_group#Network_UI.network[event.currentItem.neuron_group_tag, 0]
                Network_UI.select_neuron(self.last_group, self.last_id)
                #for neurons in Network_UI.network.NeuronGroups:
                #    neurons.color_select_box.hide()
                #    neurons.uilabel.hide()
                #    neurons.hide_cb.hide()
                #self.last_group.color_select_box.show()
                #self.last_group.uilabel.show()
                #self.last_group.hide_cb.show()


            def mdce(event):
                if self.last_group.classification is not None:
                    selected_class = self.last_group.classification[self.last_id]
                    Network_UI.select_neuron_class(self.last_group, selected_class)

            ng.image_item.mouseClickEvent = mce
            ng.image_item.mouseDoubleClickEvent = mdce



            #ng.image_item.setRect(0, -i * 10, ng.width, ng.height)

        #self.image_item.neuron_group = Network_UI.network.exc_neurons1

        #if Network_UI.group_display_count is not None:
        #    self.group_display_count=Network_UI.group_display_count

        #self.sub_modules = []
        #for i in range(self.group_display_count):
        #    self.sub_modules.append(sidebar_neuron_grid_submodule(self.add_color_dict))
        #    self.sub_modules[-1].initialize(Network_UI, np.minimum(i, len(Network_UI.group_tags)))

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def on_selected_neuron_changed(self, NetworkUI):
        return

    def update(self, Network_UI):

        for i, ng in enumerate(Network_UI.network.NeuronGroups):
            n = ng  # for eval operations

            ng.classification = ng.color_select_box.get_selected_result()
            if ng.classification is None:
                ng.classification = ng.vector()
            image = np.array(ng['Neuron_Classification_Colorizer', 0].get_color_list(ng.classification, format='[r,g,b]'))

            # selected
            if Network_UI.selected_neuron_group() == ng:
                self.selected_label.setText('Selected: ' + ng.tag)
                self.sel_rect.setRect(ng.image_item.boundingRect())
                self.sel_rect.setPos(ng.image_item.pos())
                # self.sel_rect.setPen(QColor=QColor(0,255,0,255))
                for i in range(3):
                    image[Network_UI.selected_neuron_mask(), i] = Network_UI.neuron_select_color[i]

            # parameter
            for param, color in self.add_color_dict.items():
                try:
                    data = eval(self.compiled[param])

                    if (type(data) == np.ndarray and data.dtype == np.dtype('bool')) or (type(data) == bool):
                        for i in range(3):
                            image[data, i] += color[i]
                    else:
                        for i in range(3):
                            image[:, i] += color[i] * data
                except:
                    pass

            image = np.reshape(image, (ng.height * ng.depth, ng.width, 3))  # ng.depth
            ng.image_item.setImage(np.rot90(image, 3), levels=(0, 255))
            #ng.image_item.setPos(0, i * 1000)
            #ng.image_item.setRect(0, -i * 10, ng.width, ng.height)

'''

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
            Network_UI.get_visible_neuron_groups()[index] = tag

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
                group.classification = group.vector()
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

'''