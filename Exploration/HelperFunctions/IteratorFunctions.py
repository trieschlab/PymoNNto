import numpy as np

#creates 1D, 2D or 3D generators.
#the grid starts with a low resolution step size (max-min)/5
#and doubles its resolution per axis gradually.
#The longer you let the for loop run, the more detail you will get.

def infinite_resolution_1D(minx, maxx, max_resolution=-1):
    result = []
    dx = maxx - minx
    r = -1
    while max_resolution==-1 or r<max_resolution:
        r += 1
        resolution = 5*np.power(2, r)
        for a in np.arange(minx, maxx, dx/resolution):
            new = a
            if new not in result:
                result.append(new)
                yield new

def infinite_resolution_2D(minx, maxx, miny, maxy, max_resolution=-1):
    result = []
    dx = maxx - minx
    dy = maxy - miny
    r = -1
    while max_resolution==-1 or r<max_resolution:
        r += 1
        resolution = 5*np.power(2, r)
        for a in np.arange(minx, maxx, dx/resolution):
            for b in np.arange(miny, maxy, dy/resolution):
                new = [a, b]
                if new not in result:
                    result.append(new)
                    yield new

def infinite_resolution_3D(minx, maxx, miny, maxy, minz, maxz, max_resolution=-1):
    result = []
    dx = maxx - minx
    dy = maxy - miny
    dz = maxz - minz
    r = -1
    while max_resolution==-1 or r<max_resolution:
        r += 1
        resolution = 5*np.power(2, r)
        for a in np.arange(minx, maxx, dx/resolution):
            for b in np.arange(miny, maxy, dy/resolution):
                for c in np.arange(minz, maxz, dz/resolution):
                    new = [a, b, c]
                    if new not in result:
                        result.append(new)
                        yield new

'''
def nth_sqrt(x, n):
    return np.power(x, (1 / n))


def stretched_powerxe(xmin, xmax, x, e):
    scale = (xmax-xmin)/np.power(xmax-xmin, e)
    return xmin+np.power(x-xmin, e)*scale

def stretched_powerxe_center(xmin, xmax, x, e, centerx):
    pcx = np.power(centerx, 1/e)

    sxmin = np.abs(np.power(xmin-pcx, e))
    sxmin=sxmin*(((xmin-pcx)>0)-0.5)*2

    sxmax = np.abs(np.power(xmax-pcx, e))
    sxmin=sxmin*(((xmax-pcx)>0)-0.5)*2

    scale = (xmax-xmin)/(sxmax-sxmin)

    tmp=np.power(x-pcx, e)
    tmp=tmp*(((x-pcx)>0)-0.5)*2

    return xmin+tmp*scale-sxmin*scale

x = np.arange(0.1,3.0,0.1)
import matplotlib.pyplot as plt
#plt.scatter(x,x*0)
#plt.scatter(stretched_log(0.1,3,x,2),x*0+1)
#plt.show()




def infinite_resolution_2D(minx, maxx, miny, maxy):
    result = []
    dx = maxx - minx
    dy = maxy - miny
    r = -1
    for i in range(2):
        r += 1
        resolution = 5*np.power(2, r)
        for a in np.arange(minx, maxx, dx/resolution):
            for b in np.arange(miny, maxy, dy/resolution):
                new = [a, b]
                if new not in result:
                    result.append(new)
    return np.array(result)

d = infinite_resolution_2D(0.1,3.0,0.1,3.0)

plt.scatter(stretched_powerxe_center(0.1, 3, d[:, 0], 2,0),stretched_powerxe_center(0.1, 3, d[:, 1], 2.0, 1.5))
plt.show()


#def steps(start, end, points):
#    result = []
#    if start <= 0 or end<=start:
#        return []

#    exp = nth_sqrt(end/start, points)

#    while start<end:
#        result.append(start)
#        start *= exp
#    result.append(end)
#    return result

'''