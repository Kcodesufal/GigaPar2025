import re

# Palavras-chave da linguagem
KEYWORDS = {"if", "else", "while", "for", "print", "elif", "def", "c_channel", "SEQ", "PAR"}

# Expressões regulares para cada tipo de token
TOKEN_REGEX = [
    ("NUM", r"\b\d+(\.\d+)?\b"),           # números inteiros ou decimais
    ("BOOL", r"\b(True|False)\b"),
    ("ID", r"\b[a-zA-Z_]\w*\b"),           # identificadores
    ("OP", r"==|<=|>=|!=|=|\+|-|\*|/|<|>"),  # operadores
    ("SYM", r"[{}();:]"),                  # símbolos individuais
    ("STR", r'"([^"\\]|\\.)*"')            # strings
]


def lexer(code):
    """
    Realiza a análise léxica e retorna uma lista de tokens estruturados.
    Cada token é uma tupla (tipo, valor).
    """
    tokens = []
    pos = 0

    while pos < len(code):
        if code[pos].isspace():
            pos += 1
            continue

        match = None
        for token_type, pattern in TOKEN_REGEX:
            regex = re.compile(pattern)
            match = regex.match(code, pos)
            if match:
                value = match.group(0)
                if token_type == "ID" and value in KEYWORDS:
                    tokens.append(("KEYWORD", value))
                else:
                    tokens.append((token_type, value))
                pos = match.end(0)
                break

        if not match:
            raise ValueError(f"Token inválido próximo de: '{code[pos:]}'")

    return tokens


def write_tokens_to_file(tokens, filename="tokens.txt"):
    """
    Recebe a lista de tokens estruturados e grava no arquivo em formato legível.
    Exemplo de saída:
    <if> <id, x> <=> <num, 10>
    """
    formatted_tokens = []

    for ttype, value in tokens:
        if ttype == "KEYWORD":
            formatted_tokens.append(f"<{value}>")
        elif ttype in {"NUM", "ID", "BOOL", "STR"}:
            formatted_tokens.append(f"<{ttype.lower()}, {value}>")
        elif ttype in {"OP", "SYM"}:
            formatted_tokens.append(f"<{value}>")
        else:
            formatted_tokens.append(f"<{ttype}, {value}>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(" ".join(formatted_tokens))
