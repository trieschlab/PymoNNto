from PymoNNto.Exploration.Evolution.common_UI import *
from PymoNNto.Exploration.Evolution.PlotQTObjects import *

class Overview_UI(UI_Base):

    def update_order(self):
        for i in range(self.listwidget.count()):
            item = self.listwidget.item(i)
            #print(i, item.text())
            smg=self.interactive_scatter.get_smg(item.text())
            if smg is not None:
                smg.add_virtual_multi_parameter('index', i)

    def add_item(self, dir, folder):
        found = False
        for i in range(self.listwidget.count()):
            if self.listwidget.item(i).text() == dir:
                found = True

        if not found:
            item = QListWidgetItem(dir)
            item.folder = folder
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Unchecked)
            self.listwidget.addItem(item)
            # dirs.append(dir)

    def refresh_dirs(self):
        #dirs = []
        folder = 'Plot_Project_Clones'
        for dir in os.listdir(get_epc_folder(folder)):
            if os.path.isdir(get_epc_folder(folder) + '/' + dir):
                self.add_item(dir, get_data_folder() + '/' + folder + '/' + dir + '/Data')

        folder = 'Evolution_Project_Clones'
        for dir in os.listdir(get_epc_folder(folder)):
            if os.path.isdir(get_epc_folder(folder) + '/' + dir):
                self.add_item(dir, get_data_folder() + '/' + folder + '/' + dir + '/Data')


        for dir in os.listdir(get_data_folder() + '/StorageManager/'):
            if os.path.isdir(get_data_folder() + '/StorageManager/' + dir):
                self.add_item(dir, get_data_folder())

        #self.listwidget.addItems(dirs)
        self.listwidget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def __init__(self):
        super().__init__(title='Plot Overview', create_sidebar=True)

        self.listwidget = QListWidget()

        self.add_tab(title='Plot')
        #self.Next_Tab('Plot')

        self.interactive_scatter = self.tab.add_widget(InteractiveScatter())

        self.refresh_dirs()

        def drop_event(ev):
            print(ev)
            super(QListWidget, self.listwidget).dropEvent(ev)
            self.update_order()
            self.interactive_scatter.refresh_data()

        self.update_order()

        self.listwidget.dropEvent = drop_event

        self.sidebar.add_widget(self.listwidget)

        def on_item_clicked(item):
            for i in range(self.listwidget.count()):
                item=self.listwidget.item(i)
                smg = StorageManagerGroup(item.text(), data_folder=item.folder)

                if item.checkState() == QtCore.Qt.Checked:
                    found_smg=self.interactive_scatter.get_smg(item.text())
                    if found_smg is None:
                        self.interactive_scatter.add_StorageManagerGroup(smg)
                        item.setBackground(QColor(smg.color[0],smg.color[1],smg.color[2]))
                else:
                    self.interactive_scatter.remove_StorageManagerGroup(smg)
                    item.setBackground(QColor(255,255,255))

            self.update_order()
            self.interactive_scatter.refresh_data()

        self.listwidget.itemClicked.connect(on_item_clicked)

        def on_item_doubleclicked(item):
            item = self.listwidget.itemFromIndex(item)
            smg = self.interactive_scatter.get_smg(item.text())

            if smg is not None:
                color = QColorDialog.getColor()
                print(color.red(), color.green(), color.blue())

                smg.color=(color.red(), color.green(), color.blue())
                item.setBackground(QColor(smg.color[0], smg.color[1], smg.color[2]))
                self.interactive_scatter.add_StorageManagerGroup(smg)
                self.interactive_scatter.refresh_data()

        self.listwidget.doubleClicked.connect(on_item_doubleclicked)

        btn=self.sidebar.add_widget(QPushButton('refresh'))

        def refresh_click():
            self.refresh_dirs()
            self.interactive_scatter.refresh_data()

        btn.clicked.connect(refresh_click)

        color_btn = self.sidebar.add_widget(QPushButton('color'))

        def color_click():
            self.interactive_scatter.axis_dialog('color')
            #param =
            #color_btn.setText('color: '+param)

        color_btn.clicked.connect(color_click)


########################################################### Exception handling


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

sys.excepthook = except_hook


if __name__ == '__main__':
    Overview_UI().show()
