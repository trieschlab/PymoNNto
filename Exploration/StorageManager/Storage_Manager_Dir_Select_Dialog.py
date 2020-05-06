from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

import sys
import os

from Exploration.StorageManager.StorageManager import *


class SM_D_S_Dialog(QDialog):

    def __init__(self, parent=None):
        super(SM_D_S_Dialog, self).__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)


        self.listWidget=QListWidget()

        # Trying to set up the listWidgetView
        #self.listWidget.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.EditKeyPressed)
        self.listWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        #self.listWidget.setViewMode(QtGui.QListView.ListMode)

        # Load the layers in the listWidget


        main_dir = get_data_folder() + '/StorageManager/'

        #os.path.join(main_dir, o)

        layers = [o for o in os.listdir(main_dir) if os.path.isdir(os.path.join(main_dir, o))]

        # Populate the listWidget with all the polygon layer present in the TOC
        self.listWidget.addItems(layers)

        layout.addWidget(self.listWidget)
        # put the selected layers in a list
        #selectedLayers = self.listWidget.selectedItems()



        # Add button signal to greetings slot
        self.button = QPushButton("Ok")
        self.button.clicked.connect(self.greetings)
        layout.addWidget(self.button)

        self.list=[]

        self.width = 800
        self.height = 600
        self.setWindowTitle('Select Folders')
        self.setGeometry(10, 40, self.width, self.height)

    def cancel(self):
        self.close()

    def greetings(self):
        self.list = [selected.text() for selected in self.listWidget.selectedItems()]
        self.accept()

    #def exec_(self):
    #    if QDialog.exec_(self) == QDialog.Accepted:
    #        return self.list
    #    else:
    #        return []

def Storage_Manager_Dir_Select_Dialog():
    app = QApplication(sys.argv)
    form = SM_D_S_Dialog()
    form.show()
    app.exec_()
    return form.list

if __name__ == '__main__':
    print(Storage_Manager_Dir_Select_Dialog())