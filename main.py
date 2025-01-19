import sys
from classes.scanner import MiniJavaScanner
from classes.parser import MiniJavaParser
from classes.ast import create_ast

# Verificar se o nome do arquivo foi fornecido como argumento
if len(sys.argv) < 2:
    print("Passe o nome de um arquivo.java como argumento")
else:
    scanner = MiniJavaScanner()
    i = 0

    tokens = scanner.scan(sys.argv[1])
    parser = MiniJavaParser(tokens)
    parser.parse_prog()

    if len(parser.symbol_table.errors) > 0:
        print(f"{len(parser.symbol_table.errors)} erro(s) encontrado(s):")
        for i in range(len(parser.symbol_table.errors)):
            print(f"Erro {i+1}: {parser.symbol_table.errors[i]}")
        sys.exit()

    parser.tree.render('./outputs/tree', format='png')
    print("Árvore gerada com sucesso. Arquivo criado em 'outputs/tree.png'")

    ast = create_ast(parser.tree)
    ast.render('./outputs/ast', format='png')
    print("Árvore abstrata gerada com sucesso. Arquivo criado em 'outputs/ast.png'")

    parser.symbol_table.print_table()
