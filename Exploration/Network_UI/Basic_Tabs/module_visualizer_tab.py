from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Module_visualizer import *

class module_visualizer_tab(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):

        self.di_modules=[]
        group_tags=[group.tags[0] for group in get_unique_non_partitioned_Groups(Network_UI.network.all_objects())]

        for t,timestep in enumerate(Network_UI.network.behavior_timesteps):
            for i, net_obj in enumerate(get_unique_non_partitioned_Groups(Network_UI.network.all_objects())):

                if timestep in net_obj.behavior:
                    beh=net_obj.behavior[timestep]
                    module_name, inputs, outputs, attributes, module_type = analyze_module_and_get_info(beh)
                    mdi = Module_draw_item(module_name, inputs, outputs, attributes, module_type, x=t*1200, y=i*1200, onlyff=True)
                    self.di_modules.append(mdi)

        self.add_flow_chart(Network_UI, self.di_modules, group_tags, Network_UI.network.behavior_timesteps)

        Network_UI.Next_H_Block()
        self.connections_cb = Network_UI.Add_element(QCheckBox('connections'))
        def connections_cb_changed():
            for m in self.di_modules:
                m.draw_connection_lines = self.connections_cb.isChecked()
                m.update_pic(self.di_modules)
        self.connections_cb.setChecked(True)
        self.connections_cb.stateChanged.connect(connections_cb_changed)

        self.in_out_cb = Network_UI.Add_element(QCheckBox('inputs/outputs'))
        def in_out_cb_changed():
            for m in self.di_modules:
                m.draw_in_out_blocks = self.in_out_cb.isChecked()
                m.update_pic(self.di_modules)
        self.in_out_cb.setChecked(True)
        self.in_out_cb.stateChanged.connect(in_out_cb_changed)

        self.attributes_cb = Network_UI.Add_element(QCheckBox('attributes'))
        def attributes_cb_changed():
            for m in self.di_modules:
                m.draw_attributes = self.attributes_cb.isChecked()
                m.update_pic(self.di_modules)
        self.attributes_cb.setChecked(True)
        self.attributes_cb.stateChanged.connect(attributes_cb_changed)


        self.hlines_cb = Network_UI.Add_element(QCheckBox('hlines'))
        def h_line_cb_changed():
            for l in self.h_line_list:
                if not self.hlines_cb.isChecked():
                    self.flow_tab.plot.removeItem(l)
                else:
                    self.flow_tab.plot.addItem(l)
        self.hlines_cb.setChecked(True)
        self.hlines_cb.stateChanged.connect(h_line_cb_changed)

        self.vlines_cb = Network_UI.Add_element(QCheckBox('vlines'))
        def v_line_cb_changed():
            for l in self.v_line_list:
                if not self.vlines_cb.isChecked():
                    self.flow_tab.plot.removeItem(l)
                else:
                    self.flow_tab.plot.addItem(l)
        self.vlines_cb.setChecked(True)
        self.vlines_cb.stateChanged.connect(v_line_cb_changed)

        self.keys_cb = Network_UI.Add_element(QCheckBox('keys'))
        def keys_cb_changed():
            for k in self.key_text_list:
                if not self.keys_cb.isChecked():
                    self.flow_tab.plot.removeItem(k)
                else:
                    self.flow_tab.plot.addItem(k)
        self.keys_cb.setChecked(True)
        self.keys_cb.stateChanged.connect(keys_cb_changed)

    def update(self, Network_UI):
        return

    def add_flow_chart(self, Network_UI, di_modules, group_tags, keys):
        self.flow_tab = Network_UI.Next_Tab('Flow_Chart', stretch=0)
        self.flow_tab.plot = Network_UI.Add_plot()
        self.flow_tab.plot.hideAxis('bottom')
        self.flow_tab.plot.hideAxis('left')
        self.flow_tab.modules = []

        def on_plot_click_event(event):
            for mod in self.flow_tab.modules:
                mod.selected = True

            for mod in self.flow_tab.modules:
                mod.update_pic(self.flow_tab.modules)

            self.flow_tab.plot.update()

        self.flow_tab.plot.mouseClickEvent = on_plot_click_event

        self.v_line_list = []
        self.key_text_list = []
        for i, k_s in enumerate(keys):
            text = pg.TextItem(text=str(k_s), anchor=(0, 0), color=(0,0,0))
            text.setPos(1200*i+300, 600-len(group_tags)*1200)
            self.key_text_list.append(text)
            self.flow_tab.plot.addItem(text)
            line = pg.InfiniteLine(-100 + i * 1200, 90, pen=(200,200,200))
            self.v_line_list.append(line)
            self.flow_tab.plot.addItem(line)

        self.h_line_list = []
        for i, g_s in enumerate(group_tags):
            text = pg.TextItem(text=g_s, anchor=(0, 0), color=(0,0,0))
            text.setPos(-1200*2, 600-i*1200)
            self.flow_tab.plot.addItem(text)
            line = pg.InfiniteLine(-100-i*1200, 0, pen=(100,100,100))
            self.h_line_list.append(line)
            self.flow_tab.plot.addItem(line)


        for mod in di_modules:
            self.flow_tab.modules.append(mod)
            self.flow_tab.plot.addItem(mod)

            def on_mod_click_event(event):
                for mod in self.flow_tab.modules:
                    mod.selected = False

                event.currentItem.selected = True

                for mod in self.flow_tab.modules:
                    mod.update_pic(self.flow_tab.modules)
                self.flow_tab.plot.update()

            mod.mouseClickEvent = on_mod_click_event

        for mod in self.flow_tab.modules:
            mod.update_pic(self.flow_tab.modules)
        self.flow_tab.plot.update()