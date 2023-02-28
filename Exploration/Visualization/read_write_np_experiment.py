from PymoNNto.NetworkCore.Neuron_Group import *


class NeuronGroup_read_write_event(NeuronGroup):

    ref = None
    wef = None
    current_dict = None

    def set_read_event_function(self, ref):
        self.current_dict = copy.copy(dir(self))
        self.ref = ref

    def set_write_event_function(self, wef):
        self.current_dict = copy.copy(dir(self))
        self.wef = wef

    def __getattr__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattr__(attr_name)
        print(attr_name+'-')
        if hasattr(self,attr_name):
            self.ref(self, attr_name+'-')
        return super().__getattr__(attr_name)#self.vector('uniform')

    def __getattribute__(self, attr_name):
        if attr_name in ['wef', 'ref', 'current_dict'] or self.current_dict is None or attr_name in self.current_dict:
            return super().__getattribute__(attr_name)
        #print(attr_name+'+')
        #if hasattr(self, attr_name):
        self.ref(self, attr_name+'+')
        return super().__getattribute__(attr_name)#self.vector('uniform')

    def __setattr__(self, attr_name, val):
        if self.wef is not None:
            self.wef(self, attr_name)
        super().__setattr__(attr_name, val)

def something_get(obj, attr):
    print('get', obj, attr)
    return

def something_set(obj, attr):
    print('set', obj, attr)
    return

NG_rwe = NeuronGroup_read_write_event(1, {}, None)

#print(NG_rwe.__doc__)

NG_rwe.set_read_event_function(something_get)
NG_rwe.set_write_event_function(something_set)

NG_rwe.afferent_synapses[1] = 2

print(hasattr(NG_rwe, 'x'))

#NG_rwe.x = np.zeros(10)
#y = NG_rwe.x + 10

#def dsfagsd(blub):
#    n=blub
#    return copy.copy(eval('np.mean(n.x)'))

#print(dsfagsd(NG_rwe))

