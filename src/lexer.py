import re

# Palavras-chave da linguagem
KEYWORDS = {"if", "else", "while", "for", "print", "elif", "def", "c_channel"} 
#Note como c_channel está aqui pois creio que SEMPRE irá requerir declaração explícita para seu uso. Podemos fazer o mesmo com int, String e outros tipos, caso necessário 
# ou requisitado pelo professor.

# Expressões regulares para cada tipo de token
TOKEN_REGEX = [
    ("NUM", r"\b\d+(\.\d+)?\b"),          # números inteiros ou decimais
    ("BOOL", r"\b(True|False)\b"),
    ("ID", r"\b[a-zA-Z_]\w*\b"),          # identificadores
    ("OP", r"==|<=|>=|!=|=|\+|-|\*|/|<|>"),  # operadores
    ("SYM", r"[{}();:]"),                  # símbolos individuais
    ("STR", r'"([^"\\]|\\.)*"') # Strings (dois anos pra conseguir colocar String aqui) 
]

def lexer(code):
    tokens = []
    pos = 0

    while pos < len(code):
        # Usamos isso pra ignorar espaços e quebras de linha.
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
                    tokens.append(f"<{value}>")
                elif token_type == "ID":
                    tokens.append(f"<id, {value}>")
                elif token_type == "NUM":
                    tokens.append(f"<num, {value}>")
                elif token_type == "OP":
                    tokens.append(f"<{value}>")
                elif token_type == "SYM":
                    tokens.append(f"<{value}>")
                elif token_type == "BOOL":
                    tokens.append(f"<bool, {value}>")
                elif token_type == "STR":
                    tokens.append(f"<string, {value}>")
                pos = match.end(0)
                break

        if not match:
            raise ValueError(f"Token inválido próximo de: '{code[pos:]}'")

    return tokens # No momento, estou retornando isso aqui com uma formatação similar a de string para realizar a impressão em tokens.txt.
# Implementações futuras possivelmente precisarão realizar uma chamada de função para a impressão e SÓ ENTÃO retornar os tokens brutos (sem formatação de string) 
# para que o parser possa realizar a leitura tranquilamente.

