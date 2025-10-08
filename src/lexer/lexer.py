import re

# =================================================
# DEFINIÇÕES GLOBAIS (Fora de qualquer função)
# =================================================

KEYWORDS = {
    "if", "else", "while", "print", "def", "c_channel",
    "SEQ", "PAR", "and", "or", "not"
}

TOKEN_REGEX = [
    ("NUMBER",  r"\b\d+(\.\d+)?\b"),
    ("BOOLEAN", r"\b(True|False)\b"),
    ("STRING",  r'"([^"\\]|\\.)*"'),
    ("ID",      r"\b[a-zA-Z_]\w*\b"),
    ("OP",      r"==|!=|<=|>=|=|\+|-|\*|/|<|>"),
    ("SYM",     r"[{}();:,]"),
]

COMPILED_REGEXES = [(ttype, re.compile(pattern)) for ttype, pattern in TOKEN_REGEX]

# =================================================
# FUNÇÃO PRINCIPAL DO LEXER
# =================================================

def lexer(code):
    """
    Realiza a análise léxica com suporte à indentação e retorna uma lista de tokens estruturados.
    """
    tokens = []
    indent_stack = [0]  # pilha de níveis de indentação
    lines = code.splitlines()
    lineno = 0

    for line in lines:
        lineno += 1
        # Remove comentários
        if "#" in line:
            line = line.split("#", 1)[0]

        # Ignora linhas completamente vazias
        if not line.strip():
            continue

        # Conta espaços iniciais (indentação)
        indent_level = len(line) - len(line.lstrip(" "))

        # Gera tokens de INDENT/DEDENT se o nível mudar
        if indent_level > indent_stack[-1]:
            indent_stack.append(indent_level)
            tokens.append(("INDENT", None))
        elif indent_level < indent_stack[-1]:
            while indent_level < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(("DEDENT", None))
            if indent_level != indent_stack[-1]:
                raise ValueError(f"Indentação inválida na linha {lineno}")

        pos = len(line) - len(line.lstrip(" "))
        while pos < len(line):
            # Ignora espaços internos
            if line[pos].isspace():
                pos += 1
                continue

            match = None
            for token_type, regex in COMPILED_REGEXES:
                match = regex.match(line, pos)
                if match:
                    value = match.group(0)
                    if token_type == "ID" and value in KEYWORDS:
                        tokens.append(("KEYWORD", value))
                    else:
                        tokens.append((token_type, value))
                    pos = match.end(0)
                    break

            if not match:
                raise ValueError(f"Token inválido na linha {lineno}, próximo de: '{line[pos:]}'")

        # Fim de linha explícito (útil para parser)
        tokens.append(("NEWLINE", None))

    # Fecha indentação restante
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(("DEDENT", None))

    return tokens
