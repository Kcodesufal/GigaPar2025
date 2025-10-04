# O analisador léxico é a *PRIMEIRA* parte do front-end do compilador.
# Temos que começar por ele e garantir sua comunicação com o parser, permitindo a tokenização adequada.


#Um exemplo de tokenização:
#If (x == 10) { print(100)}
#Passamos pelo lexer
#<if> <(> <id, x> <==> <num, 10> <)> <{> <print> <(> <num,100> <)> <}>