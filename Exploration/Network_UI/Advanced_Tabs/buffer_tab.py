from PymoNNto.Exploration.Network_UI.TabBase import *

class buffer_tab(TabBase):

    def __init__(self, title='Buffer'):
        super().__init__(title)

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        self.buffer_tab = Network_UI.Next_Tab(self.title)

        buffer_keys = {}
        for group_tag in Network_UI.group_tags:
            for ng in Network_UI.network[group_tag]:
                if hasattr(ng, 'buffers'):
                    for variable in ng.buffers:
                        for timescale in ng.buffers[variable]:
                            for offset in ng.buffers[variable][timescale]:
                                buffer_keys[str(variable)+' '+str(timescale)+' '+str(offset)]=1

        self.buffer_block_plot_images = []
        self.buffer_block_count=len(list(buffer_keys.keys()))
        for i in range(self.buffer_block_count):
            #Network_UI.Add_element(QLabel(''))
            image_item = Network_UI.Add_Image_Item(True, False, title='', tooltip_message='')
            self.buffer_block_plot_images.append(image_item)
            Network_UI.Next_H_Block()

    def update(self, Network_UI):
        if self.buffer_tab.isVisible():

            sub_group = Network_UI.get_selected_neuron_subgroup()
            if hasattr(sub_group, 'buffers'):
                ct = 0

                if sub_group is not None:
                    for variable in sub_group.buffers:
                        for timescale in sub_group.buffers[variable]:
                            for offset in sub_group.buffers[variable][timescale]:
                                b=sub_group.get_buffer(sub_group, variable, timescale, offset)
                                self.buffer_block_plot_images[ct][1].setLabels(title=str(variable)+' '+str(timescale)+' '+str(offset))
                                self.buffer_block_plot_images[ct][0].setImage(np.rot90(b, 3), levels=(0, 1))
                                ct+=1

                for i in range(self.buffer_block_count-ct):
                    self.buffer_block_plot_images[ct][0].clear()
