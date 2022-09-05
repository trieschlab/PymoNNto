from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.NetworkCore.Base import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.info_tabs import *
import copy
import pickle
import os

compile_class = type(compile('1+1', '<string>', 'eval'))
base_obj_type = NetworkObjectBase

class sidebar_save_load_module(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def clear_compiled_code(self, obj, visited=[]):

        if isinstance(obj, base_obj_type) and (obj not in visited):
            visited.append(obj)
            d = obj.__dict__
            for key in d:
                if type(getattr(obj, key)) in [list, dict] or isinstance(getattr(obj, key), base_obj_type):
                    self.clear_compiled_code(d[key], visited)

                if type(getattr(obj, key)) is compile_class:
                    setattr(obj, key, None)

        visited.append(obj)

        if type(obj) is list:
            for i in range(len(obj)):
                if type(obj[i]) in [list, dict] or isinstance(obj[i], base_obj_type):
                    self.clear_compiled_code(obj[i], visited)

                if type(obj[i]) is compile_class:
                    obj[i] = None

        if type(obj) is dict:
            for sub_obj_key in obj:
                if type(obj[sub_obj_key]) in [list, dict] or isinstance(obj[sub_obj_key], base_obj_type):
                    self.clear_compiled_code(obj[sub_obj_key], visited)

                if type(obj[sub_obj_key]) is compile_class:
                    obj[sub_obj_key] = None




    def initialize(self, Network_UI):

        self.folder=get_data_folder()+'/NetworkStates/'

        if not os.path.exists(self.folder):
            try:
                os.mkdir(self.folder)
            except:
                print('was not able to create Data/NetworkStates folder')

        Network_UI.sidebar.add_row()

        self.save_edit = Network_UI.sidebar.add_widget(QLineEdit('name...'))

        def save(event):
            net = copy.deepcopy(Network_UI.network)
            self.clear_compiled_code(net)
            pickle.dump(net, open(self.folder + self.save_edit.text() + '.netstate', 'wb'))
            self.load_box.addItem(self.save_edit.text())

        self.save_btn = Network_UI.sidebar.add_widget(QPushButton('save', Network_UI.main_window))
        self.save_btn.clicked.connect(save)


        self.load_box = Network_UI.sidebar.add_widget(QComboBox())
        for file in os.listdir(self.folder):
            if '.obj' in str(file):
                self.load_box.addItem(file.replace('.netstate', ''))


        def load(event):
            Network_UI.network = pickle.load(open(self.folder + self.load_box.currentText() + '.netstate', 'rb'))

            for tab in Network_UI.infotabs:
                Network_UI.tabs.removeTab(len(Network_UI.tabs) - 1)

            Network_UI.modules.append(info_tab(Network_UI))

        self.load_btn = Network_UI.sidebar.add_widget(QPushButton('load', Network_UI.main_window))
        self.load_btn.clicked.connect(load)


    def update(self, Network_UI):
        return