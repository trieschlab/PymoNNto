from time import time
import numpy as np
import random
#from NetworkBehaviour.Input.Activator import *
from NetworkCore.Base import *
from NetworkCore.Synapse_Group import *
import copy

class Network(NetworkObjectBase):

    def __init__(self, tag=None, behaviour={}): #, NeuronGroups = [], SynapseGroups = [], initialize=True,
        super().__init__(tag)

        self.NeuronGroups = []#NeuronGroups
        self.SynapseGroups = []#SynapseGroups

        self.network_behaviour = behaviour
        self.add_behaviour_keys_dict(self.network_behaviour)

        self.iteration = 0

        #if initialize:
        #    self.initialize()

    def set_mechanisms(self, keys, enabeled):
        for key in keys:
            for ng in self.NeuronGroups:
                for mechansim in ng[key]:
                    mechansim.active = enabeled

    def deactivate_mechanisms(self, keys):
        self.set_mechanisms(keys, False)

    def activate_mechanisms(self, keys):
        self.set_mechanisms(keys, True)

    def recording_off(self):
        for ng in self.NeuronGroups:
            ng.recording = False

    def recording_on(self):
        for ng in self.NeuronGroups:
            ng.recording = True

    def clear_recorder(self, keys=[]):
        for ng in self.NeuronGroups:
            for key in ng.behaviour:
                if (keys in [] or key in keys) and hasattr(ng.behaviour[key], 'clear_recorder'):
                    ng.behaviour[key].clear_recorder()

    def set_marked_variables(self, new_params, info=True, storage_manager=None):
        result = []
        result_names = []
        for ng in self.NeuronGroups:
            for key in ng.behaviour:
                b=ng.behaviour[key]
                for variable_key in b.init_kwargs:
                    while type(b.init_kwargs[variable_key]) is str and '[' in b.init_kwargs[variable_key] and ']' in b.init_kwargs[variable_key]:
                        s = b.init_kwargs[variable_key]

                        start = s.index('[')
                        end = s.index(']')
                        internal = s[start+1: end].split('#')
                        default_value = float(internal[0])
                        index = int(internal[1])

                        if new_params is not None and index < len(new_params):
                            default_value = new_params[index]

                        while len(result) <= index:
                            result.append(0)
                            result_names.append('???')
                        result[index] = default_value
                        result_names[index]=variable_key

                        b.init_kwargs[variable_key] = s[:start]+'{:.15f}'.format(default_value).rstrip('0').rstrip('.')+s[end+1:]
                        #print(b.init_kwargs[variable_key])
        if info:
            print(result)
            print(result_names)

        if storage_manager is not None:
            storage_manager.save_param(key='evolution_params', value=result)

        return result

    def find_objects(self, key):
        result = []

        for ng in self.NeuronGroups:
            result += ng[key]

        for sg in self.SynapseGroups:
            result += sg[key]

        return result

    def print_net_info(self):
        neuron_count = np.sum(np.array([ng.size for ng in self.NeuronGroups]))
        sysnape_count = np.sum(np.array([sg.src.size*sg.dst.size for sg in self.SynapseGroups]))

        print('initialize tren... Neurons: ', neuron_count, '|', len(self.NeuronGroups), ' blocks, Synapses: ', sysnape_count, '|', len(self.SynapseGroups),' blocks')

    def initialize(self, evo_replace_param_list=None, info=False, warnings=True):

        if info:
            self.print_net_info()

        if evo_replace_param_list is not None:
            self.set_marked_variables(evo_replace_param_list)

        #self.old_param_list = self.get_all_params()

        self.set_synapses_to_neuron_groups()

        self.behaviour_timesteps = []

        for ng in self.NeuronGroups:
            self.add_behaviour_keys_dict(ng.behaviour)


        self.set_variables()
        #self.save_network_state()

        self.check_unique_tags(warnings)

    def check_unique_tags(self,warnings=True):
        unique_tags=[]
        for ng in self.NeuronGroups:
            if ng.tags[0] in unique_tags:
                counts=unique_tags.count(ng.tags[0])
                new_tag=ng.tags[0]+chr(97+counts)
                unique_tags.append(ng.tags[0])
                if warnings:
                    print('Warning: NeuronGroup Tag "'+ng.tags[0]+'" already in use. The first Tag of an Object should be unique and will be renamed to "'+new_tag+'". Multiple Tags can be sperated with a "," (NeuronGroup(..., tag="tag1,tag2,..."))')
                ng.tags[0] = new_tag

            else:
                unique_tags.append(ng.tags[0])

        #for sg in self.SynapseGroups:
        #    if sg.tags[0] in unique_tags:
        #        print('Warning: NeuronGroup Tag "' + sg.tags[0] + '" already in use. The first Tag of an Object should be unique. Multiple Tags can be sperated with a "," (SynapseGroup(..., tag="tag1,tag2,..."))')
        #    unique_tags.append(sg.tags[0])

    def add_behaviour_key(self, key):
        self.behaviour_timesteps.append(key)
        self.behaviour_timesteps.sort()

    def add_behaviour_keys_dict(self, behaviour_dict):
        for key in behaviour_dict:
            if not key in self.behaviour_timesteps:
                self.add_behaviour_key(key)

    def add_behaviours_to_neuron_groups(self, behaviours, neuron_groups):
        for ng in neuron_groups:
            self.add_behaviours_to_neuron_group(copy.copy(behaviours), ng)

    def add_behaviours_to_neuron_group(self, behaviours, neuron_group):
        self.clear_tag_cache()
        original = behaviours
        #if type(behaviours) == list:
        #    start_key = self.behaviour_timesteps[-1]
        #    d = {}
        #    for b in behaviours:
        #        start_key += 1
        #        d[start_key] = b
        #    behaviours = d

        for key in behaviours:
            neuron_group.behaviour[key] = behaviours[key]
            neuron_group.behaviour[key].set_variables(neuron_group)
            neuron_group.behaviour[key].check_unused_attrs()


        self.add_behaviour_keys_dict(behaviours)
        return original

    def remove_behaviours_from_neuron_groups(self, neuron_groups, keys=[], tags=[]):
        for ng in neuron_groups:
            self.remove_behaviours_from_neuron_group(ng, keys, tags)

    def remove_behaviours_from_neuron_group(self, neuron_group, keys=[], tags=[]):
        found=[]
        found+=keys
        for key in neuron_group.behaviour:
            for tag in tags:
                if tag in neuron_group.behaviour[key].tags:
                    found.append(key)

        found=list(set(found))#unique

        for key in found:
            neuron_group.behaviour.pop(key)

        self.clear_tag_cache()

    def clear_tag_cache(self):
        self.clear_cache()

        for ng in self.NeuronGroups:
            ng.clear_cache()

            for k in ng.behaviour:
                ng.behaviour[k].clear_cache()

        for sg in self.SynapseGroups:
            sg.clear_cache()

    def set_variables(self):
        for timestep in self.behaviour_timesteps:

            if timestep in self.network_behaviour:
                self.network_behaviour[timestep].set_variables(self)
                self.network_behaviour[timestep].check_unused_attrs()

            for ng in self.NeuronGroups:
                if timestep in ng.behaviour:
                    if not ng.behaviour[timestep].run_on_neuron_init_var:
                        ng.behaviour[timestep].set_variables(ng)
                        ng.behaviour[timestep].check_unused_attrs()



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

    def simulate_iteration(self):
        self.iteration+=1
        for timestep in self.behaviour_timesteps:

            if timestep in self.network_behaviour and self.network_behaviour[timestep].behaviour_enabled:#todo: Test
                self.network_behaviour[timestep].new_iteration(self)

            for ng in self.NeuronGroups:
                ng.iteration=self.iteration
                if timestep in ng.behaviour and ng.behaviour[timestep].behaviour_enabled:
                    ng.behaviour[timestep].new_iteration(ng)

    def simulate_iterations(self, iterations, batch_size=-1, measure_block_time=False, disable_recording=False):
        time_diff=None

        if disable_recording:
            self.recording_off()

        #if measure_block_time:
        #    print('batch size: {}'.format(block_iterations))

        if batch_size==-1:
            outside_it = 1
            block_iterations = iterations
        else:
            outside_it=int(iterations/batch_size)
            block_iterations=batch_size

        for t in range(int(outside_it)):
            if measure_block_time:
                start_time = time()
            for i in range(int(block_iterations)):
                self.simulate_iteration()
            if measure_block_time:
                time_diff = (time() - start_time) * 1000

                print('\r{}xBatch: {}/{} ({}%) {:.3f}ms'.format(block_iterations,t+1, outside_it, int(100/outside_it*(t+1)),time_diff), end='')#, end='')

        for i in range(iterations%batch_size):
            self.simulate_iteration()

        if disable_recording:
            self.recording_on()

        return time_diff


    #def partition_Synapse_Groups(self, SynapseGroups=[]):
    #    #todo: make sure that all mechanisms use "s.src" and "s.dst" and not "neurons"!
    #    if SynapseGroups==[]:
    #        SynapseGroups=self.SynapseGroups.copy()

    #    for sg in SynapseGroups:
    #        self.partition_Synapse_Group(sg)

    def partition_Synapse_Group3(self, synapse_group, steps):
        return self.partition_Synapse_Group2(synapse_group, synapse_group.dst.partition(steps))

    def partition_Synapse_Group2(self, synapse_group, dst_groups):#todo:auto receptive field extraction (blocks dont need to be squared!)

        rf_x, rf_y, rf_z = synapse_group.get_max_receptive_field_size()

        syn_sub_groups=[]

        for dst_subgroup in dst_groups:

            src_x_start = np.min(dst_subgroup.x)-rf_x
            src_x_end = np.max(dst_subgroup.x)+rf_x

            src_y_start = np.min(dst_subgroup.y)-rf_y
            src_y_end = np.max(dst_subgroup.y)+rf_y

            src_z_start = np.min(dst_subgroup.z)-rf_z
            src_z_end = np.max(dst_subgroup.z)+rf_z

            src_mask = (synapse_group.src.x >= src_x_start) * (synapse_group.src.x <= src_x_end) * (synapse_group.src.y >= src_y_start) * (synapse_group.src.y <= src_y_end) * (synapse_group.src.z >= src_z_start) * (synapse_group.src.z <= src_z_end)

            sg=SynapseGroup(synapse_group.src.subGroup(src_mask), dst_subgroup)

            syn_sub_groups.append(sg)

            # partition enabled update
            if type(synapse_group.enabled) is np.ndarray:
                mat_mask = dst_subgroup.mask[:, None] * src_mask[None, :]
                sg.enabled = synapse_group.enabled[mat_mask].copy().reshape(sg.get_synapse_mat_dim())

            # copy al attributes
            sgd = synapse_group.__dict__
            for key in sgd:
                if key not in ['src', 'dst', 'enabled']:
                    setattr(sg, key, copy.copy(sgd[key]))

        #add sub Groups
        for sg in syn_sub_groups:
            self.SynapseGroups.append(sg)

        #remove original SG
        self.SynapseGroups.remove(synapse_group)

        return syn_sub_groups


    def partition_Synapse_Group(self, syn_group, receptive_field_size=1, split_size=1):

        src = syn_group.src
        dst = syn_group.dst

        #adjust param
        if type(split_size) is int:
            split_size = [split_size, split_size, split_size]

        if len(split_size) == 2:
            split_size.append(1)

        if type(receptive_field_size) is int:
            receptive_field_size = [receptive_field_size, receptive_field_size, receptive_field_size]

        if len(receptive_field_size) == 2:
            receptive_field_size.append(0)

        # check dimensions
        if hasattr(src, 'width'):
            src_min = [np.min(p) for p in [src.x, src.y, src.z]]
            src_max = [np.max(p) for p in [src.x, src.y, src.z]]
        else:
            src_min = [0, 0, 0]
            src_max = [src.size, 0, 0]

        if hasattr(dst, 'width'):
            dst_min = [np.min(p) for p in [dst.x, dst.y, dst.z]]
            dst_max = [np.max(p) for p in [dst.x, dst.y, dst.z]]
        else:
            dst_min = [0, 0, 0]
            dst_max = [dst.size, 0, 0]

        def get_start_end(step, dim, group='src'):
            if group == 'src':
                start=src_min[dim]+(src_max[dim]-src_min[dim])/split_size[dim]*step-receptive_field_size[dim]
                end=src_min[dim]+(src_max[dim]-src_min[dim])/split_size[dim]*(step+1)+receptive_field_size[dim]
            if group == 'dst':
                start=dst_min[dim]+(dst_max[dim]-dst_min[dim])/split_size[dim]*step
                end=dst_min[dim]+(dst_max[dim]-dst_min[dim])/split_size[dim]*(step+1)
            return start, end

        #calculate sub Groups
        sub_groups = []

        #src_masks = []
        dst_masks = []

        for w_step in range(split_size[0]):          #x_steps
            src_x_start, src_x_end = get_start_end(w_step, 0, 'src')
            dst_x_start, dst_x_end = get_start_end(w_step, 0, 'dst')
            for h_step in range(split_size[1]):      #y_steps
                src_y_start, src_y_end = get_start_end(h_step, 1, 'src')
                dst_y_start, dst_y_end = get_start_end(h_step, 1, 'dst')
                for d_step in range(split_size[2]):  #z_steps
                    src_z_start, src_z_end = get_start_end(d_step, 2, 'src')
                    dst_z_start, dst_z_end = get_start_end(d_step, 2, 'dst')

                    src_mask = (src.x >= src_x_start) * (src.x <= src_x_end) * (src.y >= src_y_start) * (src.y <= src_y_end) * (src.z >= src_z_start) * (src.z <= src_z_end)
                    dst_mask = (dst.x >= dst_x_start) * (dst.x <= dst_x_end) * (dst.y >= dst_y_start) * (dst.y <= dst_y_end) * (dst.z >= dst_z_start) * (dst.z <= dst_z_end)

                    #remove duplicates
                    #for old_src_mask in src_masks:
                    #    src_mask[old_src_mask] *= False

                    for old_dst_mask in dst_masks:
                        dst_mask[old_dst_mask] *= False

                    #print(np.sum(src_mask), np.sum(dst_mask))

                    #src_masks.append(src_mask)
                    dst_masks.append(dst_mask)

                    #import matplotlib.pyplot as plt
                    #plt.scatter(src.x, src.y, c=src_mask)
                    #plt.scatter(dst.x+50, dst.y, c=dst_mask)
                    #plt.show()

                    sg = SynapseGroup(syn_group.src.subGroup(src_mask), syn_group.dst.subGroup(dst_mask))

                    #partition enabled update
                    if type(syn_group.enabled) is np.ndarray:
                        mat_mask = dst_mask[:, None] * src_mask[None, :]
                        sg.enabled = syn_group.enabled[mat_mask].copy().reshape(sg.get_synapse_mat_dim())

                    #copy al attributes
                    sgd=syn_group.__dict__
                    for key in sgd:
                        if key not in ['src', 'dst', 'enabled']:
                            setattr(sg, key, copy.copy(sgd[key]))

                    sub_groups.append(sg)

        #add sub Groups
        for sg in sub_groups:
            self.SynapseGroups.append(sg)

        #remove original SG
        self.SynapseGroups.remove(syn_group)

        return sub_groups









    #def learning_off(self):


    #def learning_on(self):
    #    for ng in self.NeuronGroups:
    #        ng.learning = True

    #def clear_recorder(self):
    #    for ng in self.NeuronGroups:
    #        for key in ng.behaviour:
    #            if isinstance(ng.behaviour[key], )
    #                rr.clear_recorder()


    #def save_network_state(self):
    #    self.new_param_list=self.get_all_params()
    #    self.group_value_dicts={}
    #    for group in self.old_param_list:#same group for both
    #        value_dict={}
    #        for key in self.new_param_list[group]:
    #            if not key in self.old_param_list:
    #                val=getattr(group, key)
    #                t = type(val)
    #                if t == np.ndarray or t == list:
    #                    value_dict[key]=val.copy()
    #                else:
    #                    value_dict[key]=val
    #        self.group_value_dicts[group]=value_dict

    #def reset(self):
    #    for group in self.group_value_dicts:
    #        for key in self.group_value_dicts[group]:
    #            #print(key)
    #            val=self.group_value_dicts[group][key]
    #            t = type(val)
    #            if t == np.ndarray or t == list:
    #                setattr(group, key, val.copy())
    #            else:
    #                setattr(group, key, val)
    #
    #    for timestep in self.behaviour_timesteps:
    #        for ng in self.NeuronGroups:
    #            if timestep in ng.behaviour:
    #                ng.behaviour[timestep].reset()

    #def get_all_params(self):
    #    param_lists={}
    #    for ng in self.NeuronGroups:
    #        param_lists[ng] = [key for key in ng.__dict__]
    #    for sg in self.SynapseGroups:
    #        param_lists[sg] = [key for key in sg.__dict__]
    #    return param_lists

    #def Edge_Connect_Synapse_Group(self):
    #    #todo
    #    return


    #def split_connect(src,src_group, dst_group, x_blocks, y_blocks, receptive_field, network, syn_type):
    #    if x_blocks > 1 or y_blocks > 1:
    #        min_x = np.min(dst_group.x)
    #        max_x = np.max(dst_group.x) + 0.0001
    #        x_steps = np.arange(x_blocks + 1) * ((max_x - min_x) / x_blocks) + min_x

    #        min_y = np.min(dst_group.y)
    #        max_y = np.max(dst_group.y) + 0.0001
    #        y_steps = np.arange(y_blocks + 1) * ((max_y - min_y) / y_blocks) + min_y

            # print(x_steps,y_steps)

            # block_mat = np.empty(shape=(y_blocks, x_blocks), dtype=object)
    #        for y in range(y_blocks):
    #            for x in range(x_blocks):
    #                dst = dst_group.subGroup(
    #                    (dst_group.x >= x_steps[x]) * (dst_group.x < x_steps[x + 1]) * (dst_group.y >= y_steps[y]) * (
    #                                dst_group.y < y_steps[y + 1]))
    #                src = src_group.subGroup((src_group.x >= (x_steps[x] - receptive_field)) * (
    #                            src_group.x < (x_steps[x + 1] + receptive_field)) * (
    #                                                     src_group.y >= (y_steps[y] - receptive_field)) * (
    #                                                     src_group.y < (y_steps[y + 1] + receptive_field)))

    #                sg = SynapseGroup(src, dst, receptive_field, net=network).add_tag(syn_type)
    #    else:
    #        sg = SynapseGroup(src_group, dst_group, receptive_field, net=None).add_tag(syn_type)
    #        network.SynapseGroups.append(sg)

