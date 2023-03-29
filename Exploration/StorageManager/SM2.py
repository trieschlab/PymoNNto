from PymoNNto.Exploration.StorageManager.StorageManager import *

class StorageManager2:

    # %nr %rnd
    def __init__(self, folder, subfolder='folder+"_"+id', mainfolder='StorageManager', datafolder=get_data_folder(),
                 print_path=True):
        if os.path.exists(folder):
            path = folder
        else:
            self.path = self._ensure_folder(datafolder + '/')
            self.path = self._ensure_folder(self.path + mainfolder + '/')
            self.path = self._ensure_folder(self.path + folder + '/')

            subfolder = self._eval_subfolder(folder, subfolder)
            new = not os.path.exists(self.path + subfolder + '/')
            self.path = self._ensure_folder(self.path + subfolder + '/')

            if new:
                self.save('time', time.time())

        if print_path:
            print(self.path)

        self.config = ConfigParser()
        self.config.read(self.path + 'config.ini')


    def _eval_subfolder(self, folder, subfolder):
        try:
            if 'id' in subfolder:
                id = len(os.listdir(self.path))

            if 'rnd' in subfolder:
                rnd = str(int(np.random.rand() * 10000))

            subfolder = eval(subfolder)
        except:
            pass

        return subfolder


    @property
    def folder(self):
        return self.path


    @property
    def directory(self):
        return self.path


    def _ensure_folder(self, folder):
        if not os.path.exists(folder):
            try:
                os.mkdir(folder)
            except:
                raise Exception(folder + ' can not be created')
        return folder


    def _get_next_key_file(self, key):
        result = self.path + key + '.*'
        i = 0
        while len(glob.glob(result)) > 0:
            result = self.path + key + '_' + str(i) + '.*'
            i += 1
        return result


    # add network save pickle compile...
    def save(self, key, data, mainkey='', ):
        if type(data) == str or type(data) == int or type(data) == float or type(data) == bool:

            value = str(data)

            if not self.config.has_section(mainkey):
                self.config.add_section(mainkey)
            self.config.set(mainkey, key, str(value).replace('%', 'percent'))
            with open(self.absolute_path + self.config_file_name, 'w') as configfile:
                self.config.write(configfile)

        else:
            file = self._get_next_key_file(mainkey + key)

            if type(data) == np.ndarray:
                np.save(file + '.npy', arr=obj)

            elif type(data) == image:
                imageio.imwrite(file + '.png', image.astype(np.uint8))

            else:  # obj
                pickle.dump(data, open(file + '.obj', 'wb'))


    def load(self, key, default=None, mainkey=''):
        try:
            s = self.config.get(mainkey, key)
        except:
            return default
        if len(s) > 0:
            if s == 'True':
                return True
            if s == 'False':
                return False
            try:
                if '.' in s:
                    return float(s)
                else:
                    return int(s)
            except:
                return s
        return s


    # do not use! => render_video searches for key*.png (right order!!!) (creation date?)

    # self.get_next_frame_name(key)
    # def get_next_frame_key(self, videokey):
    #    if not key in self.frame_counter:
    #        self.frame_counter[key] = 0
    #    self.frame_counter[key] += 1
    #    return self.absolute_path+key+'{}'.format(self.frame_counter[key]-1)


    def render_video(self, key, delete_images, reset_frame_counter=True):
        call(
            ['ffmpeg', '-i', self.path + key + '_%d.png', '-c:v', 'libx264', '-strict', '-2', '-preset', 'slow', '-pix_fmt',
             'yuv420p', '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2', '-f', 'mp4', self.absolute_path + key + '.mp4'],
            shell=True)
        if delete_images:
            files = os.listdir(self.path)
            for f in files:
                if key in f and '.png' in f:
                    os.remove(self.absolute_path + f)