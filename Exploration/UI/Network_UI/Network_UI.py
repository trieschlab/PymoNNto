from Exploration.UI.UI_Base import *

#import pyqtgraph as pg
#from X_Experimental.Functions import *
#from Exploration.Visualization.Analysis_Plots import *
#from Testing.SORN.SORN_Helper import *

from Exploration.UI.Network_UI.Basic_Tabs.sidebar_activity_module import *
from Exploration.UI.Network_UI.Tabs.sidebar_image_module import *
from Exploration.UI.Network_UI.Tabs.sidebar_grammar_module import *
from Exploration.UI.Network_UI.Basic_Tabs.sidebar_fast_forward_module import *
from Exploration.UI.Network_UI.Basic_Tabs.sidebar_save_load_module import *
from Exploration.UI.Network_UI.Basic_Tabs.multi_group_plot_tab import *
from Exploration.UI.Network_UI.Tabs.chain_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.hist_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.info_tabs import *
from Exploration.UI.Network_UI.Basic_Tabs.single_group_plot_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.scatter_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.stability_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.weight_tab import *
from Exploration.UI.Network_UI.Tabs.reconstruction_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.fourier_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.partition_tab import *
from Exploration.UI.Network_UI.Tabs.sidebar_music_module import *
from Exploration.UI.Network_UI.Tabs.sidebar_drumbeat_module import *
from Exploration.UI.Network_UI.Basic_Tabs.spiketrain_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.afferent_syn_attr_plot_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.individual_weight_tab import *
from Exploration.UI.Network_UI.Tabs.sun_gravity_plot_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.stdp_buffer_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.criticality_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.buffer_tab import *
from Exploration.UI.Network_UI.Basic_Tabs.PCA_tab import *

default_modules = [
    UI_sidebar_activity_module(1),
    multi_group_plot_tab(['output', 'TH', 'weight_norm_factor', 'nox', 'refractory_counter']),
    spiketrain_tab(parameter='output'),
    weight_tab(weight_attrs=['W', 'W_temp', 'W_stable']),
    stdp_buffer_tab(),
    partition_tab(),
    PCA_tab(),
    sun_gravity_plot_tab(),
    afferent_syn_attr_plot_tab(syn_vars=['slow_add', 'fast_add']),
    sidebar_image_module(),
    sidebar_grammar_module(),
    sidebar_music_module(),
    sidebar_drumbeat_module(),
    #chain_tab(),
    buffer_tab(),
    individual_weight_tab(),
    reconstruction_tab(),
    hist_tab(),
    criticality_tab(),
    single_group_plot_tab({'activity':(0, 0, 0), 'excitation':(0, 0, 255), 'inhibition':(255, 0, 0), 'input_act':(255, 0, 255), 'TH':(0, 255, 0)}),
    stability_tab(parameter='output'),
    scatter_tab(x_var='excitation', y_var='inhibition'),
    fourier_tab(parameter='output'),
    info_tab(),
    sidebar_fast_forward_module(),
    sidebar_save_load_module()

]

class Network_UI(UI_Base):

    def __init__(self, network, modules=default_modules, label='SORN UI', group_tags=[], transmitters=[], storage_manager=None, group_display_count=None, reduced_layout=False):
        #network.simulate_iteration()
        self.recording = False
        if self.recording:
            label += ' rec.'

        for ng in network.NeuronGroups:
            if not hasattr(ng, 'color'):
                ng.color = (0, 0, 255, 255)

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
        #    network.add_behaviours_to_neuron_group({10000: NeuronRecorder(['np.mean(n.output)',
        #                           'np.mean(n.TH)',
        #                           'n.TH',
        #                           'n.excitation',
        #                           'n.inhibition',
        #                           'n.input_act',
        #                           'n.refractory_counter',
        #                           '[np.sum(s.slow_add) for s in n.afferent_synapses.get("All")]',
        #                           '[np.sum(s.fast_add) for s in n.afferent_synapses.get("All")]'], tag='UI_rec')}, group)

        super().__init__(network, label=label)

        self.main_window.keyPressEvent = self.keyPressEvent

        self.group_display_count=group_display_count

        #self.exc_group_name = exc_group_name
        #self.inh_group_name = inh_group_name
        self.group_tags=group_tags
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
        self.group_sliders=[]
        self.neuron_select_color=(0,255,0,255)

        self.modules = modules

        for module in self.modules:
            print('Initialize:', module)
            module.initialize(self)

        for group_tag in group_tags:
            for group in network[group_tag]:

                group._rec_dict={}

                #rec = NeuronRecorder([], tag='UI_rec')
                #network.add_behaviours_to_neuron_group({10000: rec}, group)

                for module in self.modules:
                    module.add_recorder_variables(group, self)

        self.init_recoders()

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.on_timer)
        timer.start(40)

    def add_recording_variable(self, group, var, timesteps):

        old_ts=0
        if var in group._rec_dict:
            old_ts=group._rec_dict[var]

        group._rec_dict[var] = max(timesteps,old_ts)
        #recorder.add_varable('n.output')

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
                    rec = NeuronRecorder(rec_time_dict[rec_length]+['n.iteration'], tag='UI_rec,rec_'+str(rec_length), max_length=rec_length)
                    self.network.add_behaviours_to_neuron_group({10000+rec_length: rec}, group)

    #def rec(self, neuron_group, rec_length=-1):
    #    return neuron_group[self.rec_tag(rec_length),0]

    #def rec_tag(self, rec_length=-1):
    #    if rec_length==-1:
    #        rec_length = self.default_rec_recording_length
    #    return 'rec_'+str(rec_length)

    def static_update_func(self, event=None):
        if self.pause:
            self.update_without_state_change=True


    def record_image(self, img, key):
        if self.storage_manager is not None and self.recording:
            image = upscale(img*255, 10)
            self.storage_manager.save_frame(image, key)

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

    def get_combined_syn_mats(self, synapses, neuron_id=None, attr='W'):
        results = {}
        shapes = {}
        for s in synapses:
            base_src = s.src.group_without_subGroup()
            base_dst = s.dst.group_without_subGroup()
            key = ','.join(s.tags)#'{}x{}'.format(id(base_dst), id(base_src))
            if not key in results:
                results[key] = np.zeros((base_dst.size, base_src.size))
                shapes[key] = (base_src.height, base_src.width)
            if hasattr(s, attr):
                if base_src == s.src and base_dst == s.dst:
                    results[key] += getattr(s,attr).copy()
                else:
                    mat_mask = s.dst.mask[:, None]*s.src.mask[None, :]
                    results[key][mat_mask] += getattr(s,attr).flatten()

        if neuron_id is not None:
            for key in results:
                results[key] = results[key][neuron_id].reshape(shapes[key])

        return results


    def on_timer(self):

        if not self.pause or self.step or self.update_without_state_change:
            self.step = False
            if not self.update_without_state_change:
                for i in range(1):
                    self.network.simulate_iteration()

            self.it = self.network.iteration

            for module in self.modules:
                module.update(self)

            #for rec in self.network['UI_rec']:
            #    rec.cut_length(self.default_recorder_length)

            self.update_without_state_change = False


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_W:
            indx = self.tabs.currentIndex()
            if indx >= 0:
                widget=self.tabs.currentWidget()
                self.tabs.removeTab(indx)
                widget.setParent(None)
                widget.show()







def get_color(type_index, layer):
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



from io import StringIO
import traceback
from PyQt5 import QtCore
from PyQt5.QtWidgets import *

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
    tbinfofile.seek(0)
    tbinfo = tbinfofile.read()
    errmsg = '%s: \n%s' % (str(excType), str(excValue))
    sections = [separator, separator, errmsg, separator, tbinfo]
    msg = '\n'.join(sections)
    #try:
    #    f = open(logFile, "w")
    #    f.write(msg)
    #    f.write(versionInfo)
    #    f.close()
    #except IOError:
    #    pass
    errorbox = QMessageBox()
    errorbox.setText(str(notice) + str(msg) + str(versionInfo))
    errorbox.exec_()

sys.excepthook = excepthook




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