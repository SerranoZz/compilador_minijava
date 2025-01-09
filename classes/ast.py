import re
from graphviz import Digraph
from collections import defaultdict

def remover_detalhes(tree):
    """
    Remove todos os nós de um objeto Digraph cujo label seja um dos seguintes:
    ',', '.', ';', '(', ')', '[', ']', '{', '}'.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os nós removidos.
    """
    # Lista de labels a serem removidos
    labels_to_remove = {",", ".", ";", "(", ")", "[", "]", "{", "}"}
    
    # Regex para capturar nós com labels
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    edges = []
    nodes_to_remove = set()

    # Identificar nós a remover
    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        if label in labels_to_remove:
            nodes_to_remove.add(node)

    # Filtrar arestas para excluir as associadas aos nós removidos
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')
    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        if parent not in nodes_to_remove and child not in nodes_to_remove:
            edges.append((parent, child))

    # Criar um novo grafo sem os nós removidos
    new_tree = Digraph()
    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        if node not in nodes_to_remove:
            new_tree.node(node, label=label)
    for parent, child in edges:
        new_tree.edge(parent, child)

    return new_tree


def remover_vazios(tree):
    """
    Remove todos os nós de um objeto Digraph cujo label seja 'ε' e também remove o pai desses nós.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os nós removidos.
    """
    # Regex para capturar nós com labels
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')

    nodes_to_remove = set()
    parent_nodes = set()
    hierarchy = defaultdict(list)

    # Identificar nós a remover e construir a hierarquia de arestas
    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        if label == "ε":
            nodes_to_remove.add(node)

    # Identificar pais dos nós removidos e manter hierarquia de arestas
    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)
        if child in nodes_to_remove:
            parent_nodes.add(parent)

    # Adicionar pais à lista de remoção
    nodes_to_remove.update(parent_nodes)

    # Construir novo grafo sem os nós removidos
    new_tree = Digraph()
    valid_edges = []

    # Adicionar nós válidos
    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        if node not in nodes_to_remove:
            new_tree.node(node, label=label)

    # Adicionar arestas válidas (evitando nós removidos)
    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        if parent not in nodes_to_remove and child not in nodes_to_remove:
            valid_edges.append((parent, child))

    for parent, child in valid_edges:
        new_tree.edge(parent, child)

    return new_tree

def remover_triviais(tree):
    """
    Remove nós intermediários (com apenas uma filha) de um grafo Digraph.
    O nó intermediário é substituído diretamente por sua filha descendente.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os nós triviais.
    """
    import re
    from collections import defaultdict

    # Regex para capturar nós e arestas
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')

    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}
    parents = {}

    # Preencher hierarquia e relações
    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)
        parents[child] = parent

    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        labels[node] = label

    # Identificar e tratar nós triviais
    for node, children in list(hierarchy.items()):
        if len(children) == 1:  # Nó intermediário encontrado
            child = children[0]
            parent = parents.get(node)
            if parent:
                # Substituir a aresta parent -> node por parent -> child
                hierarchy[parent].remove(node)
                hierarchy[parent].append(child)
                parents[child] = parent

            # Remover o nó intermediário
            del hierarchy[node]
            del labels[node]

    # Construir o novo grafo
    new_tree = Digraph()
    for node, label in labels.items():
        new_tree.node(node, label=label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def remover_filhos(tree):
    """
    Remove qualquer filho de 'classe' ou 'main' que não seja 'cmd' ou 'metodo', removendo também os nós
    que não atendem a esse critério.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os filhos e nós irrelevantes.
    """
    import re
    from collections import defaultdict

    # Regex para capturar nós e arestas
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')

    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        labels[node] = label

    # Remover filhos de 'classe' ou 'main' que não sejam 'cmd' ou 'metodo' e os próprios nós irrelevantes
    nodes_to_remove = set()  # Vamos armazenar os nós a serem removidos
    for parent, children in list(hierarchy.items()):
        # Verificar se o label do nó pai é 'classe' ou 'main'
        if labels.get(parent) in ['main']:
            # Filtrar os filhos que são 'cmd' ou 'metodo'
            valid_children = [child for child in children if labels.get(child) in ['cmd', 'metodo']]
            hierarchy[parent] = valid_children
            # Adicionar filhos removidos à lista de nós a serem removidos
            nodes_to_remove.update(set(children) - set(valid_children))

    # Remover os nós que não são válidos (não atendem aos critérios)
    for node in nodes_to_remove:
        if node in labels:
            del labels[node]
        if node in hierarchy:
            del hierarchy[node]
        for parent in hierarchy:
            if node in hierarchy[parent]:
                hierarchy[parent].remove(node)

    # Construir o novo grafo sem os nós e arestas removidos
    new_tree = Digraph()
    for node, label in labels.items():
        new_tree.node(node, label=label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def remover_irrelevantes(tree):
    """
    Remove os nós com labels em {"public", "int", "var", "params"} e as arestas conectadas a eles.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os nós e arestas removidos.
    """
    # Regex para capturar nós e arestas
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')

    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        labels[node] = label

    # Definir os labels dos nós a serem removidos
    labels_to_remove = {"public", "int", "var", "params"}

    # Remover filhos e nós com labels específicos
    nodes_to_remove = set()
    for parent, children in list(hierarchy.items()):
        # Verificar se o label do nó pai é um dos que deve ser removido
        if labels.get(parent) in labels_to_remove:
            nodes_to_remove.add(parent)
            # Remover também os filhos desses nós
            nodes_to_remove.update(children)
        # Remover filhos que têm labels específicos
        for child in children:
            if labels.get(child) in labels_to_remove:
                nodes_to_remove.add(child)

    # Remover os nós que não são válidos (não atendem aos critérios)
    for node in nodes_to_remove:
        if node in labels:
            del labels[node]
        if node in hierarchy:
            del hierarchy[node]
        for parent in hierarchy:
            if node in hierarchy[parent]:
                hierarchy[parent].remove(node)

    # Construir o novo grafo sem os nós e arestas removidos
    new_tree = Digraph()
    for node, label in labels.items():
        new_tree.node(node, label=label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def resolver_operadores(tree, label):
    """
    Substitui um nó pelo seu filho operador se o nó tiver o label especificado.
    O operador é definido por seu label: {"+", "-", "*", "/", "="}.
    O processo percorre a árvore de baixo para cima.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :param label: Label que define os nós a serem substituídos.
    :return: Novo objeto Digraph com os nós resolvidos.
    """

    # Regex para capturar nós e arestas
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')

    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    # Operadores definidos
    operators = {"+", "-", "*", "/", "=", ">", "<", "<=", ">=", "==", "!=", "&&", "!"}

    # Substituir e ajustar nós
    for parent, children in list(hierarchy.items()):
        if labels.get(parent) == label:
            for child in children:
                if labels.get(child) in operators:
                    # Atualizar o label do nó pai
                    labels[parent] = labels[child]
                    # Conectar os filhos do operador diretamente ao pai
                    grandchildren = hierarchy.pop(child, [])
                    hierarchy[parent].extend(grandchildren)
                    # Remover o nó filho usado na substituição
                    hierarchy[parent].remove(child)
                    del labels[child]
                    break

    # Reconstruir o novo grafo
    new_tree = Digraph()
    for node, node_label in labels.items():
        new_tree.node(node, label=node_label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

operators = {"+", "-", "*", "/", "=", ">", "<", "<=", ">=", "==", "!=", "&&", "!"}

def create_ast(tree):
    exp_nodes = ["mexp_aux", "mexp", "aexp_aux", "aexp", "rexp_aux", "rexp"]
    new_tree = remover_irrelevantes(remover_filhos(remover_triviais(remover_vazios(remover_detalhes(tree)))))

    for node in exp_nodes:
        new_tree = resolver_operadores(new_tree, node)

    return new_tree