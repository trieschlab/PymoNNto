import sys
from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QApplication, QDialog, QPlainTextEdit, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter

class TxtHighlighter(QSyntaxHighlighter):

    def __init__(self, document, coloration_list={}, base_char_color=QColor(0, 0, 0)):#{['a'],QColor()} #, words=[], sentences=[]
        QSyntaxHighlighter.__init__(self, document)
        self.base_char_color=base_char_color
        self.rules = []

        for color, string_list in coloration_list:
            self.rules += [(QRegExp(r'%s' % s), color) for s in string_list]


    def highlightBlock(self, text):
        self.setFormat(0, len(text), self.base_char_color)
        for expression, color in self.rules:
            index = expression.indexIn(text, 0)
            while index >= 0:
                index = expression.pos(0)
                length = len(expression.cap(0))
                _format = QTextCharFormat()
                _format.setForeground(color)#_format.setBackground(color)
                self.setFormat(index, length, _format)
                index = expression.indexIn(text, index + length)
        self.setCurrentBlockState(0)