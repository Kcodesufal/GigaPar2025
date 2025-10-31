import re

class AssemblyGenerator:
    """
    Gera código Assembly ARMv7 a partir de Código de 3 Endereços (C3E).
    Suporte a:
      - Loops, comparações, funções
      - Comparações de strings reais
      - Send/Receive de canais (aloca variáveis, nop)
      - Declaração de canais como comentários
      - Diferenciação básica entre int e float (literals) com pool .double e instruções VFP
    """

    FLOAT_RE = re.compile(r"^-?\d+\.\d+([eE][+-]?\d+)?$")
    INT_RE = re.compile(r"^-?\d+$")

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
        self.string_compare_label = "strcmp_func"

        self.temp_registers = ['r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10']
        self.used_callee_saved_regs = set()
        self.reg_index = 0
        self.param_registers = ['r0', 'r1', 'r2', 'r3']
        self.param_count = 0
        self.max_stack_used = 0
        self.stack_vars = []

        # Float constants pool: normalized_value_str -> label
        self.float_consts = {}
        self.float_counter = 0

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

    def is_float_literal(self, tok):
        if not isinstance(tok, str):
            return isinstance(tok, float)
        return bool(self.FLOAT_RE.match(tok))

    def _normalize_float_str(self, s):
        s = str(s)
        if self.INT_RE.match(s):
            return s + ".0"
        # already float-like or contains decimal/exponent
        return s

    def get_float_label(self, value_str):
        # normalize value_str to stable representation (ex: "2" -> "2.0")
        s = self._normalize_float_str(value_str)
        if s not in self.float_consts:
            lbl = f".LCF{self.float_counter}"
            self.float_counter += 1
            self.float_consts[s] = lbl
            # store as double in data section
            self.data_section.append(f"{lbl}: .double {s}")
        return self.float_consts[s]

    def get_location(self, operand):
        """
        Retorna:
          - '#<int>' para inteiros/imediatos
          - '.STRn' para strings (label)
          - '.LCFn' para literais float (label)
          - '[fp, #offset]' para variáveis alocadas
        """
        if isinstance(operand, str):
            clean_operand = operand.lstrip('-').replace('.', '', 1)
            if self.is_float_literal(operand):
                return self.get_float_label(operand)
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
            if isinstance(operand, float):
                return self.get_float_label(str(operand))
            return f"#{int(operand)}"
        raise ValueError(f"Operando não suportado: {operand}")

    def add_string_literal(self, string_value):
        label = f".STR{self.string_counter}"
        self.string_counter += 1
        clean_string = string_value.strip('"')
        self.data_section.append(f"{label}: .asciz \"{clean_string}\"")
        return label

    def reg_to_dreg(self, reg):
        # mapeia r0->d0, r1->d1, r2->d2, r3->d3, r4->d4 etc.
        m = re.match(r"r(\d+)$", reg)
        if m:
            idx = int(m.group(1))
            return f"d{idx}"
        # se já for um d-reg, retorna direto
        if re.match(r"d\d+$", reg):
            return reg
        # fallback
        return "d0"

    # --- Helper: carrega double via 32-bit literal load + vldr [tmp] ---
    def _load_double_via_ldr(self, label, dreg, tmp_reg="r12"):
        # usa ldr tmp_reg, =label  ; vldr dreg, [tmp_reg]
        # evita pseudo-instrução `vldr dX, =label` que causa "invalid type for literal pool"
        self.emit(f"ldr {tmp_reg}, ={label}")
        self.emit(f"vldr {dreg}, [{tmp_reg}]")

    def load_to_register(self, operand, reg):
        """
        Carrega operand para reg.
        reg pode ser um registrador inteiro (r0..) ou VFP (d0..).
        Se operand for float literal, usa pool .double e carregamento seguro.
        """
        loc = None
        if isinstance(operand, str) and (operand.startswith(".LCF") or operand.startswith(".STR") or operand.startswith("[")):
            loc = operand
        else:
            loc = self.get_location(operand)

        # destino VFP (d-reg)
        if reg.startswith('d'):
            if loc.startswith('.LCF'):
                # carregar double usando helper seguro
                self._load_double_via_ldr(loc, reg)
            elif loc.startswith('['):
                # load double from memory (stack variable)
                self.emit(f"vldr {reg}, {loc}")
            elif loc.startswith('#'):
                # imediato inteiro -> criar constant double e carregar
                val = loc.lstrip('#')
                lbl = self.get_float_label(f"{val}.0")
                self._load_double_via_ldr(lbl, reg)
            elif loc.startswith('.STR'):
                # não faz sentido carregar string para float/reg; carregar endereço em r12 e deixar comentário
                self.emit(f"ldr r12, ={loc}")
                self.emit_comment(f"carregado endereço de string {loc} em r12; conversão para float não implementada")
            else:
                # possivelmente já um label -> usar helper
                self._load_double_via_ldr(loc, reg)
            return

        # destino inteiro reg
        if loc.startswith('#'):
            self.emit(f"mov {reg}, {loc}")
        elif loc.startswith('.STR'):
            self.emit(f"ldr {reg}, ={loc}")
        elif loc.startswith('.LCF'):
            # carregar double para d-reg mapeado ao reg (sem conversão automática)
            dreg = self.reg_to_dreg(reg)
            self._load_double_via_ldr(loc, dreg)
            self.emit_comment(f"Nota: {loc} carregado em {dreg} (origem float); conversão explícita para inteiro não realizada")
        elif loc.startswith('['):
            self.emit(f"ldr {reg}, {loc}")
        else:
            # label into integer reg (address)
            self.emit(f"ldr {reg}, ={loc}")

    def store_from_register(self, reg, dest):
        """
        Armazena reg para dest. reg pode ser rX ou dX.
        dest tipicamente é uma pilha '[fp, #..]' ou rX (menos comum).
        """
        loc = self.get_location(dest)
        if reg.startswith('d'):
            # store double
            if loc.startswith('['):
                self.emit(f"vstr {reg}, {loc}")
            else:
                # se dest for label ou imediato, armazenar endereço não faz sentido; tentamos guardar endereço se for string
                if loc.startswith('.STR'):
                    # armazena endereço em r12 e depois (não usual) - fallback
                    self.emit(f"ldr r12, ={loc}")
                    self.emit(f"str r12, {loc}")
                else:
                    self.emit_comment(f"store_from_register: armazenamento float para {loc} não suportado diretamente")
            return

        # inteiro
        if loc.startswith('['):
            self.emit(f"str {reg}, {loc}")
        else:
            if loc != reg:
                if loc.startswith('.STR'):
                    self.emit(f"ldr r12, ={loc}")
                else:
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

        # Adiciona função de comparação de strings
        self.add_string_compare_func()

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

        if "channel_decl" in instr:
            self.handle_channel_decl(instr)
            return

        # Suporte a blocos paralelos e sequenciais como comentários
        if "BEGIN_PARALLEL" in instr:
            self.emit_comment("INÍCIO DE BLOCO PARALELO")
            return
        if "END_PARALLEL" in instr:
            self.emit_comment("FIM DE BLOCO PARALELO")
            return
        if "BEGIN_SEQUENCE" in instr:
            self.emit_comment("INÍCIO DE BLOCO SEQUENCIAL")
            return
        if "END_SEQUENCE" in instr:
            self.emit_comment("FIM DE BLOCO SEQUENCIAL")
            return

        self.emit_comment(f"Instrução C3E não reconhecida: {instr}")

    # -------------------------
    # HANDLERS
    # -------------------------
    def handle_assignment(self, instr):
        left, right = instr.split('=',1)
        dest = left.strip()
        right = right.strip()

        # Comparação de strings
        if '"' in right:
            # Se for uma comparação de strings "=="
            if '==' in right:
                lhs, rhs = right.split('==')
                lhs = lhs.strip()
                rhs = rhs.strip()
                lhs_loc = self.get_location(lhs)
                rhs_loc = self.get_location(rhs)
                dest_loc = self.allocate_stack_var(dest)
                self.emit_comment(f"Comparação de strings real: {lhs} == {rhs}")
                self.emit(f"ldr r0, ={lhs_loc}")
                self.emit(f"ldr r1, ={rhs_loc}")
                self.emit(f"ldr r2, ={dest_loc}")
                self.emit(f"bl {self.string_compare_label}")
                return
            else:
                # apenas atribuição de string
                self.load_to_register(right, 'r0')
                self.store_from_register('r0', dest)
                return

        # Expressão aritmética: detectar se há floats literais
        for op in ['+', '-', '*', '/']:
            if op in right:
                lhs, rhs = right.split(op,1)
                lhs = lhs.strip()
                rhs = rhs.strip()

                float_mode = self.is_float_literal(lhs) or self.is_float_literal(rhs)

                if float_mode:
                    # carregar ambos em d-regs (d0,d1)
                    self.load_to_register(lhs, 'd0')
                    # se rhs for inteiro literal, convertê-lo criando float constant
                    if self.is_float_literal(rhs):
                        self.load_to_register(rhs, 'd1')
                    else:
                        rhs_loc = self.get_location(rhs)
                        if isinstance(rhs_loc, str) and rhs_loc.startswith('#'):
                            val = rhs_loc.lstrip('#')
                            lbl = self.get_float_label(f"{val}.0")
                            self.load_to_register(lbl, 'd1')
                        else:
                            self.load_to_register(rhs, 'd1')

                    op_map = {'+': 'vadd.f64', '-': 'vsub.f64', '*': 'vmul.f64', '/': 'vdiv.f64'}
                    instr = op_map.get(op)
                    if not instr:
                        raise ValueError("op não suportada para float: " + op)
                    self.emit(f"{instr} d0, d0, d1")
                    self.store_from_register('d0', dest)
                else:
                    # inteiro, comportamento original
                    self.load_to_register(lhs, 'r0')
                    self.load_to_register(rhs, 'r1')
                    if op == '+':
                        self.emit("add r0, r0, r1")
                    elif op == '-':
                        self.emit("sub r0, r0, r1")
                    elif op == '*':
                        # ARM mul rd, rn, rm  -> rd = rn * rm (syntax varies); aqui usamos mul r0, r0, r1
                        self.emit("mul r0, r0, r1")
                    elif op == '/':
                        div_label = f".L_div_{len(self.asm_code)}"
                        done_label = f".L_div_done_{len(self.asm_code)}"
                        self.emit("mov r2, #0")
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

        # Comparações (inclui floats)
        for op in ['<', '>', '<=', '>=', '==', '!=']:
            if op in right:
                lhs, rhs = right.split(op,1)
                lhs = lhs.strip()
                rhs = rhs.strip()

                float_mode = self.is_float_literal(lhs) or self.is_float_literal(rhs)

                if float_mode:
                    # carregar em d0,d1
                    self.load_to_register(lhs, 'd0')
                    self.load_to_register(rhs, 'd1')
                    # comparar floats
                    self.emit("vcmp.f64 d0, d1")
                    self.emit("vmrs APSR_nzcv, FPSCR")
                    # usar mov condicional para resultado em r0
                    if op == '<':
                        self.emit("movlt r0, #1")
                        self.emit("movge r0, #0")
                    elif op == '>':
                        self.emit("movgt r0, #1")
                        self.emit("movle r0, #0")
                    elif op == '<=':
                        self.emit("movle r0, #1")
                        self.emit("movgt r0, #0")
                    elif op == '>=':
                        self.emit("movge r0, #1")
                        self.emit("movlt r0, #0")
                    elif op == '==':
                        self.emit("moveq r0, #1")
                        self.emit("movne r0, #0")
                    elif op == '!=':
                        self.emit("movne r0, #1")
                        self.emit("moveq r0, #0")
                    self.store_from_register('r0', dest)
                else:
                    # inteiro
                    self.load_to_register(lhs, 'r0')
                    self.load_to_register(rhs, 'r1')
                    self.emit("cmp r0, r1")
                    if op == '<':
                        self.emit("movlt r0, #1")
                        self.emit("movge r0, #0")
                    elif op == '>':
                        self.emit("movgt r0, #1")
                        self.emit("movle r0, #0")
                    elif op == '<=':
                        self.emit("movle r0, #1")
                        self.emit("movgt r0, #0")
                    elif op == '>=':
                        self.emit("movge r0, #1")
                        self.emit("movlt r0, #0")
                    elif op == '==':
                        self.emit("moveq r0, #1")
                        self.emit("movne r0, #0")
                    elif op == '!=':
                        self.emit("movne r0, #1")
                        self.emit("moveq r0, #0")
                    self.store_from_register('r0', dest)
                return

        # simples atribuição
        self.load_to_register(right, 'r0')
        self.store_from_register('r0', dest)

    def add_string_compare_func(self):
        self.emit_comment("Função strcmp_func: compara strings r0 e r1, resultado em r2")
        self.emit_label(self.string_compare_label)
        self.emit("push {r4, lr}")
        self.emit_label(f"{self.string_compare_label}_loop")
        self.emit("ldrb r3, [r0], #1")
        self.emit("ldrb r4, [r1], #1")
        self.emit("cmp r3, r4")
        self.emit(f"bne {self.string_compare_label}_false")
        self.emit("cmp r3, #0")
        self.emit(f"beq {self.string_compare_label}_true")
        self.emit(f"b {self.string_compare_label}_loop")
        self.emit_label(f"{self.string_compare_label}_false")
        self.emit("mov r3, #0")
        self.emit("str r3, [r2]")
        self.emit(f"b {self.string_compare_label}_end")
        self.emit_label(f"{self.string_compare_label}_true")
        self.emit("mov r3, #1")
        self.emit("str r3, [r2]")
        self.emit_label(f"{self.string_compare_label}_end")
        self.emit("pop {r4, lr}")
        self.emit("bx lr")

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
        parts = instr.replace(',', '').split()
        for var in parts[1:]:
            self.allocate_stack_var(var)
        self.emit("nop")

    def handle_receive(self, instr):
        self.emit_comment(f"Operação de recepção: {instr}")
        parts = instr.replace(',', '').split()
        for var in parts[2:]:
            self.allocate_stack_var(var)
        self.emit("nop")

    def handle_channel_decl(self, instr):
        self.emit_comment(f"Declaração de canal ignorada: {instr}")

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
        final_code.append('    b .')
        final_code.append('')
        final_code.append('.return_exit:')
        final_code.append('    mov sp, fp')
        final_code.append('    pop {fp, pc}')
        final_code.append('')
        final_code.extend(self.asm_code)
        return "\n".join(final_code)