from PymoNNto import *
import sys
import matplotlib.pyplot as plt
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import numpy as np

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt
from PIL import Image

#from X_Experimental.Functions import *
#from Testing.SORN.SORN_Helper import *


class TabBase:

    def __init__(self, title='Title'):
        self.title = title

    def add_recorder_variables(self, neuron_group, Network_UI):
        return

    def initialize(self, Network_UI):
        return

    def update(self, Network_UI):
        return

    def on_selected_neuron_changed(self, Network_UI):
        return

    def interpret_recording_variable(self, var):
        chars = '.,()[]+-*/%'
        found = False
        for c in chars:
            if c in var:
                found = True

        if not found:
            var = 'n.' + var

        return var
