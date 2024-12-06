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
        current_class = f'CLASSE{self.id_class}'
        self.tree.node(current_class, 'classe')
        self.tree.edge(father, current_class)

        self.expect("key","class", current_class)
        self.expect("id", self.peek()[1], current_class)

        if self.peek()[1] == "extends":
            self.expect("key", "extends", current_class)
            self.expect("id", self.peek()[1], current_class)

        self.expect("del","{", current_class)
 
        while self.peek() != ("del", "}"):
            token = self.peek()
            if token[0] == "type":  # Uma variável começa com um tipo
                self.parse_var(current_class)
                self.id_var += 1
            elif token[0] == "key" and self.peek()[1] == "public":  # Método começa com "public"
                self.parse_method(current_class)
                self.id_method += 1
            else:
                raise ValueError(f"Token inesperado: {self.peek()}")
        
        self.expect("del", "}", current_class)
    

    def parse_var(self, father):
        current_var = f'VAR{self.id_var}'
        self.tree.node(current_var, "var")
        self.tree.edge(father, current_var)
        self.parse_type(current_var)
        self.id_type += 1
        self.expect("id", self.peek()[1], current_var)
        self.expect("del", ";", current_var)
    

    def parse_type(self, father):
        current_type = f'TYPE{self.id_type}'
        self.tree.node(current_type, "tipo")
        self.tree.edge(father, current_type)
        if self.peek()[1] == "int":
            self.expect("type", "int", current_type)
            if self.peek()[1] == "[":
                self.expect("del", "[", current_type)
                self.expect("del", "]", current_type)
        else:
            self.expect("type" or "id", self.peek()[1], current_type)
                
    def parse_method(self, father):
        current_method = f'METODO{self.id_method}'
        self.tree.node(current_method, "metodo")
        self.tree.edge(father, current_method)
        self.expect("key", "public", current_method)
        self.parse_type(current_method)
        self.expect("id", self.peek()[1], current_method)
        self.expect("del", "(", current_method)
        
        #params

        self.expect("del", ")", current_method)
        self.expect("del", "{", current_method)

        if self.peek()[0] == "type":
            self.parse_var(current_method)
            self.id_var += 1

        #CMD

        self.expect("del", "}", current_method)

       



        


