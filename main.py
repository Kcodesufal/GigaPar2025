import src.lexer as lexer
import src.parser as parser



def main(): # Há duas opções para main: Recebemos o código a ser tokenizado via um arquivo ou via o terminal. 
    # Também é possível fazê-lo por meio de uma interface gráfica, o que pode colaborar com a nota (fiquem atentos nisso!)

        # Ler código de entrada
    with open("entrada.txt", "r", encoding="utf-8") as f:
        code = f.read()

    tokens = lexer.lexer(code)

    # Salvar saída formatada
    with open("tokens.txt", "w", encoding="utf-8") as f:
        f.write(" ".join(tokens))

    print("✅ Tokens gerados em 'tokens.txt'")



if __name__ == "__main__":
    main()