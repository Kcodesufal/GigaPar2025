# GigaPar2025
Repositório dedicado ao projeto da matéria "Compiladores". 

![Universidade Federal de Alagoas](https://upload.wikimedia.org/wikipedia/commons/7/71/Bras%C3%A3o_Ufal.png)

# Colaboradores

* Kauê Patricius Montgomery Maranhão da Costa Montenegro
* Walber Luis Santos da Paixão
* Gustavo Pereira Cordeiro


# Objetivos
Nosso objetivo atualmente consiste em apresentar a atividade 2 - Apresentaremos o parser, o lexer e o código de três endereços, juntamente com o assembly gerado.




# Algumas anotações

## Sobre a main 
 Há duas opções para main: Recebemos o código a ser tokenizado via um arquivo ou via o terminal. 
Também é possível fazê-lo por meio de uma interface gráfica, o que pode colaborar com a nota (fiquem atentos nisso!)
print("Hello World!")


## Sobre o lexer

O analisador léxico é a *PRIMEIRA* parte do front-end do compilador.
Temos que começar por ele e garantir sua comunicação com o parser, permitindo a tokenização adequada.


Um exemplo de tokenização:
If (x == 10) { print(100)}
Passamos pelo lexer
<if> <(> <id, x> <==> <num, 10> <)> <{> <print> <(> <num,100> <)> <}>

