from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *



class code_execution_tab(TabBase):

    sample_code1='''import matplotlib.pyplot as plt

synapse_tag='GLU'
synapse_var='W'

combined = Network_UI.get_combined_syn_mats(n.afferent_synapses[synapse_tag], None,synapse_var)

for mat in combined.values():

	plt.imshow(mat, vmin=0, vmax=0.005)#cmap='gray', 
	plt.show()
'''

    sample_code2='''num=0

for syn in n.afferent_synapses['GLU']:

	num+=np.sum(syn.W>0.001)

print(num)
'''

    def initialize(self, Network_UI):
        self.code_execution_tab = Network_UI.Next_Tab('code exec')
        comboBox =Network_UI.Add_element(QComboBox())
        comboBox.addItem("")
        comboBox.addItem("show synapse matrices")
        comboBox.addItem("count synapses")

        def abc(event):
            txt=comboBox.itemText(comboBox.currentIndex())

            if txt=='':
                self.code_field.setText('')

            if txt=='show synapse matrices':
                self.code_field.setText(self.sample_code1)

            if txt=='count synapses':
                self.code_field.setText(self.sample_code2)

        comboBox.currentIndexChanged.connect(abc)

        Network_UI.Next_H_Block()

        self.code_field=Network_UI.Add_element(QTextEdit())

        Network_UI.Next_H_Block(stretch=0.1)

        self.exec_btn=Network_UI.Add_element(QPushButton('Execute'))

        def exec_btn_click(event):
            net = Network_UI.network
            network = net
            n = Network_UI.network[Network_UI.neuron_select_group, 0]
            ng = n
            neurons = n
            neuron_group = n

            exec(self.code_field.toPlainText())

        self.exec_btn.clicked.connect(exec_btn_click)

        #self.code_name_te = Network_UI.Add_element(QTextEdit('code name'))
        #self.save_btn = Network_UI.Add_element(QPushButton('save'))
