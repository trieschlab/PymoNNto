from NetworkBehaviour.Structure.Structure import *

def pol2cart(theta, rho):
    x = rho * np.cos(theta)
    y = rho * np.sin(theta)
    return x, y

def cart2pol(x, y):
    theta = np.arctan2(y, x)
    rho = np.hypot(x, y)
    return theta, rho

class Ray_Line():
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy

class Box:

    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color

    def collision(self, box):
            return (self.x < box.x + box.w and
                    self.x + self.w > box.x and
                    self.y < box.y + box.h and
                    self.y + self.h > box.y)

    def get_edge_lines(self):
        return [Ray_Line(self.x, self.y, 0, self.h),
                Ray_Line(self.x, self.y, self.w, 0),
                Ray_Line(self.x + self.w, self.y, 0, self.h),
                Ray_Line(self.x, self.y + self.h, self.w, 0)]

    def get_ray_line_dist(self, ray, line):

        b_div = -ray.dy*line.dx+ray.dx*line.dy
        if b_div != 0:
            b = (ray.dy*(line.x-ray.x)-ray.dx*(line.y-ray.y))/b_div
            if b >= 0 and b <= 1:
                if ray.dx != 0:
                    dist = (line.x-ray.x+b*line.dx) / ray.dx
                    if dist>=0:
                        return dist
                elif ray.dy !=0:
                    dist = (line.y-ray.y+b*line.dy) / ray.dy
                    if dist >= 0:
                        return dist

        return np.inf


    def ray_collision_distance(self, ray):
        return np.min([self.get_ray_line_dist(ray, line) for line in self.get_edge_lines()])


#b = Box(1, 1, 10, 10)
#r = Ray_Line(5, 5, 1, 2)
#print(b.ray_collision_distance(r))

class Maze_vision_behaviour(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('maze_vision_behaviour')
        self.maze = self.get_init_attr('maze', None)

    def new_iteration(self, neurons):
        self.maze.rays = []
        image_data=[]
        for r_i in range(self.maze.ray_count):
            r = float(r_i) * 2.0 * np.pi / float(self.maze.ray_count)+0.00001
            x, y = pol2cart(r, 1.0)
            ray = Ray_Line(self.maze.player.x+self.maze.player.w/2, self.maze.player.y+self.maze.player.h/2, x, y)
            ray.dist = 1000.0
            ray.collision_box = None
            for box in self.maze.boxes:
                collision = box.ray_collision_distance(ray)
                if collision < ray.dist and collision > 0:
                    ray.dist = collision
                    ray.collision_box = box

            if ray.collision_box is not None:
                image_data.append(ray.collision_box.color[0:3])
            else:
                image_data.append([0, 0, 0])

            self.maze.rays.append(ray)

        #print(image_data)
        neurons.activity += np.array(image_data).transpose().flatten()



class Maze_sense_behaviour(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('maze_sense_behaviour')
        self.maze = self.get_init_attr('maze', None)

    def new_iteration(self, neurons):
        x = self.maze.player.x-(self.maze.maze_w-1)/2
        y = self.maze.player.y-(self.maze.maze_h-1)/2

        mask = (neurons.x == x)*(neurons.y == y)
        #print(x,y,np.sum(mask))
        neurons.activity[mask] += 1


class Maze_action_behaviour(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('maze_act_behaviour')
        self.maze = self.get_init_attr('maze', None)
        self.right= 0
        self.left = 0
        self.bottom=0
        self.top =  0

    def move_player(self, x, y):

        self.maze.player.x += x
        self.maze.player.y += y

        collision = False
        for box in self.maze.boxes:
            if box.collision(self.maze.player):
                collision = True

        if collision:
            self.maze.player.x = self.maze.player.last_x
            self.maze.player.y = self.maze.player.last_y

        return collision


    def new_iteration(self, neurons):

        self.maze.player.last_x = self.maze.player.x
        self.maze.player.last_y = self.maze.player.y

        block_size = int(len(neurons.output)/4)

        #self.right+= np.sum(neurons.output[block_size * 0:block_size * 1])
        #self.left += np.sum(neurons.output[block_size * 1:block_size * 2])
        #self.bottom+=np.sum(neurons.output[block_size * 2:block_size * 3])
        #self.top +=  np.sum(neurons.output[block_size * 3:block_size * 4])

        self.right+= np.sum(neurons.output[(neurons.x < 0) * (neurons.y < 0)])
        self.left += np.sum(neurons.output[(neurons.x > 0) * (neurons.y < 0)])
        self.bottom+=np.sum(neurons.output[(neurons.x < 0) * (neurons.y > 0)])
        self.top +=  np.sum(neurons.output[(neurons.x > 0) * (neurons.y > 0)])

        #import matplotlib.pyplot as plt
        #plt.scatter(neurons.x, neurons.y)
        #mask = (neurons.x < 0) * (neurons.y < 0)
        #plt.scatter(neurons.x[mask], neurons.y[mask])
        #plt.show()


        max_act_sum = np.max([self.right, self.left, self.bottom, self.top])

        coll = False

        if neurons.iteration % self.maze.reaction_time == 0:
            if max_act_sum > 1:

                if self.right == max_act_sum:
                    coll = coll or self.move_player(+1, 0)
                elif self.left == max_act_sum:
                    coll = coll or self.move_player(-1, 0)
                elif self.bottom == max_act_sum:
                    coll = coll or self.move_player(0, +1)
                elif self.top == max_act_sum:
                    coll = coll or self.move_player(0, -1)

            self.right = 0
            self.left = 0
            self.bottom = 0
            self.top = 0

            self.maze.player.x = np.clip(self.maze.player.x, 0, self.maze.maze_w - 1)
            self.maze.player.y = np.clip(self.maze.player.y, 0, self.maze.maze_h - 1)

        self.maze.collision = coll



class Maze_reward_behaviour(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Maze_reward_behaviour')
        self.maze = self.get_init_attr('maze', None)

    def new_iteration(self, neurons):

        if self.maze.player.collision(self.maze.goal):
            neurons.activity += 1
            self.maze.reset_player()



class Maze_punishment_behaviour(Behaviour):

    def set_variables(self, neurons):
        self.add_tag('Maze_punishment_behaviour')
        self.maze = self.get_init_attr('maze', None)

    def new_iteration(self, neurons):

        if self.maze.collision:
            neurons.activity += 1




def get_rnd_color():
    color = np.array([np.random.rand(), np.random.rand(), np.random.rand(), 1.0])
    color = color > 0.5
    color = color * 200.0
    color[3] = 255.0
    #color[2] = color[0]
    #color[1] = color[0]
    return color

class Maze:

    def add_Box(self, x, y, w, h, c, split=True):
        if split:
            for w_i in range(w):
                for h_i in range(h):
                    self.boxes.append(Box(x+w_i, y+h_i, 1, 1, get_rnd_color()))
        else:
            self.boxes.append(Box(x, y, w, h, c))

    def reset_player(self):
        self.player.x = 1
        self.player.y = 1
        self.player.last_x = self.player.x
        self.player.last_y = self.player.y


    def __init__(self, level='default'):

        self.boxes = []

        self.reaction_time=1

        self.ray_count = 32
        self.rays=[]
        self.collision = False

        if level == 'default':
            self.player = Box(1, 1, 1, 1, (0, 0, 255, 255))
            self.player.last_x = self.player.x
            self.player.last_y = self.player.y
            self.goal = Box(8, 1, 1, 1, (255, 0, 0, 255))
            self.maze_w = 10
            self.maze_h = 10

            self.add_Box(1, 0, 8, 1, get_rnd_color())
            self.add_Box(9, 0, 1, 10, get_rnd_color())
            self.add_Box(0, 0, 1, 10, get_rnd_color())
            self.add_Box(1, 9, 8, 1, get_rnd_color())

            self.add_Box(2, 5, 1, 1, get_rnd_color())
            self.add_Box(5, 1, 3, 1, get_rnd_color())
            self.add_Box(3, 4, 1, 2, get_rnd_color())
            self.add_Box(5, 2, 1, 5, get_rnd_color())
            self.add_Box(7, 5, 1, 1, get_rnd_color())

    def get_reward_neuron_behaviour(self):
        return Maze_reward_behaviour(maze=self)

    def get_reward_neuron_dimension(self):
        return NeuronDimension(width=4, height=4, depth=1)


    def get_punishment_neuron_behaviour(self):
        return Maze_punishment_behaviour(maze=self)

    def get_punishment_neuron_dimension(self):
        return NeuronDimension(width=4, height=4, depth=1)



    def get_vision_neuron_behaviour(self):
        return Maze_vision_behaviour(maze=self)

    def get_vision_neuron_dimension(self):
        return NeuronDimension(width=self.ray_count, height=3, depth=1)




    def get_location_neuron_behaviour(self):
        return Maze_sense_behaviour(maze=self)

    def get_location_neuron_dimension(self):
        return NeuronDimension(width=self.maze_w, height=self.maze_h, depth=1)

    def get_inhibitory_location_neuron_dimension(self):
        return NeuronDimension(width=int(self.maze_w/2), height=int(self.maze_h/2), depth=1)


    def get_action_neuron_behaviour(self):
        return Maze_action_behaviour(maze=self)

    def get_action_neuron_dimension(self):
        return NeuronDimension(width=8, height=8, depth=1)


    def get_sensing_neuron_behaviour(self):
        return

    def get_sensing_neuron_dimension(self):
        return


    def new_iteration(self, neurons):
        return


