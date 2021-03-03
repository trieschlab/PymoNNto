from NetworkBehaviour.Input.Pattern_Basics import *
from NetworkBehaviour.Input.Images.Helper import *
import hickle as hkl
import os.path
from NetworkBehaviour.Input.Images.PixelPattern import *

mnist_folder = '../../../MNIST'
mnist_preprocessed_patterns = mnist_folder+'/preprocessed_patterns.data'
mnist_preprocessed_labels = mnist_folder+'/preprocessed_labels.data'

class MNIST_Patterns(Pixel_Pattern):

    def get_MNIST_activation_data(self, pic_numbers=None):
        result = []
        labels = []

        if not hasattr(self, "mndata"):
            from mnist import MNIST  # pip install python-mnist
            self.mndata = MNIST(mnist_folder)
            data = self.mndata.load_testing()
            self.mnist_pictures = data[0]
            self.mnist_labels = data[1]

        for i, l in enumerate(self.mnist_labels):
            if pic_numbers is None or l in pic_numbers:
                act = np.array(self.mnist_pictures[i]).reshape(28, 28)#/255
                #act = self.edge_detector(self.mnist_pictures[i])#[d/255*1.4 for d in self.edge_detector(self.mnist_pictures[i])]
                result.append(act)
                labels.append(l)

        return result, labels

    def get_current_pattern_index(self):
        self.label_repeat_counter += 1

        if self.label_repeat_counter>self.repeat_same_label_time:
            self.label_repeat_counter = 1
            r = np.random.randint(len(self.patterns))
            self.label_repeat_label = self.labels[r]
            return r
        else:
            for _ in range(1000):#max trys to find same label
                r = np.random.randint(len(self.patterns))
                if self.labels[r] == self.label_repeat_label:
                    return r

        return np.random.randint(len(self.patterns))

    def initialize(self):
        super().initialize()
        self.grid_width = self.kwargs.get('grid_width', 28)
        self.grid_height = self.kwargs.get('grid_height', 28)

        self.repeat_same_label_time = self.kwargs.get('repeat_same_label_time', 1)
        self.label_repeat_counter=self.repeat_same_label_time
        self.label_repeat_label=''

        self.grid_channels = 2
        if not os.path.isfile(mnist_preprocessed_patterns) or not os.path.isfile(mnist_preprocessed_labels):
            data, labels = self.get_MNIST_activation_data()
            for d, l in zip(data, labels):
                onc, offc = get_LOG_On_Off(d)
                self.patterns.append(np.array([onc/np.max(onc), offc/np.max(offc)]))
                self.labels.append(l)
            hkl.dump(self.patterns, open(mnist_preprocessed_patterns, 'w'))
            hkl.dump(self.labels, open(mnist_preprocessed_labels, 'w'))
        else:
            self.patterns=hkl.load(open(mnist_preprocessed_patterns))
            self.labels=hkl.load(open(mnist_preprocessed_labels))

        print('MNIST loaded')


    #def get_pattern(self):
    #    i = 0
    #    submat = np.zeros(1)
    #    while i < 10 and sum(submat) < 1.0:
    #        i += 1
    #        submat = self.get_image_patch()

    #    if self.patch_norm:
    #        d = np.max(submat)
    #        if d == 0:
    #            d = 1
    #        return submat/d
    #    else:
    #        return submat


    #def get_pattern_dimension(self, remove_depth=True):
    #    if remove_depth:
    #        return [self.grid_height * self.dim_matrices.shape[0], self.grid_width]
    #    else:
    #        return [self.dim_matrices.shape[0], self.grid_height, self.grid_width]

    #def reconstruct_pattern(self, p):
    #    return p.reshape(self.grid_height * self.dim_matrices.shape[0], self.grid_width)


#test = MNIST_Patterns()

#num,lab = test.get_MNIST_activation_data([2])

#onc, offc = get_LOG_On_Off(num[0])

#offc=offc.astype(np.float64)
#offc/=np.max(offc)

#plt.matshow(offc)
#plt.show()
