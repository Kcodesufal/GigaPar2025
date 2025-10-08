from typing import Dict, List, Any

class SemanticError(Exception):
    """Erro semântico"""
    pass

class SymbolTable:
    """Tabela de símbolos simples com suporte a escopo"""
    def __init__(self, parent=None):
        self.symbols: Dict[str, Any] = {}
        self.parent: SymbolTable = parent

    def define(self, name: str, value: Any):
        if name in self.symbols:
            raise SemanticError(f"Símbolo '{name}' já definido neste escopo.")
        self.symbols[name] = value

    def assign(self, name: str, value: Any):
        table = self.resolve(name)
        if table is None:
            raise SemanticError(f"Variável '{name}' não definida.")
        table.symbols[name] = value

    def lookup(self, name: str):
        table = self.resolve(name)
        if table is None:
            raise SemanticError(f"Variável '{name}' não definida.")
        return table.symbols[name]

    def resolve(self, name: str):
        if name in self.symbols:
            return self
        elif self.parent:
            return self.parent.resolve(name)
        else:
            return None

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.global_scope = SymbolTable()

    def analyze(self):
        self.visit(self.ast, self.global_scope)

    def visit(self, node, scope: SymbolTable):
        nodetype = node[0]

        if nodetype == "program":
            self.visit(node[1], scope)

        elif nodetype == "stmts":
            for stmt in node[1]:
                self.visit(stmt, scope)

        elif nodetype == "assignment":
            var_name = node[1]
            expr = node[2]
            self.visit(expr, scope)
            # define a variável no escopo atual
            if not scope.resolve(var_name):
                scope.define(var_name, None)

        elif nodetype == "call":
            func_name = node[1]
            args = node[2]
            # verificar se a função foi declarada
            func_info = scope.lookup(func_name)
            if not func_info or func_info.get("type") != "function":
                raise SemanticError(f"Função '{func_name}' não declarada antes da chamada.")
            for arg in args:
                self.visit(arg, scope)

        elif nodetype == "builtin_call":
            for arg in node[2]:
                self.visit(arg, scope)

        elif nodetype == "function_stmt":
            func_name = node[1]
            params = node[2]
            body = node[3]
            # registra função no escopo atual
            scope.define(func_name, {"type": "function", "params": params})
            # cria novo escopo para corpo da função
            func_scope = SymbolTable(parent=scope)
            # define parâmetros no escopo da função
            for p in params:
                func_scope.define(p, None)
            self.visit(body, func_scope)

        elif nodetype in {"if", "if_else"}:
            cond = node[1]
            true_block = node[2]
            self.visit(cond, scope)
            self.visit(true_block, SymbolTable(parent=scope))
            if nodetype == "if_else":
                false_block = node[3]
                self.visit(false_block, SymbolTable(parent=scope))

        elif nodetype == "while":
            cond = node[1]
            body = node[2]
            self.visit(cond, scope)
            self.visit(body, SymbolTable(parent=scope))

        elif nodetype == "seq_stmt" or nodetype == "par_stmt":
            self.visit(node[1], SymbolTable(parent=scope))

        elif nodetype == "channel_stmt":
            # apenas checagem básica: variáveis devem existir
            for var in node[1:]:
                if not scope.resolve(var):
                    scope.define(var, None)  # ou erro se quiser exigir pré-declaração

        elif nodetype == "binop":
            self.visit(node[2], scope)
            self.visit(node[3], scope)

        elif nodetype == "unop":
            self.visit(node[2], scope)

        elif nodetype in {"id", "number", "boolean", "string"}:
            if nodetype == "id":
                # verificar se variável foi definida
                if not scope.resolve(node[1]):
                    raise SemanticError(f"Variável '{node[1]}' não definida.")
        else:
            raise SemanticError(f"Nó desconhecido: {nodetype}")
