class CodeGenerator:
    """
    Gera Código de 3 Endereços (C3E) a partir de uma AST semanticamente validada.
    Suporte a:
      - Blocos paralelos (PAR)
      - Blocos sequenciais (SEQ)
      - Funções, chamadas e builtins
      - Send/Receive de canais (C_CHANNEL)
    """
    def __init__(self):
        self.instructions = []  # Lista de instruções C3E geradas
        self.temp_counter = 0   # Contador para variáveis temporárias (t0, t1, ...)
        self.label_counter = 0  # Contador para rótulos (L0, L1, ...)
        self.current_function_end_label = None  # rótulo de fim da função atual

    # ===========================
    # Métodos Utilitários
    # ===========================
    def new_temp(self):
        temp = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp

    def new_label(self):
        label = f"L{self.label_counter}"
        self.label_counter += 1
        return label

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    # ===========================
    # Ponto de Entrada e Visitor
    # ===========================
    def generate(self, node):
        """Inicia a geração e retorna a lista de instruções."""
        self.visit(node)
        return self.instructions

    def visit(self, node):
        if node is None:
            return None
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
        self.visit(node[1])

    def visit_stmts(self, node):
        for stmt in node[1]:
            self.visit(stmt)

    def visit_seq_stmt(self, node):
        # ("seq_stmt", stmts)
        self.add_instruction("BEGIN_SEQUENCE")
        self.visit(node[1])
        self.add_instruction("END_SEQUENCE")

    def visit_par_stmt(self, node):
        # ("par_stmt", stmts)
        self.add_instruction("BEGIN_PARALLEL")
        self.visit(node[1])
        self.add_instruction("END_PARALLEL")

    # ========================================
    # Visitor para EXPRESSÕES
    # ========================================
    def visit_number(self, node): 
        return node[1]
    
    def visit_string(self, node): 
        return node[1]
    
    def visit_boolean(self, node): 
        return node[1]
    
    def visit_id(self, node): 
        return node[1]

    def visit_binop(self, node):
        op, left_node, right_node = node[1], node[2], node[3]
        left_addr = self.visit(left_node)
        right_addr = self.visit(right_node)
        result_addr = self.new_temp()
        self.add_instruction(f"{result_addr} = {left_addr} {op} {right_addr}")
        return result_addr

    def visit_unop(self, node):
        op, expr_node = node[1], node[2]
        expr_addr = self.visit(expr_node)
        result_addr = self.new_temp()
        self.add_instruction(f"{result_addr} = {op} {expr_addr}")
        return result_addr

    # ========================================
    # Visitor para COMANDOS (STATEMENTS)
    # ========================================
    def visit_assignment(self, node):
        var_name, expr_node = node[1], node[2]
        expr_addr = self.visit(expr_node)
        self.add_instruction(f"{var_name} = {expr_addr}")

    def visit_if(self, node):
        cond_node, true_block_node = node[1], node[2]
        end_label = self.new_label()
        cond_addr = self.visit(cond_node)
        self.add_instruction(f"if_false {cond_addr} goto {end_label}")
        self.visit(true_block_node)
        self.add_instruction(f"{end_label}:")

    def visit_if_else(self, node):
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
        init_node, cond_node, update_node, body_node = node[1], node[2], node[3], node[4]
        start_label = self.new_label()
        end_label = self.new_label()
        if init_node: self.visit(init_node)
        self.add_instruction(f"{start_label}:")
        if cond_node:
            cond_addr = self.visit(cond_node)
            self.add_instruction(f"if_false {cond_addr} goto {end_label}")
        if body_node: self.visit(body_node)
        if update_node: self.visit(update_node)
        self.add_instruction(f"goto {start_label}")
        self.add_instruction(f"{end_label}:")

    def visit_channel_stmt(self, node):
        name, c1, c2 = node[1], node[2], node[3]
        self.add_instruction(f"channel_decl {name}, {c1}, {c2}")

    # ========================================
    # Visitor para FUNÇÕES
    # ========================================
    def visit_function_stmt(self, node):
        name, params, body_node = node[1], node[2], node[3]
        end_func_label = self.new_label()
        self.add_instruction(f"goto {end_func_label}")
        self.add_instruction(f"{name}:")
        self.add_instruction("begin_func")
        for param in params:
            self.add_instruction(f"get_param {param}")
        prev_end_label = self.current_function_end_label
        self.current_function_end_label = end_func_label
        self.visit(body_node)
        self.add_instruction("return")
        self.add_instruction("end_func")
        self.add_instruction(f"{end_func_label}:")
        self.current_function_end_label = prev_end_label

    def visit_call(self, node):
        return self._handle_call(node)

    def visit_builtin_call(self, node):
        return self._handle_call(node)

    def _handle_call(self, node):
        func_name, args_nodes = node[1], node[2]
        arg_addrs = [self.visit(arg) for arg in args_nodes]
        for arg_addr in reversed(arg_addrs):
            self.add_instruction(f"param {arg_addr}")
        return_addr = self.new_temp()
        self.add_instruction(f"{return_addr} = call {func_name}, {len(arg_addrs)}")
        return return_addr

    # ========================================
    # RETURN
    # ========================================
    def visit_return_stmt(self, node):
        expr = node[1]
        if expr is None:
            self.add_instruction("return")
        else:
            ret_addr = self.visit(expr)
            self.add_instruction(f"return {ret_addr}")
        if self.current_function_end_label is not None:
            self.add_instruction(f"goto {self.current_function_end_label}")

    # ========================================
    # SUPORTE A CHANNEL SEND / RECEIVE
    # ========================================
    def visit_channel_send(self, node):
        channel_name, args = node[1], node[2]
        arg_addrs = [self.visit(arg) for arg in args]
        for a in reversed(arg_addrs):
            self.add_instruction(f"param {a}")
        self.add_instruction(f"send {channel_name}, {len(arg_addrs)}")
        return None

    def visit_channel_receive(self, node):
        channel_name, args = node[1], node[2]
        var_names = []
        for a in args:
            if a[0] != "id":
                raise Exception("Argumentos de receive devem ser variáveis (id).")
            var_names.append(a[1])
        self.add_instruction(f"receive {channel_name}, {', '.join(var_names)}")
        return None
