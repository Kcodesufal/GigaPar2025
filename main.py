from src.lexer import lexer
from src.parser import parser


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
        elif ttype in {"INDENT", "DEDENT"}:
            formatted_tokens.append(f"<{ttype}>")
        else:
            formatted_tokens.append(f"<{ttype}, {value}>")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(" ".join(formatted_tokens))


def write_ast_to_file(ast, filename="ast.txt"):
    """
    Recebe a AST (árvore sintática abstrata) e grava no arquivo em formato legível.
    Suporta nós representados como tuplas, listas ou objetos com atributos.
    """
    def format_ast(node, level=0):
        pad = "  " * level

        # Caso o nó seja uma tupla (ex: ('if', cond, bloco))
        if isinstance(node, tuple):
            head = node[0]
            children = node[1:]
            lines = [f"{pad}{head}"]
            for child in children:
                lines.append(format_ast(child, level + 1))
            return "\n".join(lines)

        # Caso seja uma lista (vários nós)
        elif isinstance(node, list):
            return "\n".join(format_ast(item, level) for item in node)

        # Caso seja um objeto do parser com atributos (ex: classe Node)
        elif hasattr(node, "__dict__"):
            lines = [f"{pad}{node.__class__.__name__}:"]
            for attr, value in vars(node).items():
                lines.append(f"{pad}  {attr}:")
                lines.append(format_ast(value, level + 2))
            return "\n".join(lines)

        # Caso seja um valor simples
        else:
            return f"{pad}{repr(node)}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(format_ast(ast))


def main():
    try:
        # E lá vamos nós, realizar a leitura do código fonte!
        with open("entrada.txt", "r", encoding="utf-8") as f:
            code = f.read()

        # =======================
        # Análise Léxica
        # =======================
        tokens = lexer.lexer(code)
        write_tokens_to_file(tokens)
        print("✅ Análise léxica concluída com sucesso! Tokens salvos em 'tokens.txt'.")

        # =======================
        # Análise Sintática
        # =======================
        p = parser.Parser(tokens)
        ast = p.parse()
        write_ast_to_file(ast)
        print("✅ Análise sintática concluída com sucesso! AST salva em 'ast.txt'.")

    except FileNotFoundError:
        print("❌ Erro: Arquivo 'entrada.txt' não encontrado.")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")


if __name__ == "__main__":
    main()
