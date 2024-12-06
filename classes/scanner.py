# Análise Léxica da linguagem MiniJava+
# Este programa representa a primeira parte de um compilador: o scanner
# Entrada: nome do programa a ser analisado (passar como argumento)
# Saída: Uma lista de tuplas identificando cada token na ordem em que aparece

import re

class MiniJavaScanner:
    def __init__(self):
        # Tipos de tokens reconhecidos por MiniJava+
        self.TYPES = [
            ("key", r"\b(System.out.println|class|extends|public|static|void|main|if|else|while|return|true|false|String|null)\b"),
            ("type", r"\b(boolean|int)\b"),
            ("id", r"[a-zA-Z_][a-zA-Z0-9_]*"),
            ("num", r"\b\d+\b"),
            ("op", r"[+\-*/=<>!]"),
            ("del", r"[{}()\[\];.,]"),
            ("blank", r"\s+"),  # O compilador vai ignorar espaços em branco
        ]
    

    """
        Extrai e classifica os tokens do código na ordem em que aparecem.
        Entrada: o código em formato de strings com os comentários já removidos.
        Saída: os tokens organizados em uma lista de tuplas.
        """
    def get_tokens(self, code):
        tokens = []
        position = 0

        while position < len(code):
            match = None
            for token_type, regex in self.TYPES:
                match = re.compile(regex).match(code, position)
                if match:
                    # Ignora espaços em branco
                    if token_type != "blank":
                        tokens.append((token_type, match.group()))
                    # Avança para a próxima palavra do código
                    position = match.end()
                    break

            # Exibe uma mensagem de erro ao não reconhecer uma palavra
            if not match:
                raise ValueError(f"Falha de reconhecimento na posição {position}: '{code[position]}'")

        return tokens


    # Remove todos os comentários do código (não serão analisados)
    # Entrada: o nome do arquivo.java a ser analisado
    # Saída: uma string com o conteúdo deste arquivo sem as linhas de comentários 
    def remove_comments(self, filename):
        # O arquivo é fechado automaticamente após a leitura
        with open(filename, 'r') as file:
            content = file.read()

        # Definindo expressões regulares para cada tipo de comentário
        single_line = r"//.*"
        mult_lines = r"/\*.*?\*/"

        # Removendo todas as linhas de comentários
        content = re.sub(single_line, '', content)
        to_remove = re.findall(mult_lines, content, re.DOTALL)
        for r in to_remove:
            content = content.replace(r, '')

        return content


    """
        Realiza o processo completo de análise léxica:
        - Remove comentários do arquivo.
        - Extrai os tokens do código limpo.
        Entrada: o nome do arquivo.java a ser analisado.
        Saída: uma lista de tokens extraídos do código.
        """
    def scan(self, filename):
        code_without_comments = self.remove_comments(filename)
        tokens = self.get_tokens(code_without_comments)
        return tokens



