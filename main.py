from src.lexer import lexer
from src.parser import parser
from src.semantic import semantic
from src.generator import generator  

'''
As funções "Write" realizam a escrita em arquivos para facilitar a visualização.
São de caráter temporário e estão aqui apenas por conveniência na hora de debugar o código e mostrar os resultados ao professor.
'''

def write_tokens_to_file(tokens, filename="tokens.txt"):
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
    def format_ast(node, level=0):
        pad = "  " * level
        if isinstance(node, tuple):
            head = node[0]
            children = node[1:]
            lines = [f"{pad}{head}"]
            for child in children:
                lines.append(format_ast(child, level + 1))
            return "\n".join(lines)
        elif isinstance(node, list):
            return "\n".join(format_ast(item, level) for item in node)
        else:
            return f"{pad}{repr(node)}"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(format_ast(ast))

def write_c3e_to_file(instructions, filename="c3e.txt"):
    """Salva a lista de instruções C3E em um arquivo, uma por linha."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(instructions))


def main():
    try:
        with open("entrada.txt", "r", encoding="utf-8") as f:
            code = f.read()

        
        tokens = lexer.lexer(code)
        write_tokens_to_file(tokens)
        print("✅ Análise léxica concluída com sucesso! Tokens salvos em 'tokens.txt'.")

       
        p = parser.Parser(tokens)
        ast = p.parse()
        write_ast_to_file(ast)
        print("✅ Análise sintática concluída com sucesso! AST salva em 'ast.txt'.")

        
        try:
            
            analyzer = semantic.SemanticAnalyzer(ast)
            analyzer.analyze()
            print("✅ Análise semântica concluída com sucesso!")

            
            code_gen = generator.CodeGenerator()
            three_address_code = code_gen.generate(ast)
            write_c3e_to_file(three_address_code)
            print("✅ Geração de código de 3 endereços concluída! Salvo em 'c3e.txt'.")
        except semantic.SemanticError as se:
            print(f"❌ Erro semântico: {se}")

    except FileNotFoundError:
        print("❌ Erro: Arquivo 'entrada.txt' não encontrado.")
    except Exception as e:
        print(f"❌ Ocorreu um erro: {e}")
        

if __name__ == "__main__":
    main()
