from typing import List, Tuple, Any
from .interface_parser import IParser

class ParserError(Exception):
    """Erro sintático genérico."""
    pass

class Parser(IParser):
    def __init__(self, tokens: List[Tuple[str, Any]]):
        self.tokens = tokens
        self.pos = 0

    # ===========================
    # Utilitários
    # ===========================
    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ("EOF", None)

    def peek(self, n=1):
        idx = self.pos + n
        return self.tokens[idx] if idx < len(self.tokens) else ("EOF", None)

    def eat(self, expected_type, expected_value=None):
        ttype, value = self.current_token()
        if ttype == expected_type and (expected_value is None or value == expected_value):
            self.pos += 1
            return value
        raise ParserError(f"Erro sintático: esperado {expected_type} '{expected_value}', encontrado {ttype} '{value}'")

    # ===========================
    # Ponto de entrada
    # ===========================
    def parse(self):
        node = self.program()
        if self.current_token()[0] != "EOF":
            raise ParserError("Tokens restantes após o fim do programa.")
        return node

    # ===========================
    # Produções principais
    # ===========================
    def program(self):
        return ("program", self.compound_stmt())

    def compound_stmt(self):
        ttype, value = self.current_token()
        if (ttype, value) == ("KEYWORD", "SEQ"):
            return self.seq_stmt()
        elif (ttype, value) == ("KEYWORD", "PAR"):
            return self.par_stmt()
        else:
            return self.stmts()

    def seq_stmt(self):
        self.eat("KEYWORD", "SEQ")
        return ("seq_stmt", self.stmts())

    def par_stmt(self):
        self.eat("KEYWORD", "PAR")
        return ("par_stmt", self.stmts())

    def stmts(self):
        stmts_list = []
        while True:
            ttype, value = self.current_token()
            if ttype == "EOF" or (ttype == "KEYWORD" and value == "else"):
                break
            can_start_stmt = (
                ttype == "ID" or
                (ttype == "KEYWORD" and value in {
                    "if", "while", "c_channel", "def", "SEQ", "PAR", "print", "input"
                })
            )
            if not can_start_stmt:
                break
            before_pos = self.pos
            stmts_list.append(self.stmt())
            if self.pos == before_pos:
                raise ParserError("Erro interno: stmt não consumiu tokens.")
        return ("stmts", stmts_list)

    # ===========================
    # Tipos de comandos (statements)
    # ===========================
    def stmt(self):
        ttype, value = self.current_token()
        if ttype == "ID":
            nxt_ttype, nxt_value = self.peek(1)
            if (nxt_ttype, nxt_value) == ("OP", "="):
                return self.assignment()
            elif (nxt_ttype, nxt_value) == ("SYM", "("):
                return self.call()
            else:
                raise ParserError(f"Erro após identificador '{value}': esperado '=' ou '('.")
        elif ttype == "KEYWORD":
            if value == "if": return self.if_stmt()
            elif value == "while": return self.while_stmt()
            elif value == "c_channel": return self.channel_stmt()
            elif value == "def": return self.function_stmt()
            elif value in ("SEQ", "PAR"): return self.compound_stmt()
            elif value in ("print", "input"): return self.builtin_call()
            else: raise ParserError(f"Comando desconhecido: '{value}'")
        else:
            raise ParserError(f"Token inesperado no início de um comando: {ttype}, {value}")

    def assignment(self):
        id_name = self.eat("ID")
        self.eat("OP", "=")
        expr_node = self.expression()
        return ("assignment", id_name, expr_node)

    def if_stmt(self):
        self.eat("KEYWORD", "if")
        self.eat("SYM", "(")
        cond = self.expression()
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        true_block = self.stmts()
        if self.current_token() == ("KEYWORD", "else"):
            self.eat("KEYWORD", "else")
            self.eat("SYM", ":")
            false_block = self.stmts()
            return ("if_else", cond, true_block, false_block)
        return ("if", cond, true_block)

    def while_stmt(self):
        self.eat("KEYWORD", "while")
        self.eat("SYM", "(")
        cond = self.expression()
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        body = self.stmts()
        return ("while", cond, body)

    def call(self):
        func_name = self.eat("ID")
        self.eat("SYM", "(")
        
        arguments = []
        # A lista de argumentos é opcional
        if self.current_token() != ("SYM", ")"):
            arguments = self.args()
            
        self.eat("SYM", ")")
        return ("call", func_name, arguments)

    def builtin_call(self):
        func_name = self.eat("KEYWORD")
        self.eat("SYM", "(")
        
        arguments = []
        # A lista de argumentos é opcional
        if self.current_token() != ("SYM", ")"):
            arguments = self.args()

        self.eat("SYM", ")")
        return ("builtin_call", func_name, arguments)

    def function_stmt(self):
        self.eat("KEYWORD", "def")
        name = self.eat("ID")
        self.eat("SYM", "(")
        params = []
        # Lógica para parâmetros de definição de função (pode ser similar a 'args')
        if self.current_token() != ("SYM", ")"):
            while True:
                params.append(self.eat("ID"))
                if self.current_token() == ("SYM", ")"):
                    break
                self.eat("SYM", ",")
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        body = self.stmts()
        return ("function_stmt", name, params, body)

    def channel_stmt(self):
        self.eat("KEYWORD", "c_channel")
        channel = self.eat("ID")
        comp1 = self.eat("ID")
        comp2 = self.eat("ID")
        return ("channel_stmt", channel, comp1, comp2)
        
    def args(self):
        """Parseia uma lista de argumentos separados por vírgula.
        
        Corresponde a: args → expression { "," expression }*
        """
        arguments = []
        
        # Primeiro argumento é obrigatório nesta regra
        arguments.append(self.expression())
        
        # Loop para os argumentos seguintes, que são opcionais e precedidos por vírgula
        while self.current_token() == ("SYM", ","):
            self.eat("SYM", ",")
            arguments.append(self.expression())
            
        return arguments

    # ===========================
    # Expressões
    # ===========================
    def expression(self):
        return self.logic_or()

    def logic_or(self):
        node = self.logic_and()
        while self.current_token() == ("KEYWORD", "or"):
            op = self.eat("KEYWORD", "or")
            node = ("binop", op, node, self.logic_and())
        return node

    def logic_and(self):
        node = self.comparison_expr()
        while self.current_token() == ("KEYWORD", "and"):
            op = self.eat("KEYWORD", "and")
            node = ("binop", op, node, self.comparison_expr())
        return node

    def comparison_expr(self):
        node = self.sum_expr()
        while self.current_token()[0] == "OP" and self.current_token()[1] in {"==", "!=", "<", ">", "<=", ">="}:
            op = self.eat("OP")
            node = ("binop", op, node, self.sum_expr())
        return node

    def sum_expr(self):
        node = self.term_expr()
        while self.current_token()[0] == "OP" and self.current_token()[1] in {"+", "-"}:
            op = self.eat("OP")
            node = ("binop", op, node, self.term_expr())
        return node

    def term_expr(self):
        node = self.unary_expr()
        while self.current_token()[0] == "OP" and self.current_token()[1] in {"*", "/"}:
            op = self.eat("OP")
            node = ("binop", op, node, self.unary_expr())
        return node

    def unary_expr(self):
        ttype, value = self.current_token()
        if ttype in {"NUMBER", "ID", "BOOLEAN", "STRING"}:
            self.pos += 1
            return (ttype.lower(), value)
        elif (ttype, value) == ("KEYWORD", "not"):
            self.eat("KEYWORD", "not")
            return ("unop", "not", self.unary_expr())
        elif (ttype, value) == ("SYM", "("):
            self.eat("SYM", "(")
            node = self.expression()
            self.eat("SYM", ")")
            return node
        else:
            raise ParserError(f"Fator inesperado: {ttype}, {value}")