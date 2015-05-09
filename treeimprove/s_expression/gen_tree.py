import copy
import itertools

from .tree import Tree
from ..improve import subtree_crossover

def generate_full_tree(max_deapth, problem_data, Node):
    """Given a maximum depth and a node generator (Node),
    returns a randomly generated full tree.

    Note that depth 0 is a single node.
    """
    
    all_node_deapths = []
    for deapth in range(max_deapth+1):
        
        # make lowest deapth nodes
        deapth_nodes = []

        for i in range(2**(deapth)):

            if deapth == max_deapth:
                leaf_flag = True
            else:
                leaf_flag = False

            # generate node
            node = Node(problem_data)
            node.set_random(leaf_flag)

            deapth_nodes.append(node)

        all_node_deapths.append(deapth_nodes)

    # add into tree root first
    tree = Tree()

    for deapth_nodes in all_node_deapths:
        for node in deapth_nodes:
            tree.append(node)

    # connect nodes together
    all_node_deapths.reverse()
    
    for i in range(max_deapth):
        lower_deapth_nodes = all_node_deapths[i]

        try:
            upper_deapth_nodes = all_node_deapths[i+1]
        except:
            break

        for lower_node in lower_deapth_nodes:
            
            # find empty space for child
            for upper_node in upper_deapth_nodes:
                
                if upper_node.left_child == None:
                    upper_node.left_child = lower_node
                    lower_node.parent = upper_node
                    break

                elif upper_node.right_child == None:
                    upper_node.right_child = lower_node
                    lower_node.parent = upper_node
                    break

    return tree

def get_all_tree_structures(max_depth, problem_data, node_constructor):
    """Returns all bare (blank nodes) tree structures up to max_depth."""
    
    # generate single node tree structure
    node = node_constructor(problem_data)
    single_node_tree = Tree()
    single_node_tree.append(node)

    # generate tripplet tree structure
    root_node = node_constructor(problem_data)
    left_node = node_constructor(problem_data)
    right_node = node_constructor(problem_data)

    root_node.left_child = left_node
    root_node.right_child = right_node
    
    left_node.parent = root_node
    right_node.parent = root_node

    root_node.type = 'op'

    tripplet_tree = Tree()
    tripplet_tree += [root_node, left_node, right_node]

    # generate remaining tree structures given max_depth
    unprocessed_trees = [copy.deepcopy(single_node_tree)]
    generated_trees = [copy.deepcopy(single_node_tree)]
    generated_trees_str = set([str(copy.deepcopy(single_node_tree))])

    while len(unprocessed_trees) != 0:
        orig_master_tree = unprocessed_trees.pop()

        # identify all leaf nodes
        leaf_i_nodes = [i_node for i_node, node in enumerate(orig_master_tree)
            if node.left_child == None]
        
        # loop leaf nodes
        for leaf_i_node in leaf_i_nodes:
            master_tree = copy.deepcopy(orig_master_tree)
            
            # make copies of all trees involved
            insert_tree = copy.deepcopy(tripplet_tree)
            
            # insert tree
            new_master_tree, _ = subtree_crossover(
                master_tree, leaf_i_node, insert_tree)

            tree_depth = new_master_tree.calc_max_depth()

            if tree_depth <= max_depth and str(new_master_tree) not in generated_trees_str:
                unprocessed_trees.append(new_master_tree)
                generated_trees.append(new_master_tree)
                generated_trees_str.add(str(new_master_tree))

    return generated_trees

def gen_all_depth_trees(max_depth, problem_data, node_constructor, max_num_trees=40000):
    """Returns all (or limited by max_num_trees) unique trees up to max_depth."""
    # generate raw structural trees only
    raw_trees = get_all_tree_structures(max_depth, problem_data, node_constructor)

    all_trees = []
    for raw_tree in raw_trees:

        leaf_i_nodes = []
        nonleaf_i_nodes = []
        
        # identify all leaf nodes and nonleaf nodes
        for i_node, node in enumerate(raw_tree):
            if node.left_child == None:
                leaf_i_nodes.append(i_node)
            else:
                nonleaf_i_nodes.append(i_node)

        # given number of leaf nodes, make all leaf node values
        all_leaf_vals = [list(seq) for seq in itertools.product(
            problem_data.arguments, repeat=len(leaf_i_nodes))]

        # given number of nonleaf nodes, make all nonleaf node values
        all_nonleaf_vals = [list(seq) for seq in itertools.product(
            problem_data.operators, repeat=len(nonleaf_i_nodes))]

        # make a trees from raw structure
        for leaf_vals in all_leaf_vals:
            for nonleaf_vals in all_nonleaf_vals:
                tree = copy.deepcopy(raw_tree)

                # set properties of leaf nodes
                for leaf_i_node, leaf_val in zip(leaf_i_nodes, leaf_vals):
                    tree[leaf_i_node].type = 'arg'
                    tree[leaf_i_node].name = leaf_val

                # set properties of nonleaf nodes
                for nonleaf_i_node, nonleaf_val in zip(nonleaf_i_nodes, nonleaf_vals):
                    tree[nonleaf_i_node].type = 'op'
                    tree[nonleaf_i_node].operator = nonleaf_val
                    tree[nonleaf_i_node].name = nonleaf_val.__name__

                all_trees.append(tree)

                if len(all_trees) == max_num_trees:
                    return all_trees

    return all_trees

