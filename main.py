import sys
from classes.scanner import MiniJavaScanner
from classes.parser import MiniJavaParser

# Verificar se o nome do arquivo foi fornecido como argumento
if len(sys.argv) < 2:
    print("Passe o nome de um arquivo.java como argumento")
else:
    scanner = MiniJavaScanner()
    i = 0
    try:
        tokens = scanner.scan(sys.argv[1])
        for token in tokens:
            print(f'{token} - {i}')
            i += 1
    except Exception as e:
        print(f"Erro: {e}")

    parser = MiniJavaParser(tokens)
    parser.parse_prog()
    parser.tree.render('tree', format='png')