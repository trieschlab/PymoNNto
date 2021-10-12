from PymoNNto.Exploration.Network_UI.TabBase import *

class weight_tab(TabBase):

    def __init__(self, title='Weights', weight_attrs=['W']):
        super().__init__(title)
        self.weight_attrs = weight_attrs

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.weight_tab = Network_UI.Next_Tab(self.title)

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
                image_item = Network_UI.Add_Image_Item(True, False, title='Neuron ' + transmitter + ' ?', tooltip_message='afferent synapse weights of selected neuron')#+self.weight_attr
                self.transmitter_weight_images[transmitter].append(image_item)
            Network_UI.Next_H_Block()

        Network_UI.Add_element(QLabel('Min Max'), stretch=0)
        self.select_min_max_box = QComboBox()
        self.select_min_max_box.addItems(['Transmitter', 'Global', 'Variable', 'Single block'])
        self.select_min_max_box.setCurrentIndex(0)
        Network_UI.Add_element(self.select_min_max_box, stretch=1)
        #Network_UI.Next_H_Block(stretch=0)

    def update(self, Network_UI):
        if self.weight_tab.isVisible() and len(Network_UI.network[Network_UI.neuron_select_group]) > 0:

            group = Network_UI.network[Network_UI.neuron_select_group, 0]
            #collect all synapse information
            syn_dict = {}

            # print(np.sum(group.W, axis=1))

            for transmitter in Network_UI.transmitters:
                syn_dict[transmitter] = {}
                for weight_attr in self.weight_attrs:

                    syn_dict[transmitter][weight_attr] = {transmitter: get_single_neuron_combined_partition_matrix(group, transmitter, weight_attr, Network_UI.neuron_select_id)}

                    #syns = get_combined_syn_mats(group.afferent_synapses[transmitter], Network_UI.neuron_select_id, weight_attr)

                    #print(np.sum(syns['GLU,syn,PC_1 => PC_1']), np.max(syns['GLU,syn,PC_1 => PC_1']))

                    #if len(syns.values()) > 0:
                    #    syn_dict[transmitter][weight_attr]=syns


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

                        #print('set transmitter', transmitter, np.min(syn_dict[transmitter][weight_attr][key]), np.max(syn_dict[transmitter][weight_attr][key]))

                        self.transmitter_weight_images[transmitter][i][0].setImage(np.rot90(syn_dict[transmitter][weight_attr][key], 3), levels=(0, max_w)) #0=image item
                        i += 1
                    #if weight_attr=='W_temp' and transmitter=='GLU':
                        #print(ss)

