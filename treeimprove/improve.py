import copy

from .s_expression.tree import Tree

# status flags for performance of sets of archive trees
STATUS_PERFECT = 0
STATUS_BETTER = 1
STATUS_WORST = 2
STATUS_NONE = 3

def get_subtree_i_nodes(tree, sub_i_root):
    """Given a tree and the index position of a subtree root 
    node within that tree, returns the indexes of all nodes 
    in the subtree.
    """

    sub_tree_i_nodes = set([])
    to_explore = [sub_i_root]

    # loop while there are still nodes to explore
    while len(to_explore) > 0:
        # get next child node to explore
        i_node = to_explore.pop()
        sub_tree_i_nodes.add(i_node)

        if tree[i_node].left_child == None:
            continue

        left_i_node = tree.index(tree[i_node].left_child)
        right_i_node = tree.index(tree[i_node].right_child)

        to_explore.append(left_i_node)
        to_explore.append(right_i_node)

    return sub_tree_i_nodes

def subtree_crossover(master_tree, i_node, insert_tree):
    """Performs partial crossover by inserting insert_tree at 
    index postion i_node of master_tree.
    """

    # create copy of archive tree to be inserted
    to_add_tree = copy.deepcopy(insert_tree)

    if i_node == 0:
        to_add_tree.ban_rules = copy.deepcopy(
            master_tree.ban_rules)
        return to_add_tree, to_add_tree[0]

    to_remove_root = master_tree[i_node]
    parent_node = master_tree[i_node].parent

    if parent_node.left_child == to_remove_root:
        parent_node.left_child = to_add_tree[0]

    else:
        parent_node.right_child = to_add_tree[0]
    
    to_add_tree[0].parent = parent_node

    # find nodes forming sub tree rooted at i_node
    to_remove_i_nodes = get_subtree_i_nodes(master_tree, i_node)

    new_master_tree = Tree()
    new_master_tree.ban_rules = \
        copy.deepcopy(master_tree.ban_rules)

    for idx, node in enumerate(master_tree):
        if idx in to_remove_i_nodes:
            continue

        new_master_tree.append(node)    

    # insert tree at end of master_tree list
    for node in to_add_tree:
        new_master_tree.append(node)

    return new_master_tree, to_add_tree[0]

def update_master_tree(master_tree, i_node, archtree):
    """Replaces node i_node of the master tree with archtree and
    re-evaluates the master_tree.

    Arguments:
    master_tree -- the tree to be changed
    i_node -- index position of the node (and rooted subtree) to be replaced
    archtree -- archive tree to be inserted.
    """

    orig_master_tree_str = str(master_tree)

    # generate new tree
    master_tree, new_subroot_node = subtree_crossover(
        master_tree, i_node, archtree.tree)

    # re-evaluate master_tree
    master_tree.calc_outputs_up(new_subroot_node)
    master_tree.calc_all_optimals()

    master_tree.calc_nodes_count_wrongs()
    master_tree.calc_nodes_count_twos()
    master_tree.calc_nodes_count_nodes_below()

    # record archtree on banned list for that (i_node, tree)
    master_tree.ban_rules.add_rule(
        orig_master_tree_str, i_node, archtree.arch_index_pos)

    return master_tree

def count_wrong_boolean(mn_optimals, mn_optimals_mask, outputs):
    """Calculates the number of errors for the Boolean case when given
    an optimal array and an output array.
    """

    wrong_count = 0
    for optimal, mask, output in zip(
        mn_optimals, mn_optimals_mask, outputs):
        
        if mask:
            continue
        if optimal != output:
            wrong_count += 1
    return wrong_count

def count_wrong_integer(optimals, outputs):
    """Calculates the number of errors for the finite algebra (integer) 
    case when given an optimal array and an output array.
    """

    wrong_count = 0
    for i in range(len(optimals)):
        optimal = optimals[i]
        out = outputs[i]

        if isinstance(optimal, tuple):
            if out not in optimal:
                wrong_count += 1

        else:
            if out != optimal:
                wrong_count += 1

    return wrong_count

def get_node_options(i_node, master_tree, tree_archive, problem_data):
    """Returns the possible options for replacing the node."""

    # find node in master_tree
    node = master_tree[i_node]

    # record better and worst options for if perfect or better not found 
    min_better_wrong = problem_data.num_fit_tests
    better_arch_trees = []

    min_worst_wrong = None
    worst_arch_trees = []

    avoid_i_arch = master_tree.ban_rules.rules[i_node]

    # dict of node data
    node_data = {}

    # loop over all other subtrees
    for i_arch_tree, archtree in enumerate(tree_archive.archive):

        if i_arch_tree in avoid_i_arch:
            continue

        if problem_data.is_boolean:
            test_count_wrong = count_wrong_boolean(
                node.optimals, node.optimals_mask, archtree.tree.outputs)

        elif problem_data.is_integer:
            test_count_wrong = count_wrong_integer(
                node.optimals, archtree.tree.outputs)

        # check for perfect answer
        if test_count_wrong == 0:

            node_data = {
                'status':STATUS_PERFECT,
                'archtree':archtree,
                'arch_tree_size':archtree.tree_size,
                'min_wrong':0,
                'count_below':node.nodes_below_count,
            }

            return node_data

        # check for better but not perfect
        elif test_count_wrong < node.wrong_count:

            if test_count_wrong < min_better_wrong:
                min_better_wrong = test_count_wrong
                better_arch_trees = [archtree]
                
            elif test_count_wrong == min_better_wrong:
                better_arch_trees.append(archtree)

            continue

        # check for worst
        if test_count_wrong > node.wrong_count:
            
            # check for first worst
            if min_worst_wrong == None:
                min_worst_wrong = test_count_wrong
                worst_arch_trees = [archtree]
                continue

            if test_count_wrong < min_worst_wrong:
                min_worst_wrong = test_count_wrong
                worst_arch_trees = [archtree]
                continue

            if test_count_wrong == min_worst_wrong:
                worst_arch_trees.append(archtree)
                continue

    if better_arch_trees:
        node_data = {
            'status':STATUS_BETTER,
            'better_arch_trees':better_arch_trees,
            
            'archtree_sizes':[archtree.tree_size 
                for archtree in better_arch_trees],

            'min_wrong':min_better_wrong,
            'count_below':node.nodes_below_count,
        }

        return node_data

    elif worst_arch_trees:
        node_data = {
            'status':STATUS_WORST,
            'worst_arch_trees':worst_arch_trees,

            'archtree_sizes':[archtree.tree_size 
                for archtree in worst_arch_trees],

            'min_wrong':min_worst_wrong,
            'count_below':node.nodes_below_count,
        }

        return node_data

    else:
        node_data = {
            'status':STATUS_NONE,
            'count_below':node.nodes_below_count
        }

        return node_data

def get_node_options_smallest(i_node, master_tree, tree_archive, problem_data):
    """Returns the possible options for replacing the node."""

    # find node in master_tree
    node = master_tree[i_node]

    # record better and worst options for if perfect or better not found 
    min_better_wrong = None
    better_arch_trees = []

    min_worst_wrong = None
    worst_arch_trees = []

    # dict of node data
    node_data = {}

    #avoid_i_arch = master_tree.inode_banned_arch[i_node]
    avoid_i_arch = master_tree.ban_rules.get_avoid_indexes(i_node)

    # loop over all other subtrees
    for i_arch_tree, archtree in enumerate(tree_archive.archive):

        if i_arch_tree in avoid_i_arch:
            continue

        if problem_data.is_boolean:
            test_count_wrong = count_wrong_boolean(
                node.optimals, node.optimals_mask, archtree.tree.outputs)

        elif problem_data.is_integer:
            test_count_wrong = count_wrong_integer(
                node.optimals, archtree.tree.outputs)

        # check for perfect answer
        if test_count_wrong == 0:

            node_data = {
                'i_node':i_node,
                'status':STATUS_PERFECT,
                'archtrees':[archtree],
                'archtree_sizes':[archtree.tree_size],
                'min_wrong':0,
                'count_below':node.nodes_below_count,
            }

            return node_data

        # check for better but not perfect
        elif test_count_wrong < node.wrong_count:

            # check for first worst
            if min_better_wrong == None:
                min_better_wrong = test_count_wrong
                better_arch_trees = [archtree]
                continue

            if test_count_wrong < min_better_wrong:
                min_better_wrong = test_count_wrong
                better_arch_trees = [archtree]
                
            elif test_count_wrong == min_better_wrong:
                better_arch_trees.append(archtree)

            continue

        # check for worst
        if test_count_wrong > node.wrong_count:
            
            # check for first worst
            if min_worst_wrong == None:
                min_worst_wrong = test_count_wrong
                worst_arch_trees = [archtree]
                continue

            if test_count_wrong < min_worst_wrong:
                min_worst_wrong = test_count_wrong
                worst_arch_trees = [archtree]
                continue

            if test_count_wrong == min_worst_wrong:
                worst_arch_trees.append(archtree)
                continue

    if better_arch_trees:
        node_data = {
            'i_node':i_node,
            'status':STATUS_BETTER,
            'archtrees':better_arch_trees,
            
            'archtree_sizes':[archtree.tree_size 
                for archtree in better_arch_trees],

            'min_wrong':min_better_wrong,
            'count_below':node.nodes_below_count,
        }

        return node_data

    elif worst_arch_trees:
        node_data = {
            'i_node':i_node,
            'status':STATUS_WORST,
            'archtrees':worst_arch_trees,

            'archtree_sizes':[archtree.tree_size 
                for archtree in worst_arch_trees],

            'min_wrong':min_worst_wrong,
            'count_below':node.nodes_below_count,
        }

        return node_data

    else:
        node_data = {
            'i_node':i_node,
            'status':STATUS_NONE,
            'count_below':node.nodes_below_count,
        }

        return node_data