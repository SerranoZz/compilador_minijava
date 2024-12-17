class SymbolTable:
    def __init__(self):
        self.table = [{}]  # Pilha de escopos

    def enter_scope(self):
        self.table.append({})  # Adiciona um novo escopo

    def exit_scope(self):
        self.table.pop()  # Remove o escopo atual

    def add_symbol(self, name, category, data_type, **attributes):
        if name in self.table[-1]:
            raise Exception(f"Erro: '{name}' já declarado no escopo atual.")
        self.table[-1][name] = {
            "category": category,
            "type": data_type,
            **attributes
        }

    def lookup(self, name):
        # Procura em escopos da pilha (do mais interno para o global)
        for scope in reversed(self.table):
            if name in scope:
                return scope[name]
        raise Exception(f"Erro: '{name}' não declarado.")
