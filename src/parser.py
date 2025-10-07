from abc import ABC, abstractmethod

STATEMENT_TOKENS = {
    'if': 'if_statement',
    'else': 'else_statement',
    'while': 'while_statement',
    'for': 'for_statement',
    'print': 'print_statement',
    'elif': 'elif_statement',
    'def': 'def_statement',
    'c_channel': 'c_channel_statement',
    'SEQ': 'seq_statement',
    'PAR': 'par_statement',
}

class Parser(ABC):
    """
    Interface base para o parser.
    Define os métodos abstratos que devem ser implementados.
    """

    @abstractmethod
    def match(self, expected):
        """
        Verifica se o token atual corresponde ao esperado.
        Args:
            expected: Token esperado
        Raises:
            SyntaxError: Se o token não corresponder ao esperado
        """
        pass

    @abstractmethod
    def parse(self):
        """
        Método principal que inicia o processo de parsing.
        Retorna a AST (Abstract Syntax Tree).
        """
        pass

class ParserImpl(Parser):
    """
    Implementação concreta do Parser.
    Contém apenas as funções básicas necessárias para o funcionamento inicial.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.current_token = None
        self.next_token()

    def next_token(self):
        if self.current < len(self.tokens):
            self.current_token = self.tokens[self.current]
            self.current += 1
        else:
            self.current_token = None
        return self.current_token

    def peek_token(self):
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return None

    def match(self, expected):
        if self.current_token == expected:
            token = self.current_token
            self.next_token()
            return token
        raise SyntaxError(f"Expected {expected}, got {self.current_token}")

    def parse(self):
        """
        Implementação básica do parse que cria a estrutura inicial da AST
        """
        program = {
            "type": "program",
            "statements": []
        }
        
        while self.current_token is not None:
            stmt = self.statement()
            if stmt:
                program["statements"].append(stmt)
        
        return program

    def statement(self):
        """
        Implementação básica para parsing de statements
        """

        # implementar o switch case para cada tipo de statement 
        if self.current_token in STATEMENT_TOKENS:
            return {
                "type": STATEMENT_TOKENS[self.current_token],
                "token": self.current_token
            }
        elif self.current_token and self.current_token.startswith("<id"):
            return self.assignment()
        
        raise SyntaxError(f"Unexpected token in statement: {self.current_token}")

    def expression(self):
        """
        Implementação básica para parsing de expressões
        """
        # Por enquanto, apenas identificamos expressões simples
        token = self.current_token
        if token.startswith(("<num", "<id", "<string", "<bool")):
            self.next_token()
            return {
                "type": "expression",
                "value": token
            }
        raise SyntaxError(f"Invalid expression: {token}")

    def assignment(self):
        """
        Implementação básica para parsing de atribuições
        """
        identifier = self.current_token
        self.next_token()
        
        if self.current_token != "<=>":
            raise SyntaxError(f"Expected '=', got {self.current_token}")
        
        self.next_token()
        value = self.expression()
        
        return {
            "type": "assignment",
            "identifier": identifier,
            "value": value
        }

# Função auxiliar para uso do parser
def parse(tokens):
    """
    Função auxiliar que cria e executa o parser
    Args:
        tokens: Lista de tokens gerada pelo lexer
    Returns:
        AST gerada pelo parser
    """
    parser = ParserImpl(tokens)
    return parser.parse()
