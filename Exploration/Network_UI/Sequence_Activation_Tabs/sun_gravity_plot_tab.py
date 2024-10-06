from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *

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

        self._stored_similarity_colors=None
        self._last_selected_neuron=-1
        self._stored_class_colors=None
        self._last_sensitivity=-1


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
        return attractor_rads

    def compute_and_apply_attraction(self, group, attractor_rads):

        movement_speed_fac = self.p1s.sliderPosition() / 100
        anti_gravity_exp = self.p2s.sliderPosition() / 100
        random_movement_fac = self.p3s.sliderPosition() / 100
        weight_exp = self.p4s.sliderPosition() / 100
        attractor_rad_fac = self.p5s.sliderPosition() / 100

        #group.buffer_posx += (group.vector('uniform') - 0.5)*0.1
        #group.buffer_posy += (group.vector('uniform') - 0.5)*0.1

        group.add_x = (group.vector('uniform') - 0.5) * random_movement_fac# + (-group.buffer_posx)*p2
        group.add_y = (group.vector('uniform') - 0.5) * random_movement_fac# + (-group.buffer_posy)*p2#np.sin(group.buffer_posy/lb*2*np.pi)*10*p2

        for sg in group.synapses(afferent, 'GLU'):
            theta_src, rho_src = cart2pol(sg.src.buffer_posx, sg.src.buffer_posy)

            if hasattr(group, 'timescale'):
                step_factor = np.power(0.9, group.timescale)
            else:
                step_factor = 0.9

            attractorx, attractory = pol2cart(theta_src, rho_src * step_factor)

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

            w = sg.ignore_transpose_mode(sg.W)

            weights = np.power(w, weight_exp)
            weights = weights/np.sum(weights)*len(weights)

            ax = 0
            sg.dst.add_x += np.sum(weights.T*xdiff_mat, axis=ax)/xdiff_mat.shape[ax]
            sg.dst.add_y += np.sum(weights.T*ydiff_mat, axis=ax)/ydiff_mat.shape[ax]

            if attractor_rad_fac>0:
                sg.dst.add_x += attractor_rad_x*attractor_rad_fac*0.001
                sg.dst.add_y += attractor_rad_y*attractor_rad_fac*0.001

        group.buffer_posx = np.clip(group.buffer_posx + group.add_x * movement_speed_fac, -100, +100)
        group.buffer_posy = np.clip(group.buffer_posy + group.add_y * movement_speed_fac, -100, +100)

    def similarity_to_color(self, group, similarity):
        result = []
        for s in similarity:
            color=(group.color[0],group.color[1],group.color[2],(1-s)*255)
            result.append(color)
        return result

    #def class_to_color(self, classes):
    #    result = []
    #    class_colors = {}
    #    for c in classes:
    #        if c not in class_colors:
    #            class_colors[c]=(np.random.rand()*255,np.random.rand()*255,np.random.rand()*255,255)
    #        result.append(class_colors[c])
    #    return result


    def get_neuron_color(self, group):

        if hasattr(group, 'classification'):
            colors = np.array(group['Neuron_Classification_Colorizer', 0].get_color_list(group.classification, format='[r,g,b]'))

        #classification = self.cb.get_selected_result()
        #colors = np.array(group['Neuron_Classification_Colorizer', 0].get_color_list(classification, format='[r,g,b]'))

        return colors


    def draw_neurons(self, painter, group, neuron_size=1, selected_neurons=None):

        color = self.get_neuron_color(group)

        painter.setPen(0)

        inactive = group.output <= 0
        active = np.invert(inactive)

        for c in unique(color, axis=0):
            mask = np.all(color == c[None,:], axis=1) * inactive #(color == c) np.all(a == b, axis=1)
            painter.setBrush(pg.mkBrush(color=c))
            for x, y in zip(group.buffer_posx[mask], group.buffer_posy[mask]):
                painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

        painter.setBrush(pg.mkBrush(color=(0,255,0,150)))
        for x, y in zip(group.buffer_posx[active], group.buffer_posy[active]):
            painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

        if selected_neurons is not None:
            painter.setBrush(pg.mkBrush(color=(0, 255, 0, 255)))
            for x, y in zip(group.buffer_posx[selected_neurons], group.buffer_posy[selected_neurons]):
                painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

        #if type(color) is tuple:
        #painter.setBrush(pg.mkBrush(color=group.color))
        #mask=group.output>0
        #inv_mask=np.invert(mask)
        #for i, p in enumerate(zip(group.buffer_posx, group.buffer_posy)):#[inv_mask]
        #    x, y=p
        #    if type(color) is list or type(color) is np.ndarray:
        #        if group.output[i] <= 0:
                    #painter.setPen(0)#pg.mkPen(color=color[i])
        #            painter.setBrush(pg.mkBrush(color=color[i]))
        #        else:
        #            #painter.setPen(0)#pg.mkPen(color=(0,255,0,150))
        #            painter.setBrush(pg.mkBrush(color=(0,255,0,150)))
        #    painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

        #painter.setPen(pg.mkPen(color=(0,255,0,150)))
        #painter.setBrush(pg.mkBrush(color=(0,255,0,150)))
        #for x, y in zip(group.buffer_posx[mask], group.buffer_posy[mask]):
        #    painter.drawEllipse(QtCore.QPointF(x, y), neuron_size, neuron_size)

    def draw_weights(self, painter, group, selected_neuron_id):
        painter.setPen(pg.mkPen(color=(255, 0, 0, 255)))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))

        for sg in group.synapses(afferent, 'GLU'):
            temp = np.where(sg.dst.id == selected_neuron_id)[0]
            if len(temp) > 0:
                indx = temp[0]
                x = sg.dst.buffer_posx[indx]
                y = sg.dst.buffer_posy[indx]

                weights = sg.ignore_transpose_mode(sg.W)[indx, :]
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
            painter.drawText(int(x),int(y),c)

    def attach_parameter_slider(self, p0s, p1s, p2s, p3s, p4s, p5s, label_cb):
        self.p0s = p0s
        self.p1s = p1s
        self.p2s = p2s
        self.p3s = p3s
        self.p4s = p4s
        self.p5s = p5s
        self.label_cb = label_cb

    #def compute_similarity(self, group, neuron_index):
    #    group._syn_differences_ = group.vector()
    #    for sg in group.synapses(afferent, 'GLU'):
    #        if neuron_index in sg.dst.id:
    #            sg.dst._syn_differences_ += np.sum(sg.W * sg.W[:,np.where(sg.dst.id==neuron_index)[0]], axis=1)

    #    m=np.max(group._syn_differences_)
    #    if m>0:
    #        group._syn_differences_=1.0-(group._syn_differences_/m)

        #print(group._syn_differences_)

    #    return group.vector('uniform')#group._syn_differences_

    def draw_labels(self, painter, group, selection):

        #group = self.label_cb.main_object
        if group==self.label_cb.main_object and selection is not None:

            if hasattr(group, 'classification'):
                tag = self.label_cb.get_selected_key()
                module = self.label_cb.get_selected_module()
                res = self.label_cb.get_selected_result()
                generator = group.network['TextGenerator', 0]
                colors = self.get_neuron_color(group)

                if tag in self.label_cb.current_modules and module is not None and generator is not None:
                    for i in range(len(selection)):
                        if selection[i]>0:
                            #painter.setPen(pg.mkPen(color=())))

                            qf = QFont('Consolas')
                            qf.setPointSizeF(1.0)
                            painter.setFont(qf)
                            painter.drawText(int(group.buffer_posx[i]), int(group.buffer_posy[i]), res[i])


                    #class_tag_dict = module.get_class_labels(tag, group.classification, generator)

                    #for c in class_tag_dict:
                    #    mask = group.classification == c
                    #    x = np.mean(group.buffer_posx[mask])
                    #    y = np.mean(group.buffer_posy[mask])

                    #    painter.setPen(pg.mkPen(color=colors[mask][0]))

                    #    qf = QFont('Consolas')
                    #    qf.setPointSizeF(1.0)
                    #    painter.setFont(qf)
                    #    painter.drawText(x, y, class_tag_dict[c])



    def update_pic(self, groups, alphabet, nui, statistics, show_weights):

        self.picture = QtGui.QPicture()
        painter = QtGui.QPainter(self.picture)

        attractor_rads=self.draw_rings(painter,alphabet,10)

        self.groups = groups

        for group in nui.network.NeuronGroups:
            if hasattr(group, 'Input_Weights'):
                self.fixate_points(group, alphabet, group.Input_Weights)
            #self.fixate_points(group, alphabet, group['TextActivator',0].mat)

        #for group in groups:
        #    self.initialize_neuron_positons(group)

        for group in nui.network.NeuronGroups:
            self.compute_and_apply_attraction(group, attractor_rads)

        painter.scale(1, -1)

        for group in groups:
            if group == nui.selected_neuron_group():
                sel = nui.selected_neuron_mask()
            else:
                sel = None
            self.draw_neurons(painter, group, self.p0s.sliderPosition() / 100, sel)

        #painter.setBrush(pg.mkBrush(color=(0,255,0,255)))
        #for x, y in zip(group.buffer_posx+attractor_rad_x, group.buffer_posy+attractor_rad_y):
        #    painter.drawEllipse(QtCore.QPointF(x, y), 1, 1)

        if show_weights:
            self.draw_weights(painter, nui.selected_neuron_group(), nui.selected_neuron_id())


        painter.setPen(pg.mkPen(color=(0, 0, 0, 255), width=10))
        painter.setBrush(pg.mkBrush(color=(0, 0, 0, 0)))


        self.draw_chars(painter, alphabet, statistics)

        #for group in nui.network.NeuronGroups:
        for group in groups:
            if group == nui.selected_neuron_group():
                sel = nui.selected_neuron_mask()
            else:
                sel = None
            self.draw_labels(painter, group, sel)

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

class sun_gravity_plot_tab(TabBase):

    def __init__(self, title='Sun Gravity Plot'):
        super().__init__(title)

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    #def on_selected_neuron_changed(self, Network_UI):
    #    self.comboBox.change_main_object(Network_UI.get_selected_neuron_group())

    def initialize(self, Network_UI):
        self.sun_gravity_plot_tab=None
        if Network_UI.network['TextGenerator', 0]:# is not None or Network_UI.network['grammar_act', 0] is not None or Network_UI.network['drum_act', 0] is not None or Network_UI.network['music_act', 0] is not None:
            self.sun_gravity_plot_tab = Network_UI.add_tab(title=self.title) #Network_UI.Next_Tab(self.title)

            #alphabet = Network_UI.network['grammar_act'][0].alphabet
            #a_list = [alphabet[i] for i in range(len(alphabet))]
            #a_list[0] = '_'
            #ydict = dict(enumerate(a_list))

            #win = pg.GraphicsWindow()
            #stringaxis = pg.AxisItem(orientation='left')
            #stringaxis.setTicks([ydict.items()])

            for group in Network_UI.network.NeuronGroups:
                group.buffer_posx, group.buffer_posy = pol2cart(group.vector('uniform') * 2 * np.pi, group.vector('uniform') * 100)

            self.last_id = -1
            self.last_group = -1

            def mdce(event):
                if self.last_group.classification is not None:
                    selected_class = self.last_group.classification[self.last_id]
                    Network_UI.select_neuron_class(self.last_group, selected_class)

            def mce(event):
                sel_index=0
                min_dist=-1
                self.last_group = None
                for group in event.currentItem.groups:
                    dx = group.buffer_posx-event.pos().x()
                    dy = group.buffer_posy-event.pos().y() * -1
                    d = np.sqrt(dx*dx+dy*dy)
                    if min_dist==-1 or np.min(d)<min_dist:
                        min_dist = np.min(d)
                        sel_index = np.argmin(d)
                        self.last_group = group
                self.last_id = sel_index
                Network_UI.select_neuron(self.last_group, sel_index)



            msg = 'Each particle is a neuron of the selected Group.\r\n' \
                  'The primary input neurons are fixed to the outer ring.\r\n' \
                  'The attraction between the neuron-particles is defined by synaptic weights.\r\n' \
                  'To avoid clustering in the center, the attraction increases exponetially with greater distance from the center.\r\n' \
                  'The point of attraction is not in the center of each particle,\r\n' \
                  'but the particlses position moved one step furter to the center, so one ring indicates one iteration step.'

            self.plot = Network_UI.tab.add_plot(x_label='buffer steps', tooltip_message=msg)#axisItems={'left': stringaxis}
            self.plot.hideAxis('bottom')
            self.plot.hideAxis('left')

            self.draw_item = DrawItem2()
            self.plot.addItem(self.draw_item)
            self.draw_item.mouseClickEvent = mce
            self.draw_item.mouseDoubleClickEvent = mdce

            #if Network_UI.network['grammar_act', 0] is not None:
            #    source = Network_UI.network['grammar_act'][0]
            #    self.base_char_masks_dict = dict([(char, source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])

            #elif Network_UI.network['drum_act', 0] is not None:
            #    source = Network_UI.network['drum_act'][0]
            #    self.base_char_masks_dict = dict([(source.instruments[char], source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])
            
            #elif Network_UI.network['music_act', 0] is not None:
            #    source = Network_UI.network['music_act'][0]
            #    self.base_char_masks_dict = dict([(source.midi_index_to_notestring(char), source.get_activation(i, Network_UI.network['prediction_source', 0])) for i, char in enumerate(source.alphabet)])

            Network_UI.tab.add_row()
            #Network_UI.Next_H_Block()

            self.sl1 = QSlider(1)
            self.sl1.setMinimum(0)
            self.sl1.setMaximum(1000)
            self.sl1.setSliderPosition(100)
            self.sl1.label = QLabel('Speed:')
            Network_UI.tab.add_widget(self.sl1.label, stretch=0)
            Network_UI.tab.add_widget(self.sl1, stretch=10)

            self.sl2 = QSlider(1)
            self.sl2.setMinimum(0)
            self.sl2.setMaximum(3000)
            self.sl2.setSliderPosition(100)
            self.sl2.label = QLabel('Anti gravity:')
            Network_UI.tab.add_widget(self.sl2.label, stretch=0)
            Network_UI.tab.add_widget(self.sl2, stretch=10)

            self.sl3 = QSlider(1)
            self.sl3.setMinimum(0)
            self.sl3.setMaximum(100)
            self.sl3.setSliderPosition(0)
            self.sl3.label = QLabel('Noise:')
            Network_UI.tab.add_widget(self.sl3.label, stretch=0)
            Network_UI.tab.add_widget(self.sl3, stretch=10)

            self.sl4 = QSlider(1)
            self.sl4.setMinimum(0)
            self.sl4.setMaximum(500)
            self.sl4.setSliderPosition(100)
            self.sl4.label = QLabel('W^:')
            Network_UI.tab.add_widget(self.sl4.label, stretch=0)
            Network_UI.tab.add_widget(self.sl4, stretch=10)

            self.sl5 = QSlider(1)
            self.sl5.setMinimum(0)
            self.sl5.setMaximum(100)
            self.sl5.setSliderPosition(0)
            self.sl5.label = QLabel('Ring attraction:')
            Network_UI.tab.add_widget(self.sl5.label, stretch=0)
            Network_UI.tab.add_widget(self.sl5, stretch=10)

            Network_UI.tab.add_row()
            #Network_UI.Next_H_Block()

            self.sl0 = QSlider(1)
            self.sl0.setMinimum(0)
            self.sl0.setMaximum(100)
            self.sl0.setSliderPosition(50)
            self.sl0.label = QLabel('Size:')
            Network_UI.tab.add_widget(self.sl0.label, stretch=0)
            Network_UI.tab.add_widget(self.sl0, stretch=10)

            self.weight_plot_cb = QCheckBox()
            self.weight_plot_cb.setText('Show weights')
            self.weight_plot_cb.setChecked(True)
            Network_UI.tab.add_widget(self.weight_plot_cb, stretch=10)

            self.comboBox = Network_UI.tab.add_widget(Analytics_Results_Select_ComboBox(Network_UI.network.NeuronGroups[0], tag='labeler', first_entry='none'), stretch=10)

            self.draw_item.attach_parameter_slider(self.sl0, self.sl1, self.sl2, self.sl3, self.sl4, self.sl5, self.comboBox)



    def update(self, Network_UI):
        groups = Network_UI.get_visible_neuron_groups()
        alphabet = []

        if self.sun_gravity_plot_tab is not None and self.sun_gravity_plot_tab.isVisible():

            if Network_UI.network['TextGenerator', 0] is not None:
                self.draw_item.update_pic(groups, Network_UI.network['TextGenerator', 0].alphabet, Network_UI, Network_UI.network['TextGenerator', 0].count_chars_in_blocks(), self.weight_plot_cb.isChecked())
                self.plot.update()

            '''
            if Network_UI.network['grammar_act', 0] is not None:
                #group = Network_UI.network['prediction_source', 0]

                self.draw_item.update_pic(groups, Network_UI.network['grammar_act', 0].alphabet, Network_UI, Network_UI.network['grammar_act', 0].get_char_input_statistics_list(), self.weight_plot_cb.isChecked())
                self.plot.update()

            elif Network_UI.network['drum_act', 0] is not None:
                source = Network_UI.network['drum_act', 0]
                for index in source.alphabet:
                    alphabet.append(source.instruments[index])

                if source.include_inverse_alphabet: # include the symbols that stand for NOT the instrument
                    for index in source.alphabet:
                        alphabet.append('! '+source.instruments[index])

                self.draw_item.update_pic(groups, alphabet, Network_UI, source.get_instrument_input_statistics_list(), self.weight_plot_cb.isChecked())
                self.plot.update()

            elif Network_UI.network['music_act', 0] is not None:
                source = Network_UI.network['music_act', 0]
                for index in source.alphabet:
                    alphabet.append(source.midi_index_to_notestring(index))
                self.draw_item.update_pic(groups, alphabet, Network_UI, source.get_note_input_statistics_list(), self.weight_plot_cb.isChecked())
                self.plot.update()

            elif
            '''


