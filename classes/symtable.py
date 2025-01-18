class SymbolTable:
    def __init__(self):
        # Armazena os símbolos em diferentes escopos
        self.scopes = [{}]
        self.errors = []
    
    def enter_scope(self):
        # Adiciona um novo escopo (e.g., ao entrar em uma classe ou método)
        self.scopes.append({})
    
    def exit_scope(self):
        # Remove o escopo atual (e.g., ao sair de uma classe ou método)
        self.scopes.pop()
    
    def add_symbol(self, name, symbol_type, additional_info=None):
        # Adiciona um símbolo ao escopo atual
        qt_info = 0
        if additional_info != None:
            qt_info = len(additional_info)

        current_scope = self.scopes[-1]
        if name in current_scope:
            self.errors.append(f"Símbolo '{name}' já declarado no escopo atual.")
            raise ValueError(f"Símbolo '{name}' já declarado no escopo atual.")
        current_scope[name] = {"type": symbol_type, "qt_info": qt_info, "info": additional_info}
    
    def find_symbol(self, name):
        # Procura o símbolo nos escopos, do mais interno ao global
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        self.errors.append(f"Símbolo '{name}' não encontrado.")
        raise ValueError(f"Símbolo '{name}' não encontrado.")

    def find_symbol_class(self, name):
        for scope_index, scope in enumerate(reversed(self.scopes)):  # Percorre os escopos de trás para frente
            for symbol, details in scope.items():
                symbol_type = details.get("type")
                if symbol_type == "class":
                    return scope[name]  # Retorna o primeiro símbolo do tipo "class"
        
        raise ValueError(f"Símbolo '{name}' não encontrado.")


    def find_symbol_method(self, name):
        scopes_to_check = self.scopes[-1:]

        for scope in reversed(scopes_to_check): 
            if name in scope:
                return scope[name]

        raise ValueError(f"Símbolo '{name}' não encontrado.")
    
    def check_parameter_match(self, function_name, provided_parameters):
        for scope in self.scopes:
            if function_name in scope:
                function_details = scope[function_name]
                expected_types = function_details["info"]

                # Agrupa as expressões se necessário
                provided_parameters = self.group_expressions(provided_parameters)

                if len(provided_parameters) != function_details["qt_info"]:
                    raise ValueError(
                        f"Erro na função '{function_name}': esperado {function_details['qt_info']} parâmetros, mas {len(provided_parameters)} foram fornecidos."
                    )

                for index, (expected_type, provided_param) in enumerate(zip(expected_types, provided_parameters)):
                    # Se o provided_param for uma lista, iterar sobre os valores
                    if isinstance(provided_param, list):
                        for param in provided_param:
                            if param.isdigit():
                                param_type = "int"
                            elif param.lower() in ["true", "false"]:
                                param_type = "boolean"
                            elif param in ['+', '-', '*']:
                                continue
                            elif self.find_symbol(param):
                                try:
                                    param_type = self.find_symbol_method(param)["type"]
                                except ValueError:
                                    try:
                                        param_type = self.find_symbol_class(param)["type"]
                                    except ValueError:
                                        raise ValueError(f"Símbolo '{param}' não encontrado.")
                            else:
                                raise TypeError(
                                    f"Erro no parâmetro {index + 1} da função '{function_name}': valor '{param}' não é um tipo válido (esperado 'int' ou 'boolean')."
                                )
                            
                            if expected_type != param_type:
                                raise TypeError(
                                    f"Erro no parâmetro {index + 1} da função '{function_name}': esperado tipo '{expected_type}', mas '{param_type}' foi fornecido."
                                )
                    else:
                        if provided_param.isdigit():
                            param_type = "int"
                        elif provided_param.lower() in ["true", "false"]:
                            param_type = "boolean"
                        elif self.find_symbol(provided_param):
                            try:
                                param_type = self.find_symbol_method(provided_param)["type"]
                            except ValueError:
                                try:
                                    param_type = self.find_symbol_class(provided_param)["type"]
                                except ValueError:
                                    raise ValueError(f"Símbolo '{provided_param}' não encontrado.")
                        else:
                            raise TypeError(
                                f"Erro no parâmetro {index + 1} da função '{function_name}': valor '{provided_param}' não é um tipo válido (esperado 'int' ou 'boolean')."
                            )

                        if expected_type != param_type:
                            raise TypeError(
                                f"Erro no parâmetro {index + 1} da função '{function_name}': esperado tipo '{expected_type}', mas '{param_type}' foi fornecido."
                            )

                return True  

        raise ValueError(f"Função '{function_name}' não encontrada na tabela de símbolos.")

        
    def group_expressions(self, vector):
        if not any(op in vector for op in ['+', '-', '*']):  # Verifica se o vector contém algum operador
            return vector
        expressions = []
        current_expression = []
        for i in range(len(vector)):
            if i + 1 < len(vector):  # Check if there is an operator after the current item
                if vector[i + 1] in ['+', '-', '*']:
                    current_expression.append(vector[i])
                elif vector[i] in ['+', '-', '*']:
                    current_expression.append(vector[i])
                else:
                    current_expression.append(vector[i])
                    expressions.append(current_expression)
                    current_expression = []
            else:
                current_expression.append(vector[i])

        if current_expression:  # Add the last expression, if any
            expressions.append(current_expression)

        return expressions

    def print_table(self):
        """Imprime a tabela de símbolos."""
        if not self.scopes or all(not scope for scope in self.scopes):
            print("A tabela de símbolos está vazia.")
            return
        
        print("Tabela de Símbolos:")
        print("-" * 80)
        print(f"{'Escopo':<10} {'Símbolo':<20} {'Tipo':<15} {'Parâmetros/Info':<30}")
        print("-" * 80)
        
        for scope_index, scope in enumerate(self.scopes):
            for symbol, details in scope.items():
                symbol_type = details["type"]
                qt_info = details["qt_info"]
                additional_info = details["info"]
                if isinstance(additional_info, list):
                    additional_info = ", ".join(additional_info)  # Junta os parâmetros em uma string
                elif isinstance(additional_info, dict):
                    additional_info = "; ".join(f"{k}={v}" for k, v in additional_info.items())
                else:
                    additional_info = additional_info or ""  # Caso seja None
                print(f"{scope_index:<10} {symbol:<20} {symbol_type:<15} {additional_info:<30}")
        print("-" * 80)
