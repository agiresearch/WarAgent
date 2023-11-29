"""
Copyright 2023 Wenyue Hua

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

__author__ = "Wenyue Hua, Kai Mei"
__copyright__ = "Copyright 2023, WarAgent"
__date__ = "2023/11/28"
__license__ = "Apache 2.0"
__version__ = "0.0.1"

import networkx as nx
import numpy as np
from sklearn.metrics.cluster import mutual_info_score
import itertools

    
######### Jaccard similarity, evaluation metric for war declaration and mobilization
def compute_average_jaccard_score(gt_edges, simulated_edges):
    def jaccard_similarity(g, h):
        i = set(g).intersection(h)
        return round(len(i) / (len(g) + len(h) - len(i)),3)

    scores = []
    for simulated_edge in simulated_edges:
        score = jaccard_similarity(gt_edges, simulated_edge)
        scores.append(score)

    return np.mean(scores)



######### Mutual information of two partitions, evaluation metric for alliance
def create_partitions(relations, all_vertices):

    def merge_tuples(relations):
        sets = [set(t) for t in relations]
        def merge_sets(sets):
            for i in range(len(sets) - 1, 0, -1):
                for j in range(i - 1, -1, -1):
                    if sets[i] & sets[j]: # check for intersection (non-empty -> True)
                        sets[j] |= sets[i] # merge i-th set into j-th set
                        sets.pop(i) # remove i-th set
                        break # terminate inner loop and continue with next i
            return sets
        merged_sets = merge_sets(sets)
        merged_tuples = [tuple(s) for s in merged_sets]
        return merged_tuples

    def flatten(lists):
        return [a for one_list in lists for a in one_list]

    target_partitions = []
    non_single_partitions = merge_tuples(relations)
    target_partitions += non_single_partitions
    for entity in all_vertices:
        if entity not in flatten(non_single_partitions):
            target_partitions.append((entity,))

    return target_partitions


def assign_group_index(partition, all_vertices):
    indices = []
    for entity in all_vertices:
        for index, one_part in enumerate(partition):
            if entity in one_part:
                indices.append(index)
    return indices


def compute_average_alliance_accuracy(gt_edges, simulated_edges, all_vertices):
    target_partitions = create_partitions(gt_edges, all_vertices)
    target_assignment = assign_group_index(target_partitions, all_vertices)

    accuracy_scores = []
    for simulated_partition in simulated_edges:
        simulated_partitions = create_partitions(simulated_partition, all_vertices) 
        simulated_assignment = assign_group_index(simulated_partitions, all_vertices)
        score = mutual_info_score(target_assignment, simulated_assignment)
        accuracy_scores.append(score)
    return np.mean(accuracy_scores)


if __name__ == '__main__':
    all_vertices = [1,2,3,4,5,6,7,8]
    score = compute_average_alliance_accuracy(gt_edges, simulated_edges, all_vertices)
    war_declaration_score = compute_average_jaccard_score(gt_edges, simulated_edges)
    print(score)
