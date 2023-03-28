import hashlib
import os
import time
import numpy as np
from PymoNNto.Exploration.StorageManager.StorageManager import *
from PymoNNto.Exploration.UI_Base import *
from PymoNNto.Exploration.Network_UI.Basic_Tabs.Helper.syntax import *


class Behavior_Parser_Object:
    md5_hash=''
    code=''
    name=''
    tags=None
    file=''
    base_class=''
    #time.ctime() for string conversion
    last_modification_time = None
    creation_time = None

    same_name=None
    same_tag=None
    base_or_derivative=None
    duplicates=None

    def __str__(self):
        return self.name+'('+self.md5_hash+')'

    def __repr__(self):
        return self.__str__()


def get_behaviors(file, base_classes=['Behavior']):

    result = []

    f = open(file, 'r')
    lines = f.readlines()

    class_found=False
    for line in lines:
        base_class_found=''
        if 'class' in line:
            for base in base_classes:
                if '('+base+')' in line:
                    base_class_found=base

        if base_class_found!='':
            class_found = True
            result.append([base_class_found])
        elif len(line)>0 and ord(line[0]) not in [10, 32]: #space or tab
                class_found = False

        if class_found:
            #if line.replace(chr(10),'').replace(chr(32),'')!=''): #do not add empty lines
            result[-1].append(line)#.replace('\n','')

    bpo_results=[]

    #if len(result)>0:
    #    print('')

    for r in result:

        bpo = Behavior_Parser_Object()

        bpo.file = file

        bpo.base_class = r.pop(0)

        name = r[0].replace('class ', '')
        name = name[0:min(name.find('('), name.find(':'))]
        bpo.name = name

        bpo.tags = []
        bpo.tags.append(name)

        for line in r:
            if 'self.add_tag(' in line and ')' in line:#self.add_tag('temporal_synapses')
                tag = line[line.index('('):line.index(')')]
                if len(tag)>=3:
                    bpo.tags.append(tag[2:-1])

        while r[-1].replace(chr(10),'').replace(chr(32),'') == '':#replace last empty lines
            r.pop(-1)
        bpo.code = ''.join(r)

        bpo.md5_hash = hashlib.md5(bpo.code.replace(chr(10),'').replace(chr(32),'').encode()).hexdigest()
        bpo.last_modification_time = os.path.getmtime(file)
        bpo.creation_time = os.path.getctime(file)

        bpo_results.append(bpo)

        #print(name)

    return bpo_results





class Behavior_UI(UI_Base):

    def __init__(self, path=get_root_folder()):#'.'
        super().__init__(title='Behavior overview')

        self.path=path

        self.hash_color_dict = {}

        file_list=[]
        for (dir_path, dir_names, file_names) in os.walk(path):
            if 'Data\\' not in dir_path:
                for f in file_names:
                    if f.endswith('.py'):
                        file_list.append(dir_path + '\\' + f)

        self.behaviors = []
        base_classes = [['Behavior']]
        while len(base_classes[-1]) > 0 and len(base_classes)<20:
            beh_temp = []
            for file_path in file_list:
                behaviors = get_behaviors(file_path, base_classes[-1])
                beh_temp+=behaviors
            base_classes.append([b.name for b in beh_temp])
            self.behaviors += beh_temp
            #print(beh_temp)

        self.sidebar.add_row()
        self.search_label = self.sidebar.add_widget(QLabel('Search:'), stretch=1)
        self.search = self.sidebar.add_widget(QLineEdit())
        self.search.setToolTip('filter filepaths, tags and behavior-names. Example: "MyBehaviorName -MyFolderName"')
        self.sidebar.set_parent_layout()

        def text_changed():
            self.update_file_list()

        self.search.textChanged.connect(text_changed)

        self.sidebar.add_widget(QLabel('Files with Behaviors:'), stretch=1)

        self.beh_list = self.sidebar.add_widget(QListWidget())

        self.sidebar.add_widget(QLabel('Versions:'),stretch=1)

        self.version_list = self.sidebar.add_widget(QListWidget(), stretch=50)



        self.behaviors=sorted(self.behaviors, key=lambda x: x.last_modification_time, reverse=True)

        print(len(self.behaviors))

        for b in self.behaviors:
            b.same_name=[b]
            b.same_tag=[]
            b.base_or_derivative=[]
            b.duplicates=[]
            for b2 in self.behaviors:
                if b is not b2:
                    if b.name==b2.name:
                        b.same_name.append(b2)
                    for t in b.tags:
                        if t in b2.tags and b2 not in b.same_tag:
                            b.same_tag.append(b2)
                    if b.base_class == b2.name or b.name == b2.base_class:
                        b.base_or_derivative.append(b2)
                    if b.md5_hash==b2.md5_hash:
                        b.duplicates.append(b2)

        self.update_file_list()

        self.add_code_tab()
        self.add_code_tab()
        self.add_code_tab()
        self.add_code_tab()

        def on_cb_click(event):
            self.version_list.clear()

            item=self.beh_list.currentItem()
            if item is not None:
                if hasattr(item, 'bpo'):
                    bpo = item.bpo
                    self.update_code_tab(bpo.code, bpo.file, bpo.last_modification_time)

                    self.version_list.addItem('same name:')

                    for b in bpo.same_name:
                        self.add_version_list_item(b)

                    self.version_list.addItem('')
                    self.version_list.addItem('same tag:')

                    for b in bpo.same_tag:
                        if b not in bpo.same_name:
                            self.add_version_list_item(b)

                    self.version_list.addItem('')
                    self.version_list.addItem('base or derivative:')

                    for b in bpo.base_or_derivative:
                        self.add_version_list_item(b)

                else:
                    file=item.text()
                    f = open(file, 'r')
                    code = f.read()
                    self.update_code_tab(code, file, os.path.getmtime(file))

        self.beh_list.currentItemChanged.connect(on_cb_click)

        def on_version_click(event):
            item=self.version_list.currentItem()
            if hasattr(item, 'bpo'):
                bpo=item.bpo
                self.update_code_tab(bpo.code, bpo.file, bpo.last_modification_time)

        self.version_list.currentItemChanged.connect(on_version_click)

    def add_code_tab(self):
        self.add_tab('Code', stretch=1)

        file_label = self.tab.add_widget(QLabel(''))
        self.tab.add_row()
        code_field = self.tab.add_widget(QPlainTextEdit())

        #self.btn = self.tab.add_widget(QPushButton('copy tab'), stretch=1)
        #def on_btn_click():
        #    self.add_code_tab()
        #self.btn.clicked.connect(on_btn_click)

        def on_txt_click(event):
            self.file_label=file_label
            self.code_field=code_field


        code_field.mouseReleaseEvent=on_txt_click

        code_field.highlight = PythonHighlighter(code_field.document(), ['neurons', 'synapses', 'network'])
        font = QFont()
        font.setPointSize(9)
        code_field.setFont(font)
        code_field.setStyleSheet("QPlainTextEdit { background-color: rgb(43, 43, 43); }")

        if not hasattr(self, 'file_label'):
            self.file_label=file_label
            self.code_field=code_field

    def searched(self, b):
        search_txt = self.search.text().split(' ')

        search_str_list = [stxt for stxt in search_txt if len(stxt)>0 and stxt[0]!='-']
        negative_search_str_list = [stxt[1:] for stxt in search_txt if len(stxt)>1 and stxt[0]=='-']

        search_found = True

        for negative_search_str in negative_search_str_list:
            if negative_search_str in b.name or negative_search_str in b.base_class or negative_search_str in b.file:
                search_found = False

        for search_str in search_str_list:
            if not (search_str in b.name or search_str in b.base_class or search_str in b.file):
                search_found = False

        return search_found

    def update_file_list(self):
        self.beh_list.clear()

        last_file = ''

        counter = 0

        for b in self.behaviors:

            if self.searched(b):

                counter += 1

                if last_file != b.file:
                    item=QListWidgetItem(b.file.replace(self.path,'.'))
                    item.setBackground(QColor(200,200,200))
                    self.beh_list.addItem(item)

                last_file = b.file

                count_info=''+str(len(b.same_name))+'|'+str(len(b.same_tag)-len(b.same_name)+1)+'|'+str(len(b.base_or_derivative))+''

                duplicates=''
                if len(b.duplicates)>0:
                    duplicates+='!'

                item=QListWidgetItem('          '+count_info+'    '+b.name+'    '+duplicates)
                item.bpo=b
                self.beh_list.addItem(item)

        self.search_label.setText('Search ('+str(counter)+'):')

    def update_code_tab(self, code, file, m_time):
        self.code_field.setPlainText(code)
        self.file_label.setText(file.replace(self.path,'.') + '    ' + time.ctime(m_time))

    def add_version_list_item(self, b):
        temp = '                   '
        if not self.searched(b):
            temp = '     [hidden]'

        new_item = QListWidgetItem(temp+'    '+b.name)  # + ' '+ b.md5_hash
        #if not self.searched(b):
        #    font=new_item.font()
        #    font.setStrikeOut(True)
        #    new_item.setFont(font)
        new_item.bpo = b
        if b.md5_hash not in self.hash_color_dict:
            self.hash_color_dict[b.md5_hash] = QColor(np.random.randint(50, 255),
                                                      np.random.randint(50, 255),
                                                      np.random.randint(50, 255))
        new_item.setBackground(self.hash_color_dict[b.md5_hash])
        self.version_list.addItem(new_item)


########################################################### Exception handling


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

sys.excepthook = except_hook

if __name__ == '__main__':
    Behavior_UI().show()


