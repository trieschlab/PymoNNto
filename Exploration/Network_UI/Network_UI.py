from PymoNNto.Exploration.UI_Base import *
from PymoNNto.NetworkBehaviour.Recorder.Recorder import *
from PymoNNto.Exploration.Network_UI.Neuron_Classification_Colorizer import *

class Network_UI(UI_Base):

    def __init__(self, network, modules=[], label='SORN UI', group_tags=[], transmitters=[], storage_manager=None, group_display_count=None, reduced_layout=False):

        network.simulate_iteration()

        network.clear_recorder()

        self.render_every_x_frames = 1

        #network.simulate_iteration()
        #self.recording = False
        #if self.recording:
        #    label += ' rec.'

        for ng in network.NeuronGroups:
            if not hasattr(ng, 'color'):
                ng.color = (0, 0, 255, 255)
            ng.add_analysis_module(Neuron_Classification_Colorizer())

        if group_tags==[]:
            for ng in network.NeuronGroups:
                if ng.tags[0] not in group_tags:
                    group_tags.append(ng.tags[0])

        if transmitters==[]:
            for sg in network.SynapseGroups:
                if sg.tags[0] not in transmitters:
                    transmitters.append(sg.tags[0])

        self.reduced_layout=reduced_layout

        #for group in network[inh_group_name]:
        #    network.add_behaviours_to_neuron_group({10000: Recorder(['np.mean(n.output)',
        #                           'np.mean(n.TH)',
        #                           'n.TH',
        #                           'n.excitation',
        #                           'n.inhibition',
        #                           'n.input_act',
        #                           'n.refractory_counter',
        #                           '[np.sum(s.slow_add) for s in n.afferent_synapses.get("All")]',
        #                           '[np.sum(s.fast_add) for s in n.afferent_synapses.get("All")]'], tag='UI_rec')}, group)

        super().__init__(network, label=label)

        self.group_display_count = group_display_count

        #self.exc_group_name = exc_group_name
        #self.inh_group_name = inh_group_name
        self.group_tags = group_tags
        self.transmitters=transmitters
        self.pause = False
        self.update_without_state_change = False
        self.storage_manager = storage_manager

        self.neuron_select_x = 0
        self.neuron_select_y = 0
        self.neuron_select_id = 0
        self.neuron_select_group = group_tags[0]#exc_group_name
        self.neuron_visible_groups = []


        #self.ts_group = 0
        #self.x_steps = 500
        #self.group_sliders = []
        self.neuron_select_color = (0, 255, 0, 255)

        self.modules = modules

        if type(self.modules) is dict:
            self.modules = self.modules.values()

        for module in self.modules:
            print('Initialize:', module)
            module.initialize(self)

        for group_tag in group_tags:
            for group in network[group_tag]:

                group._rec_dict = {}

                #rec = Recorder([], tag='UI_rec')
                #network.add_behaviours_to_neuron_group({10000: rec}, group)

                for module in self.modules:
                    module.add_recorder_variables(group, self)

        self.init_recoders()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_timer)
        self.timer.start(40)

    def select_neuron(self, group_tag, id):
        self.neuron_select_group = group_tag
        self.neuron_select_id = id
        for module in self.modules:
            module.on_selected_neuron_changed(self)
        self.static_update_func()

    def get_selected_neuron_group(self):
        return self.network[self.neuron_select_group, 0]

    def get_selected_neuron_index(self):
        return self.neuron_select_id

    def add_recording_variable(self, group, var, timesteps):

        try:
            n = group  # for eval
            eval(var) #produce error when not evaluable

            old_ts=0
            if var in group._rec_dict:
                old_ts=group._rec_dict[var]

            group._rec_dict[var] = max(timesteps,old_ts)
            #recorder.add_varable('n.output')
            return True
        except:
            return False

    def init_recoders(self):
        for group_tag in self.group_tags:
            for group in self.network[group_tag]:

                rec_time_dict={}
                for variable in group._rec_dict:
                    rec_length=group._rec_dict[variable]
                    if rec_length not in rec_time_dict:
                        rec_time_dict[rec_length]=[]
                    rec_time_dict[rec_length].append(variable)

                for rec_length in rec_time_dict:
                    rec = Recorder(rec_time_dict[rec_length] + ['n.iteration'], tag='UI_rec,rec_' + str(rec_length), max_length=rec_length)
                    self.network.add_behaviours_to_object({10000+rec_length: rec}, group)

    #def rec(self, neuron_group, rec_length=-1):
    #    return neuron_group[self.rec_tag(rec_length),0]

    #def rec_tag(self, rec_length=-1):
    #    if rec_length==-1:
    #        rec_length = self.default_rec_recording_length
    #    return 'rec_'+str(rec_length)

    def static_update_func(self, event=None):
        if self.pause:
            self.update_without_state_change=True

    def get_selected_neuron_subgroup(self):
        syn_sgs = self.get_selected_synapses()
        if len(syn_sgs) > 0:
            return syn_sgs[0]
        else:
            return None

    def get_selected_synapses(self):
        result = []
        if len(self.network[self.neuron_select_group]) > 0:
            group = self.network[self.neuron_select_group, 0]
            synapse_groups = group.afferent_synapses['All']
            for i, s in enumerate(synapse_groups):
                if (type(s.dst.mask) == np.ndarray and s.dst.mask[self.neuron_select_id]) or (type(s.dst.mask) is bool and s.dst.mask == True):
                    result.append(synapse_groups[i].dst)
        return result

    def on_timer(self):

        if not self.pause or self.step or self.update_without_state_change:
            self.step = False
            if not self.update_without_state_change:
                for i in range(self.render_every_x_frames):
                    self.network.simulate_iteration()

            self.it = self.network.iteration

            for module in self.modules:
                module.update(self)

            #for rec in self.network['UI_rec']:
            #    rec.cut_length(self.default_recorder_length)

            self.update_without_state_change = False

    def on_tab_change(self, i):
        self.static_update_func()

def get_color(type_index, layer=1):
    dim_value = max(layer * 0.9, 1.0)

    if type_index == 0:
        return (0.0, 0.0, 255.0 / dim_value, 255.0)
    if type_index == 1:
        return (255.0 / dim_value, 0.0, 0.0, 255.0)
    if type_index == 2:
        return (255.0 / dim_value, 150.0 / dim_value, 0.0, 255.0)
    if type_index == 3:
        return (255.0 / dim_value, 80.0 / dim_value, 0.0, 255.0)
    if type_index == 4:
        return (255.0 / dim_value, 0.0 , 150.0/ dim_value, 255.0)


class Analytics_Results_Select_ComboBox(QComboBox):
    popupAboutToBeShown = QtCore.pyqtSignal()

    def __init__(self, main_object, tag='classifier', first_entry=None, select_last=True):
        super().__init__()
        self.first_entry = first_entry
        self.tag = tag

        self.current_results = {}
        self.current_modules = {}

        self.main_object = None
        self.change_main_object(main_object)

        if select_last and self.count() > 0:
            self.setCurrentIndex(self.count()-1)

    def change_main_object(self, main_object):
        if self.main_object is not None:
            self.remove_update_notifier()
        self.main_object = main_object
        self.update()
        self.set_update_notifier()

    def set_update_notifier(self):
        if isinstance(self.main_object, AnalysisModule):
            self.main_object.set_update_notifier(self.update)
        else:
            for obj in self.main_object[self.tag]:
                if isinstance(obj, AnalysisModule):
                    obj.set_update_notifier(self.update)

    def remove_update_notifier(self):
        if isinstance(self.main_object, AnalysisModule):
            self.main_object.remove_update_notifier(self.update)
        else:
            for obj in self.main_object[self.tag]:
                if isinstance(obj, AnalysisModule):
                    obj.remove_update_notifier(self.update)

    def get_selected_key(self):
        return self.currentText()

    def get_selected_module(self):
        key = self.get_selected_key()
        if key in self.current_modules:
            return self.current_modules[key]

    def get_selected_result(self):
        key = self.get_selected_key()
        if key in self.current_results:
            return self.current_results[key]

    def update(self):
        current = self.currentText()

        self.clear()

        if self.first_entry is not None:
            self.addItem(self.first_entry)

        if isinstance(self.main_object, AnalysisModule):
            self.current_results = self.main_object.get_results()
            for k in self.current_results:
                self.addItem(k)
            self.current_modules = {k: self.main_object for k in self.current_results}
        else:
            self.current_results, self.current_modules = self.main_object.get_all_analysis_module_results(self.tag, True)
            for k in self.current_results:
                self.addItem(k)

        for i in range(self.count()):
            if self.itemText(i) == current:
                self.setCurrentIndex(i)


    #def showPopup(self):
    #    self.update()
    #    #self.popupAboutToBeShown.emit()
    #    super().showPopup()

'''
def get_color(type_index, layer):
    dim_value = max(layer * 1.0, 1.0)

    if type_index == 0:
        return (0.0, 0.0, 255.0 / dim_value, 255.0)
    if type_index == 1:
        return (255.0 / dim_value, 0.0, 0.0, 255.0)
    if type_index == 2:
        return (255.0 / dim_value, 150.0 / dim_value, 0.0, 255.0)
    if type_index == 3:
        return (255.0 / dim_value, 80.0 / dim_value, 0.0, 255.0)
    if type_index == 4:
        return (255.0 / dim_value, 0.0 , 150.0/ dim_value, 255.0)
'''

########################################################### Exception handling

'''

from io import StringIO
import traceback
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
#import time

def excepthook(excType, excValue, tracebackobj):
    """
    Global function to catch unhandled exceptions.

    @param excType exception type
    @param excValue exception value
    @param tracebackobj traceback object
    """
    separator = '-' * 80
    logFile = "simple.log"
    notice = \
        """An unhandled exception occurred. Please report the problem\n""" \
        """using the error reporting dialog or via email to <%s>.\n""" \
        """A log has been written to "%s".\n\nError information:\n""" % \
        ("yourmail at server.com", "")
    versionInfo = "0.0.1"
    timeString = time.strftime("%Y-%m-%d, %H:%M:%S")
    tbinfofile = StringIO()
    traceback.print_tb(tracebackobj, None, tbinfofile)
    traceback.print_stack()
    #traceback.print_exc()
    #tbinfofile.seek(0)
    #tbinfo = tbinfofile.read()
    #errmsg = '%s: \n%s' % (str(excType), str(excValue))
    #sections = [separator, separator, errmsg, separator, tbinfo]
    #msg = '\n'.join(sections)
    #try:
    #    f = open(logFile, "w")
    #    f.write(msg)
    #    f.write(versionInfo)
    #    f.close()
    #except IOError:
    #    pass
    #errorbox = QMessageBox()
    #errorbox.setText(str(notice) + str(msg) + str(versionInfo))
    #errorbox.exec_()
'''

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

sys.excepthook = except_hook




#from Exploration.Visualization.Visualization_Helper import *

#sys._excepthook = sys.excepthook
#def exception_hook(exctype, value, traceback):
#    print(exctype, value, traceback)
#    sys._excepthook(exctype, value, traceback)
#    sys.exit(1)
#sys.excepthook = exception_hook





# def record_frame(self, item=None, key='frame', width=100):
#    if self.storage_manager is not None and item is not None:
#        exporter = pg.exporters.ImageExporter(item)
#        #exporter.parameters()['width'] = width  # (note this also affects height parameter)

#        exporter.params.param('width').setValue(150, blockSignal=exporter.widthChanged)
#        exporter.params.param('height').setValue(120, blockSignal=exporter.heightChanged)

#        next=self.storage_manager.get_next_frame_name(key)
#        exporter.export(next)


#screen = QApplication.primaryScreen()
#p = screen.grabWindow(self.main_window.winId())
#p.save('test{}.png'.format(self.network.iteration), 'png')

'''
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Left:
            self.ny-=1
        if event.key() == QtCore.Qt.Key_Right:
            self.ny+=1
        if event.key() == QtCore.Qt.Key_Up:
            self.nx+=1
        if event.key() == QtCore.Qt.Key_Down:
            self.nx-=1
        self.nx = np.clip(self.nx, 0, self.ng_width - 1)
        self.ny = np.clip(self.ny, 0, self.ng_height - 1)
        self.n_id=self.ny*self.ng_width+self.nx
'''


# if not self.update_without_state_change:
#    self.avg_big_synapses_data.append(np.average(np.sum(GLU_syn > (np.max(GLU_syn, axis=1) * (1 / 2))[:, None], axis=0)))
#    self.neuron_big_synapses_data.append(np.sum(GLU_syn[self.neuron_select_id] > (np.max(GLU_syn[self.neuron_select_id]) * (1 / 2))))

# self.avg_big_synapses_curve.setData(np.arange(it - len(self.avg_big_synapses_data), it), self.avg_big_synapses_data)
# self.neuron_big_synapses_curve.setData(np.arange(it-len(self.neuron_big_synapses_data), it), self.neuron_big_synapses_data)


'''
GLU_syn = self.get_combined_syn_mat(self.network[self.neuron_select_group, ts_group]['GLU'])[0]

selected_GLU_syn = GLU_syn[self.neuron_select_id]

GABA_syn = self.network[self.neuron_select_group, ts_group]['GABA']
if len(GABA_syn) > 0:
    GABA_syn = self.get_combined_syn_mat(GABA_syn)[0]
    selected_GABA_syn = GABA_syn[self.neuron_select_id]
else:
    GABA_syn = None





asfdsf



#exc_shape = (self.network[self.exc_group_name, ts_group].height, self.network[self.exc_group_name, ts_group].width)
w_img = np.reshape(selected_GLU_syn, exc_shape)
self.weight_GLU_items[0].setImage(w_img)

if GABA_syn is not None and selected_GABA_syn is not None:
    #inh_shape = (self.network[self.inh_group_name, ts_group].height, self.network[self.inh_group_name, ts_group].width)
    w_img = np.reshape(selected_GABA_syn, inh_shape)
    self.weight_GABA_items[0].setImage(w_img)
else:
    self.weight_GABA_items[0].clear()
'''

'''
        self.graph = pg.GraphItem()
        p=self.Add_plot('', True)
        p.addItem(self.graph)
        #self.Add_Sidebar_Element(self.graph)
        #self.inp_text_label.setText('test')

        # Define positions of nodes
        pos = np.array([
            [0, 0],
            [10, 0],
            [0, 10],
            [10, 10],
            [5, 5],
            [15, 5]
        ], dtype=float)

        # Define the set of connections in the graph
        adj = np.array([
            [0, 1],
            [1, 3],
            [3, 2],
            [2, 0],
            [1, 5],
            [3, 5],
        ])

        # Define the symbol to use for each node (this is optional)
        symbols = ['o', 'o', 'o', 'o', 'o', 'o']

        # Define the line style for each connection (this is optional)
        lines = np.array([
            (255, 255, 255, 255, 1),
            (255, 255, 255, 255, 2),
            (255, 255, 255, 255, 3),
            (255, 255, 255, 255, 2),
            (255, 255, 255, 255, 1),
            (255, 255, 255, 255, 4),
        ], dtype=[('red', np.ubyte), ('green', np.ubyte), ('blue', np.ubyte), ('alpha', np.ubyte), ('width', float)])

        # Define text to show next to each symbol
        texts = ["Point %d" % i for i in range(6)]

        # Update the graph
        self.graph.setData(pos=pos, adj=adj, pen=lines, size=1, symbol=symbols, pxMode=False, text=texts)
        #https://stackoverflow.com/questions/46868432/pyqtgraph-change-color-of-node-and-its-edges-on-click
'''

# def show_info(event):
#    self.info_window.show()

# self.info_btn = QPushButton('info', self.main_window)
# self.info_btn.clicked.connect(show_info)
# self.Add_Sidebar_Element(self.info_btn)
'''
self.gaba=None
def click2(event):
    if self.gaba is not None:
        print('a')
        self.network.NeuronGroups[0].afferent_synapses['GABA'] += self.gaba
        self.gaba=None
    else:
        print('b')
        self.gaba=self.network.NeuronGroups[0].afferent_synapses['GABA']
        self.network.NeuronGroups[0].afferent_synapses['GABA']=[x for x in self.network.NeuronGroups[0].afferent_synapses['GABA'] if x not in self.gaba]
self.btn2 = QPushButton('inhibition on/off', self.main_window)
self.btn2.clicked.connect(click2)
self.Add_Sidebar_Element(self.btn2)
'''

# canvas = pg.GraphicsLayoutWidget()
# canvas.setBackground((255, 255, 255))
# self.Add_Sidebar_Element(canvas)
# self.plot_main = canvas.addPlot(row=0, col=0)
# self.plot_main.hideAxis('left')
# self.plot_main.hideAxis('bottom')
# self.main_item = pg.ImageItem(np.random.rand(291, 291, 3))
# self.plot_main.addItem(self.main_item)

# p.addItem(pg.TextItem(text=, color=(0, 255, 0), anchor=(0, 0)))  # , html='<div style="text-align: center">'


# for i,c in enumerate():
#    p.addItem(pg.TextItem(text=c,color=(0,255,0),anchor=(1, i/2)))#, html='<div style="text-align: center">'

# self.graph.show()
# self.Add_Sidebar_Element(self.graph)
# self.inp_text_label.setText('test')

# self.network.NeuronGroups = [self.network.NeuronGroups[0]]
# self.network.SynapseGroups = [self.network.SynapseGroups[0]]


# self.network.simulate_iterations(1000, 100, measure_block_time=True)

# self.ng_width = self.network[self.group_name].width
# self.ng_height = self.network[self.group_name].height

# self.inh_ng_width = self.network[self.inh_group_name].width
# self.inh_ng_height = self.network[self.inh_group_name].height