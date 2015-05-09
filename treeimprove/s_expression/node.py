import random
from bitarray import bitarray

class BaseNode(object):
    """This class is inheristed by the other node constructor calsses."""
    def __init__(self, problem_data):
        self.parent = None
        self.left_child = None
        self.right_child = None

        self.outputs = None

        self.optimals = None
        self.optimals_mask = None

        self.wrong_count = None
        self.twos_count = None

        self.type = None
        self.name = None
        self.operator = None

        self.nodes_below_count = 0
        self.single_child_arg = False

        self.problem_data = problem_data

    def __str__(self):
        if self.type == 'arg':
            return self.name

        elif self.type == 'eph':
            return self.name

        elif self.type == 'op':
            val = "({left},{right})".format(
                left=self.left_child, right=self.right_child)
            return str(self.name) + str(val)

        return 'None'

    def calc_max_depth(self):
        """Calculates the maximum depth reached by the nodes which 
        form the subtree rooted by this node (self).
        """
        if self.left_child == None:
            return 1

        # get depths from left and right children
        left_max_depth = self.left_child.calc_max_depth()
        right_max_depth = self.right_child.calc_max_depth()

        if left_max_depth > right_max_depth:
            return left_max_depth + 1
        else:
            return right_max_depth + 1

    def calc_outputs(self):
        """Generate the output array for the node. 
        Recursively calls child dependencies first."""

        # if the outputs list is not empty, give the outputs
        if self.outputs != None:
            return self.outputs

        if self.type == 'arg':
            self.outputs = self.problem_data.arg_vals[self.name]
            return self.outputs

        # get output from left and right children
        left_outputs = self.left_child.calc_outputs()
        right_outputs = self.right_child.calc_outputs()

        self.outputs = self.operator(left_outputs, right_outputs)
        return self.outputs

    def set_random(self, leaf_flag):
        """Sets the node properties (operator, argument, ... etc.)
        randomly. Ensures that leaf nodes are arguments or ephemerals
        and that internal nodes are operators as expected.
        """
        
        if leaf_flag:
            options = (self.problem_data.arguments +
                self.problem_data.ephemerals)
        else:
            options = self.problem_data.operators

        # pick one 
        chosen = random.choice(options)

        if leaf_flag:
            if chosen in self.problem_data.ephemerals:
                self.type = 'eph'
                self.name = str(chosen)

            elif chosen in self.problem_data.arguments:
                self.type = 'arg'
                self.name = chosen

        else:
            self.type = 'op'
            self.name = chosen.__name__
            self.operator = chosen

    def count_nodes_below(self):
        """Counts the number of nodes found in the 
        subtree rooted by this (self) node.
        """

        if self.type == 'arg' or self.type == 'eph':
            self.nodes_below_count = 1
            return 1

        # get output from left and right children
        left_count = self.left_child.count_nodes_below()
        right_count = self.right_child.count_nodes_below()

        self.nodes_below_count = left_count + right_count + 1
        return self.nodes_below_count

class NodeBoolean(BaseNode):
    """Extends BaseNode by implementing or overwriting methods
    which are specific to the Boolean case.
    """

    def calc_optimals(self):
        """Generate the optimals array for the node. 
        Recursively calls child dependencies first."""

        # if the node is root, give targets as optimals
        if self.parent == None:
            self.optimals = self.problem_data.target_outputs

            # dont mask any optimal
            self.optimals_mask = bitarray([False]*len(self.optimals))
            return self.optimals, self.optimals_mask

        if self.optimals != None:
            return self.optimals, self.optimals_mask

        me_left_flag = False

        # check for self is the left child
        if self.parent.left_child == self:
            b_outputs = self.parent.right_child.outputs

        else:
            b_outputs = self.parent.left_child.outputs

        rev_op = self.problem_data.op_reverse[self.parent.operator]
        A_optimals = self.parent.optimals
        A_optimal_masks = self.parent.optimals_mask

        # fill in optimal array and mask for hash values
        self.optimals = [False]*len(A_optimals)
        self.optimals_mask = [False]*len(A_optimals)

        for i in range(len(A_optimals)):

            # check for A optimal is hash
            A_mask = A_optimal_masks[i]
            if A_mask:
                self.optimals_mask[i] = True
                continue

            A_optimal = A_optimals[i]
            b_output = b_outputs[i]

            optimal = rev_op(A_optimal, b_output)
            
            if optimal == 2:
                self.optimals_mask[i] = True
                continue

            self.optimals[i] = optimal

        self.optimals = bitarray(self.optimals)
        self.optimals_mask = bitarray(self.optimals_mask)
        return self.optimals, self.optimals_mask

    def count_wrongs(self):
        """Counts the number of errors in the output array of this node."""

        self.wrong_count = 0
        for output, optimal, mask in zip(
            self.outputs, self.optimals, self.optimals_mask):
            
            if mask:
                continue
            if output != optimal:
                self.wrong_count += 1

        return self.wrong_count

    def count_twos(self):
        """Counts the number of hashes in the optimals array 
        of this node.
        """

        self.twos_count = self.optimals_mask.count(True)
        return self.twos_count
        
class NodeInteger(BaseNode):
    """Extends BaseNode by implementing or overwriting methods
    which are specific to the finite algebra (integer) case.
    """

    def calc_optimals(self):
        """Generate the optimals array for the node. 
        Recursively calls child dependencies first."""

        # if the node is root, give targets as optimals
        if self.parent == None:
            self.optimals = self.problem_data.target_outputs
            return self.optimals

        if self.optimals:
            return self.optimals

        # check for self is the left child
        if self.parent.left_child == self:
            b_outputs = self.parent.right_child.outputs
            is_left = True

        else:
            b_outputs = self.parent.left_child.outputs
            is_left = False

        rev_op = self.problem_data.op_reverse[self.parent.operator]
        A_optimals = self.parent.optimals

        self.optimals = []
        for A_optimal, b_output in zip(A_optimals, b_outputs):
            optimal = rev_op(A_optimal, b_output, is_left=is_left)
            self.optimals.append(optimal)

        return self.optimals

    def count_wrongs(self):
        """Counts the number of errors in the output array of this node."""

        self.wrong_count = 0

        for out, optimal in zip(self.outputs, self.optimals):

            if isinstance(optimal, tuple):
                if out not in optimal:
                    self.wrong_count += 1

            else:
                if out != optimal:
                    self.wrong_count += 1

        return self.wrong_count

    def count_twos(self):
        """Counts the number of hashes in the optimals array 
        of this node.
        """

        self.twos_count = 0
        for optimal in self.optimals:
            if isinstance(optimal, tuple):
                self.twos_count += len(optimal)-1
        return self.twos_count
