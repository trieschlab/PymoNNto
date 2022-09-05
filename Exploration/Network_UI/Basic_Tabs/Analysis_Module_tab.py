from PymoNNto.Exploration.Network_UI.Network_UI import *
from PymoNNto.Exploration.Network_UI.TabBase import *
from PymoNNto.Exploration.Visualization.Analysis_Plots import *

class Analysis_Module_tab(TabBase):

    def __init__(self, title='Modules'):
        super().__init__(title)

    def add_execute_btn(self, Network_UI, module):

        Network_UI.add_event('analytics mod. exec.')

        btn = Network_UI.tab.add_widget(QPushButton('execute'), stretch=2)

        caption = Network_UI.tab.add_widget(QLabel(str(module._get_base_name_())), stretch=4)
        spacing_blocks = 10

        argument_edits={}

        for attr_key in module.execution_arguments:
            attr = module.execution_arguments[attr_key]
            Network_UI.tab.add_widget(QLabel(attr_key), stretch=2)
            edit=Network_UI.tab.add_widget(QLineEdit(str(attr)), stretch=1)
            argument_edits[attr_key]=edit
            spacing_blocks -= 3

        if spacing_blocks > 0:
            Network_UI.tab.add_widget(QLabel(''), stretch=spacing_blocks)

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
            cb = Network_UI.tab.add_widget(Analytics_Results_Select_ComboBox(module), stretch=2)

            def remove_selected_clicked(event):
                key = cb.currentText()
                module.remove_result(key)

            btn = Network_UI.tab.add_widget(QPushButton('remove result'), stretch=1)
            btn.clicked.connect(remove_selected_clicked)
        else:
            Network_UI.tab.add_widget(QLabel(''), stretch=3)

    def update_progress(self, percentage):
        QApplication.instance().processEvents()
        self.progressbar.setValue(int(percentage))

    def initialize(self, Network_UI):
        self.a_module_tab = Network_UI.add_tab(title=self.title)

        for obj in [Network_UI.network]+Network_UI.network.NeuronGroups:
            caption = Network_UI.tab.add_widget(QLabel(obj.tags[0]))
            font = QFont('SansSerif', 16)
            font.setUnderline(True)
            caption.setFont(font)
            Network_UI.tab.add_row()

            for analysis_module in obj.analysis_modules:

                self.add_execute_btn(Network_UI, analysis_module)

                self.add_result_remove_menu(Network_UI, analysis_module)

                Network_UI.tab.add_row()

        self.progressbar = Network_UI.tab.add_widget(QProgressBar())
