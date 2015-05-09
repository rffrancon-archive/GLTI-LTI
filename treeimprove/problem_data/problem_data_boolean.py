import itertools
from bitarray import bitarray

from . import benchmarks_boolean

def op_and(b_vals, c_vals):
    """Logical AND operator."""
    a_vals = [False]*len(b_vals)
    for i, (b_val, c_val) in enumerate(zip(b_vals, c_vals)):
        if b_val and c_val:
            a_vals[i] = True
    return bitarray(a_vals)

def op_or(b_vals, c_vals):
    """Logical OR operator."""
    a_vals = [False]*len(b_vals)
    for i, (b_val, c_val) in enumerate(zip(b_vals, c_vals)):
        if b_val or c_val:
            a_vals[i] = True
    return bitarray(a_vals)

def op_nand(b_vals, c_vals):
    """Logical NAND operator."""
    a_vals = [False]*len(b_vals)
    for i, (b_val, c_val) in enumerate(zip(b_vals, c_vals)):
        if not (b_val and c_val):
            a_vals[i] = True
    return bitarray(a_vals)

def op_nor(b_vals, c_vals):
    """Logical NOR operator."""
    a_vals = [False]*len(b_vals)
    for i, (b_val, c_val) in enumerate(zip(b_vals, c_vals)):
        if not (b_val or c_val):
            a_vals[i] = True
    return bitarray(a_vals)

def rev_and(A, b):

    if A == False and b == False:
        return 2
    if A == False and b == True:
        return False
    if A == True and b == True:
        return True
    if A == 2 and b == True:
        return 2
    if A == 2 and b == False:
        return 2
    
    if A == True and b == False:
        return True

    print(A, b)
    print('rev_and error')
    exit()

def rev_or(A, b):

    if A == False and b == False:
        return False
    if A == True and b == True:
        return 2
    if A == True and b == False:
        return True
    if A == 2 and b == True:
        return 2
    if A == 2 and b == False:
        return 2

    if A == False and b == True:
        return False

    print(A, b)
    print('rev_or error')
    exit()

def rev_nand(A, b):

    if A == True and b == False:
        return 2
    if A == True and b == True:
        return False
    if A == False and b == True:
        return True
    if A == 2 and b == True:
        return 2
    if A == 2 and b == False:
        return 2

    if A == False and b == False:
        return True

    print(A, b)
    print('rev_nand error')
    exit()

def rev_nor(A, b):

    if A == True and b == False:
        return False
    if A == False and b == True:
        return 2
    if A == False and b == False:
        return True
    if A == 2 and b == True:
        return 2
    if A == 2 and b == False:
        return 2

    if A == True and b == True:
        return False

    print(A, b)
    print('rev_nor error')
    exit()

class ProblemDataBoolean(object):
    """This class stores all relavant Boolean benchmark methods
    and data: Target output array, available operators, input arrays,... etc.
    """

    def __init__(self, num_bits, benchmark_name):
        self.num_bits = num_bits
        self.benchmark_name = benchmark_name

        self.is_boolean = True
        self.is_integer = False

        self.operators = [op_and, op_or, op_nand, op_nor]
        self.ephemerals = []

        # primitive name : opposite primitive
        self.op_reverse = {
            op_and : rev_and,
            op_or : rev_or,
            op_nor : rev_nor,
            op_nand : rev_nand,
        }

        self.inputs = self.gen_inputs()

        self.arg_vals = self.gen_arg_vals()
        self.arguments = list(self.arg_vals)

        self.target_outputs = self.gen_targets()

    def __deepcopy__(self, memo):
        """When doing deep copy of a tree we should avoid
        making a copy of this object.
        """
        return self

    def gen_inputs(self):
        """Generate all input arrays."""

        # compute all possible input bit arrays
        inputs = [list(seq) for seq in 
            itertools.product([False, True], repeat=self.num_bits)]

        return inputs

    def gen_arg_vals(self):
        """Assignes input arrays to arguments."""

        # arg : [vals]
        arg_vals = {}
        for i_arg in range(self.num_bits):
            arg_vals['ARG' + str(i_arg)] = [False]*len(self.inputs)

        # set arguments for each fitness case
        # test for only ARG0
        if len(list(arg_vals)) == 1:
            for i_inp, inp in enumerate(self.inputs):
                arg_vals['ARG0'][i_inp] = inp
            arg_vals['ARG0'] = bitarray(arg_vals['ARG0'])
            return arg_vals

        # more than one ARG
        for i_inp, inp in enumerate(self.inputs):
            for i_arg, arg_val in enumerate(inp):
                arg_vals['ARG' + str(i_arg)][i_inp] = arg_val

        for arg_name in list(arg_vals):
            arg_vals[arg_name] = bitarray(arg_vals[arg_name])

        return arg_vals

    def gen_targets(self):
        """Generates the target output array."""

        if self.benchmark_name == 'cmpV':
            objective_func = benchmarks_boolean.objective_func_cmpV

        elif self.benchmark_name == 'majV':
            objective_func = benchmarks_boolean.objective_func_majV

        elif self.benchmark_name == 'muxV':
            objective_func = benchmarks_boolean.objective_func_muxV

        elif self.benchmark_name == 'parV':
            objective_func = benchmarks_boolean.objective_func_parV

        elif self.benchmark_name == 'muxVparV':
            objective_func = benchmarks_boolean.objective_func_muxVparV

        target_outputs = [objective_func(x, self.num_bits) 
            for x in self.inputs]
        target_outputs = bitarray(target_outputs)

        return target_outputs

    @property
    def num_fit_tests(self):
        return len(self.inputs)
    