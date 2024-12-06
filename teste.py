from graphviz import Digraph

# Criando o objeto da árvore
dot = Digraph()

# Adicionando nós
dot.node('A', 'a')
dot.node('B', 'b')
dot.node('C', 'c')
dot.node('D', 'd')

# Adicionando arestas (relações entre nós)
dot.edge('A', 'B')
dot.edge('A', 'C')
dot.edge('B', 'D')

# Renderizando o gráfico
dot.render('tree', format='png')
