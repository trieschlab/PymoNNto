from PymoNNto.Exploration.Network_UI.TabBase import *

class scatter_tab(TabBase):

    def __init__(self, x_var, y_var, title='Scatter', timesteps=500):
        super().__init__(title)
        self.x_var = x_var
        self.y_var = y_var
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        Network_UI.add_recording_variable(neuron_group, self.x_var, timesteps=self.timesteps)
        Network_UI.add_recording_variable(neuron_group, self.y_var, timesteps=self.timesteps)

    def initialize(self, Network_UI):
        self.scatter_tab = Network_UI.add_tab(self.title)

        p = Network_UI.tab.add_plot(x_label=self.x_var, y_label=self.y_var)
        self.scatter_items=[]
        for i, _ in enumerate(Network_UI.get_visible_neuron_groups()):
            spi = pg.ScatterPlotItem()
            self.scatter_items.append(spi)
            p.addItem(spi)

    def update(self, Network_UI):
        if self.scatter_tab.isVisible():
            for i, group in enumerate(Network_UI.get_visible_neuron_groups()):

                try:
                    x_values = group[self.x_var, 0, 'np'][-self.timesteps:]
                    y_values = group[self.y_var, 0, 'np'][-self.timesteps:]

                    x_val = np.mean(x_values, axis=1)
                    y_val = np.mean(y_values, axis=1)

                    self.scatter_items[i].setData(x_val.copy(), y_val.copy(), brush=group.color)
                except:
                    pass
