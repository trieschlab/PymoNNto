from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.NetworkCore.Base_Attachable_Modules import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.info_tabs import *
from PymoNNto.Exploration.HelperFunctions.Save_Load import *
import copy
import pickle
import os

class sidebar_save_load_module(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

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
            save_network(Network_UI.network, self.save_edit.text())
            #net = copy.deepcopy(Network_UI.network)
            #clear_compiled_code(net)
            #pickle.dump(net, open(self.folder + self.save_edit.text() + '.netstate', 'wb'))
            self.load_box.addItem(self.save_edit.text())

        self.save_btn = Network_UI.sidebar.add_widget(QPushButton('save', Network_UI.main_window))
        self.save_btn.clicked.connect(save)


        self.load_box = Network_UI.sidebar.add_widget(QComboBox())
        for file in os.listdir(self.folder):
            if '.netstate' in str(file):
                self.load_box.addItem(file.replace('.netstate', ''))


        def load(event):
            Network_UI.network = load_network(self.load_box.currentText())

            #Network_UI.network = pickle.load(open(self.folder + self.load_box.currentText() + '.netstate', 'rb'))

            for tab in Network_UI.infotabs:
                Network_UI.tabs.removeTab(len(Network_UI.tabs) - 1)

            Network_UI.modules.append(info_tab(Network_UI))

        self.load_btn = Network_UI.sidebar.add_widget(QPushButton('load', Network_UI.main_window))
        self.load_btn.clicked.connect(load)


    def update(self, Network_UI):
        return