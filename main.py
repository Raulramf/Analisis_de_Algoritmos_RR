import argparse
import requests
import networkx as nx
import pygraphviz as pgv
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt

# WikiTreeAPI class
class WikiTreeAPI:
    def __init__(self):
        self.base_url = "https://api.wikitree.com/api.php"

    def fetch_family_tree_data(self, individual1, individual2):
        data1 = self.fetch_ancestors(individual1)
        data2 = self.fetch_ancestors(individual2)
        if not data1  or not data2:
            return None
        ancestors1 = data1[0]['ancestors']
        ancestors2 = data2[0]['ancestors']
        return ancestors1, ancestors2

    def fetch_ancestors(self, individual_id):
        params = {
            "action": "getAncestors",
            "format": "json",
            "key": individual_id,
            "depth": 10000000
        }
        response = requests.get(self.base_url, params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred while fetching ancestors for {individual_id}: {err}")
            return None
        return response.json()

# FamilyTreeDAG class
class FamilyTreeDAG:
    def __init__(self, ancestors1, ancestors2, individual1, individual2):
        self.graph = nx.DiGraph()
        self.graph.add_node(individual1)
        self.graph.add_node(individual2)
        self._build_graph(ancestors1)
        self._build_graph(ancestors2)

    def _build_graph(self, ancestors):
        for ancestor in ancestors:
            self.graph.add_node(ancestor["Id"])
            print(f"Added node: {ancestor['Id']}")
            if ancestor["Father"]:
                self.graph.add_edge(ancestor["Father"], ancestor["Id"])
                print(f"Added edge: {ancestor['Father']} -> {ancestor['Id']}")
            if ancestor["Mother"]:
                self.graph.add_edge(ancestor["Mother"], ancestor["Id"])
                print(f"Added edge: {ancestor['Mother']} -> {ancestor['Id']}")

    def get_parents(self, node):
        return list(self.graph.predecessors(node))

    def find_root(self, node):
        root = None
        for n in nx.ancestors(self.graph, node):
            if self.graph.in_degree(n) == 0:
                root = n
                break
        return root
    def visualize_tree(self, root):
        pos = graphviz_layout(self.graph, prog='dot', root=root)
        plt.figure(figsize=(8, 8))
        nx.draw(self.graph, pos, with_labels=True, arrows=False)
        plt.show()

    def get_depth(self, node):
        root = self.find_root(node)
        return nx.shortest_path_length(self.graph, root, node)

# LCA algorithm functions
def get_ancestors(node, graph):
    ancestors = set()
    stack = [node]
    while stack:
        current = stack.pop()
        ancestors.add(current)
        stack.extend(graph.get_parents(current))
    return ancestors

def lowest_common_ancestor(node1, node2, graph):
    ancestors1 = get_ancestors(node1, graph)
    print(f"Ancestors of {node1}: {ancestors1}")
    ancestors2 = get_ancestors(node2, graph)
    print(f"Ancestors of {node2}: {ancestors2}")
    common_ancestors = ancestors1.intersection(ancestors2)

    if not common_ancestors:
        return None

    min_depth = float('inf')
    lca = None
    for ancestor in common_ancestors:
        depth = graph.get_depth(ancestor)
        if depth < min_depth:
            min_depth = depth
            lca = ancestor

    print(f"Common ancestors: {common_ancestors}")
    print(f"Lowest common ancestor: {lca}")

    return lca

# Main function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("individual1", help="WikiTree ID of the first individual")
    parser.add_argument("individual2", help="WikiTree ID of the second individual")
    args = parser.parse_args()

    api = WikiTreeAPI()
    family_tree_data = api.fetch_family_tree_data(args.individual1, args.individual2)

    if family_tree_data is None:
        print("Could not fetch family tree data for one or both individuals.")
        return

    dag = FamilyTreeDAG(family_tree_data[0], family_tree_data[1], args.individual1, args.individual2)
    lca = lowest_common_ancestor(args.individual1, args.individual2, dag)

    if lca:
        print(f"The most recent common ancestor of {args.individual1} and {args.individual2} is {lca}.")
    else:
        print(f"No common ancestor found for {args.individual1} and {args.individual2}.")

if __name__ == "__main__":
    main()

