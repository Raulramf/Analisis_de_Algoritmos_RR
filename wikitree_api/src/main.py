import argparse
from include.wikitree_api import WikiTreeAPI
from include.family_tree_dag import FamilyTreeDAG

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("individual1", help="WikiTree Name of the first individual")
    parser.add_argument("individual2", help="WikiTree Name of the second individual")
    args = parser.parse_args()

    api = WikiTreeAPI()
    family_tree_data = api.fetch_family_tree_data(args.individual1, args.individual2)

    if family_tree_data is None:
        print("Could not fetch family tree data for one or both individuals.")
        return

    dag = FamilyTreeDAG(family_tree_data[0], family_tree_data[1], args.individual1, args.individual2)
    root1 = dag.find_root(args.individual1)
    root2 = dag.find_root(args.individual2)
    if root1:
        print("Visualizing tree for " + args.individual1)
        dag.visualize_tree(root1, 'tree1.png')
    if root2:
        print("Visualizing tree for " + args.individual2)
        dag.visualize_tree(root2, 'tree2.png')

    lca = lowest_common_ancestor(args.individual1, args.individual2, dag)

    if lca:
        print(f"The most recent common ancestor of {args.individual1} and {args.individual2} is {lca}.")
    else:
        print(f"No common ancestor found for {args.individual1} and {args.individual2}.")

if __name__ == "__main__":
    main()

