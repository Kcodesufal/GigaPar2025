from typing import Dict, Any, Optional, List

class SemanticError(Exception):
    """Erro semântico detalhado."""
    def __init__(self, message: str):
        super().__init__(f"Erro semântico: {message}")


class SymbolTable:
    """Tabela de símbolos com suporte a escopos."""
    def __init__(self, parent: Optional["SymbolTable"] = None):
        self.symbols: Dict[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any):
        if name in self.symbols:
            raise SemanticError(f"Símbolo '{name}' já definido neste escopo.")
        self.symbols[name] = value

    def resolve(self, name: str) -> Optional["SymbolTable"]:
        """
        Retorna a tabela que contém 'name' ou None se não existir.
        """
        if name in self.symbols:
            return self
        if self.parent:
            return self.parent.resolve(name)
        return None

    def lookup(self, name: str):
        table = self.resolve(name)
        if table is None:
            raise SemanticError(f"Símbolo '{name}' não definido.")
        return table.symbols[name]

    def assign(self, name: str, value: Any):
        table = self.resolve(name)
        if table:
            table.symbols[name] = value
        else:
            raise SemanticError(f"Tentativa de atribuir a variável '{name}' não definida.")

    def set_type(self, name: str, new_type: str):
        """
        Atualiza o tipo do símbolo 'name' (se o símbolo existir).
        Mantém 'initialized' se já existia, caso contrário deixa como False.
        """
        table = self.resolve(name)
        if table is None:
            raise SemanticError(f"Tentativa de set_type em '{name}' que não existe.")
        info = table.symbols[name]
        if isinstance(info, dict):
            info["type"] = new_type
        else:
            # caso o valor não seja dict (não esperado), sobrescrevemos
            table.symbols[name] = {"type": new_type, "initialized": True}


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.global_scope = SymbolTable()
        self.current_function: Optional[str] = None

    def analyze(self):
        """Inicia a análise semântica do AST."""
        self.visit(self.ast, self.global_scope)

    # ===========================================================
    # VISITADOR
    # ===========================================================
    def visit(self, node, scope: SymbolTable):
        nodetype = node[0]

        if nodetype == "program":
            # ("program", stmts)
            return self.visit(node[1], scope)

        elif nodetype == "stmts":
            # ("stmts", [stmt1, stmt2, ...])
            for stmt in node[1]:
                self.visit(stmt, scope)
            return None

        elif nodetype == "assignment":
            # ("assignment", var_name, expr)
            var_name = node[1]
            expr = node[2]
            expr_type = self.visit(expr, scope)

            # define ou atualiza variável
            if scope.resolve(var_name) is None:
                scope.define(var_name, {"type": expr_type, "initialized": True})
            else:
                info = scope.lookup(var_name)
                # info pode ser um dict com "type"
                existing_type = info.get("type", "unknown") if isinstance(info, dict) else "unknown"
                if existing_type != expr_type and existing_type != "unknown":
                    raise SemanticError(
                        f"Incompatibilidade de tipo em '{var_name}'. Esperado {existing_type}, obtido {expr_type}."
                    )
                # atualiza o tipo se estava unknown
                if isinstance(info, dict):
                    info["type"] = expr_type
                    info["initialized"] = True
                else:
                    scope.assign(var_name, {"type": expr_type, "initialized": True})
            return expr_type

        elif nodetype == "function_stmt":
            # ("function_stmt", name, params, stmts)
            func_name, params, body = node[1], node[2], node[3]

            if scope.resolve(func_name) is not None:
                raise SemanticError(f"Função '{func_name}' já foi definida.")

            # Registra função no escopo atual; armazena param_types inicial como unknown
            func_info = {
                "type": "function",
                "params": params,
                "param_types": {p: "unknown" for p in params},
                "return": "unknown",
                "body": body
            }
            scope.define(func_name, func_info)

            # Cria novo escopo para função e define parâmetros com tipo unknown
            func_scope = SymbolTable(parent=scope)
            for p in params:
                func_scope.define(p, {"type": "unknown", "initialized": True})

            prev_func = self.current_function
            self.current_function = func_name
            # analisa o corpo — durante essa análise podemos inferir tipos dos parâmetros
            self.visit(body, func_scope)
            self.current_function = prev_func

            # Após analisar o corpo, extraímos os tipos inferidos dos parâmetros
            for p in params:
                p_table = func_scope.resolve(p)
                if p_table:
                    p_info = p_table.symbols[p]
                    if isinstance(p_info, dict):
                        inferred = p_info.get("type", "unknown")
                        func_info["param_types"][p] = inferred
            return None

        elif nodetype == "call":
            # ("call", func_name, [args])
            func_name = node[1]
            args = node[2]
            func_info = scope.lookup(func_name)

            if func_info.get("type") != "function":
                raise SemanticError(f"'{func_name}' não é uma função válida.")

            expected = len(func_info["params"])
            received = len(args)
            if expected != received:
                raise SemanticError(
                    f"Função '{func_name}' esperava {expected} argumento(s), recebeu {received}."
                )

            # verificamos tipos dos argumentos comparando com param_types (inferidos do corpo)
            for i, arg in enumerate(args):
                arg_type = self.visit(arg, scope)
                param_name = func_info["params"][i]
                expected_type = func_info["param_types"].get(param_name, "unknown")

                if expected_type != "unknown" and arg_type != "unknown" and arg_type != expected_type:
                    raise SemanticError(
                        f"Tipo incorreto no argumento {i+1} da função '{func_name}': esperado {expected_type}, obtido {arg_type}."
                    )
                # se a função tinha tipo unknown para o parâmetro, não forçamos inferência a partir da chamada
                # (preferimos inferir a partir do corpo da função; chamdas podem ocorrer com tipos diferentes).

            return func_info.get("return", "unknown")

        elif nodetype == "builtin_call":
            # ("builtin_call", "print", [args...])
            for arg in node[2]:
                self.visit(arg, scope)
            return "unknown"

        elif nodetype in {"if", "if_else"}:
            cond = node[1]
            true_block = node[2]
            cond_type = self.visit(cond, scope)
            if cond_type != "boolean":
                raise SemanticError(f"A condição do '{nodetype}' deve ser booleana.")
            self.visit(true_block, SymbolTable(parent=scope))
            if nodetype == "if_else":
                false_block = node[3]
                self.visit(false_block, SymbolTable(parent=scope))
            return None

        elif nodetype == "while":
            cond, body = node[1], node[2]
            cond_type = self.visit(cond, scope)
            if cond_type != "boolean":
                raise SemanticError("Condição do 'while' deve ser booleana.")
            self.visit(body, SymbolTable(parent=scope))
            return None
        elif nodetype == "for":
            # ("for", init_stmt, cond_expr, update_stmt, body)
            init_stmt, cond_expr, update_stmt, body = node[1], node[2], node[3], node[4]

            # Criar escopo próprio do loop for
            loop_scope = SymbolTable(parent=scope)

            # Analisar a inicialização (pode definir variáveis)
            self.visit(init_stmt, loop_scope)

            # Verificar tipo da condição
            cond_type = self.visit(cond_expr, loop_scope)
            if cond_type != "boolean":
                raise SemanticError("A condição do 'for' deve ser booleana.")

            # Analisar atualização (geralmente é uma atribuição)
            self.visit(update_stmt, loop_scope)

            # Analisar corpo do loop
            self.visit(body, SymbolTable(parent=loop_scope))

            return None

        # Adicionado suporte a return

        elif nodetype == "return_stmt":
            # ("return_stmt", expr ou None)

            # Verifica se estamos dentro de uma função
            if self.current_function is None:
                raise SemanticError("'return' só pode ser usado dentro de uma função.")

            # Se há uma expressão, analisa seu tipo
            return_expr = node[1]
            if return_expr is not None:
                return_type = self.visit(return_expr, scope)

                # Atualiza o tipo de retorno da função
                func_info = self.global_scope.lookup(self.current_function)
                if isinstance(func_info, dict):
                    existing_return = func_info.get("return", "unknown")

                    # Se já tinha um tipo de retorno diferente, verifica compatibilidade
                    if existing_return != "unknown" and existing_return != return_type:
                        raise SemanticError(
                            f"Função '{self.current_function}' retorna tipos inconsistentes: "
                            f"{existing_return} e {return_type}."
                        )

                    func_info["return"] = return_type

                return return_type
            else:
                # return vazio (retorna None/void)
                func_info = self.global_scope.lookup(self.current_function)
                if isinstance(func_info, dict):
                    if func_info.get("return", "unknown") == "unknown":
                        func_info["return"] = "void"
                return "void"


        elif nodetype in {"seq_stmt", "par_stmt"}:
            # ("seq_stmt", stmts) / ("par_stmt", stmts)
            self.visit(node[1], SymbolTable(parent=scope))
            return None

        elif nodetype == "channel_stmt":
            # ("channel_stmt", var1, var2, ...)
            for var in node[1:]:
                if scope.resolve(var) is None:
                    scope.define(var, {"type": "channel", "initialized": True})
            return "channel"

        elif nodetype == "binop":
            # ("binop", op, left, right)
            op, left, right = node[1], node[2], node[3]
            ltype = self.visit(left, scope)
            rtype = self.visit(right, scope)

            # Se um dos lados for 'unknown' e for um ID, inferimos o tipo com base no operador
            expected_type = None
            if op in {"+", "-", "*", "/"}:
                expected_type = "number"
            elif op in {"and", "or"}:
                expected_type = "boolean"
            elif op in {"==", "!=", ">", "<", ">=", "<="}:
                # comparações aceitam múltiplos tipos; devolvem boolean
                # se quiser, poderia inferir ambos para o mesmo tipo, porém deixamos flexível
                expected_type = "any_compare"

            # inferência simples: se um lado unknown e é id, definimos o tipo esperado
            if expected_type and expected_type != "any_compare":
                # esquerda
                if ltype == "unknown" and isinstance(left, tuple) and left[0] == "id":
                    name = left[1]
                    # tentar setar no escopo apropriado (se existir)
                    try:
                        scope.set_type(name, expected_type)
                        ltype = expected_type
                    except SemanticError:
                        # se não conseguiu, silenciosamente segue (não deveria ocorrer normalmente)
                        pass
                # direita
                if rtype == "unknown" and isinstance(right, tuple) and right[0] == "id":
                    name = right[1]
                    try:
                        scope.set_type(name, expected_type)
                        rtype = expected_type
                    except SemanticError:
                        pass

            # agora, se ambos são conhecidos e diferentes => erro
            if ltype != "unknown" and rtype != "unknown" and ltype != rtype:
                raise SemanticError(f"Operação '{op}' entre tipos incompatíveis: {ltype} e {rtype}.")

            # determinar tipo de retorno conforme operador
            if op in {"+", "-", "*", "/"}:
                return "number"
            elif op in {"and", "or"}:
                return "boolean"
            elif op in {"==", "!=", ">", "<", ">=", "<="}:
                return "boolean"
            return "unknown"

        elif nodetype == "unop":
            # ("unop", op, expr)
            op, expr = node[1], node[2]
            etype = self.visit(expr, scope)
            if op == "not" and etype != "boolean":
                raise SemanticError("Operador 'not' só é válido para booleanos.")
            if op == "-" and etype != "number":
                raise SemanticError("Operador '-' só é válido para números.")
            return etype

        elif nodetype == "id":
            var_name = node[1]
            info = scope.lookup(var_name)
            # info deve ser dict {"type": ..., "initialized": ...}
            if isinstance(info, dict):
                if not info.get("initialized", False):
                    raise SemanticError(f"Variável '{var_name}' usada antes de ser inicializada.")
                return info.get("type", "unknown")
            else:
                # se o conteúdo não for dict, retornamos unknown
                return "unknown"

        elif nodetype == "number":
            return "number"
        elif nodetype == "boolean":
            return "boolean"
        elif nodetype == "string":
            return "string"

        else:
            raise SemanticError(f"Nó desconhecido: {nodetype}")
