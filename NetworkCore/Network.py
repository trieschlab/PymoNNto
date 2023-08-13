from time import time
import numpy as np
from PymoNNto.NetworkCore.Base_Attachable_Modules import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *
import copy
import time
import sys

float32 = np.float32
float64 = np.float64

SxD = 0
DxS = 1

class Network(NetworkObjectBase):

    def __init__(self, tag=None, behavior={}, settings={}):
        self.apply_settings(settings)

        self.NeuronGroups = []
        self.SynapseGroups = []

        self.iteration = 0

        self.behavior_timesteps = []
        self.sorted_behavior_execution_list = [] #stores (key, beh_parent, behavior) triplets
        
        super().__init__(tag, self, behavior)

    # {'dtype':float32, 'syn_dim':DxS}
    def apply_settings(self, settings):
        self.def_dtype = settings.get('dtype', float32)
        self.transposed_synapse_matrix_mode = settings.get('syn_dim', DxS)!=DxS

    def all_objects(self):
        return [self]+self.NeuronGroups+self.SynapseGroups

    def _add_key_to_sorted_behavior_timesteps(self, key):
        if key not in self.behavior_timesteps:
            self.behavior_timesteps.append(key)
            self.behavior_timesteps.sort()


    def _add_behavior_to_sorted_execution_list(self, key, beh_parent, behavior):
        insert_indx=0
        for i,kpb in enumerate(self.sorted_behavior_execution_list):
            k, p, b = kpb
            if key>=k:
                insert_indx = i+1
        self.sorted_behavior_execution_list.insert(insert_indx, (key, beh_parent, behavior))
        #print([k for k,_,_ in self.sorted_behavior_execution_list])
        
    def _remove_behavior_from_sorted_execution_list(self, key, beh_parent, behavior):
        rm_indx = -1
        for i,kpb in enumerate(self.sorted_behavior_execution_list):
            k, p, b = kpb
            if key==k and beh_parent==p and behavior==b:
                rm_indx = i
                break
        if rm_indx>-1:
            self.sorted_behavior_execution_list.pop(rm_indx)
        else:
            raise Exception('behavior not found')

    #######################################
    #Behavior Management
    #######################################

    def set_behaviors(self, tag, enabeled):
        if enabeled:
            print('activating', tag)
        else:
            print('deactivating', tag)
        for obj in self.all_objects():
            for b in obj[tag]:
                b.behavior_enabled = enabeled

    def all_behaviors(self):
        result = []
        for obj in self.all_objects():
            for beh in obj.behavior.values():
                result.append(beh)
        return result

    #######################################
    #Recorder controll
    #######################################

    def recording_off(self):
        for obj in self.all_objects():
            obj.recording = False

    def recording_on(self):
        for obj in self.all_objects():
            obj.recording = True

    def clear_recorder(self, keys=None):
        for obj in self.all_objects():
            for key in obj.behavior:
                if (keys is None or key in keys) and hasattr(obj.behavior[key], 'clear_recorder'):
                    obj.behavior[key].clear_recorder()


    #######################################
    #Initialization
    #######################################

    def initialize(self, info=True, warnings=True, storage_manager=None):
        self.set_gene_variables(info=info, storage_manager=storage_manager)

        if info:
            desc=str(self)
            print(desc)
            if storage_manager is not None:
                storage_manager.save_param('info', desc)

        #self.set_synapses_to_neuron_groups()

        self.initialize_behaviors()
        self.check_unique_tags(warnings)

    #def _initialize_check(self, obj, key):##set as decorator
    #    obj_keys_before = list(obj.__dict__.keys())
    #    beh_keys_before = list(obj.behavior[key].__dict__.keys())
    #    obj.behavior[key].initialize(obj)
    #    obj_keys_after = list(obj.__dict__.keys())
    #    beh_keys_after = list(obj.behavior[key].__dict__.keys())
    #    obj.behavior[key]._created_obj_variables = list(set(obj_keys_after) - set(obj_keys_before))
    #    obj.behavior[key]._created_beh_variables = list(set(beh_keys_after) - set(beh_keys_before))

    def initialize_behaviors(self):

        for key, parent, behavior in self.sorted_behavior_execution_list:
            if not behavior.initialize_on_init and not behavior.initialize_last:
                behavior.initialize(parent)
                behavior.check_unused_attrs()

        for key, parent, behavior in self.sorted_behavior_execution_list:
            if behavior.initialize_last:
                behavior.initialize(parent)
                behavior.check_unused_attrs()
                
        for key, parent, behavior in self.sorted_behavior_execution_list:# add quick access
            for tag in behavior.tags:
                if not hasattr(parent, tag):
                    setattr(parent, tag, behavior)


    #######################################
    #Initialization helper
    #######################################

    def set_gene_variables(self, info=True, storage_manager=None):

        if get_gene_mode():
            sys.exit()

        for obj in self.all_objects():
            for key in obj.behavior:
                b = obj.behavior[key]
                b.set_gene_variables()

        if info:
            genome = get_genome()
            if len(genome)>0:
                print('genome:', genome)

        if storage_manager is not None:
            storage_manager.save_param(key='evolution_params', value=get_genome())
            storage_manager.save_param_dict(get_genome())


    def __str__(self):
        neuron_count = np.sum(np.array([ng.size for ng in self.NeuronGroups]))
        synapse_count = np.sum(np.array([sg.src.size*sg.dst.size for sg in self.SynapseGroups]))

        basic_info = '(Neurons: '+str(neuron_count)+'|'+str(len(self.NeuronGroups))+' groups, Synapses: '+str(synapse_count)+'|'+str(len(self.SynapseGroups))+' groups)'

        result = 'Network'+str(self.tags)+basic_info+'{'
        for k in sorted(list(self.behavior.keys())):
            result += str(k)+':'+str(self.behavior[k])
        result += '}'+'\r\n'

        for ng in self.NeuronGroups:
            result += str(ng)+'\r\n'

        used_tags = []
        for sg in self.SynapseGroups:
            tags = str(sg.tags)
            if tags not in used_tags:
                result += str(sg)+'\r\n'
            used_tags.append(tags)

        return result[:-2]

    def check_unique_tags(self,warnings=True):
        unique_tags=[]
        for ng in self.NeuronGroups:

            if len(ng.tags) == 0:
                ng.tags.append('NG')
                print('no tag defined for NeuronGroup. "NG" tag added')

            if ng.tags[0] in unique_tags:
                counts=unique_tags.count(ng.tags[0])
                new_tag=ng.tags[0]+chr(97+counts)
                unique_tags.append(ng.tags[0])
                if warnings:
                    print('Warning: NeuronGroup Tag "'+ng.tags[0]+'" already in use. The first Tag of an Object should be unique and will be renamed to "'+new_tag+'". Multiple Tags can be separated with a "," (NeuronGroup(..., tag="tag1,tag2,..."))')
                ng.tags[0] = new_tag

            else:
                unique_tags.append(ng.tags[0])


    #######################################
    #Iteration simulation
    #######################################

    def simulate_iteration(self, measure_behavior_execution_time=False):

        if measure_behavior_execution_time:
            if not hasattr(self, 'time_measures'):
                self.time_measures={key:0.0 for key, _, _ in self.sorted_behavior_execution_list}

        self.iteration += 1

        for key, parent, behavior in self.sorted_behavior_execution_list:
            if behavior.behavior_enabled and not behavior.empty_iteration_function:
                if measure_behavior_execution_time:
                    start_time = time.time()
                    behavior.iteration(parent)
                    self.time_measures[key] += (time.time() - start_time) * 1000
                else:
                    behavior.iteration(parent)

        if measure_behavior_execution_time:
            return self.time_measures


    def simulate_iterations(self, iterations, batch_size=100, measure_block_time=True, disable_recording=False, batch_progress_update_func=None):

        if type(iterations) is str:
            iterations=self['Clock', 0].time_to_iterations(iterations)

        if type(batch_size) is str:
            batch_size=self['Clock', 0].time_to_iterations(batch_size)

        time_diff=None

        if disable_recording:
            self.recording_off()


        if batch_size==-1:
            outside_it = 1
            block_iterations = iterations
        else:
            outside_it=int(iterations/batch_size)
            block_iterations=batch_size

        out_it=range(int(outside_it))

        for t in range(int(outside_it)):
            if measure_block_time:
                start_time = time.time()
            for i in range(int(block_iterations)):
                self.simulate_iteration()
            if measure_block_time:
                time_diff = (time.time() - start_time) * 1000
                remaining = time_diff * (outside_it-t) / 1000 / 60
                print('\r{}x {}/{} ({}%) {}ms {:.1f}min'.format(block_iterations,t+1, outside_it, int(100/outside_it*(t+1)), int(time_diff), remaining), end='')#, end='')

            if batch_progress_update_func is not None:
                batch_progress_update_func((t+1.0)/int(outside_it)*100.0, self)

        for i in range(iterations%batch_size):
            self.simulate_iteration()

        if disable_recording:
            self.recording_on()

        if measure_block_time:
            print('')

        return time_diff

    #######################################
    # Tagging
    #######################################

    def find_objects(self, key):
        result = super().find_objects(key)

        for ng in self.NeuronGroups:
            result += ng[key]

        for sg in self.SynapseGroups:
            result += sg[key]

        for am in self.analysis_modules:
            result += am[key]

        return result

    def clear_tag_cache(self):

        for obj in self.all_objects():
            obj.clear_cache()

            for k in obj.behavior:
                obj.behavior[k].clear_cache()


    ################################################################################################
    #deprecated#####################################################################################
    ################################################################################################

    @deprecated_warning("add_behaviors_to_object function will be removed in coming versions. Please use obj.add_behaviors or obj.add_behavior instead.")
    def add_behaviors_to_object(self, b_dict, obj):
        obj.add_behaviors(b_dict)

    @deprecated_warning("add_behaviors_to_objects function will be removed in coming versions. Please use obj.add_behaviors or obj.add_behavior instead.")
    def add_behaviors_to_objects(self, b_dict, objs):
        for obj in objs:
            obj.add_behaviors(b_dict)

    '''
    def set_synapses_to_neuron_groups(self):# todo: move to synapse group __init__
        for ng in self.NeuronGroups:
            ng.afferent_synapses = {}
            ng.efferent_synapses = {}

            for sg in self.SynapseGroups:
                for tag in sg.tags+['All']:
                    ng.synapses(afferent, tag) = []
                    ng.efferent_synapses[tag] = []

            for sg in self.SynapseGroups:
                if sg.dst.BaseNeuronGroup == ng:
                    for tag in sg.tags+['All']:
                        ng.synapses(afferent, tag).append(sg)

                if sg.src.BaseNeuronGroup == ng:
                    for tag in sg.tags+['All']:
                        ng.efferent_synapses[tag].append(sg)
    '''