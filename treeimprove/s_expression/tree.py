import copy
from collections import defaultdict

'''
class StateBanRules(object):
    # this version relies on the tree state and index position
    def __init__(self):
        self.rules = defaultdict(lambda: defaultdict(set))
        self.master_tree_ban_rules = None
    
    def add_rule(self, master_tree_str, i_node, banned_i_archtree):
        if i_node == 0:
            master_tree_str = 'None'

        self.rules[master_tree_str][i_node].add(banned_i_archtree)

    def set_master_tree_str(self, master_tree):
        self.master_tree_ban_rules = self.rules[str(master_tree)]
    
    def get_avoid_indexes(self, i_node):
        if i_node == 0:
            return self.rules['None'][i_node]

        return self.master_tree_ban_rules[i_node]

class NoneBanRules(object):
    def __init__(self):
        self.rules = defaultdict(set)
    
    def add_rule(self, master_tree_str, i_node, banned_i_archtree):
        #self.rules[i_node].add(banned_i_archtree)
        pass

    def set_master_tree_str(self, master_tree):
        pass
    
    def get_avoid_indexes(self, i_node):
        return set([])
'''

class IndexBanRules(object):
    """This class records the master tree index positions at which
    archtrees are inserted.
    """
    def __init__(self):
        self.rules = defaultdict(set)
    
    def add_rule(self, master_tree_str, i_node, banned_i_archtree):
        """Add a archtree to the ban list for an index postion i_node."""
        self.rules[i_node].add(banned_i_archtree)

    def set_master_tree_str(self, master_tree):
        """This is here for consistency with StateBanRules."""
        pass
    
    def get_avoid_indexes(self, i_node):
        """Returns a list of archtree indexes which can not be inserted
        at the i_node master_tree index position.
        """
        return self.rules[i_node]

class Tree(list):

    def __init__(self, *args):
        super().__init__(self, *args)
        self.total_wrongs = 0
        self.ban_rules = IndexBanRules()

    @property
    def root_node(self):
        """Returns the root node at index position 0."""
        return self[0]
    
    def __str__(self):
        return str(self.root_node)

    def calc_max_depth(self):
        """Calculates tree depth."""
        return self.root_node.calc_max_depth() - 1

    def clear_all_outputs(self):
        """Clear all output arrays in all nodes."""
        for node in self:
            node.outputs = None

    def calc_all_outputs(self):
        """Re-calculates output arrays for all nodes."""
        for node in self:
            node.outputs = None

        self.root_node.calc_outputs()

    def calc_outputs_up(self, node):
        """Calculate outputs of all nodes which are higher (closer to root)
        up in the tree than node.
        """
        if node.parent == None:
            node.calc_outputs()

        if node == None:
            return None

        node = node.parent
        
        while node != None:
            node.outputs = None
            node.calc_outputs()

            node = node.parent

    def calc_all_optimals(self):
        """Re-calculates optimal arrays for all nodes."""
        for node in self:
            node.optimals = None
            node.optimals_mask = None

        i_nodes = [0]

        while len(i_nodes) > 0:
            i_node = i_nodes.pop()
            self[i_node].calc_optimals()

            # check for reached leaf node
            if self[i_node].left_child == None:
                continue

            i_left = self.index(self[i_node].left_child)
            i_right = self.index(self[i_node].right_child)

            i_nodes.append(i_left)
            i_nodes.append(i_right)

    def calc_nodes_count_wrongs(self):
        """Calculate all node errors."""
        self.total_wrongs = 0
        for node in self:
            node.count_wrongs()
            self.total_wrongs += node.wrong_count

    def calc_nodes_count_twos(self):
        """Count number of hashes in each node optimal array."""
        for node in self:
            node.count_twos()

    def calc_nodes_count_nodes_below(self):
        """For each node, calculate the number of subrooted node(s)."""
        self.root_node.count_nodes_below()

    def get_subtree(self, subroot_node):
        """Return the subtree rooted at subroot_node."""
        # gather all subtree nodes
        sub_tree = Tree()
        to_explore = [subroot_node]

        while len(to_explore) > 0:
            node = to_explore.pop()
            sub_tree.append(node)

            if node.left_child == None:
                continue

            to_explore.append(node.left_child)
            to_explore.append(node.right_child)

        # make copy of nodes in sub tree
        sub_tree = copy.deepcopy(sub_tree)

        # set subroot_node as root
        sub_tree[0].parent = None

        return sub_tree

    @property
    def size(self):
        return len(self)

    @property
    def outputs(self):
        return self.root_node.outputs

    @property
    def optimals(self):
        return self.root_node.optimals
    