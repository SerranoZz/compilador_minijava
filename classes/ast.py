import re
from graphviz import Digraph
from collections import defaultdict

# Lista de nós que podem ser tratados por remover_irrelevantes()
exp_nodes = ["mexp_aux", "mexp", "aexp_aux", "aexp", "rexp_aux", "rexp"]
# Regex para capturar nós com labels
node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
# Regex para capturar nós e arestas
edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')
# Nós que são substituídos pelo primeiro filho
up_nodes = ["classe", "metodo", "pexp_aux"]
# Instruções para substituir os nós de comando
inst_nodes = ["if", "while", "System.out.println", "="]

def remover_detalhes(tree):
    """
    Remove todos os nós de um objeto Digraph cujo label seja um dos seguintes:
    ',', '.', ';', '(', ')', '[', ']', '{', '}'.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os nós removidos.
    """
    # Lista de labels a serem removidos
    labels_to_remove = {",", ".", ";", "(", ")", "[", "]", "{", "}"}
    
    edges = []
    nodes_to_remove = set()

    # Identificar nós a remover
    for match in node_pattern.finditer(tree.source):
        node, label = match.groups()
        if label in labels_to_remove:
            nodes_to_remove.add(node)
    
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
    Remove os nós com labels em {"public", "int", "var"} e as arestas conectadas a eles.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph sem os nós e arestas removidos.
    """
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
    labels_to_remove = {"public", "int", "var", "new", "class", "tipo"}

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
    O operador é definido por seu label: {"+", "-", "*"}.
    O processo percorre a árvore de baixo para cima.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :param label: Label que define os nós a serem substituídos.
    :return: Novo objeto Digraph com os nós resolvidos.
    """

    # Operadores definidos
    operators = {"+", "-", "*", ">", "<", "<=", ">=", "==", "!=", "&&", "!"}
    
    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

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

def subir_primeiro_filho(tree, label):
    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    # Processar nós com o label fornecido
    for node, node_label in list(labels.items()):
        if node_label == label:
            # Verificar se o nó tem filhos
            if node in hierarchy and hierarchy[node]:
                # Substituir o label pelo label do primeiro filho
                first_child = hierarchy[node][0]
                labels[node] = labels[first_child]

                # Transferir os filhos do primeiro filho para o nó atual
                grandchildren = hierarchy.pop(first_child, [])
                hierarchy[node].extend(grandchildren)

                # Remover o primeiro filho
                hierarchy[node].remove(first_child)
                del labels[first_child]

    # Reconstruir o novo grafo
    new_tree = Digraph()
    for node, node_label in labels.items():
        new_tree.node(node, label=node_label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def resolver_pexp(tree):
    """
    Substitui nós com o label "pexp" pelo label de seus dois filhos concatenados.
    Remove todos os filhos antigos do nó e transfere apenas os filhos do segundo filho.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :return: Novo objeto Digraph com os nós resolvidos.
    """

    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    # Processar nós com o label "pexp"
    for node, node_label in list(labels.items()):
        if node_label == "pexp":
            # Pegar os filhos do nó
            first_child, second_child = hierarchy[node]
            # Concatenar os labels dos filhos
            concatenated_label = labels[first_child] + "." + labels[second_child]
            # Atualizar o label do nó "pexp"
            labels[node] = concatenated_label

            # Remover os filhos antigos do nó
            hierarchy[node] = []

            # Adicionar apenas os filhos do segundo filho ao nó
            hierarchy[node].extend(hierarchy[second_child])

            # Remover os filhos do primeiro e segundo filhos da árvore
            hierarchy.pop(first_child, None)
            hierarchy.pop(second_child, None)

            # Excluir os nós do primeiro e segundo filhos
            labels.pop(first_child, None)
            labels.pop(second_child, None)

    # Reconstruir o novo grafo
    new_tree = Digraph()
    for node, node_label in labels.items():
        new_tree.node(node, label=node_label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def resolver_cmd(tree):
    """
    Substitui um nó pelo primeiro filho cujo label esteja na lista 'especiais'.

    :param tree: Objeto Digraph da biblioteca Graphviz.
    :param label: Label do nó a ser processado.
    :param especiais: Lista de labels considerados especiais.
    :return: Novo objeto Digraph com as alterações aplicadas.
    """
    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    # Processar nós com o label fornecido
    for node, node_label in list(labels.items()):
        if node_label == "cmd":
            # Verificar se o nó tem filhos
            if node in hierarchy and hierarchy[node]:
                # Encontrar o primeiro filho cujo label está na lista 'especiais'
                special_child = None
                for child in hierarchy[node]:
                    if labels[child] in inst_nodes:
                        special_child = child
                        break

                # Se encontrou um filho especial, realizar a substituição
                if special_child:
                    labels[node] = labels[special_child]

                    # Transferir os filhos do nó especial para o nó atual
                    grandchildren = hierarchy.pop(special_child, [])
                    hierarchy[node].extend(grandchildren)

                    # Remover o filho especial
                    hierarchy[node].remove(special_child)
                    del labels[special_child]

    # Reconstruir o novo grafo
    new_tree = Digraph()
    for node, node_label in labels.items():
        new_tree.node(node, label=node_label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def remover_intermediario(tree, label):
    """
    Remove o nó com o label especificado. Os filhos do nó removido se tornam filhos do pai dele.

    :param tree: Objeto Digraph da biblioteca Graphviz representando a árvore.
    :param label: Label do nó a ser removido.
    :return: Novo objeto Digraph com as alterações aplicadas.
    """
    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    # Processar nós com o label fornecido
    for node, node_label in list(labels.items()):
        if node_label == label:
            # Encontrar o pai do nó a ser removido
            parent = None
            for potential_parent, children in hierarchy.items():
                if node in children:
                    parent = potential_parent
                    break

            # Transferir os filhos do nó removido para seu pai
            if parent is not None:
                children_to_add = hierarchy.pop(node, [])
                hierarchy[parent].extend(children_to_add)
                hierarchy[parent].remove(node)

            # Remover o nó
            del labels[node]

    # Reconstruir o novo grafo
    new_tree = Digraph()
    for node, node_label in labels.items():
        new_tree.node(node, label=node_label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def otimizar_ari(tree):
    """
    Encontra nós com label de operador aritmético ("+", "-", "*") e otimiza a operação
    se seus dois filhos forem números inteiros. Resolve a operação e substitui o label do nó pai.

    :param tree: Objeto Digraph da biblioteca Graphviz representando a árvore.
    :return: Novo objeto Digraph com as otimizações aplicadas.
    """
    # Construir hierarquia e armazenar labels
    hierarchy = defaultdict(list)
    labels = {}

    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    # Operadores aritméticos permitidos
    operadores = {"+", "-", "*"}

    # Processar nós com labels de operadores aritméticos
    for node, node_label in list(labels.items()):
        if node_label in operadores:
            # Verificar se os dois filhos são números inteiros
            if node in hierarchy and len(hierarchy[node]) == 2:
                left_child, right_child = hierarchy[node]
                left_label = labels.get(left_child, "")
                right_label = labels.get(right_child, "")

                # Verificar se os labels dos filhos são números
                if left_label.isdigit() and right_label.isdigit():
                    # Resolver a operação
                    expression = f"{left_label}{node_label}{right_label}"
                    result = eval(expression)

                    # Atualizar o label do nó pai
                    labels[node] = str(result)

                    # Remover os filhos
                    hierarchy.pop(node, None)
                    del labels[left_child]
                    del labels[right_child]

    # Reconstruir o novo grafo
    new_tree = Digraph()
    for node, node_label in labels.items():
        new_tree.node(node, label=node_label)
    for parent, children in hierarchy.items():
        for child in children:
            new_tree.edge(parent, child)

    return new_tree

def create_ast(tree):
    new_tree = remover_filhos(remover_triviais(remover_irrelevantes(remover_vazios(remover_detalhes(tree)))))

    for node in exp_nodes:
        new_tree = resolver_operadores(new_tree, node)

    for node in up_nodes:
        new_tree = subir_primeiro_filho(new_tree, node)

    for node in ["exps", "params"]:
        new_tree = remover_intermediario(new_tree, node)

    new_tree = resolver_pexp(new_tree)

    new_tree = resolver_cmd(new_tree)

    new_tree = otimizar_ari(new_tree)

    return new_tree