from PymoNNto.Exploration.Network_UI.TabBase import *

class weight_tab(TabBase):

    def __init__(self, title='Weights', weight_attrs=['W']):
        super().__init__(title)
        self.weight_attrs = weight_attrs

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.weight_tab = Network_UI.add_tab(title=self.title)

        #get max synapse group size
        max_sgs=2
        for group_tag in Network_UI.group_tags:
            for ng in Network_UI.network[group_tag]:
                for transmitter in Network_UI.transmitters:
                    l = 0
                    for weight_attr in self.weight_attrs:
                        l += len(get_combined_syn_mats(ng[transmitter], None, weight_attr))
                    max_sgs = np.maximum(max_sgs, l)

        self.transmitter_weight_images = {}
        for transmitter in Network_UI.transmitters:
            self.transmitter_weight_images[transmitter] = []
            for _ in range(max_sgs):
                plt = Network_UI.tab.add_plot(title='Neuron ' + transmitter + ' ?', tooltip_message='afferent synapse weights of selected neuron')
                image = plt.add_image()
                self.transmitter_weight_images[transmitter].append([image, plt])
            Network_UI.tab.add_row()

        Network_UI.tab.add_widget(QLabel('Min Max'), stretch=0)
        self.select_min_max_box = QComboBox()
        self.select_min_max_box.addItems(['Transmitter', 'Global', 'Variable', 'Single block'])
        self.select_min_max_box.setCurrentIndex(0)
        Network_UI.tab.add_widget(self.select_min_max_box, stretch=1)

    def update(self, Network_UI):
        if self.weight_tab.isVisible():

            group = Network_UI.selected_neuron_group()
            #collect all synapse information
            syn_dict = {}

            for transmitter in Network_UI.transmitters:
                syn_dict[transmitter] = {}
                for weight_attr in self.weight_attrs:

                    if transmitter in group.afferent_synapses and len(group.afferent_synapses[transmitter])>0:
                        syn_dict[transmitter][weight_attr] = {transmitter: get_single_neuron_combined_partition_matrix(group, transmitter, weight_attr, Network_UI.selected_neuron_id())}#group.afferent_synapses[transmitter][0].W[Network_UI.selected_neuron_id()

            #determine ranges
            min_max_mode = self.select_min_max_box.currentText()

            glob_max=0
            tr_max={}
            var_max={}
            key_max = {}

            for transmitter in syn_dict:
                tr_max[transmitter]=0
                var_max[transmitter] = {}
                key_max[transmitter] = {}
                for weight_attr in syn_dict[transmitter]:
                    var_max[transmitter][weight_attr] = 0
                    key_max[transmitter][weight_attr] = {}
                    for key in syn_dict[transmitter][weight_attr]:
                        m = np.max(syn_dict[transmitter][weight_attr][key])

                        tr_max[transmitter] = max(tr_max[transmitter], m)
                        var_max[transmitter][weight_attr] = max(var_max[transmitter][weight_attr], m)
                        key_max[transmitter][weight_attr][key] = m
                        glob_max = max(glob_max, m)

            if min_max_mode == 'Global':
                max_w = glob_max

            for transmitter in syn_dict:

                if min_max_mode == 'Transmitter':
                    max_w = tr_max[transmitter]

                for image, plot in self.transmitter_weight_images[transmitter]:
                    plot.setTitle('')
                    image.clear()

                i = 0
                for weight_attr in syn_dict[transmitter]:

                    if min_max_mode == 'Variable':
                        max_w = var_max[transmitter][weight_attr]

                    for key in syn_dict[transmitter][weight_attr]:

                        if min_max_mode == 'Single block':
                            max_w = key_max[transmitter][weight_attr][key]

                        self.transmitter_weight_images[transmitter][i][1].setTitle(key+' '+weight_attr) #1=plot

                        self.transmitter_weight_images[transmitter][i][0].setImage(np.rot90(syn_dict[transmitter][weight_attr][key], 3), levels=(0, max_w)) #0=image item
                        i += 1
