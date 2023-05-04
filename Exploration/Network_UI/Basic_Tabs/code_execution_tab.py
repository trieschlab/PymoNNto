from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Visualization_Helper import *
import os
from io import StringIO
from contextlib import redirect_stdout

from PymoNNto.Exploration.Network_UI.Basic_Tabs.Helper.syntax import *

class code_execution_tab(TabBase):

    sample_code1='''import matplotlib.pyplot as plt

synapse_tag='GLU'
synapse_var='W'

combined = get_combined_syn_mats(n.synapses(afferent, synapse_tag), None,synapse_var)

for mat in combined.values():

	plt.imshow(mat, vmin=0, vmax=0.005)#cmap='gray', 
	plt.show()
'''

    sample_code2='''num=0

for syn in n.synapses(afferent, 'GLU'):

	num+=np.sum(syn.W>0.001)

print(num)
'''

    base_code = '''###Quick Access Variables###
    
# network | net
# neuron_group | neurons | ng | n
# Network_UI | ui | UI
# storage_manager | storage | sm

###Python Code###


'''

    def initialize(self, Network_UI):
        self.Network_UI=Network_UI

        self.code_execution_tab = Network_UI.add_tab(title='Code Exec.') #Network_UI.Next_Tab()
        self.comboBox = Network_UI.tab.add_widget(QComboBox())

        #self.CB_line_edit = QLineEdit()
        #self.comboBox.setLineEdit(self.CB_line_edit)

        self.txt_py_dict={}

        self.txt_py_dict[''] = self.base_code
        self.txt_py_dict["show synapse matrices"] = self.sample_code1
        self.txt_py_dict["count synapses"] = self.sample_code2

        data_folder = get_data_folder(create_when_not_found=False)+'/scripts'

        if not os.path.exists(data_folder):
            os.mkdir(data_folder)

        for d in os.listdir(data_folder):
            try:
                if '.py' in d:
                    with open(data_folder+'/'+d) as f:
                        self.txt_py_dict[d.replace('.py','')] = f.read()
            except:
                print("error in script", d)


        for txt in self.txt_py_dict:
            self.comboBox.addItem(txt)


        def on_cb_click(event):
            txt=self.comboBox.itemText(self.comboBox.currentIndex())
            self.code_field.setPlainText(self.txt_py_dict[txt])#setText
            #self.code_field.setStyleSheet("QTextEdit { background-color: rgb(255, 255, 255); }")
            self.comboBox.setStyleSheet("background-color: rgb(255, 255, 255);")

        def on_code_changed():
            #self.code_field.setStyleSheet("QTextEdit { background-color: rgb(255, 210, 210); }")
            self.comboBox.setStyleSheet("background-color : rgb(255, 210, 210);")


        self.comboBox.currentIndexChanged.connect(on_cb_click)

        Network_UI.tab.add_row()

        #self.code_field=Network_UI.tab.add_widget(QTextEdit())
        #self.code_field.setAcceptRichText(False)
        #self.code_field.setText(self.base_code)
        #self.code_field.textChanged.connect(on_code_changed)

        net = Network_UI.network
        network = net
        n = Network_UI.selected_neuron_group()
        ng = n
        neurons = n
        neuron_group = n

        self.code_field = Network_UI.tab.add_widget(QPlainTextEdit())
        special_keywords = ['Network_UI', 'net', 'n', 'ng', 'network', 'neurons', 'neuron_group']
        self.code_field.highlight = PythonHighlighter(self.code_field.document(), special_keywords)
        #self.code_field.setAcceptRichText(False)
        self.code_field.setStyleSheet("QPlainTextEdit { background-color: rgb(43, 43, 43); }")
        self.code_field.setPlainText(self.base_code)#setText
        self.code_field.textChanged.connect(on_code_changed)

        Network_UI.tab.add_row(stretch=1)

        self.exec_btn=Network_UI.tab.add_widget(QPushButton('Execute'))

        def exec_btn_click(event):
            ui = Network_UI
            UI = ui

            sm = Network_UI.storage_manager
            storage = sm
            storage_manager = sm

            net = Network_UI.network
            network = net

            n = Network_UI.selected_neuron_group()
            ng = n
            neurons = n
            neuron_group = n

            if self.show_output_window.isChecked():
                f = StringIO()
                #try:
                with redirect_stdout(f):
                    exec(self.code_field.toPlainText())
                #except Exception:
                #        pass
                s = f.getvalue()

                layout = QVBoxLayout()
                pte = QPlainTextEdit()
                pte.setPlainText(s)
                pte.setReadOnly(True)
                layout.addWidget(pte)

                dlg = QDialog()
                dlg.setWindowTitle('code stdout (prints)')
                dlg.setLayout(layout)
                dlg.resize(600, 400)
                dlg.exec()
            else:
                exec(self.code_field.toPlainText())


            print('code block executed successfuly!')

            Network_UI.add_event('code execution')

        self.exec_btn.clicked.connect(exec_btn_click)


        self.show_output_window = Network_UI.tab.add_widget(QCheckBox('Show stdout in window'))

        self.compiled = None
        self.compiled_script_txt = ''
        self.timestep_execute_cb = Network_UI.tab.add_widget(QCheckBox('Execute every timestep'))


        self.save_btn_click = Network_UI.tab.add_widget(QPushButton('Save Script'))

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

        def save_btn_click(event):
            Network_UI.text_input_dialog("Please name your script", 'save', save, self.comboBox.itemText(self.comboBox.currentIndex()).replace('.py',''))

        self.save_btn_click.clicked.connect(save_btn_click)



    def update(self, Network_UI):

        if self.timestep_execute_cb.isChecked():
            self.show_output_window.setChecked(False)

            net = Network_UI.network
            network = net
            n = Network_UI.selected_neuron_group()
            ng = n
            neurons = n
            neuron_group = n

            code = self.code_field.toPlainText()

            if self.compiled is None or self.compiled_script_txt != code:
                self.compiled = compile(code, '<string>', 'exec')
                self.compiled_script_txt = code

            exec(self.compiled)

