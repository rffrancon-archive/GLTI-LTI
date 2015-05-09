import random
from operator import itemgetter, attrgetter

from . import improve
from .archive import TreeForArchive
from .s_expression import gen_tree

def weighted_choice(choices):
    """Given a list of ordered selections c and associated
    selection probabilities w, this function selects and returns 
    one of the choices at random.

    Arguments:
    choices -- a list of (c, w) elements
    c -- object returned if element selected
    w -- probability of selecting element.
    """
    total = sum(w for c, w in choices)
    r = random.uniform(0, total)
    upto = 0
    for c, w in choices:
        if upto + w > r:
            return c
        upto += w

def select_by_archtree_size(archtrees):
    """Given a list of archive trees, selects and returns one of those
    trees at random using probabilistic weighting by tree size.
    """

    # sort by increaing tree size
    ordered_trees = sorted(archtrees, key=attrgetter("tree_size"))

    # assign selection probabilities based on rank
    probs = []
    prob = len(ordered_trees)

    for i_archtree, archtree in enumerate(ordered_trees):
        
        if i_archtree == 0:
            probs.append(prob)
            continue

        archtree_m1 = ordered_trees[i_archtree-1]

        # only decrease ranking if arch tree is larger than previous
        if archtree.tree_size != archtree_m1.tree_size:
            prob -= 1
            probs.append(prob)
            continue

        probs.append(prob)

    # create list for random selection
    choices = []
    for order_tree, prob in zip(ordered_trees, probs):
        choices.append((order_tree, prob))
    choices.reverse()

    return weighted_choice(choices)

def select_visited_node(visited_nodes_data, master_tree_size, 
    problem_data, node_constructor):
    """Select node from those which have already been visited.
    """

    # list of nodes which have 'worst'
    nodes_worst = []

    # number of nodes below for each node
    min_below_count = None
    inode_min_below = None

    # loop over all visited nodes
    for i_node, node_data in visited_nodes_data.items():

        # record the lowest min below count i_node
        if min_below_count == None:
            min_below_count = node_data['count_below']
            inode_min_below = i_node
        elif node_data['count_below'] < min_below_count:
            min_below_count = node_data['count_below']
            inode_min_below = i_node

        node_data['i_node'] = i_node

        if node_data['status'] == improve.STATUS_WORST:
            nodes_worst.append(node_data)

    # check for: none of the nodes have a 'worst' tree
    if not nodes_worst:
        # generate a random tree of depth 1
        rand_tree = gen_tree.generate_full_tree(1, problem_data, node_constructor)
        
        # evaluate tree statistics
        rand_tree.calc_all_outputs()
        rand_tree.calc_all_optimals()
        rand_tree.calc_nodes_count_wrongs()
        rand_tree.calc_nodes_count_twos()

        # wrapp in archive object for convenience
        archtree = TreeForArchive(rand_tree)
        status = 'rand'

        return inode_min_below, archtree, status

    # increasing node_count_below then min_worst_wrong
    ordered_nodes = sorted(nodes_worst, key=itemgetter('count_below', 'min_wrong'))

    # keep the top 3 ranked nodes
    ordered_nodes = ordered_nodes[:3]

    # assign probabilities based on rank
    probs = []
    prob = len(ordered_nodes)
    for i, node_data in enumerate(ordered_nodes):
        
        if i == 0:
            probs.append(prob)
            continue

        node_data_m1 = ordered_nodes[i-1]

        # dont change rank if count_below is the same
        if node_data['count_below'] != node_data_m1['count_below']:
            prob -= 1
            probs.append(prob)
            continue

        probs.append(prob)

    # create list for random selection
    choices = []
    for order_node, prob in zip(ordered_nodes, probs):
        choices.append((order_node, prob))
    choices.reverse()

    selected_node_data = weighted_choice(choices)
    
    # probabilistically select one of worst archtrees based on size
    worst_archtrees = selected_node_data['worst_arch_trees']
    selected_archtree = select_by_archtree_size(worst_archtrees)

    return selected_node_data['i_node'], selected_archtree, 'worst'

def update_unvis_ordered_nodes(visited_i_node, unvis_ordered_nodes):
    """Deletes entry visited_i_node from unvis_ordered_nodes."""

    # find correct list index
    remove_idx = None
    for i_elem, (_, _, i_node) in enumerate(unvis_ordered_nodes):
        if i_node == visited_i_node:
            remove_idx = i_elem
            break

    if remove_idx == None:
        return unvis_ordered_nodes

    # delete element
    del unvis_ordered_nodes[remove_idx]
    return unvis_ordered_nodes

def gen_init_unvis_ordered_nodes(master_tree):
    """Returns the initial node ordering for the master tree."""
    
    # gather any unvisited nodes
    unvis_ordered_nodes = []
    for i_node, node in enumerate(master_tree):
        # ignore node if cant be improved
        if node.wrong_count == 0:
            continue
        unvis_ordered_nodes.append((node.wrong_count, node.twos_count, i_node))

    # all nodes visited
    if not unvis_ordered_nodes:
        return None

    # increaing error
    unvis_ordered_nodes = sorted(unvis_ordered_nodes, key=itemgetter(0))
    
    # decreasing number of hashes (twos_count)
    unvis_ordered_nodes = sorted(unvis_ordered_nodes, key=itemgetter(1), reverse=True)

    return unvis_ordered_nodes

def get_with_wrong_nodes(master_tree):
    """Get unordered list of nodes which have wrong_count != 0."""
    with_wrong_nodes = []
    # loop all nodes in master tree
    for i_node, node in enumerate(master_tree):
        # skip nodes which don't have errors
        if node.wrong_count == 0:
            continue
        with_wrong_nodes.append(
            (node.wrong_count, node.twos_count, i_node))
    return with_wrong_nodes

def select_unvisited_node(unvis_ordered_nodes):
    """Returns i_node of unvisited node.

    Arguments:
    unvis_ordered_nodes -- list of elements: (wrong_count, twos_count, i_node).
    """

    # check if all nodes visited
    if not unvis_ordered_nodes:
        return None

    # assign probabilities based on rank
    probs = []
    prob = len(unvis_ordered_nodes)
    for i_elem, elem in enumerate(unvis_ordered_nodes):
        if i_elem == 0:
            probs.append(prob)
            continue
        elem_m1 = unvis_ordered_nodes[i_elem - 1]
        elem = unvis_ordered_nodes[i_elem]

        # if change in wrong_counts and twos_counts give different rank
        if elem_m1[0] != elem[0] and elem_m1[1] != elem[1]:
            prob -= 1
            probs.append(prob)
            continue

        probs.append(prob)

    # create list for random selection
    choices = []
    for order_node, prob in zip(unvis_ordered_nodes, probs):
        choices.append((order_node, prob))
    choices.reverse()

    # select i_node
    _, _, i_node = weighted_choice(choices)
    return i_node

def find_best_smallest_archtree(chosen_archtrees, problem_data, node_constructor):
    """Given a dictionary, chosen_archtrees, of node data returns
    selected i_node and chosen archtree for greedily minimising master_tree size."""

    # get i_node keys from dictionary
    i_nodes = list(chosen_archtrees)

    # no archtree will do, generate a random one
    if chosen_archtrees[i_nodes[0]]['status'] == improve.STATUS_NONE:
        # select node for replacement at random from master tree
        i_node = random.choice(i_nodes)

        # generate random tree of depth 1
        rand_tree = gen_tree.generate_full_tree(1, problem_data, node_constructor)
        
        # get tree stats
        rand_tree.calc_all_outputs()
        rand_tree.calc_all_optimals()
        rand_tree.calc_nodes_count_wrongs()
        rand_tree.calc_nodes_count_twos()

        # wrap in archive object for simplicity
        return i_node, TreeForArchive(rand_tree)

    # find node with lowest min_wrong
    best_min_wrong = chosen_archtrees[i_nodes[0]]['min_wrong']
    best_i_nodes = set([i_nodes[0]])

    for i_node in i_nodes:
        node_data = chosen_archtrees[i_node]
        min_wrong = node_data['min_wrong']

        if min_wrong < best_min_wrong:
            best_min_wrong = min_wrong
            best_i_nodes = set([i_node])

        elif min_wrong == best_min_wrong:
            best_i_nodes.add(i_node)

    # from best_i_nodes find archtree for minimising master_tree size
    best_i_nodes_i_trees = None
    best_min_diff_node_count = None

    for i_node in best_i_nodes:
        node_data = chosen_archtrees[i_node]

        count_below = node_data['count_below']
        archtree_sizes = node_data['archtree_sizes']

        diff_node_counts = [tree_size-count_below for tree_size in archtree_sizes]
        min_diff_node_count = min(diff_node_counts)

        i_trees = [i_tree for i_tree, diff_node_count in enumerate(diff_node_counts) 
            if diff_node_count == min_diff_node_count]

        if best_i_nodes_i_trees == None:
            best_i_nodes_i_trees = [(i_node, i_trees)]
            best_min_diff_node_count = min_diff_node_count
            continue

        if min_diff_node_count < best_min_diff_node_count:
            best_i_nodes_i_trees = [(i_node, i_trees)]
            best_min_diff_node_count = min_diff_node_count

        elif min_diff_node_count == best_min_diff_node_count:
            best_i_nodes_i_trees.append((i_node, i_trees))

    i_node, i_trees = random.choice(best_i_nodes_i_trees)
    i_tree = random.choice(i_trees)

    archtree = chosen_archtrees[i_node]['archtrees'][i_tree]

    return i_node, archtree
