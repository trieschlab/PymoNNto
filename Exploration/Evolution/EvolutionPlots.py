from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.Evolution.PlotQTObjects import *

def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y

def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho

class Radar_Plot_Item(pg.GraphicsObject):

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
            painter.drawText(int(x),int(y),char)#+' ('+str(min_a[i])+'-'+str(max_a[i])+')'

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

        if len(data)>0:#todo:test

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

        painter.end()
        self.prepareGeometryChange()
        self.informViewBoundsChanged()
        #self.update()

    def paint(self, painter, option, widget=None):
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        br = self.picture.boundingRect()
        br.setTop(max([br.top()-10, br.left()-10]))
        br.setLeft(min([br.top()-10, br.left()-10]))
        br.setRight(max([br.right()+10, br.bottom()+10]))
        br.setBottom(max([br.right()+10, br.bottom()+10]))
        return QtCore.QRectF(br)

def add_evolution_plot_items(ui, tab):
    tab.interactive_scatter = ui.tab.add_widget(InteractiveScatter('generation', 'score', 'score'))
    if hasattr(tab, 'gene_keys'):
        tab.interactive_scatter.gene_keys = tab.gene_keys

    def on_item_clicked(sm):
        data = sm.load_param_list(tab.gene_keys, return_dict=True)
        tab.clicked_evo.setText(str(data))#str(dict(zip(tab.gene_keys + ['id'] + ['generation', 'score'], data)))
        data = sm.load_param_list(['id', 'generation', 'score'], return_dict=True)
        tab.clicked_evo2.setText(str(data))

        tab.draw_item.update_pic(tab.gene_keys, tab.data, data['id'], tab.slider.value())

    tab.interactive_scatter.scatter_clicked_event = on_item_clicked

    tab.clicked_id=-1

    tab.radar_plot = ui.tab.add_plot(x_label='radar plot', tooltip_message='radar plot of the last genomes. (green=high score/red=low score/blue=selected)')
    #tab.radar_plot = ui.Add_plot(x_label='radar plot', tooltip_message='radar plot of the last genomes. (green=high score/red=low score/blue=selected)')  # axisItems={'left': stringaxis}
    tab.draw_item = Radar_Plot_Item()
    tab.radar_plot.addItem(tab.draw_item)

    def val_changed():
        if hasattr(tab, 'data'):
            tab.draw_item.update_pic(tab.gene_keys, tab.data, tab.clicked_id, tab.slider.value())

    tab.slider = ui.tab.add_widget(QSlider(Qt.Vertical))
    tab.slider.setMinimum(10)
    tab.slider.setMaximum(5000)
    tab.slider.setValue(100)
    tab.slider.valueChanged.connect(val_changed)

    tab.radar_plot.hideAxis('bottom')
    tab.radar_plot.hideAxis('left')
    tab.draw_item.update_pic([], None, None, tab.slider.value())



    ui.tab.add_row(stretch=10)

    ui.tab.add_column(stretch=0, add_to_parent=False)
    ui.tab.add_widget(QLabel('Best genome:'), stretch=0)
    ui.tab.add_widget(QLabel('Clicked genome'), stretch=0)

    ui.tab.add_column(stretch=100)
    tab.best_evo = ui.tab.add_widget(QLineEdit('...'), stretch=100)
    tab.clicked_evo = ui.tab.add_widget(QLineEdit('...'), stretch=100)

    ui.tab.add_column(stretch=50)
    tab.best_evo2 = ui.tab.add_widget(QLineEdit('...'), stretch=10)
    tab.clicked_evo2 = ui.tab.add_widget(QLineEdit('...'), stretch=10)



def update_evolution_plot(ui, tab, evo_name, gene_keys, data_folder=get_data_folder()):
    print(len(next(os.walk(data_folder + '/StorageManager/'+evo_name))[1]), 'datapoints found')

    tab.smg = StorageManagerGroup(evo_name, data_folder=data_folder)

    tab.interactive_scatter.add_StorageManagerGroup(tab.smg)
    tab.interactive_scatter.refresh_data()

    tab.smg.sort_by('score')
    tab.gene_keys = gene_keys

    result_lists = tab.smg.get_multi_param_list(gene_keys+['id']+['generation', 'score'], remove_None=True).astype(np.float64)

    tab.data = np.array(result_lists)

    tab.best_evo.setText(str(dict(zip(gene_keys, tab.data[:-3, -1]))))#'Best genome: ' +
    tab.best_evo2.setText(str(dict(zip(['id']+['generation', 'score'], tab.data[-3:, -1]))))

    tab.draw_item.update_pic(gene_keys, tab.data, tab.clicked_id, tab.slider.value())

    tab.radar_plot.update()



