import numpy as np

class Axis:
    target_name = ''
    target_attribute_name = ''
    values = []
    plotvalues = []
    axis_description = []

    current_value=-1
    current_plotvalue=-1
    step=-1

    def __repr__(self):
        return '{}|{}|{}'.format(self.current_value, self.current_plotvalue, self.step)


class Parameter_iterator():

    def __init__(self, iteration_function):
        self.axis_list = {}
        self.iteration_function = iteration_function

    def start(self):
        self.recursion_loop(list(self.axis_list.keys()))

    def recursion_loop(self, axisnames):
        if len(axisnames) > 0:
            axis = self.axis_list[axisnames[0]]
            i=0
            for axis.current_value, axis.current_plotvalue in zip(axis.values, axis.plotvalues):
                axis.step=i
                i+=1
                self.recursion_loop(axisnames[1:])
        else:
            self.iteration_function(self.axis_list)

    def set_axis_steps(self, axis_name, target_name, target_attribute_name, min, max, steps, logarithmic=True):
        self.axis_list[axis_name] = Axis()
        self.axis_list[axis_name].target_name = target_name
        self.axis_list[axis_name].target_attribute_name = target_attribute_name
        self.axis_list[axis_name].values, self.axis_list[axis_name].plotvalues, self.axis_list[axis_name].x_axis_description = self.get_stepped_values(min, max, steps, logarithmic, target_attribute_name)


    def get_stepped_values(self, min, max, steps, logarithmic=True, axis_description=''):
        values = []
        plotvalues = []
        area = max - min

        if logarithmic:
            area = np.log10(area)
            plotvalues.append(0)
        else:
            plotvalues.append(min)

        values.append(min)

        steps = steps - 1

        stepsize = area / steps
        for i in range(steps):
            pos = (i + 1) * stepsize

            if logarithmic:
                plotvalues.append(pos)
                pos = np.power(10, pos)
            else:
                plotvalues.append(pos + min)

            values.append(min + pos)

        if logarithmic:
            str_val = ['%.4f' % v for v in values]
            axis_description += ' | logarithmic: {} + 10^x | {}'.format(min, str_val)

        return values, plotvalues, axis_description



def test(axis_list):
    for axis in axis_list:
        print(axis, axis_list[axis].current_value, axis_list[axis].current_plotvalue)
    print('#####')


#pi=Parameter_iterator(test)

#pi.set_axis_steps('x', None, 'xt', 0.1, 1, 11, False)
#pi.set_axis_steps('y', None, 'yt', 1, 10, 2, False)

#pi.start()