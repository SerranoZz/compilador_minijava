import re

# Definição de tokens para MiniJava+
TOKENS = [
    ("KEYWORD", r"\b(class|public|static|void|main|int|boolean|if|else|while|return|true|false)\b"),
    ("IDENTIFIER", r"[a-zA-Z_][a-zA-Z0-9_]*"),
    ("NUMBER", r"\b\d+\b"),
    ("OPERATOR", r"[+\-*/=<>!]"),
    ("DELIMITER", r"[{}()\[\];.,]"),
    ("WHITESPACE", r"\s+"),
    ("COMMENT", r"//.*|/\*[\s\S]*?\*/"),
]

def tokenize(code):
    tokens = []
    position = 0

    while position < len(code):
        match = None
        for token_type, regex in TOKENS:
            # Indica que a substring na posição indicada combinou com a expressão regular
            match = re.compile(regex).match(code, position)
            if match:
                if token_type not in ["WHITESPACE", "COMMENT"]:
                    tokens.append((token_type, match.group()))
                position = match.end()
                break

        if not match:
            raise ValueError(f"Unexpected character: {code[position]} at position {position}")

    return tokens

# Exemplo de uso
if __name__ == "__main__":
    example_code = """
    class Main {
        public static void main(String[] args) {
            int x = 10;
            if (x > 0) {
                System.out.println(x);
            }
        }
    }
    """
    try:
        scanned_tokens = tokenize(example_code)
        for token in scanned_tokens:
            print(token)
    except ValueError as e:
        print(e)
