from graphviz import Digraph

class MiniJavaParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.id_class = 0
        self.id_method = 0
        self.id_var = 0
        self.id_type = 0
        self.id_params = 0
        self.id_cmd = 0
        self.id_exp = 0
        self.id_exp_aux = 0
        self.id_rexp = 0
        self.id_rexp_aux = 0
        self.id_aexp = 0
        self.id_aexp_aux = 0
        self.id_mexp = 0
        self.id_mexp_aux = 0
        self.id_sexp = 0
        self.id_sexp_aux = 0
        self.id_pexp = 0
        self.id_pexp_aux = 0
        self.id_exps = 0
        self.id_epsilon = 0
        self.tree = Digraph()

    def node_exists(self, node_id):
        return any(node_id in line for line in self.tree.body)
    
    def epsilon(self, father, has_son):
        current_epsilon = f'EPSILON{self.id_epsilon}'
        if self.node_exists(current_epsilon):
            self.id_epsilon += 1
            current_epsilon = f'EPSILON{self.id_epsilon}'

        if not has_son:
            self.tree.node(current_epsilon, 'ε')
            self.tree.edge(father, current_epsilon)

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

    
    ### Funções das especificações da EBNF
    # MAIN
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
        
        while self.peek()[1] != "}":
            self.parse_cmd("MAIN")

        self.expect("del","}", "MAIN")
        return
        
    def parse_class(self, father):
        current_class = f'CLASSE{self.id_class}'
        if self.node_exists(current_class):
            self.id_class += 1
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
            if token[0] == "type":  
                self.parse_var(current_class)
                self.id_var += 1
            elif token[0] == "key" and self.peek()[1] == "public":  
                self.parse_method(current_class)
                self.id_method += 1
            else:
                raise ValueError(f"Token inesperado: {self.peek()}")
        
        self.expect("del", "}", current_class)
    
    def parse_var(self, father):
        current_var = f'VAR{self.id_var}'
        if self.node_exists(current_var):
            self.id_var += 1
            current_var = f'VAR{self.id_var}'

        self.tree.node(current_var, "var")
        self.tree.edge(father, current_var)
        self.parse_type(current_var)
        self.expect("id", self.peek()[1], current_var)
        self.expect("del", ";", current_var)
    
    def parse_type(self, father):
        current_type = f'TYPE{self.id_type}'
        if self.node_exists(current_type):
            self.id_type += 1
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
        if self.node_exists(current_method):
            self.id_method += 1
            current_method = f'METODO{self.id_method}'

        self.tree.node(current_method, "metodo")
        self.tree.edge(father, current_method)
        self.expect("key", "public", current_method)
        self.parse_type(current_method)
        self.expect("id", self.peek()[1], current_method)
        self.expect("del", "(", current_method)
        
        while self.peek()[1] != ")":
            self.parse_params(current_method)

        self.expect("del", ")", current_method)
        self.expect("del", "{", current_method)

        while self.peek()[0] == "type":
            self.parse_var(current_method)

        while self.peek()[1] != "return":
            print(f'Entrei no parser_cmd pela 1 vez: {self.peek()}')
            self.parse_cmd(current_method)
        self.expect("key", "return", current_method)

        self.parse_exp(current_method)

        self.expect("del", ";", current_method)
        self.expect("del", "}", current_method)

    def parse_params(self, father):
        current_params = f'PARAMS{self.id_params}'
        if self.node_exists(current_params):
            self.id_params += 1
            current_params = f'PARAMS{self.id_params}'

        self.tree.node(current_params, "params")
        self.tree.edge(father, current_params)
        self.parse_type(current_params)
        self.expect("id", self.peek()[1], current_params)
        
        while self.peek()[1] != ")":
            self.expect("del", ",", current_params)
            self.parse_type(current_params)
            self.expect("id", self.peek()[1], current_params)

    def parse_cmd(self, father):
        current_cmd = f'CMD{self.id_cmd}'
        if self.node_exists(current_cmd):
            self.id_cmd += 1
            current_cmd = f'CMD{self.id_cmd}'

        self.tree.node(current_cmd, "cmd")
        self.tree.edge(father, current_cmd)

        token = self.peek()

        if token[0] == "del" and token[1] == "{":  # Bloco: '{ CMD }'
            self.expect("del", "{", current_cmd)
            while self.peek()[1] != "}":
                self.parse_cmd(current_cmd)
            self.expect("del", "}", current_cmd)

        elif token[0] == "key" and token[1] == "if":  # Condicional: 'if (EXP) CMD else CMD'
            self.expect("key", "if", current_cmd)
            self.expect("del", "(", current_cmd)
            self.parse_exp(current_cmd)
            self.expect("del", ")", current_cmd)
            self.parse_cmd(current_cmd)
            if self.peek() == ("key", "else"):
                self.expect("key", "else", current_cmd)
                self.parse_cmd(current_cmd)

        elif token[0] == "key" and token[1] == "while":  # Laço: 'while (EXP) CMD'
            self.expect("key", "while", current_cmd)
            self.expect("del", "(", current_cmd)
            self.parse_exp(current_cmd)
            self.expect("del", ")", current_cmd)
            self.parse_cmd(current_cmd)

        elif token[0] == "key" and token[1] == "System.out.println":  # Print: 'System.out.println (EXP);'
            self.expect("key", "System.out.println", current_cmd)
            self.expect("del", "(", current_cmd)
            self.parse_exp(current_cmd)  # Chama o parser de expressão
            self.expect("del", ")", current_cmd)
            self.expect("del", ";", current_cmd)


        elif token[0] == "id":  # Atribuição ou chamada de método
            self.expect("id", token[1], current_cmd)
            if self.peek()[0] == "op" and self.peek()[1] == "=":  # Atribuição: 'id = EXP;'
                self.expect("op", "=", current_cmd)
                self.parse_exp(current_cmd)
                self.expect("del", ";", current_cmd)
            elif  self.peek()[0] == "del" and self.peek()[1] == "[":  # Atribuição com índice: 'id[EXP] = EXP;'
                self.expect("del", "[", current_cmd)
                self.parse_exp(current_cmd)
                self.expect("del", "]", current_cmd)
                self.expect("op", "=", current_cmd)
                self.parse_exp(current_cmd)
                self.expect("del", ";", current_cmd)
            

        else:
            raise SyntaxError(f"Comando inválido ou inesperado: {token}")
        
    # Regra original: EXP -> EXP && REXP | REXP
    # Regra atual: EXP -> REXP EXP_AUX
    # Regra adicional: EXP_AUX -> && REXP EXP_AUX | ε    
    def parse_exp(self, father):
        current_exp = f'EXP{self.id_exp}'
        if self.node_exists(current_exp):
            self.id_exp += 1
            current_exp = f'EXP{self.id_exp}'
        
        self.tree.node(current_exp, 'exp')
        self.tree.edge(father, current_exp)
        self.parse_rexp(current_exp)
        self.parse_exp_aux(current_exp)

    def parse_exp_aux(self, father):
        has_son = False
        current_exp_aux = f'EXP_AUX{self.id_exp_aux}'
        if self.node_exists(current_exp_aux):
            self.id_exp_aux += 1
            current_exp_aux = f'EXP_AUX{self.id_exp_aux}'

        self.tree.node(current_exp_aux, 'exp_aux')
        self.tree.edge(father, current_exp_aux)
        
        while self.peek()[1] == '&':
            self.expect("op", "&", current_exp_aux)
            self.expect("op", "&", current_exp_aux) # Verificar se o token está pegando && ou apenas &
            self.parse_rexp(current_exp_aux)
            self.parse_exp_aux(current_exp_aux)
            has_son = True
        
        self.epsilon(current_exp_aux, has_son)

    # Regra original: REXP -> REXP < AEXP | REXP > AEXP | REXP == AEXP | REXP != AEXP | AEXP
    # Regra atual: REXP -> AEXP REXP_AUX
    # Regra adicional: REXP_AUX -> < AEXP REXP_AUX | == AEXP REXP_AUX | != AEXP REXP_AUX | ε  
    def parse_rexp(self, father):
        current_rexp = f'REXP{self.id_rexp}'
        if self.node_exists(current_rexp):
            self.id_rexp += 1
            current_rexp = f'REXP{self.id_rexp}'

        self.tree.node(current_rexp, 'rexp')
        self.tree.edge(father, current_rexp)
        self.parse_aexp(current_rexp)
        self.parse_rexp_aux(current_rexp)

    def parse_rexp_aux(self, father):
        has_son = False
        current_rexp_aux = f'REXP_AUX{self.id_rexp_aux}'
        if self.node_exists(current_rexp_aux):
            self.id_rexp_aux += 1
            current_rexp_aux = f'REXP_AUX{self.id_rexp_aux}'

        self.tree.node(current_rexp_aux, 'rexp_aux')
        self.tree.edge(father, current_rexp_aux)

        while self.peek()[1] in ['<', '=', '!']: # Verificar se o token está pegando == e != ou apenas = e !
            self.expect("op", self.peek()[1], current_rexp_aux)
            if self.peek()[1] == "=":
                self.expect("op", "=", current_rexp_aux)

            self.parse_aexp(current_rexp_aux)
            self.parse_rexp_aux(current_rexp_aux)
            has_son = True
        
        self.epsilon(current_rexp_aux, has_son)
        


    # Regra original: AEXP -> AEXP + MEXP | AEXP - MEXP | MEXP
    # Regra atual: AEXP -> MEXP AEXP_AUX
    # Regra adicional: AEXP_AUX -> + MEXP AEXP_AUX | - MEXP AEXP_AUX | ε
    def parse_aexp(self, father):
        current_aexp = f'AEXP{self.id_aexp}'
        if self.node_exists(current_aexp):
            self.id_aexp += 1
            current_aexp = f'AEXP{self.id_aexp}'

        self.tree.node(current_aexp, 'aexp')
        self.tree.edge(father, current_aexp)
        self.parse_mexp(current_aexp)
        self.parse_aexp_aux(current_aexp)

    def parse_aexp_aux(self, father):
        has_son = False
        current_aexp_aux = f'AEXP_AUX{self.id_aexp_aux}'
        if self.node_exists(current_aexp_aux):
            self.id_aexp_aux += 1
            current_aexp_aux = f'AEXP_AUX{self.id_aexp_aux}'

        self.tree.node(current_aexp_aux, 'aexp_aux')
        self.tree.edge(father, current_aexp_aux)

        while self.peek()[1] in ['+', '-']:
            self.expect("op", self.peek()[1], current_aexp_aux)
            self.parse_mexp(current_aexp_aux)
            self.parse_aexp_aux(current_aexp_aux)
            has_son = True
        
        self.epsilon(current_aexp_aux, has_son)

    # Regra original: MEXP -> MEXP * SEXP | SEXP
    # Regra atual: MEXP -> SEXP MEXP_AUX
    # Regra adicional: MEXP_AUX -> * SEXP MEXP_AUX | ε
    def parse_mexp(self, father):
        current_mexp = f'MEXP{self.id_mexp}'
        if self.node_exists(current_mexp):
            self.id_mexp += 1
            current_mexp = f'MEXP{self.id_mexp}'

        self.tree.node(current_mexp, 'mexp')
        self.tree.edge(father, current_mexp)
        self.parse_sexp(current_mexp)
        self.parse_mexp_aux(current_mexp)

    def parse_mexp_aux(self, father):
        has_son = False
        current_mexp_aux = f'MEXP_AUX{self.id_mexp_aux}'
        if self.node_exists(current_mexp_aux):
            self.id_mexp_aux += 1
            current_mexp_aux = f'MEXP_AUX{self.id_mexp_aux}'

        self.tree.node(current_mexp_aux, 'mexp_aux')
        self.tree.edge(father, current_mexp_aux)

        while self.peek()[1] == '*':
            self.expect("op", "*", current_mexp_aux)
            self.parse_sexp(current_mexp_aux)
            self.parse_mexp_aux(current_mexp_aux)
            has_son = True
        
        self.epsilon(current_mexp_aux, has_son)

    # Regra: SEXP -> ! SEXP | - SEXP | true | false | num | null | new int '[' EXP ']' | PEXP . length | PEXP '[' EXP ']' | PEXP
    # Obs: Não foi alterada
    def parse_sexp(self, father):
        current_sexp = f'SEXP{self.id_sexp}'
        if self.node_exists(current_sexp):
            self.id_sexp += 1
            current_sexp = f'SEXP{self.id_sexp}'

        self.tree.node(current_sexp, 'sexp')
        self.tree.edge(father, current_sexp)
        
        token = self.peek()

        if token[1] in ['!','-']:
            self.expect("op", token[1], current_sexp)
            self.parse_sexp(current_sexp)
        elif token[1] in ['true', 'false', 'null']:
            self.expect("key", token[1], current_sexp)
        elif token[1] == "new":
            # Quando começa com new pode ser tanto para o SEXP quanto para o PEXP
            # O que determina é o token que vem depois
            # Seria bom achar uma forma de ver mais à frente sem consumir
            self.expect("key", token[1], current_sexp)
            if self.peek()[1] == "int": # Mantém no SEXP
                self.expect("type", "int", current_sexp)
                self.expect("del", "[", current_sexp)
                self.parse_exp(current_sexp)
                self.expect("del", "]", current_sexp)
            elif self.peek()[0] == "id": # Ir para o PEXP
                self.parse_pexp(current_sexp, is_new = True)
            else: # Erro no programa
                raise ValueError(f"Token inesperado: {self.peek()}")
        elif token[0] == "num":
            self.expect("num", token[1], current_sexp)
        else:
            self.parse_pexp(current_sexp)
            token = self.peek()
            if token[1] == ".":
                self.expect("del", token[1], current_sexp)
                self.expect("key", "length", current_sexp)
            elif token[1] == "[":
                self.expect("del", token[1], current_sexp)
                self.parse_exp(current_sexp)
                self.expect("del", "]", current_sexp)
    
    # Regra original: PEXP -> id | this | new id '(' ')' | '(' EXP ')' | PEXP . id | PEXP . id '(' [EXPS] ')'
    # Regra atual: PEXP -> id PEXP_AUX | this PEXP_AUX | new id '(' ')' PEXP_AUX | '(' EXP ')' PEXP_AUX
    # Regra adicional: PEXP_AUX -> . id PEXP_AUX | . id '(' [EXPS] ')' PEXP_AUX | ε
    # Obs: O parâmetro is_new ajuda a diferenciar o SEXP do PEXP
    def parse_pexp(self, father, is_new = False):
        current_pexp = f'PEXP{self.id_pexp}'
        if self.node_exists(current_pexp):
            self.id_pexp += 1
            current_pexp = f'PEXP{self.id_pexp}'

        self.tree.node(current_pexp, 'pexp')
        self.tree.edge(father, current_pexp)

        token = self.peek()

        if is_new: # O new já foi consumido pelo SEXP
            self.expect("id", self.peek()[1], current_pexp)
            self.expect("del", "(", current_pexp)
            self.expect("del", ")", current_pexp)
            self.parse_pexp_aux(current_pexp)
        elif token[0] == "id":
            self.expect("id", token[1], current_pexp)
            self.parse_pexp_aux(current_pexp)
        elif token[1] == "this":
            self.expect("key", token[1], current_pexp)
            self.parse_pexp_aux(current_pexp)
        elif token[1] == "(":
            self.expect("del", "(", current_pexp)
            self.parse_exp(current_pexp) 
            self.expect("del", ")", current_pexp)
            self.parse_pexp_aux(current_pexp)
        else:
            raise ValueError(f"Token inesperado: {self.peek()}")

    def parse_pexp_aux(self, father):
        has_son = False
        current_pexp_aux = f'PEXP_AUX{self.id_pexp_aux}'
        if self.node_exists(current_pexp_aux):
            self.id_pexp_aux += 1
            current_pexp_aux = f'PEXP_AUX{self.id_pexp_aux}'

        self.tree.node(current_pexp_aux, 'pexp_aux')
        self.tree.edge(father, current_pexp_aux)

        if self.peek()[1] == ".":
            self.expect("del", ".", current_pexp_aux)
            self.expect("id", self.peek()[1], current_pexp_aux)
            if self.peek()[1] == '(':
                self.expect("del", "(", current_pexp_aux)
                if self.peek()[1] == ")": # EXPS é opcional
                    self.expect("del", ")", current_pexp_aux)
                else:
                    self.parse_exps(current_pexp_aux)
                    self.expect("del", ")", current_pexp_aux)
            self.parse_pexp_aux(current_pexp_aux)
            has_son = True

        self.epsilon(current_pexp_aux, has_son)
    # Regra: EXPS -> EXP {, EXP}
    # Obs: Não foi alterada
    def parse_exps(self, father):
        current_exps = f'EXPS{self.id_exps}'
        if self.node_exists(current_exps):
            self.id_exps += 1
            current_exps = f'EXPS{self.id_exps}'

        self.tree.node(current_exps, 'exps')
        self.tree.edge(father, current_exps)
        self.parse_exp(current_exps)
        while self.peek()[1] == ",":
            self.expect("del", ",", current_exps)
            self.parse_exp(current_exps)
