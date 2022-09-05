from configparser import ConfigParser
import numpy as np
import zipfile
import time
from subprocess import call
import os
import pickle
import imageio


#import matplotlib.pylab as plt
#storage_manager_folder = '../../Data/StorageManager/'

def create_folder_if_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_root_folder(create_when_not_found=True):
    path='./'
    while os.path.isdir(path):
        if os.path.isdir(path+'Data/'):
            return os.path.abspath(path).replace('\\', '/').replace('//', '/')
        path='../'+path
    return './'

def get_data_folder(create_when_not_found=True):
    path='./'
    while os.path.isdir(path):
        if os.path.isdir(path+'Data/'):
            return os.path.abspath(path+'Data/').replace('\\', '/').replace('//', '/')
        path='../'+path

    if not os.path.exists('./Data'):
        try:
            os.mkdir('./Data')
        except:
            print('was not able to create Data folder')
    return './Data'
    #raise Exception('No "Data" folder found above current working directory! Please create dirctory: ".../Project/Data".')

def zipDir(dirPath, zipPath, filter=[]):
    zipf = zipfile.ZipFile(zipPath, mode='w')
    lenDirPath = len(dirPath)
    for root, _, files in os.walk(dirPath):
        for file in files:
            filter_file=False
            for f in filter:
                if f in root or f in file+'\\':
                    filter_file = True
            if not filter_file:
                filePath = os.path.join(root, file)
                print(filePath)
                zipf.write(filePath , filePath[lenDirPath :] )
    zipf.close()

#searches for "Data" folder in project by default
#default folder: .../Data/StorageManager/main_folder_name/folder_name/
#example:
#StorageManager('Test')
#Run1: .../Data/StorageManager/Test/Test1/
#Run2: .../Data/StorageManager/Test/Test2/
#Run3: .../Data/StorageManager/Test/Test3/
#...
#parameters are saved in "config.ini"
class StorageManager:

    def get_path(self):
        return self.absolute_path

    def __init__(self, main_folder_name, folder_name=None, random_nr=False, print_msg=True, add_new_when_exists=True, data_folder=get_data_folder(), use_evolution_path=True):

        if use_evolution_path:
            import PymoNNto.Exploration.Evolution.Interface_Functions as evo_func
            #if evo_func.get_gene('evo_name', None) is not None: # and evo_func.get_gene('gen', None) is not None and evo_func.get_gene('id', None) is not None
            if 'evo_name' in evo_func.get_default_genome() and evo_func.get_default_genome()['evo_name'] is not None:
                main_folder_name = evo_func.get_gene('evo_name', None)
                folder_name = evo_func.get_gene_file(evo_func.evolution_genome)
                #add_new_when_exists = True#??? Test
                random_nr=False

        if type(main_folder_name) is dict:
            main_folder_name = self.dict_to_folder_name(main_folder_name)

        storage_manager_folder = data_folder +'/StorageManager/'

        if not os.path.exists(storage_manager_folder):
            try:
                os.mkdir(storage_manager_folder)
            except:
                print('SM folder already exists...')

        if folder_name is None:
            folder_name = main_folder_name

        self.folder_name = folder_name
        if type(random_nr) == bool and random_nr:
            self.folder_name += str(int(np.random.rand() * 10000))
        if type(random_nr) == int:
            self.folder_name += str(random_nr)

        if not os.path.exists(storage_manager_folder+main_folder_name+'/'):
            try:
                os.mkdir(storage_manager_folder+main_folder_name+'/')
            except:
                print("main folder already exists")

        if add_new_when_exists:
            if os.path.isdir(storage_manager_folder+main_folder_name+'/'+self.folder_name+'/'):
                count = 0
                while os.path.isdir(storage_manager_folder+main_folder_name+'/'+self.folder_name+'_{}/'.format(count)):
                    count += 1
                self.folder_name += '_{}'.format(count)

        #self.foldername += '_'+count#int(np.random.rand() * 10*add_randum_number)

        self.absolute_path = storage_manager_folder+main_folder_name+'/'+self.folder_name+'/'

        new = False
        if not os.path.exists(self.absolute_path):
            try:
                os.mkdir(self.absolute_path)
            except:
                print('target folder already exits')
            new = True

        self.config_file_name = 'config.ini'
        self.config=None

        self.frame_counter = {}

        if new:
            if print_msg:
                print(self.absolute_path)
            self.save_param('time', time.time())

    def dict_to_folder_name(self, dict):
        result = ''
        for k, v in dict.items():
            if result != '':
                result += '_'
            result += str(k).replace(' ', '')+'='+str(v).replace(' ', '')
        return result

    def init_config(self):
        if self.config is None:
            self.config = ConfigParser()
            self.config.read(self.absolute_path + self.config_file_name)

    def get_all_params(self, section='Parameters'):
        self.init_config()
        return dict(self.config.items(section)).keys()

    def save_recorder(self, tag, recorder, keys=[]):
        if type(keys) is str:
            keys=[keys]
        if len(keys) == 0:
            keys=recorder.variables.keys()
        for key in keys:
            self.save_np(tag+key, np.array(recorder.variables[key]))


    def save_str(self, key, string):
        text_file = open(self.absolute_path + key + '.txt', "w")
        text_file.write(string)
        text_file.close()


    def load_str(self, key):
        text_file = open(self.absolute_path + key + '.txt', "r")
        string = text_file.read()
        text_file.close()
        return string


    def save_np(self, key, obj):
        np.save(self.absolute_path + key + '.npy', arr=obj)

    def save_obj(self, key, obj):
        pickle.dump(obj, open(self.absolute_path + key + '.obj', 'wb'))

    def load_obj(self, key):
        return pickle.load(open(self.absolute_path + key + '.obj', 'rb'))

    def has_obj(self, key):
        return os.path.isfile(self.absolute_path + key + '.obj')

    def save_param_dict(self, d, section='Parameters'):
        for key in d:
            self.save_param(key, d[key], section)

    def save_param(self, key, value, section='Parameters'):
        self.init_config()
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, str(value).replace('%','percent'))
        with open(self.absolute_path+self.config_file_name, 'w') as configfile:
            self.config.write(configfile)

    def get_next_frame_name(self, key):
        if not key in self.frame_counter:
            self.frame_counter[key] = 0
        self.frame_counter[key] += 1
        return self.absolute_path+key+'{}.png'.format(self.frame_counter[key]-1)


    def save_frame(self, image, key):
        #plt.imshow(image)  # Needs to be in row,col order
        #plt.savefig(self.absolute_path+key+'{}.png'.format(self.frame_counter[key]))
        #im = Image.fromarray(image)
        #im.save(self.absolute_path+key+'{}.png'.format(self.frame_counter[key]))
        imageio.imwrite(self.get_next_frame_name(key), (image).astype(np.uint8))#
        #scipy.misc.imsave(self.absolute_path+key+'{}.png'.format(self.frame_counter[key]), image)



    def render_video(self, key, delete_images, reset_frame_counter=True):

        #ffmpeg -r 25 -i frame%09d.png -vcodec mpeg4 -b 10000000 -y video.mp4
        #call(['ffmpeg', '-r', '25', '-i', self.absolute_path + key + '%d.png', '-vcodec', 'mpeg4', '-q:v', '1', '-b', '10000000', '-y', self.absolute_path + key + '.mp4'], shell=True)#

        # ffmpeg -i temp-%d.png -c:v libx264 -strict -2 -preset slow -pix_fmt yuv420p -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -f mp4 output.mp4 #, '-r', '25'
        call(['ffmpeg', '-i', self.absolute_path + key + '%d.png', '-c:v', 'libx264', '-strict', '-2', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-f', 'mp4', self.absolute_path + key + '.mp4'], shell=True)
        if delete_images:
            files = os.listdir(self.absolute_path)
            for f in files:
                if key in f and '.png' in f:
                    #print(self.absolute_path+f)
                    #os.remove(f)#todo savety check
                    os.remove(self.absolute_path + f)

        if reset_frame_counter:
            self.frame_counter[key] = 0

    def load_param(self, key, section='Parameters', default=None, return_string=False):#casting!!!
        self.init_config()
        try:
            s = self.config.get(section, key)
        except:
            return default
        if return_string:
            return s
        if len(s) > 0:
            if s=='True':
                return True
            if s=='False':
                return False
            try:
                if '.' in s:
                    return float(s)
                else:
                    return int(s)
            except:
                return s
        return s

    def load_param_list(self, keys, section='Parameters', return_dict=False, default=None, return_string=False):
        result = []
        for key in keys:
            result.append(self.load_param(key, section, default, return_string))

        if return_dict:
            return dict(zip(keys, result))
        else:
            return result

    def load_np(self, key):
        return np.load(self.absolute_path + key + '.npy')

    def copy_project_files(self, base_folder='../../'):
        zf = zipfile.ZipFile(self.absolute_path+"backup.zip", "w")
        for dirname, subdirs, files in os.walk(base_folder):#
            #print(dirname, subdirs, files)
            if dirname != base_folder and not 'Data' in dirname and not '.git' in dirname and not '.idea' in dirname and not '.zip' in dirname:
                zf.write(dirname)
                for filename in files:
                    zf.write(os.path.join(dirname, filename))
        zf.close()

class SimpleStorageManager(StorageManager):

    def __init__(self, folder):
        self.absolute_path = folder

        self.config_file_name = 'config.ini'
        self.config = None

        self.frame_counter = {}


class StorageManagerGroup:

    def __init__(self, Tag, main_folder_name=None, data_folder=get_data_folder()):

        storage_manager_folder = data_folder + '/StorageManager/'

        if main_folder_name is None:
            main_folder_name = Tag

        self.absolute_path = storage_manager_folder + main_folder_name + '/'
        self.Tag = Tag
        self.data_folder = data_folder

        self.vp={}

        self.StorageManager_file_appendixes = []
        self.refresh()


    def refresh(self):
        self.StorageManagerList = []
        if os.path.exists(self.absolute_path):
            for folder in os.listdir(self.absolute_path):
                if os.path.isdir(self.absolute_path+folder) and self.Tag in folder:
                    self.StorageManagerList.append(StorageManager(self.Tag, folder, add_new_when_exists=False, data_folder=self.data_folder))


    def sort_by(self, param, section='Parameters'):
        self.StorageManagerList = sorted(self.StorageManagerList, key=lambda sm: sm.load_param(param, section, default=-np.inf))

    def remove_None(self, l, remove_None=True):
        if remove_None:
            return list(filter(lambda a: a is not None, l))
        else:
            return l

    def get_param_list(self, param, section='Parameters', remove_None=False):
        if param == '#SM#':
            return self.StorageManagerList
        else:
            return self.remove_None([sm.load_param(param, section) for sm in self.StorageManagerList], remove_None)

    def get_np_list(self, np_name, remove_None=False):
        return self.remove_None([sm.load_np(np_name) for sm in self.StorageManagerList], remove_None)

    def get_obj_list(self, obj_name, remove_None=False):
        return self.remove_None([sm.load_obj(obj_name) for sm in self.StorageManagerList], remove_None)

    def add_virtual_multi_parameter(self, param, value): #add readout parameter that is not stored in config files for easier access
        if (type(value) is list or type(value) is np.ndarray) and len(value)==len(self.StorageManagerList):
            self.vp[param] = np.array(value)
        else:
            self.vp[param] = np.array([value for _ in self.StorageManagerList])

    def get_multi_param_list(self, params, section='Parameters', remove_None=True):
        remove = True
        results = []
        for param in params:
            if param in self.vp:
                results.append(self.vp[param])#virtual parameter
            else:
                results.append(np.array(self.get_param_list(param, section)))#stored parameter
            remove*=(results[-1]!=None)*(results[-1]!=np.nan)
        results = np.array(results)
        if remove_None:
            results=results[:,remove]#np.where(results is not None)#.any(axis=1)
        return results#.astype(np.float64)

    def get_multi_param_dict(self, params, section='Parameters', remove_None=True):
        return dict(zip(params,self.get_multi_param_list(params,section,remove_None)))

    def remove_duplicates_get_eval(self, x, y, evalstr='np.average(a)'):
        unique = np.unique(x)
        result = np.zeros(len(unique))
        for i, u in enumerate(unique):
            a = y[x == u]
            result[i] = eval(evalstr)
        return unique, result

    def __getitem__(self, query):
        result = []
        parts = query.replace('=', '|').replace(' ', '|').replace('>', '|').replace('<', '|').split('|')
        key_q = parts[0]

        for sm in self.StorageManagerList:
            param = sm.load_param(key_q, return_string=True)
            if param is not None:
                new_q = query.replace(key_q, param)
                if eval(new_q):
                    result.append(sm)

        return result

    def get_all_params(self, section='Parameters', include_virtual_parameters=True):
        result_dict = {}
        for sm in self.StorageManagerList:
            for param in sm.get_all_params(section):
                result_dict[param] = True
        if include_virtual_parameters:
            for v in self.vp:
                result_dict[v]=True
        return result_dict.keys()




