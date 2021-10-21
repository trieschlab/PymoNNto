from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *
import os


class code_execution_tab(TabBase):

    sample_code1='''import matplotlib.pyplot as plt

synapse_tag='GLU'
synapse_var='W'

combined = get_combined_syn_mats(n.afferent_synapses[synapse_tag], None,synapse_var)

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
        self.Network_UI=Network_UI

        #Network_UI.Next_H_Block()

        #self.timed_execution_list_view = Network_UI.Add_element(QListView(), sidebar=True)
        #self.timed_execution_model=QtGui.QStandardItemModel()
        #self.timed_execution_list_view.setModel(self.timed_execution_model)

        #item = QtGui.QStandardItem("TEST")  # str(execution_time)+' | '+base_name)
        #item.setCheckable(True)
        #check = QtCore.Qt.Checked  # if checked else QtCore.Qt.Unchecked
        #item.setCheckState(check)
        #self.timed_execution_model.appendRow(item)

        self.code_execution_tab = Network_UI.Next_Tab('Code Exec.')
        self.comboBox = Network_UI.Add_element(QComboBox())

        self.txt_py_dict={}

        self.txt_py_dict[''] = ''
        self.txt_py_dict["show synapse matrices"] = self.sample_code1
        self.txt_py_dict["count synapses"] = self.sample_code2

        try:
            data_folder = get_data_folder(create_when_not_found=False)+'/scripts'

            if not os.path.exists(data_folder):
                os.mkdir(data_folder)

            for d in os.listdir(data_folder):
                if '.py' in d:
                    with open(data_folder+'/'+d) as f:
                        self.txt_py_dict[d.replace('.py','')] = f.read()

                    self.add_timed_script(d)
        except:
            pass

        for txt in self.txt_py_dict:
            self.comboBox.addItem(txt)


        def on_cb_click(event):
            txt=self.comboBox.itemText(self.comboBox.currentIndex())
            self.code_field.setText(self.txt_py_dict[txt])
            self.code_field.setStyleSheet("QTextEdit { background-color: rgb(255, 255, 255); }")

        def on_code_changed():
            self.code_field.setStyleSheet("QTextEdit { background-color: rgb(255, 210, 210); }")

        self.comboBox.currentIndexChanged.connect(on_cb_click)

        Network_UI.Next_H_Block()

        self.code_field=Network_UI.Add_element(QTextEdit())

        self.code_field.setAcceptRichText(False)

        self.code_field.textChanged.connect(on_code_changed)

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

            print('code block executed successfuly!')

        self.exec_btn.clicked.connect(exec_btn_click)

        self.save_btn_click = Network_UI.Add_element(QPushButton('Save Script'))

        def save(input_txt):
            data_folder = get_data_folder(create_when_not_found=False)+'/scripts'
            name=data_folder + '/'+input_txt+'.py'
            with open(name, "w") as f:
                f.write(self.code_field.toPlainText())

            n=input_txt
            found = n in self.txt_py_dict

            self.txt_py_dict[n] = self.code_field.toPlainText()

            if not found:
                self.comboBox.addItem(n)
                self.comboBox.setCurrentIndex(len(self.txt_py_dict)-1)

            self.code_field.setStyleSheet("QTextEdit { background-color: rgb(255, 255, 255); }")

            #self.add_timed_script(name)

        def save_btn_click(event):
            Network_UI.text_input_dialog("Please name your script", 'save', save, self.comboBox.itemText(self.comboBox.currentIndex()).replace('.py',''))

        self.save_btn_click.clicked.connect(save_btn_click)

        self.compiled = None
        self.compiled_script_txt = ''
        self.timestep_execute_cb = Network_UI.Add_element(QCheckBox('Execute every timestep'))

    def update(self, Network_UI):

        if self.timestep_execute_cb.isChecked():

            net = Network_UI.network
            network = net
            n = Network_UI.network[Network_UI.neuron_select_group, 0]
            ng = n
            neurons = n
            neuron_group = n

            code = self.code_field.toPlainText()

            if self.compiled is None or self.compiled_script_txt != code:
                self.compiled = compile(code, '<string>', 'exec')
                self.compiled_script_txt = code

            exec(self.compiled)





