# Análise Léxica
# TO DO:
# Contar espaços em branco --> DONE
# Separar cada token em lexemas, incluindo (,[,{,},],) que não tem espaço
# Classificar cada token

import sys
import os
import re

# Unidades lógicas (lexemas) --> lista de listas
unities = []
# Tokens e seus tipos --> lista de tuplas
tokens = []
# Quantidade de caracteres por linha (tokens e espaços em branco) --> lista de inteiros
num_char = []
# Símbolo que representa qualquer espaço em branco (incluindo quebras de linha)
any_blank = r"[\s]" # Será usado pelo comando re.findall()
# Arquivo temporário
TMP = "tmp.java"
# Tokens encontrados e seus identificadores --> Lista de tuplas
TOKENS = []



def remove_comments(filename):
    with open(filename, 'r') as file:
        content = file.read()
    # Definindo expressões regulares para cada tipo de comentário
    single_line = r"//.*"
    mult_lines= r"/\*.*?\*/"
    content = re.sub(single_line,'',content)
    to_remove = re.findall(mult_lines, content, re.DOTALL)
    for r in to_remove:
        content = content.replace(r,'')
    return content


def format_delimiters(content):
    for d in ['(',')','[',']','{','}',',',';']:
        content = content.replace(d,f' {d} ')
    #print(content)
    tmp = open(TMP,'w')
    tmp.write(content)
    tmp.close()


def regular_expressions(string):
    if re.match(r"\b(System.out.println|class|public|static|void|main|if|else|while|return|true|false)\b",string):
        return 'key'
    elif re.match(r"\b(boolean|int)\b",string):
        return 'type'
    elif re.match(r"[a-zA-Z_][a-zA-Z0-9_]*",string):
        return 'id'
    elif re.match(r"\b\d+\b",string):
        return 'num'
    elif re.match(r"[+\-*/=<>!&]",string):
        return 'op'
    elif re.match(r"[{}()\[\];.,]",string):
        return 'del'
    return 'not_found'


def print_unities():
    for list in unities:
        print(list)


def read_file(filename):
    any_blank = r"[\s]"
    with open(filename,'r') as file:
        for line in file:            
            num_char.append(len(re.findall(any_blank, line)))
            only_text = line.strip() # Remove espaços em branco no início e no final da linha
            words = only_text.split(' ')
            for word in words:
                if len(word)>0:
                    result = regular_expressions(word)
                    if result == 'not_found':
                        print(f"A palavra {word} não foi reconhecida!")
                    TOKENS.append((result,word))
            #unities.append(words)
            
            #regular_expressions(only_text) 
    #print_unities()


if __name__ == "__main__":
    # Verificar se o nome do arquivo foi fornecido como argumento
    if len(sys.argv) < 2:
        print("Uso: python script.py <nome_arquivo>")
    else:
        format_delimiters(remove_comments(sys.argv[1]))
        #read_file(sys.argv[1])
        read_file(TMP) # O argumento passado é o nome do arquivo que será lido
        #for i, n in enumerate(num_char):
        #    print(f"Quantidade de espaços em branco na linha {i+1}: {n}")
        print(TOKENS)
        os.remove(TMP)
