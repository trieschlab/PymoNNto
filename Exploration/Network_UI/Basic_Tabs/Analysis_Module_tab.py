from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Analysis_Plots import *

class Analysis_Module_tab(TabBase):

    def __init__(self, title='Modules'):
        super().__init__(title)

    def add_execute_btn(self, Network_UI, module):

        btn = Network_UI.Add_element(QPushButton('execute'), stretch=2)

        caption = Network_UI.Add_element(QLabel(str(module._get_base_name_())), stretch=4)
        spacing_blocks = 10

        argument_edits={}

        for attr_key in module.execution_arguments:
            attr = module.execution_arguments[attr_key]
            Network_UI.Add_element(QLabel(attr_key), stretch=2)
            edit=Network_UI.Add_element(QLineEdit(str(attr)), stretch=1)
            argument_edits[attr_key]=edit
            spacing_blocks -= 3

        if spacing_blocks > 0:
            Network_UI.Add_element(QLabel(''), stretch=spacing_blocks)

        def execute_clicked(event):
            Network_UI.pause = True
            module.add_progress_update_function(self.update_progress)
            arguments = {}
            for key in argument_edits:
                try:
                    arguments[key] = eval(argument_edits[key].text())
                except:
                    arguments[key] = argument_edits[key].text()

            module(**arguments)
            module.add_progress_update_function(None)


        btn.setEnabled(module.is_executable())
        btn.clicked.connect(execute_clicked)

    def add_result_remove_menu(self, Network_UI, module):

        if module.is_executable():
            cb = Network_UI.Add_element(Analytics_Results_Select_ComboBox(module), stretch=2)

            def remove_selected_clicked(event):
                key = cb.currentText()
                module.remove_result(key)

            btn = Network_UI.Add_element(QPushButton('remove result'), stretch=1)
            btn.clicked.connect(remove_selected_clicked)
        else:
            Network_UI.Add_element(QLabel(''), stretch=3)

    def update_progress(self, percentage):
        QApplication.instance().processEvents()
        self.progressbar.setValue(percentage)

    def initialize(self, Network_UI):
        self.a_module_tab = Network_UI.Next_Tab(self.title)

        print(Network_UI.network.NeuronGroups[0].analysis_modules)

        for obj in [Network_UI.network]+Network_UI.network.NeuronGroups:#Network_UI.network.all_objects()
            caption = Network_UI.Add_element(QLabel(obj.tags[0]))
            font = QFont('SansSerif', 16)
            font.setUnderline(True)
            caption.setFont(font)
            Network_UI.Next_H_Block()

            for analysis_module in obj.analysis_modules:

                self.add_execute_btn(Network_UI, analysis_module)

                self.add_result_remove_menu(Network_UI, analysis_module)

                Network_UI.Next_H_Block()

        self.progressbar = Network_UI.Add_element(QProgressBar())
