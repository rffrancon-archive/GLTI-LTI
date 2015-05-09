import operator
import itertools
from collections import defaultdict

from . import benchmarks_integer as benchmarks

def a1(b_vals, c_vals):
    op_def = [
        [2, 1, 2],
        [1, 0, 0],
        [0, 0, 1]
    ]
    ret_vals = [0]*len(b_vals)
    for i in range(len(b_vals)):
        b = b_vals[i]
        c = c_vals[i]
        ret_vals[i] = op_def[b][c]
    return ret_vals

def a2(b_vals, c_vals):
    op_def = [
        [2, 0, 2],
        [1, 0, 2],
        [1, 2, 1]
    ]
    ret_vals = [0]*len(b_vals)
    for i in range(len(b_vals)):
        b = b_vals[i]
        c = c_vals[i]
        ret_vals[i] = op_def[b][c]
    return ret_vals

def a3(b_vals, c_vals):
    op_def = [
        [1, 0, 1],
        [1, 2, 0],
        [0, 0, 0]
    ]
    ret_vals = [0]*len(b_vals)
    for i in range(len(b_vals)):
        b = b_vals[i]
        c = c_vals[i]
        ret_vals[i] = op_def[b][c]
    return ret_vals

def a4(b_vals, c_vals):
    op_def = [
        [1, 0, 1],
        [0, 2, 0],
        [0, 1, 0]
    ]
    ret_vals = [0]*len(b_vals)
    for i in range(len(b_vals)):
        b = b_vals[i]
        c = c_vals[i]
        ret_vals[i] = op_def[b][c]
    return ret_vals

def a5(b_vals, c_vals):
    op_def = [
        [1, 0, 2],
        [1, 2, 0],
        [0, 1, 0]
    ]
    ret_vals = [0]*len(b_vals)
    for i in range(len(b_vals)):
        b = b_vals[i]
        c = c_vals[i]
        ret_vals[i] = op_def[b][c]
    return ret_vals

def b1(b_vals, c_vals):
    op_def = [
        [1, 3, 1, 0],
        [3, 2, 0, 1],
        [0, 1, 3, 1],
        [1, 0, 2, 0]
    ]
    ret_vals = [0]*len(b_vals)
    for i in range(len(b_vals)):
        b = b_vals[i]
        c = c_vals[i]
        ret_vals[i] = op_def[b][c]
    return ret_vals

a_data = defaultdict(dict)

def map_reverse(op, variables):
    """Produces the reverse mapping for the finite algebra op.
    
    Arguments:
    variables -- the numbers used by the operators. For three variable
    operators these variables are: 0, 1, and 2.
    """

    # compute inverse of catagorical finite algebra operator
    all_A_vals = []
    for seq in itertools.product(variables, repeat=max(variables)):
        seq_set = set(seq)
        seq_list = list(seq_set)
        seq_list.sort()
        seq_tuple = tuple(seq_list)
        if seq_tuple not in all_A_vals:
            all_A_vals.append(seq_tuple)
    all_A_vals.append(tuple(variables))

    all_data = []

    for b in variables:
        for c in variables:
            a = op([b], [c])[0]
            all_data.append((a, b, c))

    a_data = defaultdict(dict)
    for a_target in all_A_vals:

        b_allC = defaultdict(set)
        c_allB = defaultdict(set)

        for data in all_data:
            a, b, c = data

            if a in a_target:
                b_allC[b].add(c)
                c_allB[c].add(b)

        a_data[a_target]['b'] = {b:tuple(b_allC[b]) for b in b_allC.keys()}
        a_data[a_target]['c'] = {c:tuple(c_allB[c]) for c in c_allB.keys()}

    for a_vals in a_data.keys():
        missing_b_vals = []
        max_vals = []
        best_b = None
        for val in variables:
            if val not in a_data[a_vals]['b'].keys():
                missing_b_vals.append(val)
            else:
                if len(max_vals) < len(a_data[a_vals]['b'][val]):
                    max_vals = a_data[a_vals]['b'][val]
                    best_b = set([val])

                if max_vals == a_data[a_vals]['b'][val]:
                    best_b.add(val)

        best_b = tuple(best_b)

        missing_c_vals = []
        max_vals = []
        best_c = None
        for val in variables:
            if val not in a_data[a_vals]['c'].keys():
                missing_c_vals.append(val)
            else:
                if len(a_data[a_vals]['c'][val]) > len(max_vals):
                    max_vals = a_data[a_vals]['c'][val]
                    best_c = set([val])

                if max_vals == a_data[a_vals]['c'][val]:
                    best_c.add(val)

        best_c = tuple(best_c)

        for miss_b in missing_b_vals:
            a_data[a_vals]['b'][miss_b] = best_c

        for miss_c in missing_c_vals:
            a_data[a_vals]['c'][miss_c] = best_b

    return a_data

def rev_op(a, other, is_left=False):
    """If is_left is True, we are finding the optimums of 
    node b (other=c), otherwise node c (other=b).
    """

    if type(a) == int:
        a = (a,)

    # finding values of node b, given c
    if is_left:
        ret_val = a_data[a]['c'][other]
        if len(ret_val) == 1:
            return ret_val[0]
        return ret_val

    # finding values of node c, given b
    else:
        ret_val = a_data[a]['b'][other]
        if len(ret_val) == 1:
            return ret_val[0]
        return ret_val

class ProblemDataInteger(object):
    """This class stores all relavant finite algebra (integer) benchmark methods
    and data: Target output array, available operators, input arrays,... etc.
    """

    def __init__(self, benchmark_name):
        self.benchmark_name = benchmark_name

        self.is_boolean = False
        self.is_integer = True

        if self.benchmark_name in ['D_A1', 'M_A1']:
            op = a1
            self.variables = [0, 1, 2]

        if self.benchmark_name in ['D_A2', 'M_A2']:
            op = a2
            self.variables = [0, 1, 2]

        if self.benchmark_name in ['D_A3', 'M_A3']:
            op = a3
            self.variables = [0, 1, 2]

        if self.benchmark_name in ['D_A4', 'M_A4']:
            op = a4
            self.variables = [0, 1, 2]

        if self.benchmark_name in ['D_A5', 'M_A5']:
            op = a5
            self.variables = [0, 1, 2]

        if self.benchmark_name in ['D_A5', 'M_A5']:
            op = a5
            self.variables = [0, 1, 2]

        if self.benchmark_name in ['D_B', 'M_B']:
            op = b1
            self.variables = [0, 1, 2, 3]

        self.operators = [op]

        global a_data
        a_data = map_reverse(op, self.variables)

        '''
        # for checking the psudo-inverse operator mapping by hand
        for a_val in a_data.keys():
            print a_val
            print 'given b, find c : ', a_data[a_val]['b']
            print 'given c, find b : ', a_data[a_val]['c']
            print ''
        exit()
        '''

        self.op_reverse = {
            op : rev_op,
        }

        self.ephemerals = []

        self.input_patterns = self.gen_inputs()

        self.arg_vals = self.gen_arg_vals()
        self.arguments = list(self.arg_vals)

        self.target_outputs = self.gen_targets()

    def __deepcopy__(self, memo):
        """When doing deepcopy of a tree we avoid
        making a copy of this object.
        """
        return self

    def gen_inputs(self):
        """Generate all input arrays."""

        # compute all possible input bit arrays
        if self.benchmark_name in ['D_A1', 'D_A2', 'D_A3', 'D_A4', 'D_A5', 'D_B']:
            input_patterns = [list(seq) for seq in 
                itertools.product(self.variables, repeat=3)]

        elif self.benchmark_name in ['M_A1', 'M_A2', 'M_A3', 'M_A4', 'M_A5']:
            temp = [list(seq) for seq in itertools.product([0, 1], repeat=3)]
            temp += [list(seq) for seq in itertools.product([0, 2], repeat=3)]
            temp += [list(seq) for seq in itertools.product([1, 2], repeat=3)]

            input_patterns = []

            for inp in temp:
                if (inp[0] == inp[2]) and (inp[1] != inp[0]):
                    continue
                if inp in input_patterns:
                    continue
                input_patterns.append(inp)

        elif self.benchmark_name in ['M_B']:
            temp = [list(seq) for seq in itertools.product([0, 1], repeat=3)]
            temp += [list(seq) for seq in itertools.product([0, 2], repeat=3)]
            temp += [list(seq) for seq in itertools.product([1, 2], repeat=3)]

            temp += [list(seq) for seq in itertools.product([0, 3], repeat=3)]
            temp += [list(seq) for seq in itertools.product([1, 3], repeat=3)]
            temp += [list(seq) for seq in itertools.product([2, 3], repeat=3)]

            input_patterns = []

            for inp in temp:
                if (inp[0] == inp[2]) and (inp[1] != inp[0]):
                    continue
                if inp in input_patterns:
                    continue
                input_patterns.append(inp)

        return input_patterns

    def gen_arg_vals(self):
        """Assignes input arrays to arguments."""

        # arg : [vals]
        arg_vals = {}
        for i_arg in range(3):
            arg_vals['ARG' + str(i_arg)] = []

        # set arguments for each fitness case
        for input_point in self.input_patterns:

            if type(input_point) != type([]):
                arg_vals['ARG0'].append(input_point)
                continue
            
            for i_arg, arg_val in enumerate(input_point):
                arg_vals['ARG' + str(i_arg)].append(arg_val)

        return arg_vals

    def gen_targets(self):
        """Generates the target output array."""
        
        if self.benchmark_name in ['D_A1', 'D_A2', 'D_A3', 'D_A4', 'D_A5', 'D_B']:
            objective_func = benchmarks.objective_func_discrim

        elif self.benchmark_name in ['M_A1', 'M_A2', 'M_A3', 'M_A4', 'M_A5', 'M_B']:
            objective_func = benchmarks.objective_func_malcev

        target_outputs = [objective_func(input_pattern) 
            for input_pattern in self.input_patterns]

        return target_outputs

    @property
    def num_fit_tests(self):
        return len(self.input_patterns)
    