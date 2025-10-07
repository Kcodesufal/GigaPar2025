from typing import List, Tuple, Any

class ParserError(Exception):
    """Erro sintático genérico."""
    pass

class Parser:
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

    def accept(self, expected_type, expected_value=None):
        ttype, value = self.current_token()
        if ttype == expected_type and (expected_value is None or value == expected_value):
            self.pos += 1
            return True
        return False

    # ===========================
    # Ponto de entrada
    # ===========================
    def parse(self):
        node = self.programa_minipar()
        if self.current_token()[0] != "EOF":
            raise ParserError("Tokens restantes após o fim do programa.")
        return node

    # ===========================
    # Produções principais
    # ===========================
    def programa_minipar(self):
        return ("programa_minipar", self.bloco_stmt())

    def bloco_stmt(self):
        ttype, value = self.current_token()
        if (ttype, value) == ("KEYWORD", "SEQ"):
            return self.bloco_SEQ()
        elif (ttype, value) == ("KEYWORD", "PAR"):
            return self.bloco_PAR()
        else:
            return self.stmts()

    def bloco_SEQ(self):
        self.eat("KEYWORD", "SEQ")
        return ("SEQ", self.stmts())

    def bloco_PAR(self):
        self.eat("KEYWORD", "PAR")
        return ("PAR", self.stmts())

    def stmts(self):
        stmts_list = []
        while True:
            ttype, value = self.current_token()
            if ttype in {"EOF", "SYM"} and value in {")", "}"}:
                break
            if ttype in {"ID", "KEYWORD"}:
                before = self.pos
                stmts_list.append(self.stmt())
                if self.pos == before:
                    raise ParserError("Erro interno: stmt não consumiu tokens.")
                continue
            break
        return ("stmts", stmts_list)

    # ===========================
    # Tipos de comandos
    # ===========================
    def stmt(self):
        ttype, value = self.current_token()
        if ttype == "ID":
            nxt = self.peek(1)
            if nxt[1] == "=":
                return self.atribuicao()
            elif nxt[1] == "(":
                return self.func_call()
            else:
                raise ParserError(f"Erro após identificador '{value}': esperado '=' ou '('.")
        elif ttype == "KEYWORD":
            if value == "if":
                return self.if_stmt()
            elif value == "while":
                return self.while_stmt()
            elif value == "c_channel":
                return self.c_channel_decl()
            elif value == "def":
                return self.function_def()
            elif value in ("SEQ", "PAR"):
                return self.bloco_stmt()
            elif value in ("print", "input"):
                return self.func_call_keyword(value)
            else:
                raise ParserError(f"Comando desconhecido: '{value}'")
        else:
            raise ParserError(f"Token inesperado: {ttype}, {value}")

    def atribuicao(self):
        id_name = self.eat("ID")
        self.eat("OP", "=")
        expr_node = self.expr()
        return ("atrib", id_name, expr_node)

    def if_stmt(self):
        self.eat("KEYWORD", "if")
        self.eat("SYM", "(")
        cond = self.expr()
        self.eat("SYM", ")")
        self.eat("SYM", ":")  # ':' obrigatório
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
        cond = self.expr()
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        body = self.stmts()
        return ("while", cond, body)

    def func_call(self):
        func_name = self.eat("ID")
        self.eat("SYM", "(")
        args = []
        while not (self.current_token()[0] == "SYM" and self.current_token()[1] == ")"):
            if self.current_token()[0] == "EOF":
                raise ParserError("Esperado ')' para encerrar chamada de função.")
            args.append(self.expr())
        self.eat("SYM", ")")
        return ("func_call", func_name, args)

    def func_call_keyword(self, func_name):
        self.eat("KEYWORD", func_name)
        self.eat("SYM", "(")
        args = []
        while not (self.current_token()[0] == "SYM" and self.current_token()[1] == ")"):
            if self.current_token()[0] == "EOF":
                raise ParserError(f"Esperado ')' após chamada de função {func_name}.")
            args.append(self.expr())
        self.eat("SYM", ")")
        return ("func_call", func_name, args)

    def function_def(self):
        self.eat("KEYWORD", "def")
        name = self.eat("ID")
        self.eat("SYM", "(")
        params = []
        while not (self.current_token()[0] == "SYM" and self.current_token()[1] == ")"):
            if self.current_token()[0] == "EOF":
                raise ParserError("Esperado ')' ao final dos parâmetros da função.")
            params.append(self.eat("ID"))
        self.eat("SYM", ")")
        self.eat("SYM", ":")
        body = self.stmts()
        return ("def", name, params, body)

    def c_channel_decl(self):
        self.eat("KEYWORD", "c_channel")
        channel = self.eat("ID")
        comp1 = self.eat("ID")
        comp2 = self.eat("ID")
        return ("c_channel", channel, comp1, comp2)

    # ===========================
    # Expressões
    # ===========================
    def expr(self):
        return self.or_expr()

    def or_expr(self):
        node = self.and_expr()
        while self.current_token() == ("KEYWORD", "or"):
            self.eat("KEYWORD", "or")
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self):
        node = self.compare_expr()
        while self.current_token() == ("KEYWORD", "and"):
            self.eat("KEYWORD", "and")
            node = ("and", node, self.compare_expr())
        return node

    def compare_expr(self):
        node = self.add_expr()
        while self.current_token()[0] == "OP" and self.current_token()[1] in {"==", "!=", "<", ">", "<=", ">="}:
            op = self.eat("OP")
            node = ("binop", op, node, self.add_expr())
        return node

    def add_expr(self):
        node = self.mul_expr()
        while self.current_token()[0] == "OP" and self.current_token()[1] in {"+", "-"}:
            op = self.eat("OP")
            node = ("binop", op, node, self.mul_expr())
        return node

    def mul_expr(self):
        node = self.factor()
        while self.current_token()[0] == "OP" and self.current_token()[1] in {"*", "/"}:
            op = self.eat("OP")
            node = ("binop", op, node, self.factor())
        return node

    def factor(self):
        ttype, value = self.current_token()
        if ttype in {"NUM", "ID", "BOOL", "STR"}:
            self.pos += 1
            return (ttype, value)
        elif (ttype, value) == ("KEYWORD", "not"):
            self.eat("KEYWORD", "not")
            return ("not", self.factor())
        elif (ttype, value) == ("SYM", "("):
            self.eat("SYM", "(")
            node = self.expr()
            self.eat("SYM", ")")
            return node
        else:
            raise ParserError(f"Fator inesperado: {ttype}, {value}")
