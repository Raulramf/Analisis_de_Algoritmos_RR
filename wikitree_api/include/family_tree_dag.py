import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt

class FamilyTreeDAG:
    def __init__(self, ancestors1, ancestors2, individual1, individual2):
        self.graph = nx.DiGraph()
        self.ancestors = {}
        self.num_nodes = 0
        self.num_edges = 0
        self.graph.add_node(individual1)
        self.graph.add_node(individual2)
        self._build_graph(ancestors1, individual1)
        self._build_graph(ancestors2, individual2)

    def _build_graph(self, ancestors, individual):
        id_to_name = {ancestor['Id']: ancestor['Name'] for ancestor in ancestors}
        for ancestor in ancestors:
            ancestor_id = ancestor['Name']
            father_id = ancestor['Father']
            mother_id = ancestor['Mother']

            self.num_nodes += 1

            self.graph.add_edge(ancestor_id, individual)
            if father_id:
                father_name = id_to_name.get(father_id)
                if father_name:
                    self.graph.add_edge(str(father_id), ancestor_id)
            if mother_id:
                mother_name = id_to_name.get(mother_id)
                if mother_name:
                    self.graph.add_edge(str(mother_id), ancestor_id)

            if individual not in self.ancestors:
                self.ancestors[individual] = set()
                self.ancestors[individual].add(ancestor_id)
            if father_id:
                self.ancestors[individual].add(father_id)
            if mother_id:
                self.ancestors[individual].add(mother_id)

    def get_parents(self, node):
        return list(self.graph.predecessors(node))

    def find_root(self, node):
        root = None
        for n in nx.ancestors(self.graph, node):
            if self.graph.in_degree(n) == 0:
                root = n
                break
            if root is None:
                print("No root found")
        return root

    def visualize_tree(self, root, filename):
        pos = graphviz_layout(self.graph, prog='dot', root=root)
        plt.figure(figsize=(8, 8))
        nx.draw(self.graph, pos, with_labels=True, arrows=False)
        plt.savefig(filename)
        plt.close()

    def get_depth(self, node):
        root = self.find_root(node)
        if root is not None:
            path_length = nx.shortest_path_length(self.graph, root)
            depth = path_length[node] if node in path_length else None
            if depth is not None:
                print(f"Depth from root to node: {depth}")
            else:
                print(f"No path from root to node")
            return depth
        else:
            return None

def get_ancestors(node, graph, memo=None, visited=None):
    if memo is None:
        memo = {}
    if visited is None:
        visited = set()

    if node in memo:
        return memo[node]

    ancestors = set()
    for parent in graph.get_parents(node):
        if parent in visited:
            continue
        visited.add(parent)
        ancestors.add(parent)
        ancestors.update(get_ancestors(parent, graph, memo, visited))

    memo[node] = ancestors
    return ancestors

def lowest_common_ancestor(individual1, individual2, dag):
    ancestors1 = get_ancestors(individual1, dag)
    ancestors2 = get_ancestors(individual2, dag)
    common_ancestors = ancestors1.intersection(ancestors2)

    if not common_ancestors:
        return None

    min_depth = float('inf')
    lca = None
    for ancestor in common_ancestors:
        depth = dag.get_depth(ancestor)
        if depth is None:
            continue
        if depth < min_depth:
            min_depth = depth
            lca = ancestor

    print(f"Lowest common ancestor: {lca}")

    return lca
