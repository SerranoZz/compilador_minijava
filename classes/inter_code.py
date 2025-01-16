import re
from graphviz import Digraph
from collections import defaultdict, deque

# Os nós de operadores representam expressões
operators = ["+", "-", "*", ">", "<", "<=", ">=", "==", "!=", "&&", "!"]
# Os nós de palavras reservadas representam instruções
inst = ["System.out.println", "if", "while"]
# Regex para capturar nós com labels
node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
# Regex para capturar nós e arestas
edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')
# Cada item é uma linha do código intermediário
code = []
# Identifica quais são os parâmetros de cada método na ordem correta
params_list = []
# Contador de temporários
temp = 0
# Controle de else
c_else = 0

def new_temp():
    global temp
    temp += 1
    return temp

def new_else():
    global c_else
    c_else += 1
    return c_else

# Considerando que não há vetores na linguagem
def l_value(label):
    if label not in inst and "." not in label and label not in operators:
        return True
    return False

def r_value(tree, id, label):
    if "." in label: # O nó é uma chamada de método
        t = new_temp()
        code.append(f"t{t} := {call_method(tree, id, label)}")
        return f"t{t}"
    if label not in inst and label not in operators: # O nó é um número ou uma variável
        return label
    hierarchy, labels = extrair_hierarquia_e_labels(tree)
    first_op_id = hierarchy[id][0] 
    first_op_label = labels.get(first_op_id, first_op_id)
    second_op_id = hierarchy[id][1] 
    second_op_label = labels.get(second_op_id, second_op_id)
    if label in operators: # O nó é uma expressão aritmética ou relacional
        t = new_temp()
        code.append(f"t{t} := {r_value(tree,first_op_id,first_op_label)} {label} {r_value(tree,second_op_id,second_op_label)}")
        return f"t{t}"

def build_method(tree, id, parent_label, label):
    params_children = []
    for iten in params_list:
        if iten[0] == f'{parent_label}.{label}':
            i= -1
            while ('.' not in iten[i]):
                params_children.append(iten[i])
                i -=1 
            break
    hierarchy, labels = extrair_hierarquia_e_labels(tree)
    for child_id in hierarchy[id]:
        child_label = labels.get(child_id, child_id)
        if child_label in inst: 
            find_instruction(tree, child_id, child_label)
        elif child_label == "=":
            assign(tree, child_id, child_label)
        elif child_label not in params_children and child_label != "return":
            return_value = [child_id, child_label]
    code.append(f"return {r_value(tree, return_value[0], labels.get(return_value[1], return_value[1]))}")

def find_instruction(tree, id, label):
    inst_fuctions = [instruction_print,instruction_if,instruction_while]
    inst_fuctions[inst.index(label)](tree, id)

def assign(tree, id, label):
    # Supondo que o primeiro filho é sempre o identificador
    hierarchy, labels = extrair_hierarquia_e_labels(tree)
    code.append(f"{labels.get(hierarchy[id][0])} := {r_value(tree, hierarchy[id][1], labels.get(hierarchy[id][1], hierarchy[id][1]))}")

def call_method(tree, id, label):
    n_params = 0
    hierarchy, labels = extrair_hierarquia_e_labels(tree)

    # Carrega os parâmetros na ordem inversa
    idx = len(hierarchy[id])-1
    while idx >= 0:
        n_params += 1
        code.append(f"param {r_value(tree, hierarchy[id][idx], labels.get(hierarchy[id][idx], hierarchy[id][idx]))}")
        idx -= 1
    return f"call {label}, {n_params}"

def find_way(tree, id, label):
    if label in inst:
        find_instruction(tree, id, label)
    elif label in operators:
        return r_value(tree, id, label)
    elif "." in label:
        return call_method(tree, id, label)
    elif label == "=":
        assign(tree, id, label)
    else:
        params(label)

def params(label):
    t = new_temp()
    code.append(f"t{t} := {label}")
      
def instruction_while(tree, id):
    print("Está no while")

def instruction_if(tree, id):
    n = new_else()
    after = f"end_if_{n}"    
    hierarchy, labels = extrair_hierarquia_e_labels(tree)
    if len(hierarchy[id]) == 4: # Tem else
        codition = hierarchy[id][3] # A condição aparece como último filho
        if_block = hierarchy[id][0] # As intruções em casa de valor verdadeiro são o primeiro filho
        else_block = hierarchy[id][2] # O else é o segundo filho e suas instruções são o terceiro
        after = f"else_{n}"
    
    code.append(f"ifFalse {r_value(tree, codition, labels.get(codition, codition))} goto {after}")
    find_way(tree, if_block, labels.get(if_block, if_block))
    code.append(f"goto end_{after}")
    code.append(f"{after}:")

    if len(hierarchy[id]) == 4:
        find_way(tree, else_block, labels.get(else_block, else_block))
        code.append(f"end_{after}:")


def instruction_print(tree, id):
    hierarchy, labels = extrair_hierarquia_e_labels(tree)
    # Possui apenas um filho
    child_id = hierarchy[id][0]
    child_label = labels.get(child_id, child_id)
    code.append(f"print {r_value(tree, child_id, child_label)}")

def extrair_hierarquia_e_labels(tree):
    """
    Extrai a hierarquia (arestas pai-filho) e os labels dos nós de uma árvore.

    :param tree: Objeto Digraph da biblioteca Graphviz representando a árvore.
    :return: Dois dicionários: hierarchy (pai -> filhos) e labels (nó -> label).
    """
    hierarchy = defaultdict(list)
    labels = {}

    # Extrair arestas (pai -> filho)
    edge_pattern = re.compile(r'(\S+)\s*->\s*(\S+)')
    for match in edge_pattern.finditer(tree.source):
        parent, child = match.groups()
        hierarchy[parent].append(child)

    # Extrair labels dos nós
    node_pattern = re.compile(r'(\S+)\s*\[label="?([^"\]]+)"?\]')
    for match in node_pattern.finditer(tree.source):
        node, node_label = match.groups()
        labels[node] = node_label

    return hierarchy, labels

def get_params(label):
    for iten in params_list:
        if label == iten[0]:
            return ", ".join(iten[1:])

def filho_classe(class_label, node, tree):
    hierarchy, labels = extrair_hierarquia_e_labels(tree)
    for child_id in hierarchy[node]:
        child_label = labels.get(child_id, child_id)
        f_params = get_params(f"{class_label}.{child_label}")
        code.append(f"\n{class_label}.{child_label}({f_params}):")
        build_method(tree, child_id, class_label, child_label)


# Funções a serem chamadas
def filho_main(node, tree):
    """
    Imprime todos os filhos do nó 'main'.

    :param node: Nome do nó 'main'.
    :param tree: Objeto Digraph da biblioteca Graphviz representando a árvore.
    """
    hierarchy, labels = extrair_hierarquia_e_labels(tree)

    code.append("main:")

    # Usa o id do nó na hierarquia para encontrar os filhos deste nó
    for child_id in hierarchy[node]:
        child_label = labels.get(child_id, child_id)
        find_way(tree, child_id, child_label)

def parse_file(filename):
    # Regex para capturar classes e métodos com seus parâmetros
    class_pattern = re.compile(r'class\s+(\w+)')
    method_pattern = re.compile(r'public\s+\w+\s+(\w+)\(([^)]*)\)')

    # Variável para armazenar a classe atual
    current_class = None

    # Abrir e ler o arquivo
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            # Verificar se a linha define uma classe
            class_match = class_pattern.match(line)
            if class_match:
                current_class = class_match.group(1)

            # Verificar se a linha define um método
            method_match = method_pattern.match(line)
            if method_match and current_class:
                method_name = method_match.group(1)
                parameters = method_match.group(2).strip()
                parameter_list = [param.split()[-1] for param in parameters.split(',') if param]  # Extrair nomes dos parâmetros
                params_list.append([f"{current_class}.{method_name}"] + parameter_list)

def save_in_file():
    with open('./outputs/inter_code.txt', 'w') as f:
        for line in code:
            f.write(line+'\n')

def iniciar_busca(tree, filename):
    """
    Percorre os filhos da raiz da árvore e chama as funções apropriadas para 'main' e 'classe'.

    :param tree: Objeto Digraph da biblioteca Graphviz representando a árvore.
    """

    hierarchy, labels = extrair_hierarquia_e_labels(tree)

    # Verificar se a raiz existe e é "prog"
    root = None
    for node, node_label in labels.items():
        if node_label == "prog":
            root = node
            break

    if root is None:
        raise ValueError("A raiz da árvore não foi encontrada.")

    parse_file(filename)

    # Percorrer os filhos de 'prog'
    for child_id in hierarchy.get(root, []):
        child_label = labels.get(child_id, "")
        if child_label == "main":
            filho_main(child_id, tree)
        else:
            filho_classe(child_label, child_id, tree)

    save_in_file()
