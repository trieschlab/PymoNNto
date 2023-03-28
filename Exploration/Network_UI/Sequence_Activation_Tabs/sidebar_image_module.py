from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *

class sidebar_image_module(TabBase):

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):

        if Network_UI.network['image_act', 0] is not None:

            def image_activator_on_off(event):
                Network_UI.network['image_act', 0].behavior_enabled = self.input_select_box.currentText() != 'None'

            self.input_select_box = QComboBox()
            self.input_select_box.addItem("Images")
            self.input_select_box.addItem("None")
            self.input_select_box.currentIndexChanged.connect(image_activator_on_off)
            Network_UI.Add_Sidebar_Element(self.input_select_box)

            #self.image_history_image = Network_UI.Add_Image_Item(False, True, title='', stretch=0.3)
            self.image_history = []

            self.prediction_history_image = Network_UI.Add_Image_Item(False, True, title='', stretch=1)
            self.prediction_history = []

            self.backprop_image = Network_UI.Add_Image_Item(False, True, title='', stretch=1)

    def max_div(self, pattern):
        ms = np.max(pattern)
        if ms > 0:
            return pattern / ms
        else:
            return pattern.copy()

    def update(self, Network_UI):

        # save data timestep
        if not Network_UI.update_without_state_change and Network_UI.network['image_act', 0] is not None:
            image_act = Network_UI.network['image_act', 0]

            #index = image_act.current_pattern_index
            #if index >- 1:
            #    pattern = image_act.patterns[image_act.current_pattern_index].copy()
            #    pattern.resize((3, image_act.grid_width, image_act.grid_height))
            #    self.image_history.append(np.rot90(np.dstack(pattern), 3))
            #    self.image_history.append(np.ones((1, self.image_history[0].shape[1], 3)))
            #    self.image_history_image.setImage(np.concatenate(self.image_history, axis=0), levels=(0, 1))

            group = Network_UI.selected_neuron_group()
            if hasattr(group, 'Input_Mask'):
                pattern = self.max_div(group.output[group.Input_Mask])
                #print(pattern)
                pattern.resize((3, image_act.grid_height, image_act.grid_width))
                #group['n.output', 0, 'np'][]
                self.prediction_history.append(np.rot90(np.dstack(pattern), 3))
                self.prediction_history.append(np.ones((1, self.prediction_history[0].shape[1], 3)))
                self.prediction_history_image.setImage(np.concatenate(self.prediction_history, axis=0), levels=(0, 1))

                RALN = Reconstruct_Analyze_Label_Network(Network_UI.network)
                RALN.zero_recon()
                group.recon = group.output.copy()
                RALN.propagation('W', 6, 'backward', 'forget', 'all', temporal_recon_groups=[Network_UI.selected_neuron_group()], exponent=None, normalize=False, filter_weakest_percent=None)

                baseline = self.max_div(group.temporal_recon[-1][group.Input_Mask])
                images = []
                for r in group.temporal_recon:
                    pattern = np.clip(self.max_div(r[group.Input_Mask])-baseline/2, 0, None)
                    pattern.resize((3, image_act.grid_height, image_act.grid_width))
                    images.insert(0, np.rot90(np.dstack(pattern), 3))
                    images.insert(0, np.ones((1,  images[0].shape[1], 3)))
                self.backprop_image.setImage(np.concatenate(images, axis=0), levels=(0, 1))

            for _ in range(len(self.image_history)-5*2): self.image_history.pop(0)
            for _ in range(len(self.prediction_history)-5*2): self.prediction_history.pop(0)

