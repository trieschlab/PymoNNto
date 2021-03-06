from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Analysis_Plots import *

class stability_tab(TabBase):

    def __init__(self, parameter, title='stability', timesteps=500):
        super().__init__(title)
        self.parameter=parameter
        self.timesteps=timesteps

    def add_recorder_variables(self, neuron_group, Network_UI):
        try:#if hasattr(neuron_group, self.parameter):
            Network_UI.add_recording_variable(neuron_group, 'n.'+self.parameter, timesteps=self.timesteps)
        except:
            print(self.parameter, 'cannot be added to recorder')

    def initialize(self, Network_UI):
        self.stab_tab = Network_UI.Next_Tab(self.title)

        self.image_items = []

        for group_tag1 in Network_UI.neuron_visible_groups:
            self.image_items.append([])
            for group_tag2 in Network_UI.neuron_visible_groups:
                tooltip_msg='x-axis:network average '+self.parameter+' at timestep t\r\ny-axis:corresponding network average '+self.parameter+' at tiemstp t+1'
                self.image_items[-1].append(Network_UI.Add_Image_Item(False, False, title=group_tag1 + self.parameter +'(t) vs ' + group_tag2 + self.parameter +'(t+1)', tooltip_message=tooltip_msg))
            Network_UI.Next_H_Block()

        self.resolution_slider = QSlider(1)  # QtCore.Horizontal
        self.resolution_slider.setMinimum(2)
        self.resolution_slider.setMaximum(200)
        self.resolution_slider.setSliderPosition(50)
        self.resolution_slider.mouseReleaseEvent = Network_UI.static_update_func
        self.resolution_slider.setToolTip('drag to change resolution')
        Network_UI.Add_element(self.resolution_slider)  # , stretch=0.1

    def update(self, Network_UI):
        if self.stab_tab.isVisible():

            for y, group_tag1 in enumerate(Network_UI.neuron_visible_groups):
                for x, group_tag2 in enumerate(Network_UI.neuron_visible_groups):

                    if len(Network_UI.network[group_tag1]) >= 0 and len(Network_UI.network[group_tag2]) >= 0:
                        group1 = Network_UI.network[group_tag1, 0]
                        group2 = Network_UI.network[group_tag2, 0]

                        try:#if hasattr(group1, self.parameter) and hasattr(group2, self.parameter):
                            act1 = np.mean(np.array(group1['n.'+self.parameter, 0][-self.timesteps:]), axis=1)
                            act2 = np.mean(np.array(group2['n.'+self.parameter, 0][-self.timesteps:]), axis=1)
                            self.image_items[y][x].setImage(get_t_vs_tp1_mat(act1, act2, self.resolution_slider.sliderPosition(), False))
                        except:
                            print(self.parameter, 'cannot be evaluated')
