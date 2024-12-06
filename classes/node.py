#Classe que lida com os nós da árvore sintática

class Node:
    def __init__(self, name, children=None, token=None):
        self.name = name  # Nome da produção ou terminal
        self.children = children if children else []  # Nós filhos
        self.token = token  # Token (apenas para terminais)

    def __repr__(self):
        return f"Node({self.name}, {self.children})"