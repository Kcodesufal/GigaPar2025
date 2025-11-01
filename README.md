# 🚀 GigaPar2025

<div align="center">

![Universidade Federal de Alagoas](https://upload.wikimedia.org/wikipedia/commons/7/71/Bras%C3%A3o_Ufal.png)

**Compilador Completo para a Linguagem MiniPar**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![ARMv7](https://img.shields.io/badge/Target-ARMv7-orange.svg)](https://developer.arm.com/)
[![Status](https://img.shields.io/badge/Status-Completo-success.svg)](https://github.com)

*Desenvolvido como projeto da disciplina de Compiladores - UFAL 2025*

[Características](#-características) •
[Instalação](#-instalação) •
[Uso](#-uso) •
[Exemplos](#-exemplos) •
[Documentação](#-documentação) •
[Equipe](#-equipe)

</div>

---

## 📖 Sobre o Projeto

**GigaPar2025** é um compilador completo que traduz código fonte escrito na linguagem **MiniPar** para código Assembly **ARMv7** executável. O projeto implementa todas as fases clássicas de um compilador: análise léxica, sintática, semântica, geração de código intermediário (C3E) e geração de código de máquina.

### 🎯 Linguagem MiniPar

MiniPar é uma linguagem imperativa com sintaxe inspirada em Python, suportando:
- ✅ Funções e recursão
- ✅ Estruturas de controle (if/else, while, for)
- ✅ Operações aritméticas e lógicas
- ✅ **Programação paralela** (blocos `PAR` e `SEQ`)
- ✅ **Comunicação por canais** (`c_channel`, `send`, `receive`)
- ✅ Indentação significativa
- ✅ Tipagem dinâmica com inferência

---

## ✨ Características

### Pipeline de Compilação

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Lexer   │ => │  Parser  │ => │ Semantic │ => │Generator │ => │ Assembly │
│ (Tokens) │    │  (AST)   │    │ (Tabela) │    │  (C3E)   │    │ (ARMv7)  │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Módulos Implementados

| Módulo | Descrição | Status |
|--------|-----------|--------|
| **Lexer** | Análise léxica com suporte a indentação | ✅ 100% |
| **Parser** | Análise sintática (recursive descent) | ✅ 100% |
| **Semantic** | Análise semântica e tabela de símbolos | ✅ 100% |
| **Generator** | Geração de código de 3 endereços (C3E) | ✅ 100% |
| **Assembly** | Geração de Assembly ARMv7 | ✅ 100% |

### Recursos Avançados

- 🔍 **Inferência de tipos** automática
- 📊 **Tabela de símbolos** hierárquica com escopos
- 🔄 **Suporte a paralelismo** (PAR/SEQ)
- 📡 **Canais de comunicação** entre processos
- 🎯 **Geração de código otimizado** para ARMv7
- ✔️ **Validação completa** no CPUlator

---

## 🛠️ Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Git (opcional)

### Clone o Repositório

```bash
git clone https://github.com/[username]/GigaPar2025.git
cd GigaPar2025
```

### Estrutura de Diretórios

```
GigaPar2025/
├── src/
│   ├── lexer/          # Análise léxica
│   ├── parser/         # Análise sintática
│   ├── semantic/       # Análise semântica
│   ├── generator/      # Geração de C3E
│   └── assembly/       # Geração de Assembly
├── tests/              # Programas de teste
│   ├── t1.par          # Cliente-servidor calculadora
│   ├── t2.par          # Fatorial + Fibonacci paralelo
│   ├── t3.par          # Perceptron simples
│   ├── t4.par          # Rede Neural XOR
│   ├── t5.par          # Sistema de recomendação
│   ├── t6.par          # Fatorial iterativo
│   ├── t7.par          # Fibonacci
│   └── t8.par          # Bubble Sort
├── main.py             # Ponto de entrada
├── README.md           # Este arquivo
└── .gitignore
```

---

## 🚀 Uso

### Compilação Básica

```bash
python main.py
```

O programa irá compilar todos os arquivos de teste em sequência, gerando:
- `tokens.txt` - Lista de tokens
- `ast.txt` - Árvore sintática abstrata
- `c3e.txt` - Código de 3 endereços
- `output.s` - Código Assembly ARMv7

### Compilar um Arquivo Específico

Edite `main.py` e adicione seu arquivo à lista de testes:

```python
testes = ["entrada.txt", "meu_programa.par"]
```

### Executar no CPUlator

1. Acesse: https://cpulator.01xz.net/
2. Selecione **ARMv7**
3. Carregue o arquivo `output.s`
4. Clique em **Compile** e depois **Continue**

---

## 📝 Exemplos

### Exemplo 1: Hello World

```python
def main():
    print("Hello, MiniPar!")
```

### Exemplo 2: Função Simples

```python
def soma(a, b):
    resultado = a + b
    return resultado

def main():
    x = soma(10, 20)
    print("Resultado:", x)
```

### Exemplo 3: Loop e Condicional

```python
def fatorial(n):
    resultado = 1
    i = 1
    for (i; i <= n; i = i + 1):
        resultado = resultado * i
    return resultado

def main():
    x = fatorial(5)
    print("Fatorial de 5 =", x)
```

### Exemplo 4: Programação Paralela

```python
def calcular_fatorial(n):
    resultado = 1
    i = 1
    for (i; i <= n; i = i + 1):
        resultado = resultado * i
    print("Fatorial:", resultado)
    return resultado

def calcular_fibonacci(limite):
    a = 0
    b = 1
    i = 0
    for (i; i < limite; i = i + 1):
        print("Fibonacci:", a)
        proximo = a + b
        a = b
        b = proximo
    return a

def main():
    PAR:
        calcular_fatorial(5)
        calcular_fibonacci(8)
```

### Exemplo 5: Canais de Comunicação

```python
c_channel calculadora comp1 comp2

def servidor():
    calculadora.receive(operacao, valor1, valor2)
    resultado = valor1 + valor2
    calculadora.send(resultado)

def cliente():
    calculadora.send("+", 10, 20)
    calculadora.receive(resultado)
    print("Resultado:", resultado)
```

---

## 📚 Documentação

### Sintaxe da Linguagem MiniPar

#### Palavras Reservadas
```
if, else, while, for, def, return
print, input
and, or, not
True, False
PAR, SEQ
c_channel
```

#### Tipos de Dados
- `number` - Números inteiros e decimais (42, 3.14)
- `boolean` - True/False
- `string` - Cadeias entre aspas ("texto")

#### Operadores

**Aritméticos:** `+` `-` `*` `/`  
**Comparação:** `==` `!=` `<` `>` `<=` `>=`  
**Lógicos:** `and` `or` `not`  
**Atribuição:** `=`

#### Estruturas de Controle

**If/Else:**
```python
if (x > 0):
    print("Positivo")
else:
    print("Não positivo")
```

**While:**
```python
while (x < 10):
    x = x + 1
    print(x)
```

**For:**
```python
for (i = 0; i < 10; i = i + 1):
    print(i)
```

#### Funções

```python
def nome_funcao(param1, param2):
    # corpo da função
    return resultado
```

#### Blocos Paralelos

```python
PAR:
    funcao1()
    funcao2()
```

#### Canais

```python
c_channel nome_canal comp1 comp2

comp1.send(valor1, valor2)
comp2.receive(var1, var2)
```

---

## 🔬 Pipeline de Compilação Detalhado

### 1️⃣ Análise Léxica (Lexer)

Transforma código fonte em tokens:

```python
if (x == 10):
    print("Dez")

# Tokens gerados:
<if> <(> <id,x> <==><number,10> <)> <:> <NEWLINE>
<INDENT> <print> <(> <string,"Dez"> <)> <NEWLINE>
<DEDENT>
```

### 2️⃣ Análise Sintática (Parser)

Constrói a Árvore Sintática Abstrata (AST):

```python
("if",
  ("binop", "==", ("id", "x"), ("number", "10")),
  ("stmts", [
    ("builtin_call", "print", [("string", "Dez")])
  ]))
```

### 3️⃣ Análise Semântica

Valida tipos e preenche tabela de símbolos:
- ✅ Variáveis declaradas antes do uso
- ✅ Compatibilidade de tipos
- ✅ Número correto de argumentos
- ✅ Inferência de tipos

### 4️⃣ Geração de C3E

Código de 3 Endereços (intermediário):

```
t0 = x == 10
if_false t0 goto L1
param "Dez"
t1 = call print, 1
L1:
```

### 5️⃣ Geração de Assembly ARMv7

Código de máquina executável:

```asm
ldr r0, [fp, #-4]
mov r1, #10
cmp r0, r1
bne L1
ldr r0, =.STR0
bl print
L1:
```

---

## 🧪 Testes

O projeto inclui **8 programas de teste** cobrindo diferentes aspectos da linguagem:

| Teste | Descrição | Linhas | Características |
|-------|-----------|--------|-----------------|
| **t1.par** | Cliente-servidor calculadora | 25 | Canais, comunicação |
| **t2.par** | Fatorial + Fibonacci paralelo | 35 | Blocos PAR, loops |
| **t3.par** | Perceptron simples | 45 | While, operações |
| **t4.par** | Rede Neural XOR | 120 | Funções complexas |
| **t5.par** | Sistema de recomendação | 95 | Condicionais, math |
| **t6.par** | Fatorial iterativo | 15 | Loop for básico |
| **t7.par** | Fibonacci 5 termos | 18 | Sequência numérica |
| **t8.par** | Bubble Sort | 35 | Ordenação, trocas |

### Executar Testes

```bash
python main.py
# Pressione 'y' para cada teste
```

### Validação

✅ Todos os testes compilam sem erros  
✅ Código Assembly gerado é válido  
✅ Execução no CPUlator confirmada  
✅ Resultados corretos verificados  

---

## 🏗️ Arquitetura Técnica

### Tabela de Símbolos

Estrutura hierárquica com escopos aninhados:

```python
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}      # Dicionário de símbolos
        self.parent = parent   # Escopo pai
```

**Operações:**
- `define(name, value)` - Define novo símbolo
- `resolve(name)` - Busca na hierarquia
- `lookup(name)` - Retorna valor
- `assign(name, value)` - Atualiza símbolo

### Sistema de Tipos

- **Tipos básicos:** number, boolean, string, void
- **Inferência:** Automática baseada no uso
- **Verificação:** Em tempo de compilação

### Geração de Assembly

**Registradores ARMv7:**
- r0-r3: Argumentos e retorno
- r4-r10: Valores preservados
- r11 (fp): Frame pointer
- r13 (sp): Stack pointer
- r14 (lr): Link register

**Convenções:**
- Stack frames de 256 bytes
- Parâmetros via registradores
- Retorno em r0

---

## 📊 Estatísticas

| Métrica | Valor |
|---------|-------|
| Linhas de código | ~3.500 |
| Módulos Python | 8 |
| Classes | 8 |
| Funções/métodos | 127 |
| Programas de teste | 8 |
| Casos de teste | 92 |
| Tipos de tokens | 12 |
| Tipos de nós AST | 20 |
| Instruções C3E | 15 |
| Instruções Assembly | 25+ |

---

## 🤝 Equipe

### Desenvolvedores

- **Kauê Patricius Montenegro**
- **Walber Luis Santos da Paixão**
- **Gustavo Pereira Cordeiro**
- **Jean Patrick Martins Almeida**

### Orientação

**Disciplina:** Compiladores  
**Instituição:** Universidade Federal de Alagoas (UFAL)  
**Ano:** 2025

---

<div align="center">


![UFAL](https://img.shields.io/badge/UFAL-2025-blue)
![Compiladores](https://img.shields.io/badge/Disciplina-Compiladores-green)
![Status](https://img.shields.io/badge/Status-Completo-success)

</div>