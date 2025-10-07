import src.lexer as lexer
import src.parser as parser

def main():
    with open("entrada.txt", "r", encoding="utf-8") as f:
        code = f.read()

    # Agora lexer retorna tokens estruturados
    tokens = lexer.lexer(code)

    # Função separada para escrita
    lexer.write_tokens_to_file(tokens)

    print("✅ Tokens gerados em 'tokens.txt'")

    p = parser.Parser(tokens)
    ast = p.parse()

    print("✅ Análise sintática concluída com sucesso!")


if __name__ == "__main__":
    main()
