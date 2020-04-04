from NetworkBehaviour.Input.Pattern_Basics import *

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

from NetworkBehaviour.Input.TREN.Helper import *

from NetworkBehaviour.Input.TREN.PixelPattern import *

#from scipy.ndimage import *
#from scipy import signal
#import scipy.ndimage.filters as fi
#import matplotlib.pyplot as plt

class TNAP_Image_Patches(Pixel_Pattern):

    def dim_contains(self, str):
        for dim in self.dimensions:
            for s in str:
                if s in dim:
                    return True
        return False


    def get_filters(self):

        print('rendering images...')

        self.image_path = self.kwargs.get('image_path', '')
        self.dimensions = self.kwargs.get('dimensions', ['ImageFilter.FIND_EDGES'])
        self.channel_norm = self.kwargs.get('channel_norm', 'max')

        pil_image = Image.open(self.image_path)
        pil_image_gray = pil_image.convert('L')
        image_rgb = np.array(pil_image).astype(np.float32)
        white = np.array(pil_image_gray).astype(np.float32)

        if self.dim_contains(['red']): red = image_rgb[:, :, 0]
        if self.dim_contains(['green']): green = image_rgb[:, :, 1]
        if self.dim_contains(['blue']): blue = image_rgb[:, :, 2]
        if self.dim_contains(['rgbw']): rgbw = get_rgbw(image_rgb[:, :, 0], image_rgb[:, :, 1], image_rgb[:, :, 2], white)
        #if self.dim_contains(['center_red']): on_center_red, off_center_red = get_LOG_On_Off(image_rgb[:, :, 0])
        #if self.dim_contains(['center_green']): on_center_green, off_center_green = get_LOG_On_Off(image_rgb[:, :, 1])
        #if self.dim_contains(['center_blue']): on_center_blue, off_center_blue = get_LOG_On_Off(image_rgb[:, :, 2])
        if self.dim_contains(['center_white']): on_center_white, off_center_white = get_LOG_On_Off(white)
        if self.dim_contains(['center_red_green']): on_center_red_green, off_center_red_green = get_multi_color_LOG_On_Off(image_rgb[:, :, 0], image_rgb[:, :, 1])
        if self.dim_contains(['center_yellow_blue']): on_center_yellow_blue, off_center_yellow_blue = get_multi_color_LOG_On_Off(image_rgb[:, :, 0]*image_rgb[:, :, 1], image_rgb[:, :, 2])
        if self.dim_contains(['center_green_red']): on_center_green_red, off_center_green_red = get_multi_color_LOG_On_Off(image_rgb[:, :, 1], image_rgb[:, :, 0])
        if self.dim_contains(['center_blue_yellow']): on_center_blue_yellow, off_center_blue_yellow = get_multi_color_LOG_On_Off(image_rgb[:, :, 2], image_rgb[:, :, 0]*image_rgb[:, :, 1])


        filters = []
        for dim in self.dimensions:

            res = eval(dim)

            if res is object and issubclass(res, ImageFilter.BuiltinFilter):
                res = np.array(pil_image_gray.filter(res))

            #print(dim)
            #plt.imshow(res, cmap=plt.cm.gist_gray, interpolation='nearest')#filters[-1]
            #plt.show()

            if self.channel_norm is 'max':
                filters.append(res / np.maximum(np.max(res), 1))
            elif self.channel_norm is 'sum':
                filters.append(res / np.maximum(np.sum(res), 1))
            else:
                filters.append(res)



        return np.array(filters)



    def initialize(self):
        super().initialize()
        self.patch_norm = self.kwargs.get('patch_norm', True)

        self.patterns.append(self.get_filters())
        self.labels.append('image_patch')

        self.grid_channels = len(self.patterns[0])


    #def get_image_patch(self):
    #    x = np.random.randint(self.dim_matrices.shape[2] - self.grid_width)
    #    y = np.random.randint(self.dim_matrices.shape[1] - self.grid_height)
    #    submat = self.dim_matrices[:, y:y + self.grid_height, x:x + self.grid_width].flatten()

    #    return submat


    def get_pattern_values(self, pattern):
        i = 0
        result = np.zeros(1)
        while i < 10 and np.sum(result) < 1.0:
            i += 1
            result = super().get_pattern_values(pattern)

        if self.patch_norm:
            d = np.max(result)
            if d == 0:
                d = 1
            return result/d
        else:
            return result

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






class TNAP_Foveation_Image_Patches(TNAP_Image_Patches):

    def get_multi_dim_resort_mask(self, resort_mask, depth):
        result = []
        print(resort_mask.shape)
        for i in range(depth):
            result.append(resort_mask+(self.hup*self.wup)*i)#resort_mask.shape[0]
            #result = np.concatenate([result, resort_mask+resort_mask.shape[0]*i])
        return np.array(result).flatten().astype(np.int32)

    def get_receptive_field_resort_mask(self, w, h, tw, th, sharpness, depth):
        result_img = np.zeros((w, h))

        for x in range(w):
            for y in range(h):
                dx = w / 2 - x
                dy = h / 2 - y
                dist = np.sqrt(dx * dx + dy * dy)
                d = np.clip(1 - (dist) / (w / 2), 0, None)
                result_img[x, y] = np.maximum(np.power(d, sharpness), 0.0000001)

        rif = result_img.flatten()
        rif = rif / sum(rif)
        result = np.random.choice(np.array(list(range(rif.shape[0]))), tw * th, False, rif)

        return result_img, self.get_multi_dim_resort_mask(result, depth)

    def compress_receptive_field(self, patch, resort_mask):
        return patch.flatten()[resort_mask].reshape(self.grid_channels, self.grid_height, self.grid_width)#self.

    def decompress_receptive_field(self, patch, resort_mask, upscale_size):
        f_pic = np.zeros((upscale_size)).flatten()
        f_pic[resort_mask] = patch.flatten()
        return f_pic.reshape(self.get_pattern_dimension())

    def fill_gaps_simple(self, image):
        from scipy import signal
        decomp_img = image / np.max(image)
        blured = signal.convolve2d(image, gkern(int(np.max(image.shape) / 10), np.maximum(np.max(image.shape) / 50, 1)),boundary='symm', mode='same')
        blured = blured / np.max(blured)  # * 1.3
        return decomp_img + blured * (decomp_img == 0)

    def initialize(self):
        super().initialize()

        self.foveation_upscale = self.kwargs.get('foveation_upscale', 1.0)
        self.foveation_sharpness = self.kwargs.get('foveation_sharpness', 1.5)
        if self.foveation_upscale > 1.0:
            self.wup = int(self.grid_width * self.foveation_upscale)
            self.hup = int(self.grid_height * self.foveation_upscale)
            self.retina_pic, self.foveation_mask = self.get_receptive_field_resort_mask(self.wup, self.hup, self.grid_width, self.grid_height, self.foveation_sharpness, self.grid_channels)
        else:
            self.foveation_mask = True
            self.wup = self.grid_width
            self.hup = self.grid_height

    def get_pattern_values(self, pattern):
        x = np.random.randint(pattern.shape[2] - self.wup)
        y = np.random.randint(pattern.shape[1] - self.hup)
        #import matplotlib.pyplot as plt
        #plt.matshow(pattern[:, y:y + self.hup, x:x + self.wup].reshape((450*2,450)), cmap=plt.cm.gist_gray)
        return self.compress_receptive_field(pattern[:, y:y + self.hup, x:x + self.wup], self.foveation_mask)

    def get_retina_pic_dimension(self):
        return (self.wup, self.hup)

    def get_retina_pic(self):
        result=np.zeros(self.get_pattern_dimension()).flatten()
        if self.foveation_upscale > 1.0:
            result[self.foveation_mask]+=1
        return result.reshape(self.get_vstackpattern_dimension())

    def get_pattern_dimension(self):
        return (self.grid_channels, self.hup, self.wup)

    def reconstruct_pattern(self, p):
        return self.decompress_receptive_field(p, self.foveation_mask, self.wup * self.hup * self.grid_channels).reshape(self.get_pattern_dimension())
