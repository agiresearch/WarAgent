import networkx as nx
import numpy as np
from sklearn.metrics.cluster import mutual_info_score
import itertools
# def construct_graph(edges):
#     g = nx.Graph()
#     nodes  = [i in range(1, 9)]
#     for node in nodes:
#         g.add_node(i)
#     for edge in edges:
#         g.add_edges_from(edges)
        
#     return g

# [Britain, France, Germany, Austria, Russia, Serbia, USA, Ottoman]

gt_edges = [(1,2), (3,4), (5,6), (2,5), (3,8)] # alliance

# gt_edges = [(4,6), (5,4), (3,5), (3,2), (1,3)] # war

# gt_edges = [6,4,5,3,2,1,8] # mobilization

# A -> S (July 28), R -> A (July 30), G -> R (Aug 1), G -> F (Aug 3), B-> G (Aug 4), S -> G (Aug 6), F -> A (Aug 11),  B -> A (Aug 12)

# August 2: Germany invades Luxembourg. Western Skirmish at Joncherey, first military action on the Western Front.
# August 4: German invasion of Belgium (1914)[19] to outflank the French army. Rape of Belgium

# August 5: Battle of Liège. The Germans besiege and then capture the fortresses of Liège, Belgium.

# June 28 , 1914 -- Aug 12, 1914

# gt_graph = construct_graph(edges)

# [Britain, France, Germany, Austria, Russia, Serbia, USA, Ottoman]

simulated_edges = [
    [(1,2), (3,4), (5,6), (2,5), (5,7)],
    [(1,2), (3,4), (5,6), (5,8), (2,7)],
    [(3,4), (5,6), (1,4), (1,2), (1,3)],
    [(1,2), (5,6), (2,5), (3,4)],
    [(1,2), (5,6), (3,4), (5,8)]
]

# simulated_edges = [
#     [(4,6), (3,6), (3,5), (3,2), (5,4), (2,4), (1,3)],
#     [(4,6), (3,6), (5,4), (3,5), (4,8), (3,8)],
#     [(4,6), (5,4), (3,5), (3,6), (1,5), (1,6), (2,5), (2,6)],
#     [(4,6), (5,4), (3,5)],
#     [(4,6), (5,4), (3,5), (4,8)]
# ] # war

# simulated_edges = [
#     [4,6,5,3,2,1],
#     [6,4,5,3,2,8,1,7],
#     [6,4,5,3,1,2],
#     [6,4,5,3,2,1,8],
#     [6,4,5,3,2,1,8]
# ] # mobilization

# distances = []
    
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
