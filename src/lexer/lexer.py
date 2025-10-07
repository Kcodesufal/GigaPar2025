import re

# =================================================
# DEFINIÇÕES GLOBAIS (Fora de qualquer função)
# =================================================

# Palavras-chave da linguagem
KEYWORDS = {
    "if", "else", "while", "print", "def", "c_channel", 
    "SEQ", "PAR", "and", "or", "not"
}

# Expressões regulares para cada tipo de token
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
    Realiza a análise léxica e retorna uma lista de tokens estruturados.
    """
    tokens = []
    pos = 0
    
    while pos < len(code):
        # Ignora espaços em branco
        if code[pos].isspace():
            pos += 1
            continue

        # Ignora comentários de linha única
        if code[pos] == '#':
            next_line_pos = code.find('\n', pos)
            pos = next_line_pos if next_line_pos != -1 else len(code)
            continue

        match = None
        # Usa a lista de regex já compilados
        for token_type, regex in COMPILED_REGEXES:
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