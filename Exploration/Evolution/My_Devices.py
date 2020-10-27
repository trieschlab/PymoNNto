from SORNSim.Exploration.Evolution.Computing_Devices import *


class XPS_Server(Evolution_Server_Local_Windows):
    def __init__(self):
        super().__init__('XPS', '../../../Evolution/')
        self.cores=6

class BV_Server(Evolution_Server_SSH):
    def __init__(self):
        super().__init__('BV', 'Evolution/', 'hey3kmuagjunsk2b.myfritz.net', 'marius', None)
        self.cores = 4

class Poppy_Server(Evolution_Server_SSH):
    def __init__(self):
        super().__init__('Poppy', 'Documents/Evolution/', 'poppy.fias.uni-frankfurt.de', 'vieth', None)
        self.cores = 4

class XMEN_Server(Evolution_Server_SSH_Slurm):
    def __init__(self):
        super().__init__('SlurmXMEN', 'Documents/XMEN_Evolution/', 'poppy.fias.uni-frankfurt.de', 'vieth', None, '*command* --partition=x-men --mem=32000 --cpus-per-task=32', 'x-men')
        self.cores = 2

class Sleuths_Server(Evolution_Server_SSH_Slurm):
    def __init__(self):
        super().__init__('SlurmSleuths', 'Documents/Sleuths_Evolution/', 'poppy.fias.uni-frankfurt.de', 'vieth', None, '*command* --partition=sleuths --reservation triesch-shared --mem=8000 --cpus-per-task=1', 'sleuths')#srun #32000 !!!
        self.cores = 2

#class XPS_Server(Evolution_Server_Base):
#    def __init__(self):
#        super().__init__('XPS', '???/')

def get_devices(local=True):
    result = [BV_Server(), Poppy_Server()]#,XMEN_Server(), Sleuths_Server()
    if local:
        result += [XPS_Server()]#, Poppy_Server(), XMEN_Server(), Sleuths_Server(), XPS_Server()
    return result