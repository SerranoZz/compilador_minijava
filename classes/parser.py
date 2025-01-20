from graphviz import Digraph
from classes.symtable import SymbolTable
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
        self.symbol_table = SymbolTable()
        self.tree = Digraph()


    def find_second_class_position(self):
        first_class_pos = None
        second_class_pos = None

        # Itera pelos self.tokens para encontrar o primeiro "key" "class"
        for index, (token_type, token_value) in enumerate(self.tokens):
            if token_type == "key" and token_value == "class":
                if first_class_pos is None:
                    first_class_pos = index
                elif first_class_pos is not None and second_class_pos is None:
                    second_class_pos = index
                    break  # Encontrou o segundo "class", não precisamos continuar

        return second_class_pos

    def evaluate_exp(self, expressao):
        # Define os operadores permitidos
        operadores = {'+', '-', '*'}
        
        # Filtra os elementos que não são operadores
        operandos = [item for item in expressao if item not in operadores]
        
        # Verifica se todos os operandos são números
        if all(op.replace('.', '', 1).isdigit() for op in operandos):
            # Avalia a expressão usando o eval para números
            resultado = eval(''.join(expressao))
            return resultado

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
            raise SyntaxError(f"Token Esperado: {category} '{value}', Token Lido: {self.peek()}")

        self.tree.node(f'{self.current}', f'{value}')
        self.tree.edge(father, f'{self.current}')
    
    def flatten_list(self, nested_list):
        flat_list = []
        for item in nested_list:
            if isinstance(item, list):
                flat_list.extend(self.flatten_list(item))  # Chama recursivamente para cada lista interna
            else:
                flat_list.append(item)
        return flat_list
    
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
        
        return has_son
    
    #Início do Parser
    def parse_prog(self):
        self.tree.node('PROG', 'prog')
        self.tree.node('MAIN', 'main')
        self.tree.edge('PROG', 'MAIN')
        self.current = self.find_second_class_position()
        if self.current is not None:
            while self.match("key", "class"):
                self.current -= 1  # Voltar para não consumir o "CLASS"
                self.parse_class("PROG")
                self.id_class += 1
        self.current = 0
        self.parse_main()

    ### Funções das especificações da EBNF
    # MAIN
    def parse_main(self):
        self.symbol_table.enter_scope()
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
        self.symbol_table.enter_scope()

        current_class = f'CLASSE{self.id_class}'
        if self.node_exists(current_class):
            self.id_class += 1
            current_class = f'CLASSE{self.id_class}'
        self.tree.node(current_class, 'classe')
        self.tree.edge(father, current_class)

        self.expect("key","class", current_class)
        test = self.symbol_table.find_symbol(self.peek()[1])
        if not isinstance(test, str):
            if test not in self.symbol_table.errors:
                self.symbol_table.errors.append(f"Classe '{self.peek()[1]}' já foi declarada.")

        error = self.symbol_table.add_symbol(self.peek()[1], "class")
        self.expect("id", self.peek()[1], current_class)

        if self.peek()[1] == "extends":
            self.expect("key", "extends", current_class)
            test = self.symbol_table.find_symbol(self.peek()[1])
            if isinstance(test, str):
                if test not in self.symbol_table.errors:
                    self.symbol_table.errors.append(test)
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
        
        var_type = self.parse_type(current_var)
        self.symbol_table.add_symbol(self.peek()[1], var_type)
        self.expect("id", self.peek()[1], current_var)
        self.expect("del", ";", current_var)
    
    def parse_type(self, father):
        var_type = ''
        current_type = f'TYPE{self.id_type}'
        if self.node_exists(current_type):
            self.id_type += 1
            current_type = f'TYPE{self.id_type}'
        self.tree.node(current_type, "tipo")
        self.tree.edge(father, current_type)
        
        if self.peek()[1] == "int":
            var_type = 'int'
            self.expect("type", "int", current_type)
            if self.peek()[1] == "[":
                self.expect("del", "[", current_type)
                self.expect("del", "]", current_type)
                var_type = 'array int'
        else:
            var_type = self.peek()[1]
            self.expect("type" or "id", self.peek()[1], current_type)
        
        return var_type
                
    def parse_method(self, father):
        self.symbol_table.enter_scope()
        params = []

        current_method = f'METODO{self.id_method}'
        if self.node_exists(current_method):
            self.id_method += 1
            current_method = f'METODO{self.id_method}'
        self.tree.node(current_method, "metodo")
        self.tree.edge(father, current_method)

        self.expect("key", "public", current_method)
        method_var = self.parse_type(current_method)
        method_name = self.peek()[1]
        self.expect("id", self.peek()[1], current_method)
        self.expect("del", "(", current_method)

        while self.peek()[1] != ")":
            params = self.parse_params(current_method)

        self.symbol_table.add_symbol(method_name, f'method {method_var}',params)

        self.expect("del", ")", current_method)
        self.expect("del", "{", current_method)

        while self.peek()[0] == "type":
            self.parse_var(current_method)

        while self.peek()[1] != "return":
            self.parse_cmd(current_method)
        self.expect("key", "return", current_method)

        self.parse_exp(current_method)

        self.expect("del", ";", current_method)
        self.expect("del", "}", current_method)


    def parse_params(self, father):
        params = []
        current_params = f'PARAMS{self.id_params}'
        if self.node_exists(current_params):
            self.id_params += 1
            current_params = f'PARAMS{self.id_params}'
        self.tree.node(current_params, "params")
        self.tree.edge(father, current_params)

        params_type = self.parse_type(current_params)
        params.append(f'{params_type}')
        self.symbol_table.add_symbol(self.peek()[1], f'{params_type}', f'param')
        self.expect("id", self.peek()[1], current_params)
        
        while self.peek()[1] != ")":
            self.expect("del", ",", current_params)
            params_type = self.parse_type(current_params)
            params.append(f'{params_type}')
            self.symbol_table.add_symbol(self.peek()[1], f'{params_type}', f'param')
            self.expect("id", self.peek()[1], current_params)

        return params

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
            self.parse_exp(current_cmd)  
            self.expect("del", ")", current_cmd)
            self.expect("del", ";", current_cmd)


        elif token[0] == "id":  # Atribuição ou chamada de método
            test = self.symbol_table.find_symbol_method(token[1])
            if isinstance(test, str):
                test = self.symbol_table.find_symbol_class(token[1])
                if isinstance(test, str):
                    if test not in self.symbol_table.errors:
                        self.symbol_table.errors.append(f"Símbolo '{token[1]}' não encontrado.")

            self.expect("id", token[1], current_cmd)
            if self.peek()[0] == "op" and self.peek()[1] == "=":  
                self.expect("op", "=", current_cmd)
                value = self.parse_exp(current_cmd)
                result = self.evaluate_exp(self.flatten_list(value))
                if result != None:
                    #Será utilizado na geração de código
                    #print(result)
                    pass
                    
                self.expect("del", ";", current_cmd)
            elif  self.peek()[0] == "del" and self.peek()[1] == "[":  
                self.expect("del", "[", current_cmd)
                self.parse_exp(current_cmd)
                self.expect("del", "]", current_cmd)
                self.expect("op", "=", current_cmd)
                self.parse_exp(current_cmd)
                self.expect("del", ";", current_cmd)
        else:
            if self.peek()[1] == "}":
                return
            else:
                raise SyntaxError(f"Comando inválido ou inesperado: {token}")
        
    # Regra original: EXP -> EXP && REXP | REXP
    # Regra atual: EXP -> REXP EXP_AUX
    # Regra adicional: EXP_AUX -> && REXP EXP_AUX | ε    
    def parse_exp(self, father):
        result = []
        current_exp = f'EXP{self.id_exp}'
        if self.node_exists(current_exp):
            self.id_exp += 1
            current_exp = f'EXP{self.id_exp}'
        
        self.tree.node(current_exp, 'exp')
        self.tree.edge(father, current_exp)
        left = self.parse_rexp(current_exp)
        if left is not None:
            result.append(left)
        right = self.parse_exp_aux(current_exp)
        if right is not None:
            result.append(right)
        
        return result if result else None

    def parse_exp_aux(self, father):
        has_son = False
        result = []
        current_exp_aux = f'EXP_AUX{self.id_exp_aux}'
        if self.node_exists(current_exp_aux):
            self.id_exp_aux += 1
            current_exp_aux = f'EXP_AUX{self.id_exp_aux}'

        self.tree.node(current_exp_aux, 'exp_aux')
        self.tree.edge(father, current_exp_aux)
        
        while self.peek()[1] == '&':
            result.append(self.peek()[1])
            self.expect("op", "&", current_exp_aux)
            result.append(self.peek()[1])
            self.expect("op", "&", current_exp_aux) 
            left = self.parse_rexp(current_exp_aux)
            if left is not None:
                result.append(left)
            right = self.parse_exp_aux(current_exp_aux)
            if right is not None:
                result.append(left)
            has_son = True
    
        self.epsilon(current_exp_aux, has_son)

        return result if result else None

    # Regra original: REXP -> REXP < AEXP | REXP > AEXP | REXP == AEXP | REXP != AEXP | AEXP
    # Regra atual: REXP -> AEXP REXP_AUX
    # Regra adicional: REXP_AUX -> < AEXP REXP_AUX | == AEXP REXP_AUX | != AEXP REXP_AUX | ε  
    def parse_rexp(self, father):
        result = []
        current_rexp = f'REXP{self.id_rexp}'
        if self.node_exists(current_rexp):
            self.id_rexp += 1
            current_rexp = f'REXP{self.id_rexp}'

        self.tree.node(current_rexp, 'rexp')
        self.tree.edge(father, current_rexp)
        left = self.parse_aexp(current_rexp)
        if left is not None:
            result.append(left)
        right = self.parse_rexp_aux(current_rexp)
        if right is not None:
            result.append(right)

        return result if result else None

    def parse_rexp_aux(self, father):
        result = []
        has_son = False
        current_rexp_aux = f'REXP_AUX{self.id_rexp_aux}'
        if self.node_exists(current_rexp_aux):
            self.id_rexp_aux += 1
            current_rexp_aux = f'REXP_AUX{self.id_rexp_aux}'

        self.tree.node(current_rexp_aux, 'rexp_aux')
        self.tree.edge(father, current_rexp_aux)

        while self.peek()[1] in ['<', '>', '=', '!']:
            result.append(self.peek()[1])
            self.expect("op", self.peek()[1], current_rexp_aux)
            if self.peek()[1] == "=":
                result.append(self.peek()[1])
                self.expect("op", "=", current_rexp_aux)

            left = self.parse_aexp(current_rexp_aux)
            if left is not None:
                result.append(left)
            right = self.parse_rexp_aux(current_rexp_aux)
            if right is not None:
                result.append(right)
            has_son = True
        
        self.epsilon(current_rexp_aux, has_son)

        return result if result else None
        


    # Regra original: AEXP -> AEXP + MEXP | AEXP - MEXP | MEXP
    # Regra atual: AEXP -> MEXP AEXP_AUX
    # Regra adicional: AEXP_AUX -> + MEXP AEXP_AUX | - MEXP AEXP_AUX | ε
    def parse_aexp(self, father):
        result = []
        current_aexp = f'AEXP{self.id_aexp}'
        if self.node_exists(current_aexp):
            self.id_aexp += 1
            current_aexp = f'AEXP{self.id_aexp}'
        self.tree.node(current_aexp, 'aexp')
        self.tree.edge(father, current_aexp)

        left = self.parse_mexp(current_aexp)
        if left is not None:
            result.append(left)
        right = self.parse_aexp_aux(current_aexp)
        if right is not None:
            result.append(right)

        return result if result else None

    def parse_aexp_aux(self, father):
        result = []
        has_son = False
        current_aexp_aux = f'AEXP_AUX{self.id_aexp_aux}'
        if self.node_exists(current_aexp_aux):
            self.id_aexp_aux += 1
            current_aexp_aux = f'AEXP_AUX{self.id_aexp_aux}'

        self.tree.node(current_aexp_aux, 'aexp_aux')
        self.tree.edge(father, current_aexp_aux)

        while self.peek()[1] in ['+', '-']:
            result.append(self.peek()[1])
            self.expect("op", self.peek()[1], current_aexp_aux)
            left = self.parse_mexp(current_aexp_aux)
            if left is not None:
                result.append(left)
            right = self.parse_aexp_aux(current_aexp_aux)
            if right is not None:
                result.append(right)
            has_son = True
        
        self.epsilon(current_aexp_aux, has_son)

        return result if result else None

    # Regra original: MEXP -> MEXP * SEXP | SEXP
    # Regra atual: MEXP -> SEXP MEXP_AUX
    # Regra adicional: MEXP_AUX -> * SEXP MEXP_AUX | ε
    def parse_mexp(self, father):
        result = []
        current_mexp = f'MEXP{self.id_mexp}'
        if self.node_exists(current_mexp):
            self.id_mexp += 1
            current_mexp = f'MEXP{self.id_mexp}'

        self.tree.node(current_mexp, 'mexp')
        self.tree.edge(father, current_mexp)
        left = self.parse_sexp(current_mexp)
        if left is not None:
            result.append(left)
        right = self.parse_mexp_aux(current_mexp)
        if right is not None:
            result.append(right)

        return result if result else None

    def parse_mexp_aux(self, father):
        result = []
        has_son = False
        current_mexp_aux = f'MEXP_AUX{self.id_mexp_aux}'
        if self.node_exists(current_mexp_aux):
            self.id_mexp_aux += 1
            current_mexp_aux = f'MEXP_AUX{self.id_mexp_aux}'

        self.tree.node(current_mexp_aux, 'mexp_aux')
        self.tree.edge(father, current_mexp_aux)

        while self.peek()[1] == '*':
            result.append(self.peek()[1])
            self.expect("op", "*", current_mexp_aux)
            left = self.parse_sexp(current_mexp_aux)
            if left is not None:
                result.append(left)
            right = self.parse_mexp_aux(current_mexp_aux)
            if right is not None:
                result.append(right)
            has_son = True
        
        self.epsilon(current_mexp_aux, has_son)
    
        return result if result else None

    # Regra: SEXP -> ! SEXP | - SEXP | true | false | num | null | new int '[' EXP ']' | PEXP . length | PEXP '[' EXP ']' | PEXP
    # Obs: Não foi alterada
    def parse_sexp(self, father):
        result = []
        current_sexp = f'SEXP{self.id_sexp}'
        if self.node_exists(current_sexp):
            self.id_sexp += 1
            current_sexp = f'SEXP{self.id_sexp}'

        self.tree.node(current_sexp, 'sexp')
        self.tree.edge(father, current_sexp)
        
        token = self.peek()

        if token[1] in ['!','-']:
            result.append(token[1])
            self.expect("op", token[1], current_sexp)
            value1 = self.parse_sexp(current_sexp)
            if value1 is not None:
                result.append(value1)
        elif token[1] in ['true', 'false', 'null']:
            result.append(token[1])
            self.expect("key", token[1], current_sexp)
        elif token[1] == "new":
            # Quando começa com new pode ser tanto para o SEXP quanto para o PEXP
            # O que determina é o token que vem depois
            # Seria bom achar uma forma de ver mais à frente sem consumir
            self.expect("key", token[1], current_sexp)
            if self.peek()[1] == "int": # Mantém no SEXP
                self.expect("type", "int", current_sexp)
                self.expect("del", "[", current_sexp)
                value2 = self.parse_exp(current_sexp)
                self.expect("del", "]", current_sexp)
            elif self.peek()[0] == "id": # Ir para o PEXP
                test = self.symbol_table.find_symbol(self.peek()[1])
                if isinstance(test, str):
                    if test not in self.symbol_table.errors:
                        self.symbol_table.errors.append(test)
                result.append(self.peek()[1])
                value3 = self.parse_pexp(current_sexp, is_new = True)
                if value3 is not None:
                    result.append(value3)
            else: # Erro no programa
                raise ValueError(f"Token inesperado: {self.peek()}")
        elif token[0] == "num":
            result.append(token[1])
            self.expect("num", token[1], current_sexp)
        else:
            value4 = self.parse_pexp(current_sexp)
            if value4 is not None:
                result.append(value4)
            token = self.peek()
            if token[1] == ".length":
                self.expect("key", token[1], current_sexp)
            elif token[1] == "[":
                self.expect("del", token[1], current_sexp)
                value5 = self.parse_exp(current_sexp)
                if value5 is not None:
                    result.append(value5)
                self.expect("del", "]", current_sexp)
        
        return result if result else None
    
    # Regra original: PEXP -> id | this | new id '(' ')' | '(' EXP ')' | PEXP . id | PEXP . id '(' [EXPS] ')'
    # Regra atual: PEXP -> id PEXP_AUX | this PEXP_AUX | new id '(' ')' PEXP_AUX | '(' EXP ')' PEXP_AUX
    # Regra adicional: PEXP_AUX -> . id PEXP_AUX | . id '(' [EXPS] ')' PEXP_AUX | ε
    # Obs: O parâmetro is_new ajuda a diferenciar o SEXP do PEXP
    def parse_pexp(self, father, is_new = False):
        result = []
        current_pexp = f'PEXP{self.id_pexp}'
        if self.node_exists(current_pexp):
            self.id_pexp += 1
            current_pexp = f'PEXP{self.id_pexp}'

        self.tree.node(current_pexp, 'pexp')
        self.tree.edge(father, current_pexp)

        token = self.peek()

        if is_new: # O new já foi consumido pelo SEXP
            test = self.symbol_table.find_symbol(self.peek()[1])
            if isinstance(test, str):
                if test not in self.symbol_table.errors:
                    self.symbol_table.errors.append(test)
            self.expect("id", self.peek()[1], current_pexp)
            self.expect("del", "(", current_pexp)
            self.expect("del", ")", current_pexp)
            value = self.parse_pexp_aux(current_pexp)
            if value is not None:
                result.append(value)
        elif token[0] == "id":
            test = self.symbol_table.find_symbol_method(token[1])
            if isinstance(test, str):
                test = self.symbol_table.find_symbol_class(token[1])
                if isinstance(test, str):
                    if test not in self.symbol_table.errors:
                        self.symbol_table.errors.append(f"Símbolo '{token[1]}' não encontrado.")

            result.append(token[1])
            self.expect("id", token[1], current_pexp)
            value = self.parse_pexp_aux(current_pexp)
            if value is not None:
                result.append(value)
        elif token[1] == "this":
            self.expect("key", token[1], current_pexp)
            value = self.parse_pexp_aux(current_pexp)
            if value is not None:
                result.append(value)
        elif token[1] == "(":
            self.expect("del", "(", current_pexp)
            left = self.parse_exp(current_pexp)
            if left is not None: 
                result.append(left)
            self.expect("del", ")", current_pexp)
            right = self.parse_pexp_aux(current_pexp)
            if right is not None:
                result.append(right)
        else:
            raise ValueError(f"Token inesperado: {self.peek()}")
        
        return result if result else None

    def parse_pexp_aux(self, father):
        result = []
        arguments = []
        has_son = False
        current_pexp_aux = f'PEXP_AUX{self.id_pexp_aux}'
        if self.node_exists(current_pexp_aux):
            self.id_pexp_aux += 1
            current_pexp_aux = f'PEXP_AUX{self.id_pexp_aux}'

        self.tree.node(current_pexp_aux, 'pexp_aux')
        self.tree.edge(father, current_pexp_aux)

        if self.peek()[1] == ".":
            self.expect("del", ".", current_pexp_aux)
            self.symbol_table.find_symbol(self.peek()[1])
            result.append(self.peek()[1])
            self.expect("id", self.peek()[1], current_pexp_aux)
            if self.peek()[1] == '(':
                self.expect("del", "(", current_pexp_aux)
                if self.peek()[1] == ")": # EXPS é opcional
                    self.expect("del", ")", current_pexp_aux)
                else:
                    value1 = self.parse_exps(current_pexp_aux)
                    if value1 is not None:
                        arguments.append(value1)
                    self.expect("del", ")", current_pexp_aux)
            value2 = self.parse_pexp_aux(current_pexp_aux)
            if value2 is not None:
                result.append(value2)
            has_son = True
        self.epsilon(current_pexp_aux, has_son)

        if len(arguments) > 0 and len(result) > 0:
            #print(self.flatten_list(arguments))
            test = self.symbol_table.check_parameter_match(self.flatten_list(result)[0], self.flatten_list(arguments))
            if isinstance(test, str):
                if test not in self.symbol_table.errors:
                    if test not in self.symbol_table.errors:
                        self.symbol_table.errors.append(test)

        return result if result else None
    # Regra: EXPS -> EXP {, EXP}
    # Obs: Não foi alterada
    def parse_exps(self, father):
        result = []
        current_exps = f'EXPS{self.id_exps}'
        if self.node_exists(current_exps):
            self.id_exps += 1
            current_exps = f'EXPS{self.id_exps}'

        self.tree.node(current_exps, 'exps')
        self.tree.edge(father, current_exps)
        value1 = self.parse_exp(current_exps)
        if value1 is not None:
            result.append(value1)
        while self.peek()[1] == ",":
            self.expect("del", ",", current_exps)
            value2 = self.parse_exp(current_exps)
            if value2 is not None:
                result.append(value2)
        
        return result if result else None
