from PymoNNto.Exploration.Network_UI.TabBase import *

class sidebar_module_quick_access(TabBase):

    def __init__(self, module_tags=[]):
        self.module_tags = module_tags

    def module_on_off(self, cb, Network_UI):
        module_tag=cb.module_tag
        print(module_tag)
        Network_UI.network.set_mechanisms([module_tag], cb.isChecked())
        Network_UI.add_event(module_tag + ' (' + str(cb.isChecked()) + ')')

    def add_cb(self, module_tag, Network_UI):

        def module_on_off(event):
            print(module_tag)
            Network_UI.network.set_mechanisms([module_tag], cb.isChecked())
            Network_UI.add_event(module_tag + ' (' + str(cb.isChecked()) + ')')

        cb = QCheckBox()
        cb.module_tag = module_tag
        cb.setText(module_tag)
        cb.setChecked(Network_UI.network[module_tag, 0].behaviour_enabled)
        cb.stateChanged.connect(module_on_off)
        Network_UI.Add_Sidebar_Element(cb)

    def initialize(self, Network_UI):

        for module_tag in self.module_tags:
            if Network_UI.network.has_module(module_tag):# Network_UI.network[self.module_tag, 0] is not None:
                self.add_cb(module_tag, Network_UI)

        '''
        if Network_UI.network['STDP', 0] is not None:
            def learning_on_off(event):
                Network_UI.network.set_mechanisms(['STDP'], self.stdp_cb.isChecked())
                Network_UI.add_event('STDP (' + str(self.stdp_cb.isChecked()) + ')')

            self.stdp_cb = QCheckBox()
            self.stdp_cb.setText('STDP')
            self.stdp_cb.setChecked(Network_UI.network['STDP', 0].behaviour_enabled)
            self.stdp_cb.stateChanged.connect(learning_on_off)
            Network_UI.Add_Sidebar_Element(self.stdp_cb)

        if Network_UI.network['Text_Activator', 0] is not None:
            def activator_on_off(event):
                Network_UI.network['Text_Activator', 0].behaviour_enabled = self.act_cb.isChecked()
                Network_UI.add_event('Text_Activator (' + str(self.act_cb.isChecked()) + ')')

            self.act_cb = QCheckBox()
            self.act_cb.setText('Text input:')
            self.act_cb.setChecked(Network_UI.network['Text_Activator', 0].behaviour_enabled)
            self.act_cb.stateChanged.connect(activator_on_off)
            Network_UI.Add_Sidebar_Element(self.act_cb)
        '''