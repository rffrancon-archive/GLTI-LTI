import time

import treeimprove as ti
from treeimprove.problem_data.problem_data_integer \
    import ProblemDataInteger as ProblemData
from treeimprove.s_expression.node import NodeInteger as node_constructor
import treeimprove.s_expression.gen_tree as gen_tree

def run(paramaters):
    benchmark_name = paramaters['benchmark_name']

    max_archive_size = paramaters['max_archive_size']
    max_time = paramaters['max_time']

    verbose = paramaters['verbose']

    if verbose:
        print(benchmark_name)

    logbook = ti.utilities.Logbook()
    logbook.header = ([
        'iteration', 'len_master_tree', 
        'count_wrongs', 'total_wrongs', 
        'picked_node', 'status'
    ])

    start_time = time.time()

    # generate problem object
    problem_data = ProblemData(benchmark_name)

    # make unevaluated trees for archive
    trees_uneval = [gen_tree.generate_full_tree(
        2, problem_data, node_constructor) for i in range(2500)]

    if verbose:
        print('num pre-archive trees : ', len(trees_uneval))
    
    # initiate archive and add trees_uneval
    tree_archive = ti.archive.TreeArchive(
        max_archive_size, False, memory_efficient=False)
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

    # generate master tree
    master_tree = gen_tree.generate_full_tree(2, problem_data, node_constructor)

    # calculate all statistics for master_tree
    master_tree.calc_all_outputs()
    master_tree.calc_all_optimals()

    master_tree.calc_nodes_count_wrongs()
    master_tree.calc_nodes_count_twos()

    logbook.record(
        iteration=0, len_master_tree=len(master_tree), 
        count_wrongs=master_tree[0].wrong_count, 
        total_wrongs=master_tree.total_wrongs,
        picked_node=None, status=None
    )

    if verbose:
        print(logbook.stream)

    solution_found_flag = False
    current_time = 0

    # i_node : node_data
    visited_nodes_data = {}
    unvis_ordered_nodes = ti.select.gen_init_unvis_ordered_nodes(master_tree)

    end = False
    
    for i_iter in range(1, int(1e6)):

        # pick an unvisited node to improve
        i_node = ti.select.select_unvisited_node(unvis_ordered_nodes)

        # check for some unvisited nodes
        if i_node != None:

            # get node change stratergy
            node_data = ti.improve.get_node_options(
                i_node, master_tree, tree_archive, problem_data)

            status = node_data['status']

            # check for perfect solution
            if status == ti.improve.STATUS_PERFECT:
                status = 'perfect'

                archtree = node_data['archtree']

                master_tree = ti.improve.update_master_tree(master_tree, i_node, archtree)
                
                visited_nodes_data = {}
                unvis_ordered_nodes = ti.select.gen_init_unvis_ordered_nodes(
                    master_tree)

            # check for better solution
            elif status == ti.improve.STATUS_BETTER:
                status = 'better'

                better_arch_trees = node_data['better_arch_trees']
                archtree = ti.select.select_by_archtree_size(better_arch_trees)

                prev_wrong_count = master_tree[0].wrong_count
                prev_outputs = master_tree[0].outputs

                master_tree = ti.improve.update_master_tree(master_tree, i_node, archtree)

                new_wrong_count = master_tree[0].wrong_count
                new_outputs = master_tree[0].outputs

                hip_optimals = master_tree[0].optimals

                if new_wrong_count == prev_wrong_count:
                    end = True
                
                visited_nodes_data = {}
                unvis_ordered_nodes = ti.select.gen_init_unvis_ordered_nodes(
                    master_tree)

            # check for not perfect and not better
            elif (status == ti.improve.STATUS_NONE) or (status == ti.improve.STATUS_WORST):
                status = 'none'

                visited_nodes_data[i_node] = node_data

                unvis_ordered_nodes = ti.select.update_unvis_ordered_nodes(
                    i_node, unvis_ordered_nodes)

        # check for all nodes visited
        else:

            # pick visited node to change
            i_node, archtree, status = ti.select.select_visited_node(
                visited_nodes_data, len(master_tree), problem_data, node_constructor)
            master_tree = ti.improve.update_master_tree(master_tree, i_node, archtree)
            
            visited_nodes_data = {}
            unvis_ordered_nodes = ti.select.gen_init_unvis_ordered_nodes(
                master_tree)

        logbook.record(iteration=i_iter, len_master_tree=len(master_tree), 
            count_wrongs=master_tree[0].wrong_count,
            total_wrongs=master_tree.total_wrongs,
            picked_node=i_node, status=status)

        if i_iter%100 == 0:
            current_time = time.time() - start_time
        
        if verbose and (i_iter%100 == 0):
            print(logbook.stream)
            print('current time : ', current_time)

        if current_time > max_time:
            break

        # check for perfect master_tree solution
        if master_tree[0].wrong_count == 0:
            solution_found_flag = True
            break

    if verbose:
        print(logbook.stream)

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
        'archive_tree_deapth':None,

        'benchmark_name':benchmark_name,
        'alg_name':'LTI',
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
        'max_time':5000,
        'verbose':True,
    }

    run(paramaters)