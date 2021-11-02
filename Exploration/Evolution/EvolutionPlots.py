from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.StorageManager.StorageManager import *

def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y

def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho

class DrawItem2(pg.GraphicsObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.picture = QtGui.QPicture()

    #base_char_masks_dict

    def get_axis_position(self, axis_id, number_of_axis, min_val, max_val, value):
        number_of_axis=max(number_of_axis,3)
        value_range=(max_val-min_val)
        if value_range==0:
            value_range=1.0
        return pol2cart(axis_id / number_of_axis * 2 * np.pi, 100.0/value_range*(value-min_val))


    def draw_rings(self, painter, alphabet, num_rings):


        for i in range(num_rings):
            c=int(220)
            painter.setPen(pg.mkPen(color=(c, c, c, 255)))
            r = 100/num_rings*(i+1)#np.power(0.9, i)


            painter.setBrush(pg.mkBrush(color=(c, c, c, 0)))
            painter.drawEllipse(QtCore.QPointF(0, 0), r, r)
            '''
            for d, char in enumerate(alphabet):
                x, y = pol2cart(d / len(alphabet) * 2 * np.pi, r)
                painter.setBrush(pg.mkBrush(color=(c, c, c, 255)))
                painter.drawEllipse(QtCore.QPointF(x, y), 1, 1)

                if i == 0:
                    painter.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(x, y))
            '''

        for d, char in enumerate(alphabet):
            x, y = self.get_axis_position(d, len(alphabet),0,100,100)
            #pol2cart(d / len(alphabet) * 2 * np.pi, 100)
            painter.setBrush(pg.mkBrush(color=(0, 0, 0, 255)))
            painter.setPen(pg.mkPen(color=(0, 0, 0, 255)))
            painter.drawLine(QtCore.QPointF(0, 0), QtCore.QPointF(x, y))


    #def fixate_points(self, group, alphabet, input_mat):
    #    for i, char in enumerate(alphabet):
    #        bm=input_mat[:, i]
    #        x, y = pol2cart(i / len(alphabet) * 2 * np.pi, 100)
    #        group.buffer_posx[bm > 0.1] = x
    #        group.buffer_posy[bm > 0.1] = y

    def draw_chars(self, painter, alphabet, data):
        for i, char in enumerate(alphabet):
            x, y = self.get_axis_position(i, len(alphabet),0,100,110)#pol2cart(i / len(alphabet) * 2 * np.pi, 110)

            #min_a = data.min(axis=1)
            #max_a = data.max(axis=1)

            qf = QFont('Arial')
            qf.setPointSizeF(5.0)
            #qf.setStretch(2)
            painter.setFont(qf)
            painter.drawText(x,y,char)#+' ('+str(min_a[i])+'-'+str(max_a[i])+')'

    def draw_genome(self, painter, alphabet, len_alphabet, min_a, max_a, vals):
        positions = []
        for i, a in enumerate(alphabet):
            positions.append(self.get_axis_position(i, len_alphabet, min_a[i], max_a[i], vals[i]))

        for p_i in range(len(positions)):
            if p_i != 0:
                painter.drawLine(QtCore.QPointF(positions[p_i - 1][0], positions[p_i - 1][1]),
                                 QtCore.QPointF(positions[p_i][0], positions[p_i][1]))
            else:
                painter.drawLine(QtCore.QPointF(positions[p_i][0], positions[p_i][1]),
                                 QtCore.QPointF(positions[-1][0], positions[-1][1]))

    def draw_genomes(self, alphabet, data, painter, max_gene_draw):

        #mask = data[-2, :] % np.ceil(data.shape[1]/100) == 0
        #masked_data=data[:, mask]
        # mask = [i%10 == 0 for i in range(data.shape[1])]

        if data.shape[1] > max_gene_draw:
            masked_data = data[:, -max_gene_draw:]
        else:
            masked_data = data

        min_a = data.min(axis=1)
        max_a = data.max(axis=1)

        masked_min_a = masked_data.min(axis=1)
        masked_max_a = masked_data.max(axis=1)

        la = len(alphabet)
        score_diff = (masked_max_a[-1] - masked_min_a[-1])

        if la > 0:
            for j in range(masked_data.shape[1]):
                if score_diff > 0:
                    c = int(255.0/score_diff*(masked_data[-1, j]-masked_min_a[-1]))
                else:
                    c = 0
                painter.setPen(pg.mkPen(color=(255-c, c, 0, 255), width=1))

                self.draw_genome(painter, alphabet, la, min_a, max_a, masked_data[:, j])

    def draw_clicked_genome(self, alphabet, data, painter, clicked_id):
        min_a = data.min(axis=1)
        max_a = data.max(axis=1)

        painter.setPen(pg.mkPen(color=(0, 0, 255, 255), width=3))
        self.draw_genome(painter, alphabet, len(alphabet), min_a, max_a, data[:, clicked_id])

    def update_pic(self, alphabet, data, clicked_id, max_gene_draw=100): #, groups, alphabet, p0, p1, p2, p3, p4, p5, nui, statistics, show_weights):

        self.data=data
        self.alphabet=alphabet

        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)
        painter.scale(1, -1)

        self.draw_rings(painter, alphabet, 10)

        if data is not None:
            self.draw_genomes(alphabet, data, painter, max_gene_draw)

            if clicked_id!=-1:
                self.draw_clicked_genome(alphabet, data, painter, clicked_id)

            painter.setPen(pg.mkPen(color=(0, 0, 0, 255)))
            self.draw_chars(painter, alphabet, data)



        '''
        self.groups=groups

        #for group in groups:
        #    self.initialize_neuron_positons(group)

        for group in nui.network.NeuronGroups:
            self.compute_and_apply_attraction(group, p1, p2, p3, p4, p5, attractor_rads)

        painter.scale(1, -1)

        for group in groups:
            self.draw_neurons(painter, group, p0)

        #painter.setBrush(pg.mkBrush(color=(0,255,0,255)))
        #for x, y in zip(group.buffer_posx+attractor_rad_x, group.buffer_posy+attractor_rad_y):
        #    painter.drawEllipse(QtCore.QPointF(x, y), 1, 1)

        if show_weights:
            for group in groups:
                if group == nui.selected_neuron_group():
                    self.draw_weights(painter, group, nui.selected_neuron_id())


        painter.setPen(pg.mkPen(color=(0, 0, 0, 255), width=10))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))

        for group in nui.network.NeuronGroups:
            if hasattr(group, 'Input_Weights'):
                self.fixate_points(group, alphabet, group.Input_Weights)

        self.draw_chars(painter, alphabet, statistics)
        '''

        painter.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        #self.update()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        br = self.picture.boundingRect()
        br.setTop(max(br.top()-10, br.left()-10))
        br.setLeft(min(br.top()-10, br.left()-10))
        br.setRight(max(br.right()+10, br.bottom()+10))
        br.setBottom(max(br.right()+10, br.bottom()+10))
        return QtCore.QRectF(br)

def add_evolution_plot_items(ui, tab):
    tab.curves, tab.plot = ui.Add_plot_curve(x_label='generations', y_label='score', number_of_curves=3, return_plot=True, colors=[(0, 0, 0), (0, 0, 0), (0, 0, 0)])
    tab.item = pg.FillBetweenItem(curve1=tab.curves[1], curve2=tab.curves[2], brush=(255, 0, 0, 100))
    tab.plot.addItem(tab.item)
    tab.scatter = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(255, 255, 255, 120))
    tab.plot.addItem(tab.scatter)

    tab.clicked_generation=-1
    tab.clicked_score=-1
    tab.clicked_id=-1

    def clicked(plot, points):
        print('clicked')
        #for p in points:
        if len(points) > 0:
            p = points[-1]
            tab.clicked_generation = p._data[0]
            tab.clicked_score = p._data[1]
            tab.scatter2.setData(x=[tab.clicked_generation],y=[tab.clicked_score])

            if tab.data is not None and tab.gene_keys is not None:
                tab.clicked_id = np.where((tab.data[-2] == tab.clicked_generation) & (tab.data[-1] == tab.clicked_score))
                if len(tab.clicked_id) > 0:
                    tab.clicked_id = tab.clicked_id[0]
                    if len(tab.clicked_id) > 0:
                        tab.clicked_id = tab.clicked_id[0]
                        tab.clicked_evo.setText('Clicked genome: ' + str(dict(zip(tab.gene_keys + ['gen', 'score'], tab.data[:, tab.clicked_id]))))

                        tab.draw_item.update_pic(tab.gene_keys, tab.data, tab.clicked_id, tab.slider.value())

    tab.scatter.sigClicked.connect(clicked)

    tab.scatter2 = pg.ScatterPlotItem(size=10, brush=pg.mkBrush(0, 0, 255, 255))
    tab.plot.addItem(tab.scatter2)

    #g = pg.GraphItem()
    #tab.plot.addItem(g)
    # Update the graph
    #g.setData(pos=np.array([[100, 100]]), pen=['r'], brush=['r'], size=10, symbol=['o'], pxMode=False)

    tab.radar_plot = ui.Add_plot(x_label='radar plot', tooltip_message='radar plot of the last 100 genomes. (green=high score/red=low score/blue=selected)')  # axisItems={'left': stringaxis}
    tab.draw_item = DrawItem2()
    tab.radar_plot.addItem(tab.draw_item)

    def val_changed():
        if hasattr(tab, 'data'):
            tab.draw_item.update_pic(tab.gene_keys, tab.data, tab.clicked_id, tab.slider.value())

    tab.slider = ui.Add_element(QSlider(Qt.Vertical))
    tab.slider.setMinimum(10)
    tab.slider.setMaximum(5000)
    tab.slider.setValue(100)
    tab.slider.valueChanged.connect(val_changed)

    tab.radar_plot.hideAxis('bottom')
    tab.radar_plot.hideAxis('left')
    tab.draw_item.update_pic([], None, None, tab.slider.value())
    #tab.draw_item.mouseClickEvent = c



    ui.Next_H_Block(stretch=0.0)
    tab.best_evo = ui.Add_element(QLineEdit('...'), stretch=0)

    ui.Next_H_Block(stretch=0.0)
    tab.clicked_evo = ui.Add_element(QLineEdit('...'), stretch=0)



def update_evolution_plot(ui, tab, evo_name, gene_keys, data_folder=get_data_folder()):
    print(len(next(os.walk(data_folder + '/StorageManager/'+evo_name))[1]), 'datapoints found')

    smg = StorageManagerGroup(evo_name, data_folder=data_folder)

    smg.sort_by('gen')

    tab.gene_keys = gene_keys

    result_lists = smg.get_multi_param_list(gene_keys+['gen', 'score'], remove_None=True)

    xa, ya = smg.remove_duplicates_get_eval(result_lists[-2], result_lists[-1], evalstr='np.average(a)')
    xs, ymi = smg.remove_duplicates_get_eval(result_lists[-2], result_lists[-1], evalstr='np.min(a)')
    xs, yma = smg.remove_duplicates_get_eval(result_lists[-2], result_lists[-1], evalstr='np.max(a)')

    tab.curves[0].setData(xa, ya)
    tab.curves[1].setData(xa, ymi)
    tab.curves[2].setData(xa, yma)

    tab.scatter.setData(x=result_lists[-2], y=result_lists[-1])

    tab.data = np.array(result_lists)

    tab.best_evo.setText('Best genome: ' + str(dict(zip(gene_keys+['gen', 'score'], tab.data[:, -1]))))

    tab.draw_item.update_pic(gene_keys, tab.data, tab.clicked_id, tab.slider.value())

    tab.radar_plot.update()



