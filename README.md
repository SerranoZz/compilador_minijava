# README: Compilador em Python para a Linguagem MiniJava+

Este projeto implementa um **scanner** para a linguagem **MiniJava+**, representando a primeira fase de um compilador. A análise léxica identifica e classifica os tokens de um código-fonte conforme as regras da linguagem.

## Objetivo
- Extrair **tokens** (unidades léxicas) de um arquivo fonte em **MiniJava+**.

---

## Requisitos
- **Python 3.8+** instalado no sistema.
- Código-fonte em MiniJava+ com extensão `.java`.

---

## Como Funciona

### Entrada
Um arquivo `.java` com o código-fonte da linguagem MiniJava+.

### Saída
Uma lista de tuplas exibida no console. Cada tupla contém:
1. O tipo do token (ex.: `key`, `id`, `num`).
2. O lexema correspondente (ex.: `class`, `main`, `10`).

---

## Como Executar

1. Salve o código em um arquivo chamado, por exemplo, **`scanner.py`**.
2. Prepare um arquivo `.java` com o código-fonte a ser analisado. Exemplo:

**`exemplo.java`**:
```java
class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
    }
}
```

3. Execute o scanner com o comando:
   ```bash
   python3 scanner.py exemplo.java
   ```

---

## Exemplo de Saída
Dado o código acima (`exemplo.java`), a saída será:
```
('key', 'class')
('id', 'Main')
('del', '{')
('key', 'public')
('key', 'static')
('key', 'void')
('id', 'main')
('del', '(')
('id', 'String')
('del', '[')
('del', ']')
('id', 'args')
('del', ')')
('del', '{')
('id', 'System.out.println')
('del', '(')
('id', '"Hello, World!"')
('del', ')')
('del', ';')
('del', '}')
('del', '}')
```

---

## Observações
- Comentários (tanto de uma linha quanto de várias linhas) são removidos antes da análise.
- Tokens inválidos geram mensagens de erro indicando a posição no código.

---

## Mais informações
- **Veja o relatório para saber mais sobre o programa como um todo (Scanner + Parser).
