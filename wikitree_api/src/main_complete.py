# Mariana Monroy  29834
# Ivelisse Franco 30306
# Raúl Ramírez    35073
# Juan Vazquez    35077

import argparse                                                     # Importa la biblioteca argparse para manejar los argumentos de línea de comando
import requests                                                     # Importa la biblioteca requests para realizar solicitudes HTTP
import networkx as nx                                               # Importa la biblioteca networkx para la creación, manipulación y estudio de la estructura de redes complejas
from networkx.drawing.nx_agraph import graphviz_layout              # Importa el método graphviz_layout para posicionar los nodos utilizando Graphviz
import matplotlib.pyplot as plt                                     # Importa la biblioteca matplotlib.pyplot para la creación de gráficos
import json

# Clase para interactuar con la API de WikiTree
class WikiTreeAPI:
    def __init__(self):                                             # Define el método de inicialización
        self.base_url = "https://api.wikitree.com/api.php"          # Define la URL base para la API de WikiTree

    # Método para obtener los datos de los árboles genealógicos de dos individuos
    def fetch_family_tree_data(self, individual1, individual2):
        data1, filename1 = self.fetch_ancestors(individual1)                   # Obtiene los ancestros del primer individuo
        data2, filename2 = self.fetch_ancestors(individual2)                   # Obtiene los ancestros del segundo individuo
        if not data1  or not data2:                                 # Si no se pueden obtener datos para uno o ambos individuos, regresa None
            return None
        return data1[0]['ancestors'], data2[0]['ancestors'], filename1, filename2         # Regresa los ancestros de ambos individuos

    # Método para obtener los ancestros de un individuo
    def fetch_ancestors(self, individual_id):
        params = {                                                  # Define los parámetros para la solicitud de la API
            "action": "getAncestors",
            "format": "json",
            "key": individual_id,                                   # La llave con la que se busca a la persona, a partir del ID proporcionado por la base de datos de WikiTree
            "depth": 4                                              # La profundidad siendo las generaciones que recorrerá
        }
        response = requests.get(self.base_url, params=params)       # Realiza la solicitud a la API y guarda la respuesta
        try:
            response.raise_for_status()                                                             # Verifica si la solicitud fue exitosa. Si hubo un error, se lanza una excepción
        except requests.exceptions.HTTPError as err:                                                # Captura la excepción en caso de un error HTTP
            print(f"HTTP error occurred while fetching ancestors for {individual_id}: {err}")       # Imprime el error
            return None
        data = response.json()   # Regresa la respuesta de la API en formato JSON

        filename = f"ancestors_{individual_id}.txt"
        with open(filename, 'w') as file:
            json.dump(data, file)
        return data, filename

# Clase para representar el árbol genealógico como un grafo dirigido acíclico (DAG)
class FamilyTreeDAG:
    def __init__(self, ancestors1, ancestors2, individual1, individual2):                           # Define el método de inicialización
        self.graph = nx.DiGraph()                                   # Crea un grafo dirigido vacío
        self.ancestors = {}
        self.num_nodes = 0
        self.num_edges = 0
        self.graph.add_node(individual1)                            # Añade el primer individuo como un nodo al grafo
        self.graph.add_node(individual2)                            # Añade el segundo individuo como un nodo al grafo
        self._build_graph(ancestors1, individual1)                  # Construye el grafo para el primer individuo
        self._build_graph(ancestors2, individual2)                  # Construye el grafo para el segundo individuo

    # Método para construir el grafo a partir de los ancestros de un individuo
    def _build_graph(self, ancestors, individual):
        id_to_name = {ancestor['Id']: ancestor['Name'] for ancestor in ancestors}
        for ancestor in ancestors:                                  # Itera sobre cada ancestro
            ancestor_id = ancestor['Name']                          # Obtiene el nombre del ancestro
            father_id = ancestor['Father']                          # Obtiene el nombre del padre del ancestro
            mother_id = ancestor['Mother']                          # Obtiene el nombre de la madre del ancestro

            self.num_nodes += 1


            self.graph.add_edge(ancestor_id, individual)            # Añade una arista entre el ancestro y el individuo al grafo
            if father_id:       # Si el ancestro tiene un padre...
                father_name = id_to_name.get(father_id)
                if father_name:
                    self.graph.add_edge(str(father_id), ancestor_id)    # Añade una arista entre el padre y el ancestro al grafo
            if mother_id:       # Si el ancestro tiene una madre...
                mother_name = id_to_name.get(mother_id)
                if mother_name:
                    self.graph.add_edge(str(mother_id), ancestor_id)    # Añade una arista entre la madre y el ancestro al grafo

            if individual not in self.ancestors:
                self.ancestors[individual] = set()
                self.ancestors[individual].add(ancestor_id)
            if father_id:
                self.ancestors[individual].add(father_id)
            if mother_id:
                self.ancestors[individual].add(mother_id)

    # Método para obtener los padres de un nodo
    def get_parents(self, node):
        return list(self.graph.predecessors(node))                  # Regresa la lista de los padres del nodo

    # Método para encontrar la raíz (ancestro más antiguo) de un nodo
    def find_root(self, node):
        root = None                                                 # Inicializa la raíz como None
        for n in nx.ancestors(self.graph, node):                    # Itera sobre todos los ancestros del nodo
            if self.graph.in_degree(n) == 0:                        # Si el ancestro no tiene predecesores (es decir, es una raíz)...
                root = n                                            # Establece la raíz como ese ancestro
                break                                               # Se rompe el ciclo para que no itere infinitamente
            if root is None:
                print("No root found")
        return root                                                 # y regresa la raíz

    # Método para visualizar el árbol y guardarlo en un archivo
    def visualize_tree(self, root, filename):
        pos = graphviz_layout(self.graph, prog='dot', root=root)    # Obtiene las posiciones de los nodos para la visualización
        plt.figure(figsize=(8, 8))                                  # Crea una nueva figura
        nx.draw(self.graph, pos, with_labels=True, arrows=False)    # Dibuja el grafo
        plt.savefig(filename)                                       # Guarda la figura en un archivo
        plt.close()                                                 # Cierra la figura

    # Método para obtener la profundidad de un nodo desde la raíz
    def get_depth(self, node):
        root = self.find_root(node)
        if root is not None:                                            # Si el nodo tiene una raíz...
            path_length = nx.shortest_path_length(self.graph, root)     # Calcula la longitud del camino más corto desde la raíz a todos los otros nodos
            depth = path_length[node] if node in path_length else None  # Calcula la profundidad del nodo
            if depth is not None:                                       # Si la profundidad se pudo calcular...
                print(f"Depth from root to node: {depth}")              # Imprime la profundidad.
            else:                                                       # De otra forma
                print(f"No path from root to node")                     # Imprime un mensaje
            return depth
        else:
            return None  # or any other special value

def get_ancestors(node, graph, memo=None, visited=None):
    if memo is None:                                                     # Si existe un diccionario de memorización...
        memo = {}                                                        # Se inicializa un diccionario vacío
    if visited is None:                                                  # Si no existe un conjunto de nodos visitados...
        visited = set()                                                  # Se inicializa un conjunto vacío de los nodos que se vayan visitando

    if node in memo:                                                     # Si el nodo ya se ha procesado anteriormente...
        return memo[node]                                                # Regresa los ancestros memorizados del nodo

    ancestors = set()                                                    # Inicializa un conjunto vacío de ancestros
    for parent in graph.get_parents(node):                               # Itera sobre los padres del nodo
        if parent in visited:                                            # Si el padre ya se ha visitado...
            continue                                                     # Salta a la siguiente iteración.
        visited.add(parent)                                              # Añade el padre al conjunto de nodos visitados
        ancestors.add(parent)                                            # Añade el padre al conjunto de ancestros
        ancestors.update(get_ancestors(parent, graph, memo, visited))    # Agrega los ancestros del padre al conjunto de ancestros

    memo[node] = ancestors                                               # Memoriza los ancestros del nodo
    return ancestors                                                     # Regresa los ancestros del nodo

def lowest_common_ancestor(individual1, individual2, dag):
    ancestors1 = get_ancestors(individual1, dag)                         # Obtiene los ancestros del primer individuo
    ancestors2 = get_ancestors(individual2, dag)                         # Obtiene los ancestros del segundo individuo
    common_ancestors = ancestors1.intersection(ancestors2)               # Encuentra los ancestros comunes de ambos individuos

    if not common_ancestors:                                             # Si no hay ancestros comunes...
        return None                                                      # Regresa none

    min_depth = float('inf')    # Inicializa la profundidad mínima con infinito. Esto se hace para poder encontrar el ancestro común más reciente, es decir, el que tiene la menor profundidad
    lca = None                  # Inicializa el ancestro común más reciente como None
    for ancestor in common_ancestors:       # Itera sobre cada ancestro común
        depth = dag.get_depth(ancestor)     # Obtiene la profundidad del ancestro
        if depth is None:       # se salta a al ancestro del cual no se puede calcular su profundidad
            continue
        if depth < min_depth:   # Si la profundidad del ancestro es menor que la profundidad mínima actual...
            min_depth = depth   # Actualiza la profundidad mínima
            lca = ancestor      # Actualiza el ancestro común más reciente

    print(f"Lowest common ancestor: {lca}")

    return lca                  # Regresa el ancestro común más reciente


# Función Principal
def main():
    parser = argparse.ArgumentParser()                                                      # Crea un nuevo analizador de argumentos
    parser.add_argument("individual1", help="WikiTree Name of the first individual")        # Añade un argumento para el nombre del primer individuo
    parser.add_argument("individual2", help="WikiTree Name of the second individual")       # Añade un argumento para el nombre del segundo individuo
    args = parser.parse_args()                                                              # Analiza los argumentos proporcionados al script

    api = WikiTreeAPI()                                                                     # Crea una nueva instancia de la API de WikiTree
    family_tree_data = api.fetch_family_tree_data(args.individual1, args.individual2)       # Obtiene los datos del árbol genealógico de ambos individuos

    if family_tree_data is None:                                                            # Si no se pudo obtener los datos del árbol genealógico...
        print("Could not fetch family tree data for one or both individuals.")              # Imprime un mensaje
        return                                                                              # Termina la ejecución del script

    dag = FamilyTreeDAG(family_tree_data[0], family_tree_data[1], args.individual1, args.individual2)       # Crea un nuevo grafo dirigido acíclico (DAG) a partir de los datos del árbol genealógico


    root1 = dag.find_root(args.individual1)                                                 # Encuentra la raíz del árbol genealógico del primer individuo
    root2 = dag.find_root(args.individual2)                                                 # Encuentra la raíz del árbol genealógico del segundo individuo
    if root1:                                                                               # Si el primer individuo tiene una raíz...
        print("Visualizing tree for " + args.individual1)                                   # Imprime un mensaje
        dag.visualize_tree(root1, 'tree1.png')                                              # Se visualiza el arbol y se guarda en un archivo 'png'
    if root2:                                                                               # Si el segundo individuo tiene una raíz...
        print("Visualizing tree for " + args.individual2)                                   # Aplica lo mismo que con el primero
        dag.visualize_tree(root2, 'tree2.png')

    lca = lowest_common_ancestor(args.individual1, args.individual2, dag)

    if lca:
        print(f"The most recent common ancestor of {args.individual1} and {args.individual2} is {lca}.")
    else:
        print(f"No common ancestor found for {args.individual1} and {args.individual2}.")

if __name__ == "__main__":
    main()
