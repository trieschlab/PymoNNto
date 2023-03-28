from PymoNNto.Exploration.Network_UI.TabBase import *

class sidebar_module_quick_access(TabBase):

    def __init__(self, module_tags=[]):
        self.module_tags = module_tags

    def module_on_off(self, cb, Network_UI):
        module_tag=cb.module_tag
        print(module_tag)
        Network_UI.network.set_behaviors(module_tag, cb.isChecked())
        Network_UI.add_event(module_tag + ' (' + str(cb.isChecked()) + ')')

    def add_cb(self, module_tag, Network_UI):

        def module_on_off(event):
            print(module_tag)
            Network_UI.network.set_behaviors(module_tag, cb.isChecked())
            Network_UI.add_event(module_tag + ' (' + str(cb.isChecked()) + ')')

        cb = QCheckBox()
        cb.module_tag = module_tag
        cb.setText(module_tag)
        cb.setChecked(Network_UI.network[module_tag, 0].behavior_enabled)
        cb.stateChanged.connect(module_on_off)
        Network_UI.sidebar.add_widget(cb)

    def initialize(self, Network_UI):

        for module_tag in self.module_tags:
            if Network_UI.network.has_module(module_tag):
                self.add_cb(module_tag, Network_UI)
