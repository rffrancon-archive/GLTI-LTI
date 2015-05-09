from collections import defaultdict
from operator import attrgetter

from bitarray import bitarray

class TreeForArchive(object):
    """This object serves as containers for trees
    in the archive.
    """

    def __init__(self, tree):
        self.tree = tree
        self.tree_str = str(self.tree)
        self.tree_size = self.tree.size
        self.arch_index_pos = None

        self.outputs = self.tree.outputs

    def __eq__(self, other):
        return other.tree_str == self.tree_str

    def __hash__(self):
        return hash(self.tree_str)

class ArchivedTreesList(list):
    """The tree archive."""

    def __init__(self, memory_efficient=False, boolean_flag=False):
        super().__init__()
        self.memory_efficient = memory_efficient
        self.boolean_flag = boolean_flag

    def add(self, new_archtree):
        """Adds new_archtree to the archive. Usually, this is only called from
        a TreeArchive instance.

        Always ensures that the archive is semantically unique.

        A larger tree within the archive which has the same outputs as new_archtree 
        is replaced by new_archtree. 
        """

        # loop over currently stored arch_trees checking for no matching str
        for arch_tree in self:
            if arch_tree.tree_str == new_archtree.tree_str:
                return False

        # evaluate tree outputs
        new_archtree.tree.calc_all_outputs()

        if self.boolean_flag:
            new_archtree.outputs = bitarray(
                new_archtree.tree.outputs.tolist())
        else:
            new_archtree.outputs = list(new_archtree.tree.outputs)

        # clear outputs from tree nodes if memory efficient
        if self.memory_efficient:
            new_archtree.tree.clear_all_outputs()

        # loop over currently stored arch_trees
        for i_arch_tree, arch_tree in enumerate(self):

            # compare outputs value-by-value
            if arch_tree.outputs == new_archtree.outputs:
                 
                # outputs are equal, check for smaller size
                if new_archtree.tree_size < arch_tree.tree_size:
                    self[i_arch_tree] = new_archtree
                    return True

                # outputs were the same and size was larger or the same
                return False

        self.append(new_archtree)
        return True

class TreeArchive(object):
    """This class manages the tree archive list (ArchivedTreesList)."""

    def __init__(self, max_archive_size, split_subtrees_flag=False, 
        memory_efficient=False, boolean_flag=False, verbose=False):

        self.archive = ArchivedTreesList(memory_efficient, boolean_flag)
        
        self.max_archive_size = max_archive_size
        self.split_subtrees_flag = split_subtrees_flag
        
        self.count_miss = 0
        self.trees_outputs = []

        self.verbose = verbose
        
    def add_tree(self, tree):
        """Attempts to add tree (and all subtrees if split_subtrees_flag is True)
        into the archive.
        """

        if len(self.archive) == self.max_archive_size:
            return False

        if self.split_subtrees_flag:

            # split tree into all its sub trees
            for node in tree:

                # get subtree
                sub_tree = tree.get_subtree(node)

                # wrap in archive container
                arch_sub_tree = TreeForArchive(sub_tree)

                # add prepared sub tree to archive
                if not self.archive.add(arch_sub_tree):
                    self.count_miss += 1

                if len(self.archive) == self.max_archive_size:
                    return False

        else:
            # wrap in archive container
            arch_tree = TreeForArchive(tree)

            # add prepared sub tree to archive
            if not self.archive.add(arch_tree):
                self.count_miss += 1

            if len(self.archive) == self.max_archive_size:
                return False

        return True

    def populate_archive(self, trees):
        """Attempts to add each tree in trees into the archive."""

        num_added = 0

        # add individuals into archive
        for i_tree, tree in enumerate(trees):
            if not self.add_tree(tree):
                break
                
            else:
                num_added += 1
                if self.verbose and i_tree%500 == 0:
                    print('num_trees added : ', num_added)

        # convert archive into tree size sorted list
        self.archive = list(self.archive)
        self.archive.sort(key=attrgetter('tree_size'))

        for i_arch_tree, arch_tree in enumerate(self.archive):
            arch_tree.arch_index_pos = i_arch_tree

    def gather_tree_outputs(self):
        """Gathers each output array from each tree in the archive
        into a single matrix.
        """

        self.trees_outputs = []

        for arch_tree in self.archive:
            self.trees_outputs.append(arch_tree.outputs)
            arch_tree.outputs = None

    def get_all_count_wrongs(self, mn_optimals, mn_optimals_mask):
        """Calculates errors from all trees in the library using
        the output marix generated by gather_tree_outputs.
        """

        wrong_counts = [0]*len(self.trees_outputs)

        # loop over all archive trees
        for i_tree, tree_outputs in enumerate(self.trees_outputs):
            
            # loop over all master tree node optimal values
            for optimal, mask, tree_output in zip(
                mn_optimals, mn_optimals_mask, tree_outputs):

                if mask:
                    continue

                if optimal != tree_output:
                    wrong_counts[i_tree] += 1

        return wrong_counts
