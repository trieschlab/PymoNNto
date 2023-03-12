from PymoNNto import *
import scipy.cluster.hierarchy as sch
import pandas as pd

class Classifier_base(AnalysisModule):

    def initialize(self, neurons):
        self.add_tag('classifier')
        self.add_tag('cluster_matrix_classifier')
        self.corrMatrices={}

    def get_cluster_matrix(self, key):
        if key in self.corrMatrices:
            classification = self.get_results()[key]#self.last_call_result()
            idx = np.argsort(classification)
            return self.corrMatrices[key].iloc[idx, :].T.iloc[idx, :], idx #[idx, :].T.iloc[idx, :]
        else:
            print('module has to be executed first.')

    def get_data_matrix(self, neurons):
        return #overrride

    def execute(self, neurons, sensitivity=2):
        print('computing cluster classes...')

        data = self.get_data_matrix(neurons)

        mask = np.sum(data, axis=1) > 0
        #mask = np.sum(data, axis=0) > 0#test!
        self.update_progress(10)

        df = pd.DataFrame(data[mask])  # .T
        #df = pd.DataFrame(data[:, mask])  # .T#test!
        self.corrMatrix = df.corr()
        self.update_progress(40)

        self.corrMatrices[self.current_key] = self.corrMatrix

        pairwise_distances = sch.distance.pdist(self.corrMatrix)
        self.update_progress(60)
        linkage = sch.linkage(pairwise_distances, method='complete')
        self.update_progress(70)
        cluster_distance_threshold = pairwise_distances.max() / sensitivity
        idx_to_cluster_array = sch.fcluster(linkage, cluster_distance_threshold, criterion='distance')
        self.update_progress(90)

        #result = np.zeros(data.shape[0]) - 1
        #result = np.zeros(data.shape[1]) - 1#test!

        #print(result.shape, mask, idx_to_cluster_array)
        result = idx_to_cluster_array
        #result[mask] = idx_to_cluster_array

        #match_groups
        if self.current_key in self.result_storage:
            old = self.result_storage[self.current_key]
            new = result.copy()

            oc = np.max(old) + 1
            nc = np.max(new) + 1
            mc = np.maximum(oc, nc)
            map_matrix = np.zeros((int(mc), int(mc)))

            for c in np.unique(old):
                old_c_indx = np.where(old == c)[0]
                values = new[old_c_indx]
                for v in values:
                    map_matrix[int(c), int(v)] += 1

            mapping = {}
            for _ in range(int(nc)):
                oi, ni = np.unravel_index(map_matrix.argmax(), map_matrix.shape)
                map_matrix[oi, :] = -1
                map_matrix[:, ni] = -1
                mapping[ni] = oi
                result[new == ni] = oi
            print('applied class mapping from old state (new_c:old_c)', mapping)
        return result #classification is stored/updated in the results list

'''
old = np.array([2,3,2,1,1,0])
new = np.array([1,0,1,2,1,0])

oc = np.max(old) + 1
nc = np.max(new) + 1
mc = np.maximum(oc, nc)
map_matrix = np.zeros((int(mc), int(mc)))

for c in np.unique(old):
    old_c_indx = np.where(old == c)[0]
    values = new[old_c_indx]
    for v in values:
        map_matrix[int(c), int(v)] += 1

result = np.zeros(new.shape)

mapping = {}
for _ in range(int(nc)):
    oi, ni = np.unravel_index(map_matrix.argmax(), map_matrix.shape)
    print(oi, ni)
    map_matrix[oi, :] = -1
    map_matrix[:, ni] = -1
    mapping[ni] = oi
    result[new == ni] = oi

print(result)
print(mapping)
'''



