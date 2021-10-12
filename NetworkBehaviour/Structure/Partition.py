from PymoNNto.NetworkCore.Behaviour import *
from PymoNNto.NetworkCore.Synapse_Group import *

class Partition(Behaviour):
    visualization_module_inputs = ['s.src.x', 's.src.y', 's.src.z', 's.dst.x', 's.dst.y', 's.dst.z']
    visualization_module_outputs = ['s.network.SynapseGroups']

    set_variables_on_init = True

    def partition(self, synapses, dst_group_masks):  # todo:auto receptive field extraction (blocks dont need to be squared!)

        rf_x, rf_y, rf_z = synapses.get_max_receptive_field_size()

        syn_sub_groups = []

        for dst_mask in dst_group_masks:

            dst_subgroup = synapses.dst.subGroup(dst_mask)

            src_mask = synapses.src.get_subgroup_receptive_field_mask(dst_subgroup, [rf_x, rf_y, rf_z])

            #src_x_start = np.min(dst_subgroup.x) - rf_x
            #src_x_end = np.max(dst_subgroup.x) + rf_x

            #src_y_start = np.min(dst_subgroup.y) - rf_y
            #src_y_end = np.max(dst_subgroup.y) + rf_y

            #src_z_start = np.min(dst_subgroup.z) - rf_z
            #src_z_end = np.max(dst_subgroup.z) + rf_z

            #src_mask = (synapses.src.x >= src_x_start) * (synapses.src.x <= src_x_end) * (synapses.src.y >= src_y_start) * (synapses.src.y <= src_y_end) * (synapses.src.z >= src_z_start) * (synapses.src.z <= src_z_end)

            syn_sub_groups.append(synapses.get_sub_synapse_group(src_mask, dst_mask))

        print('partitioned into', len(syn_sub_groups), 'SynapseGroups')

        # add sub Groups
        for sg in syn_sub_groups:
            sg.tags.append('partitioned')
            synapses.network.SynapseGroups.append(sg)

        # remove original SG
        synapses.network.SynapseGroups.remove(synapses)

        return syn_sub_groups


    def set_variables(self, synapses):

        split_size = self.get_init_attr('split_size', 'auto')

        if split_size == 'auto':
            best_block_size = 7
            w = int((synapses.src.width/best_block_size+synapses.dst.width/best_block_size)/2)
            h = int((synapses.src.height/best_block_size+synapses.dst.height/best_block_size)/2)
            d = int((synapses.src.depth / best_block_size + synapses.dst.depth / best_block_size) / 2)
            split_size = [np.maximum(w, 1), np.maximum(h, 1), np.maximum(d, 1)]
            if split_size[0]<3 and split_size[1]<3 and split_size[2]<3:
                return #do not partition in this case

        #split_size = synapses.dst.partition_size()
        dst_sub_masks = synapses.dst.partition_masks(split_size)
        self.partition(synapses, dst_sub_masks)#this removes "synapses" from network and adds new SynapseGroups!


    def new_iteration(self, synapses):
        return

#p=Partition()
#p.visualize_module()