from NetworkBehaviour.Input.Images.PixelPattern import *

class Line_Patterns(Pixel_Pattern):

    def initialize(self):
        super().initialize()

        center_x = self.kwargs.get('center_x', 1)
        center_y = self.kwargs.get('center_y', 1)
        degree = self.kwargs.get('degree', 1)
        line_length = self.kwargs.get('line_length', 1)

        pattern_count=0
        if type(center_x) in [list, np.ndarray]: pattern_count = np.maximum(pattern_count, len(center_x))
        if type(center_y) in [list, np.ndarray]: pattern_count = np.maximum(pattern_count, len(center_y))
        if type(degree) in [list, np.ndarray]: pattern_count = np.maximum(pattern_count, len(degree))
        if pattern_count == 0: pattern_count=1

        if not type(center_x) in [list, np.ndarray]: center_x=np.ones(pattern_count)*center_x
        if not type(center_y) in [list, np.ndarray]: center_y=np.ones(pattern_count)*center_y
        if not type(degree) in [list, np.ndarray]: degree=np.ones(pattern_count)*degree

        for i in range(pattern_count):
            self.patterns.append(np.array([getLinePicture(degree[i], center_x[i], center_y[i], line_length/2, self.grid_width, self.grid_height)]))
            self.labels.append('deg{}cy{}cx{}'.format(degree[i], center_x[i], center_y[i]))