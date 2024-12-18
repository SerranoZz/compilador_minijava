class SymbolTable:
    def __init__(self):
        # Armazena os símbolos em diferentes escopos
        self.scopes = [{}]
    
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
            raise ValueError(f"Símbolo '{name}' já declarado no escopo atual.")
        current_scope[name] = {"type": symbol_type, "qt_info": qt_info, "info": additional_info}
    
    def find_symbol(self, name):
        # Procura o símbolo nos escopos, do mais interno ao global
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
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
