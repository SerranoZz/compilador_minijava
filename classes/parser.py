from graphviz import Digraph

class MiniJavaParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.id_class = 0
        self.id_method = 0
        self.id_var = 0
        self.id_type = 0
        self.tree = Digraph()

    def peek(self):
        """Retorna o token atual sem consumir."""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def advance(self):
        """Consome o token atual e avança para o próximo."""
        if self.current < len(self.tokens):
            self.current += 1

    def match(self, category, value=None):
        """Verifica se o token atual corresponde à categoria e valor."""
        token = self.peek()
        if token and token[0] == category and (value is None or token[1] == value):
            self.advance()
            return token
        

    def expect(self, category, value, father):
        """Garante que o token atual é o esperado; caso contrário, gera um erro."""
        token = self.match(category, value)
        if not token:
            raise SyntaxError(f"Expected {category} '{value}', got {self.peek()}")

        self.tree.node(f'{self.current}', f'{value}')
        self.tree.edge(father, f'{self.current}')
    
    #Início do Parser
    def parse_prog(self):
        self.tree.node('PROG', 'prog')
        self.tree.node('MAIN', 'main')
        self.tree.edge('PROG', 'MAIN')
        self.parse_main()
        self.current += 1
        while self.match("key", "class"):
            self.current -= 1  # Voltar para não consumir o "CLASS"
            self.parse_class("PROG")
            self.id_class += 1

    
    #Funções das especificações da EBNF
    def parse_main(self):
        self.expect("key","class", "MAIN")
        self.expect("id", self.peek()[1], "MAIN")
        self.expect("del","{", "MAIN")
        self.expect("key","public", "MAIN")
        self.expect("key","static", "MAIN")
        self.expect("key","void", "MAIN")
        self.expect("key","main", "MAIN")
        self.expect("del","(", "MAIN")
        self.expect("key","String", "MAIN")
        self.expect("del","[", "MAIN")
        self.expect("del","]", "MAIN")
        self.expect("id", self.peek()[1], "MAIN")
        self.expect("del",")", "MAIN")
        self.expect("del","{", "MAIN")
        
        #CMD

        self.expect("del","}", "MAIN")
        return
        

    def parse_class(self, father):
        classe_atual = f'CLASSE{self.id_class}'
        self.tree.node(classe_atual, 'classe')
        self.tree.edge(father, classe_atual)

        self.expect("key","class", classe_atual)
        self.expect("id", self.peek()[1], classe_atual)

        if self.peek()[1] == "extends":
            self.expect("key", "extends", classe_atual)
            self.expect("id", self.peek()[1], classe_atual)

        self.expect("del","{", classe_atual)
 
        while self.peek() != ("del", "}"):
            token = self.peek()
            if token[0] == "type":  # Uma variável começa com um tipo
                self.parse_var(classe_atual)
                self.id_var += 1
            elif token[0] == "key" and self.peek()[1] == "public":  # Método começa com "public"
                self.parse_method(classe_atual)
                self.id_method += 1
            else:
                raise ValueError(f"Token inesperado: {self.peek()}")
        
        self.expect("del", "}", classe_atual)
    

    def parse_var(self, father):
        var_atual = f'VAR{self.id_var}'
        self.tree.node(var_atual, "var")
        self.tree.edge(father, var_atual)
        self.parse_type(var_atual)
        self.id_type += 1
        self.expect("id", self.peek()[1], var_atual)
        self.expect("del", ";", var_atual)
    

    def parse_type(self, father):
        type_atual = f'TYPE{self.id_type}'
        self.tree.node(type_atual, "tipo")
        self.tree.edge(father, type_atual)
        if self.peek()[1] == "int":
            self.expect("type", "int", type_atual)
            if self.peek()[1] == "[":
                self.expect("del", "[", type_atual)
                self.expect("del", "]", type_atual)
        else:
            self.expect("type" or "id", self.peek()[1], type_atual)
                
    def parse_method(self, father):
        metodo_atual = f'METODO{self.id_method}'
        self.tree.node(metodo_atual, "metodo")
        self.tree.edge(father, metodo_atual)
        self.expect("key", "public", metodo_atual)
        self.parse_type(metodo_atual)
        self.expect("id", self.peek()[1], metodo_atual)
        self.expect("del", "(", metodo_atual)
        
        #params

        self.expect("del", ")", metodo_atual)
        self.expect("del", "{", metodo_atual)
        self.parse_var(metodo_atual)
        
        #CMD
        
        self.expect("del", "}", metodo_atual)

       



        


