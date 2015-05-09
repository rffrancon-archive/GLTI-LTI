import copy
import time

import treeimprove as ti
from treeimprove.problem_data.problem_data_integer \
    import ProblemDataInteger as ProblemData
from treeimprove.s_expression.node import NodeInteger as node_constructor
import treeimprove.s_expression.gen_tree as gen_tree

def run(paramaters):
    benchmark_name = paramaters['benchmark_name']

    max_archive_size = paramaters['max_archive_size']
    archive_tree_deapth = paramaters['archive_tree_deapth']
    max_time = paramaters['max_time']

    verbose = paramaters['verbose']

    if verbose:
        print(benchmark_name)

    logbook = ti.utilities.Logbook()
    logbook.header = [
        'iteration', 'len_master_tree', 
        'count_wrongs', 'total_wrongs', 
        'picked_node', 'status'
    ]

    start_time = time.time()

    # generate problem object
    problem_data = ProblemData(benchmark_name)

    # make unevaluated trees for archive
    trees_uneval = gen_tree.gen_all_depth_trees(
        archive_tree_deapth, problem_data, node_constructor)

    if verbose:
        print('num pre-archive trees : ', len(trees_uneval))
    
    # initiate archive and add trees_uneval
    tree_archive = ti.archive.TreeArchive(
        max_archive_size, split_subtrees_flag=False, verbose=verbose)
    tree_archive.populate_archive(trees_uneval)

    archive_size = len(tree_archive.archive)
    if verbose:
        print('archive_size : ', archive_size)

    if max_archive_size != None:
        if archive_size != max_archive_size:
            print('archive_size != max_archive_size')
            print('archive_size : ', archive_size)
            print('max_archive_size : ', max_archive_size)
            return None

    # pick best (or smallest if equal) tree from archive as master tree
    best_wrong_count = None
    best_i_arch_tree = None
    master_tree = None

    for i_arch_tree, arch_tree in enumerate(tree_archive.archive):
        tree = arch_tree.tree
        
        tree.root_node.optimals = problem_data.target_outputs
        wrong_count = tree.root_node.count_wrongs()
        tree.root_node.optimals = []

        if best_wrong_count == None:
            best_wrong_count = wrong_count
            best_i_arch_tree = i_arch_tree
            master_tree = copy.deepcopy(tree_archive.archive[best_i_arch_tree].tree)
            continue

        if wrong_count < best_wrong_count:
            best_wrong_count = wrong_count
            best_i_arch_tree = i_arch_tree
            master_tree = copy.deepcopy(tree_archive.archive[best_i_arch_tree].tree)
            continue

        if wrong_count == best_wrong_count and len(tree) < len(master_tree):
            best_wrong_count = wrong_count
            best_i_arch_tree = i_arch_tree
            master_tree = copy.deepcopy(tree_archive.archive[best_i_arch_tree].tree)
            continue

    master_tree.ban_rules.add_rule('', 0, best_i_arch_tree)

    # calculate all statistics for master_tree
    master_tree.calc_all_outputs()
    master_tree.calc_all_optimals()

    master_tree.calc_nodes_count_wrongs()
    master_tree.calc_nodes_count_twos()
    master_tree.calc_nodes_count_nodes_below()

    logbook.record(iteration=0, len_master_tree=len(master_tree), 
        count_wrongs=master_tree[0].wrong_count, 
        total_wrongs=master_tree.total_wrongs,
        picked_node=None, status=None)

    if verbose:
        print(logbook.stream)

    solution_found_flag = False
    current_time = 0
    
    for i_iter in range(1, int(1e6)):

        # getmlist of nodes which have some wrong outputs
        wrong_nodes = ti.select.get_with_wrong_nodes(master_tree)

        none = {}
        worst = {}
        better = {}
        perfect = {}

        master_tree.ban_rules.set_master_tree_str(master_tree)

        for wrong_count, twos_count, i_node in wrong_nodes:
            
            node_data = ti.improve.get_node_options_smallest(
                i_node, master_tree, tree_archive, problem_data)

            if node_data['status'] == ti.improve.STATUS_NONE:
                none[i_node] = node_data

            elif node_data['status'] == ti.improve.STATUS_WORST:
                worst[i_node] = node_data

            elif node_data['status'] == ti.improve.STATUS_BETTER:
                better[i_node] = node_data

            elif node_data['status'] == ti.improve.STATUS_PERFECT:
                perfect[i_node] = node_data

        chosen_archtrees = None

        # check for at least one perfect
        if perfect:
            chosen_archtrees = perfect
            status = 'perfect'

        elif better:
            chosen_archtrees = better
            status = 'better'

        elif worst:
            chosen_archtrees = worst
            status = 'worst'

        elif none:
            chosen_archtrees = none
            status = 'none'

        # find best size reducing arch_tree
        i_node, arch_tree = ti.select.find_best_smallest_archtree(
            chosen_archtrees, problem_data, node_constructor)

        # insert arch_tree into master_tree
        master_tree = ti.improve.update_master_tree(master_tree, i_node, arch_tree)

        logbook.record(
            iteration=i_iter, 
            len_master_tree=len(master_tree), 
            count_wrongs=master_tree[0].wrong_count,
            total_wrongs=master_tree.total_wrongs,
            picked_node=i_node, 
            status=status
        )

        if i_iter%100 == 0:
            current_time = time.time() - start_time

            if verbose:
                print('current_time : ', current_time)
        
        if verbose:
            print(logbook.stream)
            #print('current time : ', current_time)

        if current_time > max_time:
            break

        # check for perfect master_tree solution
        if master_tree[0].wrong_count == 0:
            solution_found_flag = True
            break

    end_time = time.time()
    time_taken = end_time - start_time

    # count nodes which are operators
    num_op = 0
    for node in master_tree:
        if node.type == 'op':
            num_op += 1

    results_data = {
        'tree_str':str(master_tree),
        'tree_len':len(master_tree),

        'number_of_operators':num_op,
        'time_taken':time_taken,
        'solution_found_flag':solution_found_flag,
        
        'logbook':logbook, 
        'max_archive_size':max_archive_size,
        'archive_size':archive_size,
        'archive_tree_deapth':archive_tree_deapth,

        'benchmark_name':benchmark_name,
        'alg_name':'small-LTI',
    }

    if verbose:
        print(logbook.stream)
        print('time_taken : ', time_taken)
        print('solution_found_flag : ', solution_found_flag)
        print('tree_len : ', len(master_tree))
        print('number_of_operators : ', num_op)

    return results_data

if __name__ == '__main__':

    benchmark_name = 'D_A1'
    #benchmark_name = 'D_A2'
    #benchmark_name = 'D_A3'
    #benchmark_name = 'D_A4'
    #benchmark_name = 'D_A5'

    #benchmark_name = 'M_A1'
    #benchmark_name = 'M_A2'
    #benchmark_name = 'M_A3'
    #benchmark_name = 'M_A4'
    #benchmark_name = 'M_A5'

    #benchmark_name = 'D_B'
    #benchmark_name = 'M_B'

    paramaters = {
        'benchmark_name':benchmark_name, 

        'max_archive_size':None,
        'archive_tree_deapth':2,
        'max_time':5000,

        'verbose':True,
    }

    run(paramaters)