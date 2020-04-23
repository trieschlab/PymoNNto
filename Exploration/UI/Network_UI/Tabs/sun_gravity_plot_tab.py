from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

from Exploration.Visualization.Reconstruct_Analyze_Label.Reconstruct_Analyze_Label import *

from PyQt5 import QtCore, QtGui, QtWidgets, uic

import pyqtgraph as pg


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

    def draw_rings(self, painter, alphabet, num_rings):

        attractor_rads = []
        for i in range(num_rings):
            c=int(200+i*5.5)
            painter.setPen(pg.mkPen(color=(c, c, c, 255)))
            r = 100*np.power(0.9, i)
            attractor_rads.append(r)

            painter.setBrush(pg.mkBrush(color=(c, c, c, 0)))
            painter.drawEllipse(QtCore.QPointF(0, 0), r, r)

            for d, char in enumerate(alphabet):
                x, y = pol2cart(d / len(alphabet) * 2 * np.pi, r)
                painter.setBrush(pg.mkBrush(color=(c, c, c, 255)))
                painter.drawEllipse(QtCore.QPointF(x, y), 1, 1)
        return  attractor_rads

    def compute_and_apply_attraction(self, group, movement_speed_fac, anti_gravity_exp, random_movement_fac, weight_exp, attractor_rad_fac, attractor_rads):

            #group.buffer_posx += (group.get_random_neuron_vec() - 0.5)*0.1
            #group.buffer_posy += (group.get_random_neuron_vec() - 0.5)*0.1

            group.add_x = (group.get_random_neuron_vec() - 0.5) * random_movement_fac# + (-group.buffer_posx)*p2
            group.add_y = (group.get_random_neuron_vec() - 0.5) * random_movement_fac# + (-group.buffer_posy)*p2#np.sin(group.buffer_posy/lb*2*np.pi)*10*p2

            for sg in group.afferent_synapses['GLU']:
                theta_src, rho_src = cart2pol(sg.src.buffer_posx, sg.src.buffer_posy)
                attractorx, attractory = pol2cart(theta_src, rho_src*0.9)

                theta_dst, rho_dst = cart2pol(sg.dst.buffer_posx, sg.dst.buffer_posy)
                rd = np.array(attractor_rads)[:, None]-rho_dst[None, :]

                #get closest attractor
                if attractor_rad_fac > 0:
                    closest = np.array([rd[indx, i] for i, indx in enumerate(np.argmin(np.abs(rd), axis=0))])
                    #move_to_rad = np.choose(np.argmax(np.abs(rd), axis=1), rd)
                    attractor_rad_x, attractor_rad_y = pol2cart(theta_dst, closest)

                    f = np.abs(attractor_rad_x) + np.abs(attractor_rad_y)
                    attractor_rad_x[f > 0] /= f[f > 0]/len(attractor_rad_x)
                    attractor_rad_y[f > 0] /= f[f > 0]/len(attractor_rad_y)

                xdiff_mat = attractorx[:, None]-sg.dst.buffer_posx[None, :]
                ydiff_mat = attractory[:, None]-sg.dst.buffer_posy[None, :]

                f = np.abs(xdiff_mat)+np.abs(ydiff_mat)
                xdiff_mat[f > 0] /= f[f > 0]/len(xdiff_mat)
                ydiff_mat[f > 0] /= f[f > 0]/len(ydiff_mat)

                xdiff_mat[(f < 3) * (f > 0)] *= 1/3*(f[(f < 3) * (f > 0)])
                ydiff_mat[(f < 3) * (f > 0)] *= 1/3*(f[(f < 3) * (f > 0)])

                #d=np.sqrt(xdiff_mat*xdiff_mat+ydiff_mat*ydiff_mat)

                #xdiff_mat[d < 0.1] *= -10
                #ydiff_mat[d < 0.1] *= -10

                #print(rho)

                rho_src = np.power(rho_src, anti_gravity_exp)
                rho_src = rho_src/np.sum(rho_src)*len(rho_src)

                xdiff_mat *= rho_src[:, None]
                ydiff_mat *= rho_src[:, None]

                #xdiff_mat=xdiff_mat*xdiff_mat*xdiff_mat
                #ydiff_mat=ydiff_mat*ydiff_mat*ydiff_mat

                weights = np.power(sg.W, weight_exp)
                weights = weights/np.sum(weights)*len(weights)

                ax = 0
                sg.dst.add_x += np.sum(weights.T*xdiff_mat, axis=ax)/xdiff_mat.shape[ax]
                sg.dst.add_y += np.sum(weights.T*ydiff_mat, axis=ax)/ydiff_mat.shape[ax]

                if attractor_rad_fac>0:
                    sg.dst.add_x += attractor_rad_x*attractor_rad_fac*0.001
                    sg.dst.add_y += attractor_rad_y*attractor_rad_fac*0.001

            group.buffer_posx = np.clip(group.buffer_posx + group.add_x * movement_speed_fac, -100, +100)
            group.buffer_posy = np.clip(group.buffer_posy + group.add_y * movement_speed_fac, -100, +100)




    def draw_neurons(self, painter, group, neuron_size=1):
        painter.setPen(pg.mkPen(color=group.color))
        painter.setBrush(pg.mkBrush(color=group.color))
        mask=group.output>0
        inv_mask=np.invert(mask)
        for x, y in zip(group.buffer_posx[inv_mask], group.buffer_posy[inv_mask]):
            painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

        painter.setPen(pg.mkPen(color=(255,255,255,50)))
        painter.setBrush(pg.mkBrush(color=(255,255,255,50)))
        for x, y in zip(group.buffer_posx[mask], group.buffer_posy[mask]):
            painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

    def draw_weights(self, painter, group, selected_neuron_id):
        painter.setPen(pg.mkPen(color=(255, 0, 0, 255)))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))

        for sg in group.afferent_synapses['GLU']:
            temp = np.where(sg.dst.id == selected_neuron_id)[0]
            if len(temp) > 0:
                indx = temp[0]
                x = sg.dst.buffer_posx[indx]
                y = sg.dst.buffer_posy[indx]
                weights = sg.W[indx, :]
                max_w = np.max(weights)
                # painter.drawEllipse(QtCore.QPointF(x, y), 0.1, 0.1)
                for i, w in enumerate(weights):
                    if w > 0.0:
                        xs = sg.src.buffer_posx[i]
                        ys = sg.src.buffer_posy[i]
                        if xs != x and ys != y:
                            cv = 255.0 / max_w * w
                            cv = (cv * cv) / (255)
                            painter.setPen(pg.mkPen(color=(255, 0, 0, cv)))
                            painter.drawLine(QtCore.QPointF(x, y), QtCore.QPointF(xs, ys))  #


    def fixate_points(self, group, alphabet, input_mat):
        for i, char in enumerate(alphabet):
            bm=input_mat[:, i]
            x, y = pol2cart(i / len(alphabet) * 2 * np.pi, 100)
            group.buffer_posx[bm > 0.1] = x
            group.buffer_posy[bm > 0.1] = y


    def draw_chars(self, painter, alphabet, statistics):
        for i, char in enumerate(alphabet):
            x, y = pol2cart(i / len(alphabet) * 2 * np.pi, 110)

            val = float(statistics[i]) / float(np.max(statistics)) * 20.0

            qf=QFont('Arial')
            qf.setPointSizeF(2+val/4.0)
            #qf.setStretch(2)
            painter.setFont(qf)
            if char==' ':
                c='_'
            else:
                c=char
            painter.drawText(x,y,c)


    def update_pic(self, groups, alphabet, p0, p1, p2, p3, p4, p5, nui, statistics, show_weights):

        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)

        attractor_rads=self.draw_rings(painter,alphabet,10)

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
                if group.tags[0] == nui.neuron_select_group:
                    self.draw_weights(painter, group, nui.neuron_select_id)


        painter.setPen(pg.mkPen(color=(0, 0, 0, 255), width=10))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))

        for group in nui.network.NeuronGroups:
            if hasattr(group, 'Input_Weights'):
                self.fixate_points(group, alphabet, group.Input_Weights)

        self.draw_chars(painter, alphabet, statistics)

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

class sun_gravity_plot_tab():

    def __init__(self, title='Sun Gravity Plot'):
        self.title = title

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None or Network_UI.network['drum_act', 0] is not None or Network_UI.network['music_act', 0] is not None:
            self.sun_gravity_plot_tab = Network_UI.Next_Tab(self.title)

            #alphabet = Network_UI.network['grammar_act'][0].alphabet
            #a_list = [alphabet[i] for i in range(len(alphabet))]
            #a_list[0] = '_'
            #ydict = dict(enumerate(a_list))

            #win = pg.GraphicsWindow()
            #stringaxis = pg.AxisItem(orientation='left')
            #stringaxis.setTicks([ydict.items()])

            for group in  Network_UI.network.NeuronGroups:
                group.buffer_posx, group.buffer_posy = pol2cart(group.get_random_neuron_vec() * 2 * np.pi, group.get_random_neuron_vec() * 100)

            def c(event):
                for group in event.currentItem.groups:
                    dx = group.buffer_posx-event.pos().x()
                    dy = group.buffer_posy-event.pos().y()*-1
                    d = np.sqrt(dx*dx+dy*dy)

                    indices = np.where(d<1)[0]

                    if len(indices) > 0:
                        Network_UI.neuron_select_group = group.tags[0]
                        Network_UI.neuron_select_id = indices[0]

            msg = 'Each particle is a neuron of the selected Group.\r\n' \
                  'The primary input neurons are fixed to the outer ring.\r\n' \
                  'The attraction between the neuron-particles is defined by synaptic weights.\r\n' \
                  'To avoid clustering in the center, the attraction increases exponetially with greater distance from the center.\r\n' \
                  'The point of attraction is not in the center of each particle,\r\n' \
                  'but the particlses position moved one step furter to the center, so one ring indicates one iteration step.'

            self.plot = Network_UI.Add_plot(x_label='buffer steps', tooltip_message=msg)#axisItems={'left': stringaxis}
            self.draw_item = DrawItem2()
            self.plot.addItem(self.draw_item)
            self.draw_item.mouseClickEvent = c

            if Network_UI.network['grammar_act', 0] is not None: 
                source = Network_UI.network['grammar_act'][0]
                self.base_char_masks_dict=dict([(char, source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])

            elif Network_UI.network['drum_act', 0] is not None: 
                source = Network_UI.network['drum_act'][0]
                self.base_char_masks_dict=dict([(source.instruments[char], source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])
            
            elif Network_UI.network['music_act', 0] is not None: 
                source = Network_UI.network['music_act'][0]
                self.base_char_masks_dict=dict([(source.midi_index_to_notestring(char), source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])
            

            Network_UI.Next_H_Block()

            self.sl0 = QSlider(1)
            self.sl0.setMinimum(0)
            self.sl0.setMaximum(100)
            self.sl0.setSliderPosition(50)
            self.sl0.label = QLabel('Size:')
            Network_UI.Add_element(self.sl0.label)
            Network_UI.Add_element(self.sl0, stretch=10)

            self.sl1 = QSlider(1)
            self.sl1.setMinimum(0)
            self.sl1.setMaximum(1000)
            self.sl1.setSliderPosition(100)
            self.sl1.label = QLabel('Speed:')
            Network_UI.Add_element(self.sl1.label)
            Network_UI.Add_element(self.sl1, stretch=10)

            self.sl2 = QSlider(1)
            self.sl2.setMinimum(0)
            self.sl2.setMaximum(1000)
            self.sl2.setSliderPosition(100)
            self.sl2.label = QLabel('Anti gravity:')
            Network_UI.Add_element(self.sl2.label)
            Network_UI.Add_element(self.sl2, stretch=10)

            self.sl3 = QSlider(1)
            self.sl3.setMinimum(0)
            self.sl3.setMaximum(100)
            self.sl3.setSliderPosition(0)
            self.sl3.label = QLabel('Noise:')
            Network_UI.Add_element(self.sl3.label)
            Network_UI.Add_element(self.sl3, stretch=10)

            self.sl4 = QSlider(1)
            self.sl4.setMinimum(0)
            self.sl4.setMaximum(500)
            self.sl4.setSliderPosition(100)
            self.sl4.label = QLabel('W^:')
            Network_UI.Add_element(self.sl4.label)
            Network_UI.Add_element(self.sl4, stretch=10)

            self.sl5 = QSlider(1)
            self.sl5.setMinimum(0)
            self.sl5.setMaximum(100)
            self.sl5.setSliderPosition(0)
            self.sl5.label = QLabel('Ring attraction:')
            Network_UI.Add_element(self.sl5.label)
            Network_UI.Add_element(self.sl5, stretch=10)

            self.weight_plot_cb = QCheckBox()
            self.weight_plot_cb.setText('Show weights')
            self.weight_plot_cb.setChecked(True)
            Network_UI.Add_element(self.weight_plot_cb, stretch=10)



    def update(self, Network_UI):
        if Network_UI.network['grammar_act', 0] is not None and self.sun_gravity_plot_tab.isVisible():
            #group = Network_UI.network['prediction_source', 0]

            groups = [Network_UI.network[tag, 0] for tag in Network_UI.neuron_visible_groups]

            self.draw_item.update_pic(groups, Network_UI.network['grammar_act', 0].alphabet, self.sl0.sliderPosition()/100, self.sl1.sliderPosition()/100, self.sl2.sliderPosition()/100, self.sl3.sliderPosition()/100, self.sl4.sliderPosition()/100, self.sl5.sliderPosition()/100, Network_UI, Network_UI.network['grammar_act', 0].get_char_input_statistics_list(), self.weight_plot_cb.isChecked())
            self.plot.update()

        elif Network_UI.network['drum_act', 0] is not None and self.sun_gravity_plot_tab.isVisible(): 
            groups = [Network_UI.network[tag, 0] for tag in Network_UI.neuron_visible_groups]
            source = Network_UI.network['drum_act', 0]
            alphabet = []
            for index in source.alphabet:
                alphabet.append(source.instruments[index])
            
            if source.include_inverse_alphabet: # include the symbols that stand for NOT the instrument
                for index in source.alphabet:
                    alphabet.append('! '+source.instruments[index])
            
            self.draw_item.update_pic(groups, alphabet, self.sl0.sliderPosition()/100, self.sl1.sliderPosition()/100, self.sl2.sliderPosition()/100, self.sl3.sliderPosition()/100, self.sl4.sliderPosition()/100, self.sl5.sliderPosition()/100, Network_UI, source.get_instrument_input_statistics_list(), self.weight_plot_cb.isChecked())
            self.plot.update()

        elif Network_UI.network['music_act', 0] is not None and self.sun_gravity_plot_tab.isVisible(): 
            groups = [Network_UI.network[tag, 0] for tag in Network_UI.neuron_visible_groups]
            source = Network_UI.network['music_act', 0]
            alphabet = []
            for index in source.alphabet:
                alphabet.append(source.midi_index_to_notestring(index))
            self.draw_item.update_pic(groups, alphabet, self.sl0.sliderPosition()/100, self.sl1.sliderPosition()/100, self.sl2.sliderPosition()/100, self.sl3.sliderPosition()/100, self.sl4.sliderPosition()/100, self.sl5.sliderPosition()/100, Network_UI, source.get_note_input_statistics_list(), self.weight_plot_cb.isChecked())
            self.plot.update()
