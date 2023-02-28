from PymoNNto.Exploration.Network_UI.TabBase import *

class spiketrain_tab(TabBase):

    def __init__(self, parameter, title='Spiketrain', timesteps=1000):
        super().__init__(title)
        self.parameter=parameter
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        if hasattr(neuron_group, self.parameter):
            Network_UI.add_recording_variable(neuron_group, self.parameter, timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.scatter_tab = Network_UI.add_tab(title=self.title)

        self.spiketrain_images=[]
        for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
            if i!=0:
                Network_UI.tab.add_row()
            self.spiketrain_images.append(Network_UI.tab.add_plot(tooltip_message=self.parameter+' of each neuron(rows) at each timestep(columns)').add_image())


    def update(self, Network_UI):
        if self.scatter_tab.isVisible():
            for i, group_tag in enumerate(Network_UI.neuron_visible_groups):
                group = Network_UI.network[group_tag, 0]


                try:
                    data = group[self.parameter, 0, 'np'][-self.timesteps:].astype(np.float64)
                    mi=0#np.min(data)
                    ma=np.max(data)
                    if group_tag == Network_UI.selected_neuron_group().tags[0]:
                        id=Network_UI.selected_neuron_id()
                        data[:, id-1:id+2] += 0.2*ma
                        data[:, id] += 0.3*ma
                    self.spiketrain_images[i].setImage(data, levels=(mi, ma))#np.rot90(, 3)
                except:
                    print(self.parameter, "cannot be evaluated")