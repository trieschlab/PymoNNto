from PymoNNto.Exploration.Network_UI.TabBase import *

class chain_tab(TabBase):

    def __init__(self, title='Chain'):
        super().__init__(title)

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None:
            self.chaintab = Network_UI.Next_Tab(self.title)

            alphabet = Network_UI.network['grammar_act'][0].alphabet
            a_list = [alphabet[i] for i in range(len(alphabet))]
            a_list[0] = '_'
            ydict = dict(enumerate(a_list))

            win = pg.GraphicsWindow()
            stringaxis = pg.AxisItem(orientation='left')
            stringaxis.setTicks([ydict.items()])

            p = Network_UI.Add_plot(axisItems={'left': stringaxis}, x_label='buffer steps')

            self.graph = pg.GraphItem()
            # p=self.Add_plot('', True)
            p.addItem(self.graph)

            source = Network_UI.network['grammar_act'][0]
            RALN = Reconstruct_Analyze_Label_Network(Network_UI.network)
            groups = Network_UI.network['prediction_source']#Network_UI.exc_group_name  # , network.NeuronGroups[1]

            def update():
                RALN.label_and_group_neurons(Network_UI.network['prediction_source', 0], [source.get_activation(char, Network_UI.network['prediction_source', 0]) for char in range(source.get_alphabet_length())], 'W', 20)
                _, self.edges = RALN.visualize_label_and_group_neurons(x_attribute_name='temporal_layer',
                                                                       y_attribute_name='class_label',
                                                                       weight_attribute_name='W',
                                                                       groups=groups,
                                                                       weight_limit=None,
                                                                       n_biggest=1,
                                                                       source=source,
                                                                       return_graph=True)  # 1/3#None#1/3#0.5

                self.nodes = RALN.get_neuron_positions(Network_UI.network['prediction_source', 0],
                                                       x_attribute_name='temporal_layer',
                                                       y_attribute_name='class_label',
                                                       y_scale=0.0005)

            self.update_btn = QPushButton('update live buffers', Network_UI.main_window)
            self.update_btn.clicked.connect(update)

            Network_UI.Next_H_Block()
            Network_UI.Add_element(self.update_btn)


            #def plot_buffer_chains(event):
            #    # self.network.NeuronGroups = [self.network.NeuronGroups[0]]
            #    # self.network.SynapseGroups = [self.network.SynapseGroups[0]]
            #    source = Network_UI.network['grammar_act', 0]
            #    RALN = Reconstruct_Analyze_Label_Network(Network_UI.network)
            #    groups = Network_UI.network[Network_UI.exc_group_name, 0]  # , network.NeuronGroups[1]
            #    RALN.label_and_group_neurons(Network_UI.network[Network_UI.exc_group_name, 0],
            #                                 [source.get_activation(char) for char in range(source.get_alphabet_length())],
            #                                 'W', 10)
            #    RALN.visualize_label_and_group_neurons(x_attribute_name='temporal_layer', y_attribute_name='class_label',
            #                                           weight_attribute_name='W', groups=groups, weight_limit=None,
            #                                           n_biggest=3, source=source)  # 1/3#None#1/3#0.5
            #
            #self.pbc_btn = QPushButton('plot buffer chains', Network_UI.main_window)
            #self.pbc_btn.clicked.connect(plot_buffer_chains)
            #Network_UI.Add_element(self.pbc_btn)
            # self.Add_Sidebar_Element(self.update_btn)


    def update(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None and self.chaintab.isVisible() and hasattr(self, "nodes"):
            group = Network_UI.network['prediction_source', 0]

            pos = np.array(self.nodes, dtype=float)
            colors = [(act * 255, 0, 0, 50) for act in group.output]

            if Network_UI.network[Network_UI.neuron_select_group, 0] is Network_UI.network['prediction_source', 0]:
                GLU_syn = Network_UI.get_combined_syn_mats(group['GLU'])
                GLU_syn = GLU_syn[list(GLU_syn.keys())[0]]
                big_syn_indices = np.where(GLU_syn[Network_UI.neuron_select_id] > (np.max(GLU_syn[Network_UI.neuron_select_id]) * (1 / 2)))[0]
                adj = np.array([[s, Network_UI.neuron_select_id] for s in big_syn_indices])  # np.array(self.edges)##[self.neuron_select_id, 1]
                colors[Network_UI.neuron_select_id] = (0, 255, 0, 255)
                self.graph.setData(pos=pos, adj=adj, size=0.5, symbol='o', pxMode=False, symbolBrush=colors, symbolPen=None)
            else:
                self.graph.setData(pos=pos, size=0.5, symbol='o', pxMode=False, symbolBrush=colors, symbolPen=None)

            self.graph.update()

            #selected_GLU_syn = GLU_syn[Network_UI.neuron_select_id]

            #GABA_syn = Network_UI.network[Network_UI.neuron_select_group, 0]['GABA']
            #if len(GABA_syn) > 0:
            #    GABA_syn = Network_UI.get_combined_syn_mats(GABA_syn)
            #    GABA_syn = GABA_syn[list(GABA_syn.keys())[0]]
            #    selected_GABA_syn = GABA_syn[Network_UI.neuron_select_id]
            #else:
            #    GABA_syn = None
