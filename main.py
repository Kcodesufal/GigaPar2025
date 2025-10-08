from src.lexer import lexer

def write_tokens_to_file(tokens, filename="tokens.txt"):
    """
    Recebe a lista de tokens e grava no arquivo em formato legível.
    """
    formatted_tokens = []
    for ttype, value in tokens:
        if ttype == "KEYWORD":
            formatted_tokens.append(f"<{value}>")
        elif ttype in {"NUMBER", "ID", "BOOLEAN", "STRING"}:
            formatted_tokens.append(f"<{ttype.lower()}, {value}>")
        elif ttype in {"OP", "SYM"}:
            formatted_tokens.append(f"<{value}>")
        else:
            formatted_tokens.append(f"<{ttype}, {value}>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(" ".join(formatted_tokens))

def main():
    try:
        with open('entrada.txt', 'r', encoding='utf-8') as f:
            code = f.read()

        tokens = lexer.lexer(code)
        
        write_tokens_to_file(tokens)

        print("Análise léxica concluída com sucesso! Tokens salvos em 'tokens.txt'.")

    except FileNotFoundError:
        print("Erro: Arquivo 'entrada.txt' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()