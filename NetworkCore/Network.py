from time import time
import numpy as np
from PymoNNto.NetworkCore.Base_Attachable_Modules import *
from PymoNNto.NetworkCore.Synapse_Group import *
from PymoNNto.Exploration.Evolution.Interface_Functions import *
import copy
import time
import sys

class Network(NetworkObjectBase):

    def __init__(self, tag=None, behaviour={}):
        super().__init__(tag, self, behaviour)

        self.NeuronGroups = []
        self.SynapseGroups = []

        self.iteration = 0


    def set_behaviours(self, tag, enabeled):
        if enabeled:
            print('activating', tag)
        else:
            print('deactivating', tag)
        for obj in self.all_objects():
            for b in obj[tag]:
                b.behaviour_enabled = enabeled

    def recording_off(self):
        for obj in self.all_objects():
            obj.recording = False

    def recording_on(self):
        for obj in self.all_objects():
            obj.recording = True

    def all_objects(self):
        return [self]+self.NeuronGroups+self.SynapseGroups

    def all_behaviours(self):
        result = []
        for obj in self.all_objects():
            for beh in obj.behaviour.values():
                result.append(beh)
        return result

    def clear_recorder(self, keys=None):
        for obj in self.all_objects():
            for key in obj.behaviour:
                if (keys is None or key in keys) and hasattr(obj.behaviour[key], 'clear_recorder'):
                    obj.behaviour[key].clear_recorder()

    def set_gene_variables(self, info=True, storage_manager=None):

        if get_gene_mode():
            sys.exit()

        for obj in self.all_objects():
            for key in obj.behaviour:
                b = obj.behaviour[key]
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
        for k in sorted(list(self.behaviour.keys())):
            result += str(k)+':'+str(self.behaviour[k])
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


    def find_objects(self, key):
        result = super().find_objects(key)

        for ng in self.NeuronGroups:
            result += ng[key]

        for sg in self.SynapseGroups:
            result += sg[key]

        for am in self.analysis_modules:
            result += am[key]

        return result

    def initialize(self, info=True, warnings=True, storage_manager=None):

        self.set_gene_variables(info=info, storage_manager=storage_manager)

        if info:
            desc=str(self)
            print(desc)
            if storage_manager is not None:
                storage_manager.save_param('info', desc)

        self.set_synapses_to_neuron_groups()
        self.behaviour_timesteps = []

        for obj in self.all_objects():
            for b_key in obj.behaviour:
                self._add_key_to_sorted_behaviour_timesteps(b_key)

        self.set_variables()
        self.check_unique_tags(warnings)

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



    def _add_key_to_sorted_behaviour_timesteps(self, key):
        if key not in self.behaviour_timesteps:
            self.behaviour_timesteps.append(key)
            self.behaviour_timesteps.sort()




    def clear_tag_cache(self):

        for obj in self.all_objects():
            obj.clear_cache()

            for k in obj.behaviour:
                obj.behaviour[k].clear_cache()

    def _set_variables_check(self, obj, key):
        obj_keys_before = list(obj.__dict__.keys())
        beh_keys_before = list(obj.behaviour[key].__dict__.keys())
        obj.behaviour[key].set_variables(obj)
        obj_keys_after = list(obj.__dict__.keys())
        beh_keys_after = list(obj.behaviour[key].__dict__.keys())
        obj.behaviour[key]._created_obj_variables = list(set(obj_keys_after) - set(obj_keys_before))
        obj.behaviour[key]._created_beh_variables = list(set(beh_keys_after) - set(beh_keys_before))

    def set_variables(self):

        for timestep in self.behaviour_timesteps:

            for obj in self.all_objects():

                if timestep in obj.behaviour:
                    if not obj.behaviour[timestep].set_variables_on_init:
                        self._set_variables_check(obj, timestep)
                        #obj.behaviour[timestep].set_variables(obj)
                        obj.behaviour[timestep].check_unused_attrs()


    def set_synapses_to_neuron_groups(self):
        for ng in self.NeuronGroups:

            ng.afferent_synapses = {'All':[]}
            ng.efferent_synapses = {'All':[]}

            for sg in self.SynapseGroups:
                for tag in sg.tags:
                    ng.afferent_synapses[tag] = []
                    ng.efferent_synapses[tag] = []

            for sg in self.SynapseGroups:
                if sg.dst.BaseNeuronGroup == ng:
                    for tag in sg.tags+['All']:
                        ng.afferent_synapses[tag].append(sg)

                if sg.src.BaseNeuronGroup == ng:
                    for tag in sg.tags+['All']:
                        ng.efferent_synapses[tag].append(sg)


    def simulate_iteration(self, measure_behaviour_execution_time=False):

        if measure_behaviour_execution_time:
            time_measures={ts:0.0 for ts in self.behaviour_timesteps}

        self.iteration += 1
        for timestep in self.behaviour_timesteps:

            for net_obj in self.all_objects():
                net_obj.iteration=self.iteration
                if timestep in net_obj.behaviour and net_obj.behaviour[timestep].behaviour_enabled:
                    if measure_behaviour_execution_time:
                        start_time = time.time()
                        net_obj.behaviour[timestep].new_iteration(net_obj)
                        time_measures[timestep] += (time.time() - start_time) * 1000
                    else:
                        net_obj.behaviour[timestep].new_iteration(net_obj)

        if measure_behaviour_execution_time:
            return time_measures


    def simulate_iterations(self, iterations, batch_size=-1, measure_block_time=True, disable_recording=False, batch_progress_update_func=None):

        if type(iterations) is str:
            iterations=self['Clock', 0].time_to_iterations(iterations)

        time_diff=None

        if disable_recording:
            self.recording_off()


        if batch_size==-1:
            outside_it = 1
            block_iterations = iterations
        else:
            outside_it=int(iterations/batch_size)
            block_iterations=batch_size

        for t in range(int(outside_it)):
            if measure_block_time:
                start_time = time.time()
            for i in range(int(block_iterations)):
                self.simulate_iteration()
            if measure_block_time:
                time_diff = (time.time() - start_time) * 1000
                remaining = time_diff * (outside_it-t) / 1000 / 60
                print('\r{}xBatch: {}/{} ({}%) {}ms {}min'.format(block_iterations,t+1, outside_it, int(100/outside_it*(t+1)), int(time_diff), int(remaining)), end='')#, end='')

            if batch_progress_update_func is not None:
                batch_progress_update_func((t+1.0)/int(outside_it)*100.0, self)

        for i in range(iterations%batch_size):
            self.simulate_iteration()

        if disable_recording:
            self.recording_on()

        if measure_block_time:
            print('')

        return time_diff

    ################################################################################################
    #deprecated#####################################################################################
    ################################################################################################

    @deprecated_warning("add_behaviours_to_object function will be removed in coming versions. Please use obj.add_behaviours or obj.add_behaviour instead.")
    def add_behaviours_to_object(self, b_dict, obj):
        obj.add_behaviours(b_dict)

    @deprecated_warning("add_behaviours_to_objects function will be removed in coming versions. Please use obj.add_behaviours or obj.add_behaviour instead.")
    def add_behaviours_to_objects(self, b_dict, objs):
        for obj in objs:
            obj.add_behaviours(b_dict)