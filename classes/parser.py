from graphviz import Digraph

class MiniJavaParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
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
            self.current -= 0  # Voltar para não consumir o "CLASS"
            self.tree.node('CLASSE', 'classe')
            self.tree.edge('PROG', 'CLASSE')
            self.parse_class()

        

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
        #cmd = self.parse_cmd()
        self.expect("del","}", "MAIN")
        return
        

    def parse_class(self):
        self.expect("key","class", "CLASSE")
        self.expect("id", None, "CLASSE")

        if self.peek()[1] == "extends":
            self.expect("key", "extends", "CLASSE")
            self.expect("id", None, "CLASSE")

        self.expect("del","{", "CLASSE")
 
        while self.peek() != ("del", "}"):
            token = self.peek()
            if token[0] == "type":  # Uma variável começa com um tipo
                self.parse_var()
            elif token[0] == "key" and self.current_token()[1] == "public":  # Método começa com "public"
                self.parse_method()
            else:
                raise ValueError(f"Token inesperado: {self.peek()}")
        
        self.expect("del", "}", "CLASSE")

    
    def parse_type(self):
        self.tree.node("VAR", "var")
        self.expect("type" or "id", self.peek()[1], "VAR")
        self.expect("id", self.peek()[1], "VAR")
        self.expect("del", ";", "VAR")
    

    def parse_method(self):
        self.tree.node("METODO", "metodo")
        self.expect("key", "public", "METODO")
        self.expect("type" or "id", self.peek()[1], "METODO")
        self.expect("id", self.peek()[1], "METODO")
        self.expect("del", "(", "METODO")
        
        if self.peek()[1] == "extends":
            self.expect("key", "extends", "CLASSE")
            self.expect("id", None, "CLASSE")


       



        


