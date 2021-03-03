#from mnist import MNIST #pip install python-mnist
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


def rotatearoundpoint(p, rot, middle):
    aa = p[0] - middle[0]
    bb = p[1] - middle[1]
    cc = np.sqrt(aa * aa + bb * bb)
    a = 0
    if cc != 0:
        a = np.rad2deg(np.arcsin(aa / cc))
    if bb < 0:
        a = 180 - a
    a = np.deg2rad(a + rot)
    aa = np.sin(a) * cc
    bb = np.cos(a) * cc
    return (middle[0] + aa, middle[1] + bb)


def picture_to_array(image, max=1):
    pil_image_gray = image.convert('L')
    result = np.array(pil_image_gray).astype(np.float64)
    return result/np.maximum(max, np.max(image))


#def picture_to_array(image, max=1):
#    result = []
#    for y in range(image.size[1]):
#        for x in range(image.size[0]):
#            val = image.getpixel((x, y))
#            result.append(val)
#            if val > max:
#                max = val
#    for i, val in enumerate(result):
#        result[i] = val / max
#    return result


def getRotLinePicture(deg, width=15, height=15):
    im = Image.new('L', (width, height), (0))
    draw = ImageDraw.Draw(im)
    rot_point = rotatearoundpoint((width / 2, 0), deg, (0, 0))
    draw.line(
        (width / 2 - rot_point[0], height / 2 - rot_point[1], width / 2 + rot_point[0], height / 2 + rot_point[1]),
        fill=255)
    return picture_to_array(im)


def getVerLinePicture(x, width=15, height=15):
    im = Image.new('L', (width, height), (0))
    draw = ImageDraw.Draw(im)
    draw.line((x, 0, x, height - 0), fill=255)
    return picture_to_array(im)
    # im.show()
    # im.save("Data/im{}.png".format(deg))


def getVerLinePictureSmooth(x, width=15, height=15):
    im = Image.new('L', (width, height), (0))
    draw = ImageDraw.Draw(im)
    for i in [-2, -1, 0, 1, 2]:
        shade = 255 - abs(i) * 80
        draw.line((x + i, 0, x + i, height - 0), fill=shade)
    return picture_to_array(im)
    # im.show()
    # im.save("Data/im{}.png".format(deg))


def getHorLinePicture(y, width=15, height=15):
    im = Image.new('L', (width, height), (0))
    draw = ImageDraw.Draw(im)
    draw.line((0, y, width - 0, y), fill=255)
    return picture_to_array(im)
    # im.show()
    # im.save("Data/im{}.png".format(deg))


def getHorLinePictureSmooth(y, width=15, height=15):
    im = Image.new('L', (width, height), (0))
    draw = ImageDraw.Draw(im)
    for i in [-2, -1, 0, 1, 2]:
        shade = 255 - abs(i) * 80
        draw.line((0, y + i, width - 0, y + i), fill=shade)
    return picture_to_array(im)


def getLinePicture(deg, center_x, center_y, length, width, height):
    im = Image.new('L', (width, height), (0))
    draw = ImageDraw.Draw(im)
    rot_point = rotatearoundpoint((length / 2, 0), deg, (0, 0))
    draw.line((center_x - np.floor(rot_point[0]), center_y - np.floor(rot_point[1]), center_x + np.floor(rot_point[0]), center_y + np.floor(rot_point[1])), fill=255)
    return picture_to_array(im)


def get_rgbw(r, g, b, w):
    result = np.zeros(r.shape)
    for x in range(int(r.shape[1] / 2)):
        for y in range(int(r.shape[0] / 2)):
            x2 = x * 2
            y2 = y * 2
            result[y2, x2] = np.sum(r[y2:y2 + 2, x2:x2 + 2]) / 4
            result[y2 + 1, x2] = np.sum(g[y2:y2 + 2, x2:x2 + 2]) / 4
            result[y2, x2 + 1] = np.sum(b[y2:y2 + 2, x2:x2 + 2]) / 4
            result[y2 + 1, x2 + 1] = np.sum(w[y2:y2 + 2, x2:x2 + 2]) / 4

    return result


def get_log_kenel(sigma):
    size = int(2 * (np.ceil(3 * sigma)) + 1)
    x, y = np.meshgrid(np.arange(-size / 2, size / 2 + 1), np.arange(-size / 2, size / 2 + 1))
    normal = 1 / (2.0 * np.pi * sigma ** 2)
    kernel = ((x ** 2 + y ** 2 - (2.0 * sigma ** 2)) / sigma ** 4) * np.exp(
        -(x ** 2 + y ** 2) / (2.0 * sigma ** 2)) / normal
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # zs = kernel#np.array(fun(np.ravel(X), np.ravel(Y)))
    # ax.plot_surface(x, y, zs)
    # ax.set_xlabel('X Label')
    # ax.set_ylabel('Y Label')
    # ax.set_zlabel('Z Label')
    # plt.show()
    return kernel


def get_multi_color_LOG_On_Off(c1, c2):
    from scipy import signal
    kernel = get_log_kenel(1)
    p_kernel = kernel * (kernel > 0)
    n_kernel = kernel * (kernel < 0)

    c1_p = signal.convolve2d(c1, p_kernel, boundary='symm', mode='same')  # center
    c2_n = signal.convolve2d(c2, n_kernel, boundary='symm', mode='same')  # surround

    LOG = c1_p + c2_n
    on_center = (LOG > 0) * LOG
    off_center = (LOG < 0) * LOG * -1

    return on_center.astype(np.float64), off_center.astype(np.float64)


def get_LOG_On_Off(data, sigma=1):
    import scipy.ndimage as ndimage
    LOG = ndimage.gaussian_laplace(data.astype(np.int32), sigma=sigma)
    on_center = (LOG > 0) * LOG
    off_center = (LOG < 0) * LOG * -1
    return on_center, off_center


def gkern(kernlen=9, nsig=2):
    import scipy.ndimage.filters as fi
    #print(kernlen, nsig)
    inp = np.zeros((kernlen, kernlen))
    inp[kernlen // 2, kernlen // 2] = 1
    return fi.gaussian_filter(inp, nsig)