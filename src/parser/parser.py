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
        raise ParserError(
            f"Erro sintático: esperado {expected_type} '{expected_value}', encontrado {ttype} '{value}'"
        )

    def skip_newlines(self):
        """Ignora tokens NEWLINE consecutivos."""
        while self.current_token()[0] == "NEWLINE":
            self.pos += 1

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
        return ("program", self.stmts())

    def stmts(self):
        stmts_list = []
        self.skip_newlines()

        while True:
            ttype, value = self.current_token()
            if ttype in {"EOF", "DEDENT"}:
                break
            if ttype == "NEWLINE":
                self.skip_newlines()
                continue
            stmt_node = self.stmt()
            stmts_list.append(stmt_node)
            self.skip_newlines()
        return ("stmts", stmts_list)

    # ===========================
    # Tipos de comandos
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
            elif value == "for": return self.for_stmt()  # <--- NOVO
            elif value == "c_channel": return self.channel_stmt()
            elif value == "def": return self.function_stmt()
            elif value in ("SEQ", "PAR"): return self.compound_stmt()
            elif value in ("print", "input"): return self.builtin_call()
            else: raise ParserError(f"Comando desconhecido: '{value}'")
        else:
            raise ParserError(f"Token inesperado no início de um comando: {ttype}, {value}")

    # ===========================
    # Estruturas compostas
    # ===========================
    def compound_stmt(self):
        ttype, value = self.current_token()
        if (ttype, value) == ("KEYWORD", "SEQ"):
            self.eat("KEYWORD", "SEQ")
            self.eat("SYM", ":")
            self.skip_newlines()
            self.eat("INDENT")
            body = self.stmts()
            self.eat("DEDENT")
            return ("seq_stmt", body)
        elif (ttype, value) == ("KEYWORD", "PAR"):
            self.eat("KEYWORD", "PAR")
            self.eat("SYM", ":")
            self.skip_newlines()
            self.eat("INDENT")
            body = self.stmts()
            self.eat("DEDENT")
            return ("par_stmt", body)
        else:
            return self.stmts()

    def if_stmt(self):
        self.eat("KEYWORD", "if")
        self.eat("SYM", "(")
        cond = self.expression()
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        self.skip_newlines()
        self.eat("INDENT")
        true_block = self.stmts()
        self.eat("DEDENT")

        if self.current_token() == ("KEYWORD", "else"):
            self.eat("KEYWORD", "else")
            self.eat("SYM", ":")
            self.skip_newlines()
            self.eat("INDENT")
            false_block = self.stmts()
            self.eat("DEDENT")
            return ("if_else", cond, true_block, false_block)

        return ("if", cond, true_block)

    def while_stmt(self):
        self.eat("KEYWORD", "while")
        self.eat("SYM", "(")
        cond = self.expression()
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        self.skip_newlines()
        self.eat("INDENT")
        body = self.stmts()
        self.eat("DEDENT")
        return ("while", cond, body)

    # ===========================
    # NOVO: for estilo C/Python
    # ===========================
    def for_stmt(self):
        self.eat("KEYWORD", "for")
        self.eat("SYM", "(")

        # Parte 1: inicialização (pode ser vazia)
        init = None
        if self.current_token() != ("SYM", ";"):
            if self.current_token()[0] == "ID" and self.peek(1) == ("OP", "="):
                init = self.assignment()
            else:
                init = self.expression()
        self.eat("SYM", ";")

        # Parte 2: condição (pode ser vazia)
        cond = None
        if self.current_token() != ("SYM", ";"):
            cond = self.expression()
        self.eat("SYM", ";")

        # Parte 3: incremento (pode ser vazia)
        update = None
        if self.current_token() != ("SYM", ")"):
            if self.current_token()[0] == "ID" and self.peek(1) == ("OP", "="):
                update = self.assignment()
            else:
                update = self.expression()
        self.eat("SYM", ")")

        # Corpo
        self.eat("SYM", ":")
        self.skip_newlines()
        self.eat("INDENT")
        body = self.stmts()
        self.eat("DEDENT")

        return ("for", init, cond, update, body)

    def function_stmt(self):
        self.eat("KEYWORD", "def")
        name = self.eat("ID")
        self.eat("SYM", "(")
        params = []
        if self.current_token() != ("SYM", ")"):
            while True:
                params.append(self.eat("ID"))
                if self.current_token() == ("SYM", ")"):
                    break
                self.eat("SYM", ",")
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        self.skip_newlines()
        self.eat("INDENT")
        body = self.stmts()
        self.eat("DEDENT")
        return ("function_stmt", name, params, body)

    # ===========================
    # Outros statements
    # ===========================
    def assignment(self):
        id_name = self.eat("ID")
        self.eat("OP", "=")
        expr_node = self.expression()
        return ("assignment", id_name, expr_node)

    def call(self):
        func_name = self.eat("ID")
        self.eat("SYM", "(")
        args = []
        if self.current_token() != ("SYM", ")"):
            args = self.args()
        self.eat("SYM", ")")
        return ("call", func_name, args)

    def builtin_call(self):
        func_name = self.eat("KEYWORD")
        self.eat("SYM", "(")
        args = []
        if self.current_token() != ("SYM", ")"):
            args = self.args()
        self.eat("SYM", ")")
        return ("builtin_call", func_name, args)

    def channel_stmt(self):
        self.eat("KEYWORD", "c_channel")
        channel = self.eat("ID")
        comp1 = self.eat("ID")
        comp2 = self.eat("ID")
        return ("channel_stmt", channel, comp1, comp2)

    # ===========================
    # Argumentos e expressões
    # ===========================
    def args(self):
        args = [self.expression()]
        while self.current_token() == ("SYM", ","):
            self.eat("SYM", ",")
            args.append(self.expression())
        return args

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
