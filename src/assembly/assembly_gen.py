class AssemblyGenerator:
    """
    Gera código Assembly ARMv7 a partir de Código de 3 Endereços (C3E).
    Versão corrigida com suporte a loops, comparações e divisão segura.
    """

    def __init__(self):
        self.asm_code = []
        self.data_section = []
        self.var_locations = {}
        self.stack_offset = 0
        self.string_counter = 0
        self.channels = {}
        self.current_function = None
        self.function_counter = 0
        self.labels_defined = set()

        self.temp_registers = ['r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10']
        self.used_callee_saved_regs = set()
        self.reg_index = 0
        self.param_registers = ['r0', 'r1', 'r2', 'r3']
        self.param_count = 0
        self.max_stack_used = 0
        self.stack_vars = []

    # -------------------------
    # UTILITÁRIOS
    # -------------------------
    def emit(self, instr):
        self.asm_code.append(f"    {instr}")

    def emit_label(self, label):
        if label not in self.labels_defined:
            self.asm_code.append(f"{label}:")
            self.labels_defined.add(label)

    def emit_comment(self, comment):
        self.asm_code.append(f"    @ {comment}")

    def allocate_stack_var(self, var_name):
        if var_name not in self.var_locations:
            self.stack_offset += 4
            offset = -self.stack_offset
            self.var_locations[var_name] = f"[fp, #{offset}]"
            self.stack_vars.append(var_name)
            if self.stack_offset > self.max_stack_used:
                self.max_stack_used = self.stack_offset
        return self.var_locations[var_name]

    def get_location(self, operand):
        if isinstance(operand, str):
            clean_operand = operand.lstrip('-').replace('.', '', 1)
            if clean_operand.isdigit():
                return f"#{operand}"
            if operand.startswith('"'):
                label = self.add_string_literal(operand)
                return label
            if operand in self.var_locations:
                return self.var_locations[operand]
            else:
                return self.allocate_stack_var(operand)
        if isinstance(operand, (int, float)):
            return f"#{int(operand)}"
        raise ValueError(f"Operando não suportado: {operand}")

    def add_string_literal(self, string_value):
        label = f".STR{self.string_counter}"
        self.string_counter += 1
        clean_string = string_value.strip('"')
        self.data_section.append(f'{label}: .asciz "{clean_string}"')
        return label

    def load_to_register(self, operand, reg):
        loc = self.get_location(operand)
        if loc.startswith('#'):
            self.emit(f"mov {reg}, {loc}")
        elif loc.startswith('.STR'):
            self.emit(f"ldr {reg}, ={loc}")
        elif loc.startswith('['):
            self.emit(f"ldr {reg}, {loc}")
        else:
            if loc != reg:
                self.emit(f"mov {reg}, {loc}")

    def store_from_register(self, reg, dest):
        loc = self.get_location(dest)
        if loc.startswith('['):
            self.emit(f"str {reg}, {loc}")
        else:
            if loc != reg:
                self.emit(f"mov {loc}, {reg}")

    def reset_function_state(self):
        self.var_locations = {}
        self.stack_offset = 0
        self.reg_index = 0
        self.param_count = 0
        self.used_callee_saved_regs = set()
        self.max_stack_used = 0
        self.stack_vars = []

    # -------------------------
    # GERAÇÃO
    # -------------------------
    def generate(self, c3e_instructions):
        self.emit_comment("Código gerado pelo compilador GigaPar2025")
        self.emit_comment("Arquitetura: ARMv7")
        self.asm_code.append("")

        for instr in c3e_instructions:
            self.process_instruction(instr)

        return self.assemble_final_code()

    def process_instruction(self, instr):
        parts = instr.strip().split()
        if not parts: 
            return

        if instr.endswith(':'):
            self.emit_label(instr.rstrip(':'))
            return

        if '=' in instr and not any(x in instr for x in ['==','!=','<=','>=']):
            self.handle_assignment(instr)
            return

        if parts[0] == "if_false": 
            self.handle_if_false(parts)
            return
        if parts[0] == "goto": 
            self.handle_goto(parts)
            return
        if parts[0] == "param": 
            self.handle_param(parts)
            return
        if "call" in instr and '=' in instr: 
            self.handle_call(instr)
            return
        if parts[0] == "begin_func": 
            self.handle_begin_func(instr)
            return
        if parts[0] == "end_func": 
            self.handle_end_func()
            return
        if parts[0] == "get_param": 
            self.handle_get_param(parts)
            return
        if parts[0] == "return": 
            self.handle_return(parts)
            return
        if parts[0] == "send": 
            self.handle_send(instr)
            return
        if parts[0] == "receive": 
            self.handle_receive(instr)
            return
        if "BEGIN PARALLEL" in instr: 
            self.emit_comment("INÍCIO DE BLOCO PARALELO")
            return
        if "END PARALLEL" in instr: 
            self.emit_comment("FIM DE BLOCO PARALELO")
            return

        self.emit_comment(f"Instrução C3E não reconhecida: {instr}")

    # -------------------------
    # HANDLERS
    # -------------------------
    def handle_assignment(self, instr):
        left, right = instr.split('=',1)
        dest = left.strip()
        right = right.strip()

        # Operadores aritméticos
        for op in ['+', '-', '*', '/']:
            if op in right:
                lhs, rhs = right.split(op)
                lhs = lhs.strip()
                rhs = rhs.strip()
                self.load_to_register(lhs, 'r0')
                self.load_to_register(rhs, 'r1')
                if op == '+':
                    self.emit("add r0, r0, r1")
                elif op == '-':
                    self.emit("sub r0, r0, r1")
                elif op == '*':
                    self.emit("mul r0, r0, r1")
                elif op == '/':
                    # Divisão segura sem udiv
                    div_label = f".L_div_{len(self.asm_code)}"
                    done_label = f".L_div_done_{len(self.asm_code)}"
                    self.emit("mov r2, #0")       # quociente
                    self.emit(f"{div_label}:")
                    self.emit("cmp r0, r1")
                    self.emit(f"blt {done_label}")
                    self.emit("sub r0, r0, r1")
                    self.emit("add r2, r2, #1")
                    self.emit(f"b {div_label}")
                    self.emit(f"{done_label}:")
                    self.emit("mov r0, r2")
                self.store_from_register('r0', dest)
                return

        # Comparações lógicas: <,>,<=,>=,==,!=
        for op in ['<', '>', '<=', '>=', '==', '!=']:
            if op in right:
                lhs, rhs = right.split(op)
                lhs = lhs.strip()
                rhs = rhs.strip()
                self.load_to_register(lhs, 'r0')
                self.load_to_register(rhs, 'r1')
                true_label = f".L_true_{len(self.asm_code)}"
                done_label = f".L_done_{len(self.asm_code)}"
                self.emit(f"cmp r0, r1")
                if op == '<':
                    self.emit(f"movlt r0, #1")
                    self.emit(f"movge r0, #0")
                elif op == '>':
                    self.emit(f"movgt r0, #1")
                    self.emit(f"movle r0, #0")
                elif op == '<=':
                    self.emit(f"movle r0, #1")
                    self.emit(f"movgt r0, #0")
                elif op == '>=':
                    self.emit(f"movge r0, #1")
                    self.emit(f"movlt r0, #0")
                elif op == '==':
                    self.emit(f"moveq r0, #1")
                    self.emit(f"movne r0, #0")
                elif op == '!=':
                    self.emit(f"movne r0, #1")
                    self.emit(f"moveq r0, #0")
                self.store_from_register('r0', dest)
                return

        # Atribuição direta
        self.load_to_register(right, 'r0')
        self.store_from_register('r0', dest)

    def handle_if_false(self, parts):
        cond, label = parts[1], parts[3]
        self.load_to_register(cond, 'r0')
        self.emit("cmp r0, #0")
        self.emit(f"beq {label}")

    def handle_goto(self, parts):
        label = parts[1]
        self.emit(f"b {label}")

    def handle_param(self, parts):
        if len(parts) >= 2:
            self.allocate_stack_var(parts[1])

    def handle_call(self, instr):
        left, right = instr.split('=',1)
        result = left.strip()
        parts = right.strip().split()
        func_name = parts[1].rstrip(',')
        self.param_count = 0
        self.emit(f"bl {func_name}")
        if result != '_':
            self.store_from_register('r0', result)

    def handle_begin_func(self, instr):
        parts = instr.strip().split()
        func_name = f"func_{self.function_counter}"
        if len(parts) >= 2:
            func_name = parts[1]
        self.current_function = func_name
        self.emit_label(func_name)
        self.reset_function_state()
        self.emit("push {fp, lr}")
        self.emit("mov fp, sp")
        self.emit("sub sp, sp, #256")
        self.emit_comment(f"Stack frame para {func_name}")

    def handle_end_func(self):
        self.emit("add sp, sp, #256")
        self.emit("pop {fp, pc}")
        self.current_function = None

    def handle_get_param(self, parts):
        if len(parts) >= 2:
            self.allocate_stack_var(parts[1])

    def handle_return(self, parts):
        if len(parts) > 1:
            self.load_to_register(parts[1], 'r0')
        self.emit("b .return_exit")

    def handle_send(self, instr):
        self.emit_comment(f"Operação de envio: {instr}")
        self.emit("nop")

    def handle_receive(self, instr):
        self.emit_comment(f"Operação de recepção: {instr}")
        parts = instr.replace(',', '').split()
        for var in parts[2:]:
            self.allocate_stack_var(var)

    # -------------------------
    # MONTAGEM FINAL
    # -------------------------
    def assemble_final_code(self):
        final_code = []
        final_code.append('.arch armv7-a')
        final_code.append('.arm')
        final_code.append('')
        if self.data_section:
            final_code.append('.section .data')
            final_code.extend(self.data_section)
            final_code.append('')
        final_code.append('.section .text')
        final_code.append('.global _start')
        final_code.append('.global main')
        final_code.append('')
        final_code.append('_start:')
        final_code.append('    ldr sp, =0x8000')
        final_code.append('    bl main')
        final_code.append('    mov r0, #0')
        final_code.append('    mov r7, #1')
        final_code.append('    svc 0')
        final_code.append('')
        final_code.append('.return_exit:')
        final_code.append('    mov sp, fp')
        final_code.append('    pop {fp, pc}')
        final_code.append('')
        final_code.extend(self.asm_code)
        return "\n".join(final_code)
