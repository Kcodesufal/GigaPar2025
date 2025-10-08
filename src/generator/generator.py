class CodeGenerator:
    """
    Gera Código de 3 Endereços (C3E) a partir de uma AST semanticamente validada.
    Implementa suporte ao comando `return`.
    """
    def __init__(self):
        self.instructions = []  # A lista de instruções C3E geradas
        self.temp_counter = 0   # Contador para variáveis temporárias (t0, t1, ...)
        self.label_counter = 0  # Contador para rótulos (L0, L1, ...)
        self.current_function_end_label = None  # rótulo de fim da função atual (se em função)

    # ===========================
    # Métodos Utilitários
    # ===========================
    def new_temp(self):
        """Cria, registra e retorna uma nova variável temporária."""
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def new_label(self):
        """Cria e retorna um novo rótulo para saltos."""
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def add_instruction(self, instruction):
        """Adiciona uma instrução formatada à lista de instruções."""
        self.instructions.append(instruction)

    # ===========================
    # Ponto de Entrada e Visitor
    # ===========================
    def generate(self, node):
        """Ponto de entrada: inicia a geração e retorna a lista de instruções."""
        self.visit(node)
        return self.instructions

    def visit(self, node):
        """
        Método visitor principal que despacha para o método correto
        baseado no tipo do nó da AST.
        """
        if node is None:
            return None  # Partes opcionais do 'for' podem ser None

        # A AST é baseada em tuplas, onde o primeiro elemento é o tipo do nó.
        nodetype = node[0]
        method_name = f'visit_{nodetype}'

        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f'Nenhum método visit_{node[0]} encontrado')

    # ============================================
    # Visitor para ESTRUTURAS GERAIS E BLOCOS
    # ============================================
    def visit_program(self, node):
        # ("program", stmts)
        self.visit(node[1])

    def visit_stmts(self, node):
        # ("stmts", [stmt1, stmt2, ...])
        for stmt in node[1]:
            self.visit(stmt)

    def visit_seq_stmt(self, node):
        # ("seq_stmt", stmts)
        self.visit(node[1])

    def visit_par_stmt(self, node):
        # ("par_stmt", stmts)
        self.add_instruction("# BEGIN PARALLEL BLOCK")
        self.visit(node[1])
        self.add_instruction("# END PARALLEL BLOCK")

    # ========================================
    # Visitor para EXPRESSÕES
    # ========================================
    def visit_number(self, node): return node[1]
    def visit_string(self, node): return node[1]
    def visit_boolean(self, node): return node[1]
    def visit_id(self, node): return node[1]

    def visit_binop(self, node):
        # ("binop", op, left, right)
        op, left_node, right_node = node[1], node[2], node[3]

        left_addr = self.visit(left_node)
        right_addr = self.visit(right_node)

        result_addr = self.new_temp()
        self.add_instruction(f"{result_addr} = {left_addr} {op} {right_addr}")

        return result_addr

    def visit_unop(self, node):
        # ("unop", op, expr)
        op, expr_node = node[1], node[2]

        expr_addr = self.visit(expr_node)
        result_addr = self.new_temp()

        # O operador unário é prefixado
        self.add_instruction(f"{result_addr} = {op} {expr_addr}")

        return result_addr

    # ========================================
    # Visitor para COMANDOS (STATEMENTS)
    # ========================================
    def visit_assignment(self, node):
        # ("assignment", var_name, expr)
        var_name, expr_node = node[1], node[2]

        expr_addr = self.visit(expr_node)
        self.add_instruction(f"{var_name} = {expr_addr}")

    def visit_if(self, node):
        # ("if", cond, true_block)
        cond_node, true_block_node = node[1], node[2]

        end_label = self.new_label()

        cond_addr = self.visit(cond_node)
        self.add_instruction(f"if_false {cond_addr} goto {end_label}")

        self.visit(true_block_node)

        self.add_instruction(f"{end_label}:")

    def visit_if_else(self, node):
        # ("if_else", cond, true_block, false_block)
        cond_node, true_block_node, false_block_node = node[1], node[2], node[3]

        else_label = self.new_label()
        end_label = self.new_label()

        cond_addr = self.visit(cond_node)
        self.add_instruction(f"if_false {cond_addr} goto {else_label}")

        self.visit(true_block_node)
        self.add_instruction(f"goto {end_label}")

        self.add_instruction(f"{else_label}:")
        self.visit(false_block_node)

        self.add_instruction(f"{end_label}:")

    def visit_while(self, node):
        # ("while", cond, body)
        cond_node, body_node = node[1], node[2]

        start_label = self.new_label()
        end_label = self.new_label()

        self.add_instruction(f"{start_label}:")

        cond_addr = self.visit(cond_node)
        self.add_instruction(f"if_false {cond_addr} goto {end_label}")

        self.visit(body_node)
        self.add_instruction(f"goto {start_label}")

        self.add_instruction(f"{end_label}:")

    def visit_for(self, node):
        # ("for", init, cond, update, body)
        init_node, cond_node, update_node, body_node = node[1], node[2], node[3], node[4]

        start_label = self.new_label()
        end_label = self.new_label()

        # inicialização (pode ser None)
        if init_node:
            self.visit(init_node)

        self.add_instruction(f"{start_label}:")

        if cond_node:
            cond_addr = self.visit(cond_node)
            self.add_instruction(f"if_false {cond_addr} goto {end_label}")

        if body_node:
            self.visit(body_node)
        if update_node:
            self.visit(update_node)

        self.add_instruction(f"goto {start_label}")

        self.add_instruction(f"{end_label}:")

    def visit_channel_stmt(self, node):
        # ("channel_stmt", name, comp1, comp2)
        name, c1, c2 = node[1], node[2], node[3]
        self.add_instruction(f"channel_decl {name}, {c1}, {c2}")

    # ========================================
    # Visitor para FUNÇÕES
    # ========================================
    def visit_function_stmt(self, node):
        # ("function_stmt", name, params, body)
        name, params, body_node = node[1], node[2], node[3]

        # Rótulo para pular a definição da função durante execução normal
        end_func_label = self.new_label()
        self.add_instruction(f"goto {end_func_label}")

        # Início da definição da função
        self.add_instruction(f"{name}:")
        self.add_instruction("begin_func")
        for param in params:
            self.add_instruction(f"get_param {param}")  # instrução para receber o parâmetro

        # marca o rótulo de fim da função para que 'return' saiba para onde saltar
        prev_end_label = self.current_function_end_label
        self.current_function_end_label = end_func_label

        # gera corpo
        self.visit(body_node)

        # se o corpo não tiver retorno explícito, garantimos um retorno "void"
        # (emitimos instrução de retorno vazia antes do end da função)
        self.add_instruction("return")

        # fim da definição
        self.add_instruction("end_func")
        self.add_instruction(f"{end_func_label}:")

        # restaura o rótulo anterior (caso de funções aninhadas)
        self.current_function_end_label = prev_end_label

    def visit_call(self, node):
        # ("call", func_name, [args])
        return self._handle_call(node)

    def visit_builtin_call(self, node):
        # ("builtin_call", func_name, [args])
        return self._handle_call(node)

    def _handle_call(self, node):
        func_name, args_nodes = node[1], node[2]

        # 1. Avalia todos os argumentos primeiro
        arg_addrs = [self.visit(arg) for arg in args_nodes]

        # 2. Empurra os parâmetros para a chamada (em ordem inversa é comum)
        for arg_addr in reversed(arg_addrs):
            self.add_instruction(f"param {arg_addr}")

        # 3. Prepara um temporário para o valor de retorno
        return_addr = self.new_temp()

        # 4. Gera a instrução de chamada
        self.add_instruction(f"{return_addr} = call {func_name}, {len(arg_addrs)}")

        return return_addr

    # ========================================
    # RETURN
    # ========================================
    def visit_return_stmt(self, node):
        # ("return_stmt", expr ou None)
        expr = node[1]

        if expr is None:
            # retorno vazio (void)
            self.add_instruction("return")
        else:
            ret_addr = self.visit(expr)
            self.add_instruction(f"return {ret_addr}")

        # garante que o fluxo salte para o fim da função (se estivermos dentro de uma função)
        if self.current_function_end_label is not None:
            self.add_instruction(f"goto {self.current_function_end_label}")
