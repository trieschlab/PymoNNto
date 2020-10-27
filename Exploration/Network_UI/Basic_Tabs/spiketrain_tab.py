from SORNSim.Exploration.Network_UI.TabBase import *

class spiketrain_tab(TabBase):

    def __init__(self, parameter, title='Spiketrain', timesteps=1000):
        super().__init__(title)
        self.parameter=parameter
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.parameter):
            Network_UI.add_recording_variable(neuron_group, 'n.'+self.parameter, timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.scatter_tab = Network_UI.Next_Tab(self.title)

        self.spiketrain_images=[]
        for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
            if i!=0:
                Network_UI.Next_H_Block()
            self.spiketrain_images.append(Network_UI.Add_Image_Item(False, tooltip_message=self.parameter+' of each neuron(rows) at each timestep(columns)'))


    def update(self, Network_UI):
        if self.scatter_tab.isVisible():
            for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
                group = Network_UI.network[group_tag, 0]

                if hasattr(group, self.parameter):
                    #rec = Network_UI.rec(group, self.timesteps)

                    data = group['n.'+self.parameter, 0, 'np'][-self.timesteps:]
                    if group_tag == Network_UI.neuron_select_group:
                        id=Network_UI.neuron_select_id
                        data[:, id-1:id+2] += 0.2
                        data[:, id] += 0.3
                    self.spiketrain_images[i].setImage(data, levels=(0, 1))#np.rot90(, 3)