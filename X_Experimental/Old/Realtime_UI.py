from Exploration.UI_Base import *

import pyqtgraph as pg


#from Exploration.Visualization.Visualization_Helper import *


class TREN_Realtime_UI(UI_Base):

    def __init__(self, network, Cortex_PC_Neurons, LGN_PC_Neurons, label="Network_Test", reconstruction_groups=[]):
        super().__init__(network, label=label)

        self.Cortex_PC_Neurons = Cortex_PC_Neurons
        self.LGN_PC_Neurons = LGN_PC_Neurons

        ###########
        #Sidebar
        ###########

        canvas = pg.GraphicsLayoutWidget()
        canvas.setBackground((255, 255, 255))
        self.Add_Sidebar_Element(canvas)
        self.plot_main = canvas.addPlot(row=0, col=0)
        #self.Add_Sidebar_Spacing()


        self.neurons = []
        for y in range(Cortex_PC_Neurons.height):
            for x in range(Cortex_PC_Neurons.width):
                it = pg.ImageItem(np.random.rand(1, 1))
                it.setLevels([0, 1], True)
                it.scale(1, 1)
                it.x = x
                it.y = y
                it.id = x+Cortex_PC_Neurons.width*y
                it.setPos(y, x)
                self.plot_main.addItem(it)
                self.neurons.append(it)

        self.clicked_id = 0

        def onclick(event):
            items = it.scene().items(event.scenePos())
            ids = [x.id for x in items if isinstance(x, pg.ImageItem)]
            if len(ids) > 0:
                print("Plots:", ids)
                for dc in self.data_curves:
                    self.data_curves[dc][self.clicked_id].setData(pen=pg.mkPen(color=(0, 0, 0), width=1))

                self.clicked_id = ids[0]

                for dc in self.data_curves:
                    self.data_curves[dc][self.clicked_id].setData(pen=pg.mkPen(color=(0, 255, 0), width=5))


        it.scene().sigMouseClicked.connect(onclick)



        def click(event):
            LGN_PC_Neurons[1].active = not self.LGN_PC_Neurons[1].active

        self.btn = QPushButton('input on/off', self.main_window)
        self.btn.clicked.connect(click)
        self.Add_Sidebar_Element(self.btn)


        canvas = pg.GraphicsLayoutWidget()
        canvas.setBackground((255, 255, 255))
        self.Add_Sidebar_Element(canvas)
        self.recon_plot = canvas.addPlot(row=0, col=0)

        self.recon_item = pg.ImageItem(np.random.rand(291, 291, 3))
        self.recon_item.scale(0.1, 0.1)
        self.recon_item.setPos(-10, 0)
        self.recon_plot.addItem(self.recon_item)



        canvas = pg.GraphicsLayoutWidget()
        canvas.setBackground((255, 255, 255))
        self.Add_Sidebar_Element(canvas)
        self.input_plot = canvas.addPlot(row=0, col=0)

        self.input_item = pg.ImageItem(np.random.rand(291, 291, 3))
        self.input_item.scale(0.1, 0.1)
        self.input_item.setPos(-10, 0)
        self.input_plot.addItem(self.input_item)
        self.input_index_buffer = np.ones(self.Cortex_PC_Neurons.reconstruction_steps)*-1





        ###########
        #Blocks
        ###########



        variables=['n.norm_value', 'n.activity', 'n[8].avg', 'n.output_activity_history[0]', 'n.weight_change_sum']
        self.neu_rec = TRENRecorder_eval(variables, gapwidth=10)
        self.syn_rec = TRENSynapseRecorder_eval(['syn.GLU_Synapses'], gapwidth=10)
        network.add_behaviours_to_neuron_group([self.neu_rec, self.syn_rec], Cortex_PC_Neurons)

        for i in range(20):
            self.network.simulate_iteration()

        self.plot = []
        self.Next_H_Block()

        self.data_curves = {}
        for label in variables:
            self.plot.append(self.Add_plot())
            data = np.array(self.neu_rec[label])
            self.data_curves[label] = self.add_curves(data, self.plot[-1])

            if len(self.plot) % 4 == 0:
                self.Next_H_Block()


        #self.Next_H_Block()


        self.recons=[]

        for recon_group in reconstruction_groups:
            self.plot.append(self.Add_plot())
            item = pg.ImageItem(np.random.rand(291, 291, 3))
            item.scale(0.1, 0.1)
            item.setPos(-10, 0)
            item.group = recon_group
            self.plot[-1].addItem(item)
            self.recons.append(item)

            if len(self.plot) % 4 == 0:
                self.Next_H_Block()

        #self.plot.append(self.Add_plot())
        #data = np.array(self.syn_rec['syn.GLU_Synapses'])[:, 0:100]
        #self.weight_curve = self.add_curves(data, self.plot[-1])



        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.on_timer)
        timer.start(40)


    def add_curves(self, data, plot):
        curves = []
        for n_i in range(data.shape[1]):
            curves.append(pg.PlotCurveItem(data[:, n_i], pen=(0, 0, 0)))
            plot.addItem(curves[-1])
        return curves


    def update_curves(self, org_data, curves):
        data = np.array(org_data)

        if data.shape[0] > 1000:
            for _ in range(data.shape[0]-1000):
                org_data.pop(0)

        for n_i in range(data.shape[1]):
            curves[n_i].setData(data[:, n_i])


    def on_timer(self):
        for i in range(1):
            self.network.simulate_iteration()

        #image=get_whole_Network_weight_image(self.Cortex_PC_Neurons, neuron_src_groups=None)

        if self.network.iteration % 100 == 0:
            for dc in self.data_curves:
                self.update_curves(self.neu_rec[dc], self.data_curves[dc])

            for item in self.recons:
                image = self.network.get_reconstruction(item.group, None, self.LGN_PC_Neurons, 'GLU_Synapses', item.group.reconstruction_steps, individual_norm=True)
                image = get_RGB_neuron_weight_image([image, None, None], [item.group.height*item.group.depth, item.group.width], [self.LGN_PC_Neurons.height*self.LGN_PC_Neurons.depth, self.LGN_PC_Neurons.width], v_split_first=True)#pattern_f
                item.setImage(np.flip(image.transpose(1, 0, 2), axis=1))

        group = self.Cortex_PC_Neurons

        image = self.network.get_network_activity_reconstruction(self.LGN_PC_Neurons, 'GLU_Synapses', group.reconstruction_steps, active_groups=[group])
        image = np.sum(image, axis=0).reshape(2, 28, 28)#.reshape((2, 28, 28))
        img = np.zeros((28, 28, 3))
        #print(img[:, :, 0:2].shape)
        #print(image[0].shape)
        #print(image[0].transpose().shape)
        img[:, :, 0] = np.flip(image[0].transpose(), axis=1)
        img[:, :, 1] = np.flip(image[1].transpose(), axis=1)
        self.recon_item.setImage(img)
        #import scipy.misc
        #scipy.misc.imsave('../Data/temp/outfile{}.png'.format(self.iteration), image)



        pattern_group = self.LGN_PC_Neurons[1].TNAPatterns[0]
        indx=int(self.input_index_buffer[-1])
        #scores=[]
        #for indx_f in self.input_index_buffer:
        #    indx=int(indx_f)
        if indx != -1:
            input_image = np.array(pattern_group.patterns[indx])
            img = np.zeros((28, 28, 3))
            img[:, :, 0] = np.flip(input_image[0].transpose(), axis=1)
            img[:, :, 1] = np.flip(input_image[1].transpose(), axis=1)
            #scores.append(np.sum(np.abs(input_image/np.sum(input_image)-image/np.sum(image))))
            self.input_item.setImage(img)
        #print(scores)
        self.input_index_buffer = np.roll(self.input_index_buffer, 1)
        self.input_index_buffer[0] = pattern_group.current_pattern_index




        #self.update_curves(self.neu_rec['n.norm_value'], self.norm_curve)
        #self.update_curves(self.neu_rec['n.activity'], self.act_curve)

        #data = np.array(self.neu_rec['n.norm_value'])

        #if data.shape[0] > 1000:
        #    for _ in range(data.shape[0]-1000):
        #        self.neu_rec['n.norm_value'].pop(0)

        #for n_i in range(data.shape[1]):
        #    self.norm_curve[n_i].setData(data[:, n_i])


        #data = np.array(self.syn_rec['syn.GLU_Synapses'])[:, 100*self.clicked_id:100*self.clicked_id+100]

        #if data.shape[0] > 1000:
        #    for _ in range(data.shape[0]-1000):
        #        self.syn_rec['syn.GLU_Synapses'].pop(0)

        #for n_i in range(data.shape[1]):
        #    self.weight_curve[n_i].setData(data[:, n_i])

        for n in self.neurons:
            n.setImage(np.array([[self.Cortex_PC_Neurons.output_activity_history[0][n.id]]]))#.activity[n.id]
            n.setLevels([0, 1], True)

        self.neurons[self.clicked_id].setLevels([-1, 1], True)
        #self.curve.setData(self.neu_rec['n.norm_value'])


        #self.otherplot.clear()
        #tem = pg.ImageItem(np.random.rand(100, 100))
        #item.scale(0.5, 0.5)
        #item.setPos(10, 10)
        #self.otherplot.addItem(item)