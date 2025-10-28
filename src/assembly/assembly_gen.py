class AssemblyGenerator:
    """
    Gera código Assembly ARMv7 a partir de Código de 3 Endereços (C3E).
    Versão unificada com correções para SP, callee-saved regs, receive
    e integração com otimizador. Usa syscall 'exit' (swi 0).
    """

    def __init__(self):
        self.asm_code = []
        self.data_section = []
        self.var_locations = {}
        self.stack_offset = 0 # Offset para alocação DEPOIS dos params/callee-saved
        self.string_counter = 0
        self.channels = {}
        
        self.stack_pushes = 0 # Contador para limpar 'param'
        self.used_callee_saved_regs = set() # Rastreia r4-r11 usados

        self.temp_registers = ['r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11']
        self.reg_index = 0
        self.param_registers = ['r0', 'r1', 'r2', 'r3']

    # ============================================
    # MÉTODOS UTILITÁRIOS
    # ============================================
    def emit(self, instruction):
        self.asm_code.append(f"    {instruction}")

    def emit_label(self, label):
        self.asm_code.append(f"{label}:")

    def emit_comment(self, comment):
        self.asm_code.append(f"    @ {comment}")

    def allocate_register(self, var_name):
        """Aloca um registrador (r4-r11) ou espaço na pilha."""
        if var_name not in self.var_locations:
            if self.reg_index < len(self.temp_registers):
                reg = self.temp_registers[self.reg_index]
                self.var_locations[var_name] = reg
                self.reg_index += 1
                self.used_callee_saved_regs.add(reg) # Marca para push/pop
            else:
                self.stack_offset += 4
                current_total_offset = self.stack_pushes * 4 + len(self.used_callee_saved_regs) * 4 + self.stack_offset
                self.var_locations[var_name] = f"[sp, #{current_total_offset}]"
                self.emit_comment(f"Spilling {var_name} to {self.var_locations[var_name]}")

        return self.var_locations[var_name]


    def get_location(self, operand):
        """Retorna a localização (imediato, registrador, ou pilha [sp, #offset])."""
        if isinstance(operand, str) and operand.lstrip('-').replace('.', '', 1).isdigit():
            return f"#{operand}"
        if isinstance(operand, (int, float)): # Se for número diretamente
             return f"#{int(operand)}"

        # Se for variável (inclui temporárias tX)
        if isinstance(operand, str):
            if operand in self.var_locations:
                return self.var_locations[operand]
            else:
                # Aloca na pilha se não existir (deveria ser raro se C3E está correto)
                self.emit_comment(f"Variável '{operand}' não encontrada, alocando na pilha...")
                return self.allocate_register(operand) # Reusa a lógica de alocação

        raise ValueError(f"Tipo de operando não suportado: {operand}")


    def add_string_literal(self, string_value):
        label = f".STR{self.string_counter}"
        self.string_counter += 1
        clean_string = string_value.strip('"')
        self.data_section.append(f'{label}: .asciz "{clean_string}"')
        return label

    def load_to_register(self, operand, register):
        loc = self.get_location(operand)
        if loc.startswith('#'):
            value = int(loc[1:])
            if -256 <= value <= 255 or (0 <= value <= 65535):
                 self.emit(f"mov {register}, #{value}") # Correção: Adicionar #
            else:
                self.emit(f"movw {register}, #{value & 0xFFFF}")
                if value > 65535:
                    self.emit(f"movt {register}, #{(value >> 16) & 0xFFFF}")
        elif loc.startswith('['):
            self.emit(f"ldr {register}, {loc}")
        else: # É um registrador
            if loc != register:
                self.emit(f"mov {register}, {loc}")

    def store_from_register(self, register, dest_var_name):
        # Destino é sempre um nome de variável que mapeamos para localização
        loc = self.get_location(dest_var_name)
        if loc.startswith('['):
            self.emit(f"str {register}, {loc}")
        else: # Destino é um registrador
            if loc != register:
                self.emit(f"mov {loc}, {register}")

    # ============================================
    # GERAÇÃO PRINCIPAL
    # ============================================
    def generate(self, c3e_instructions):
        self.emit_comment("Código gerado pelo compilador GigaPar2025")
        self.emit_comment("Arquitetura: ARMv7")
        self.asm_code.append("")
        for instruction in c3e_instructions:
            self.process_instruction(instruction)
        return self.assemble_final_code()

    def process_instruction(self, instruction):
        parts = instruction.strip().split()
        if not parts: return
        if parts[0].startswith('#'): self.emit_comment(' '.join(parts[1:])); return
        if parts[0] == "channel_decl": self.handle_channel_decl(instruction); return
        if '=' in instruction and not any(x in instruction for x in ['==', '!=', '<=', '>=']): self.handle_assignment(instruction); return
        if parts[0] == "if_false": self.handle_if_false(parts); return
        if parts[0] == "goto": self.handle_goto(parts); return
        if instruction.endswith(':'): self.emit_label(instruction.rstrip(':')); return
        if parts[0] == "param": self.handle_param(parts); return
        if "call" in instruction and '=' in instruction: self.handle_call(instruction); return
        if parts[0] == "begin_func": self.handle_begin_func(); return
        if parts[0] == "end_func": self.handle_end_func(); return
        if parts[0] == "get_param": self.handle_get_param(parts); return
        if parts[0] == "return": self.handle_return(parts); return
        if parts[0] == "send": self.handle_send(instruction); return
        if parts[0] == "receive": self.handle_receive(instruction); return
        if "BEGIN PARALLEL" in instruction: self.emit_comment("INÍCIO DE BLOCO PARALELO"); return
        if "END PARALLEL" in instruction: self.emit_comment("FIM DE BLOCO PARALELO"); return
        # Fallback para instrução não reconhecida
        self.emit_comment(f"Instrução C3E não reconhecida: {instruction}")
        self.emit(f"nop @ {instruction}")


    # ============================================
    # HANDLERS
    # ============================================
    def handle_channel_decl(self, instruction):
        parts = instruction.replace(',', '').split()
        if len(parts) >= 4:
            channel_name, comp1, comp2 = parts[1], parts[2], parts[3]
            self.channels[channel_name] = {'comp1': comp1, 'comp2': comp2}
            self.emit_comment(f"Canal declarado: {channel_name} entre {comp1} e {comp2}")

    def handle_assignment(self, instruction):
        left, right = instruction.split('=', 1)
        dest = left.strip()
        right = right.strip()
        if any(op in right for op in [' + ', ' - ', ' * ', ' / ', ' == ', ' != ', ' < ', ' > ', ' <= ', ' >= ', ' and ', ' or ']):
            self.handle_binary_op(dest, right)
        elif right.startswith('not ') or right.startswith('- '):
            self.handle_unary_op(dest, right)
        else: # Atribuição simples: dest = operand
            # Usamos r0 como registrador intermediário
            self.load_to_register(right, 'r0')
            self.store_from_register('r0', dest)

    def handle_binary_op(self, dest, expr):
        operators = [' + ', ' - ', ' * ', ' / ', ' == ', ' != ', ' < ', ' > ', ' <= ', ' >= ', ' and ', ' or ']
        op = None
        for operator in operators:
             if operator in expr:
                 op = operator.strip()
                 left, right = expr.split(operator, 1)
                 break
        if not op: return
        left = left.strip()
        right = right.strip()

        self.load_to_register(left, 'r0')
        self.load_to_register(right, 'r1')
        if op == '+': self.emit("add r0, r0, r1")
        elif op == '-': self.emit("sub r0, r0, r1")
        elif op == '*': self.emit("mul r0, r0, r1")
        elif op == '/': self.emit("sdiv r0, r0, r1")
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            self.emit("cmp r0, r1")
            if op == '==': self.emit("moveq r0, #1"); self.emit("movne r0, #0")
            elif op == '!=': self.emit("movne r0, #1"); self.emit("moveq r0, #0")
            elif op == '<': self.emit("movlt r0, #1"); self.emit("movge r0, #0")
            elif op == '>': self.emit("movgt r0, #1"); self.emit("movle r0, #0")
            elif op == '<=': self.emit("movle r0, #1"); self.emit("movgt r0, #0")
            elif op == '>=': self.emit("movge r0, #1"); self.emit("movlt r0, #0")
        elif op == 'and': self.emit("and r0, r0, r1")
        elif op == 'or': self.emit("orr r0, r0, r1")

        self.store_from_register('r0', dest)

    def handle_unary_op(self, dest, expr):
        if expr.startswith('not '):
            operand = expr[4:].strip()
            self.load_to_register(operand, 'r0')
            self.emit("mvn r0, r0")
            self.store_from_register('r0', dest)
        elif expr.startswith('- '):
            operand = expr[2:].strip()
            self.load_to_register(operand, 'r0')
            self.emit("rsb r0, r0, #0")
            self.store_from_register('r0', dest)

    def handle_if_false(self, parts):
        condition = parts[1]; label = parts[3]
        self.load_to_register(condition, 'r0')
        self.emit("cmp r0, #0")
        self.emit(f"beq {label}")

    def handle_goto(self, parts):
        label = parts[1]
        self.emit(f"b {label}")

    def handle_param(self, parts):
        """Prepara parâmetro C3E 'param value'."""
        param = parts[1]
        self.load_to_register(param, 'r0')
        self.emit("push {r0}")
        self.stack_pushes += 1 # Conta push para limpar depois

    def handle_call(self, instruction):
        """Gera C3E 'result = call func, n'."""
        left, right = instruction.split('=', 1)
        result = left.strip()
        parts = right.strip().split()
        func_name = parts[1].rstrip(',')
        n_args = int(parts[2])
        self.emit(f"bl {func_name}")
        if n_args > 0:
            self.emit(f"add sp, sp, #{n_args * 4}")
            # Desconta os pushes que a chamada limpou
            self.stack_pushes -= n_args
        self.store_from_register('r0', result) # Resultado da função está em r0

    def handle_begin_func(self): self.emit("push {fp, lr}"); self.emit("mov fp, sp")
    def handle_end_func(self): self.emit("mov sp, fp"); self.emit("pop {fp, pc}")
    def handle_get_param(self, parts): param_name = parts[1]; self.emit(f"ldr r0, [fp, #8]"); self.store_from_register('r0', param_name)
    def handle_return(self, parts):
        if len(parts) > 1: self.load_to_register(parts[1], 'r0')
        pass # Deixa a execução cair para o epílogo no assemble_final_code

    def handle_send(self, instruction):
        # Mantém como NOP por enquanto, focar no receive/cálculos
        self.emit_comment(f"Operação de envio (NOP): {instruction}")
        self.emit("nop  @ send operation")

    def handle_receive(self, instruction):
        """Trata C3E 'receive channel, var1, var2, ...' mapeando para a pilha."""
        self.emit_comment(f"Operação de recepção: {instruction}")
        parts = instruction.replace(',', '').split()
        
        if len(parts) < 2: return # Precisa do canal e pelo menos uma var
            
        var_names = parts[2:] # Pega 'a', 'b', 'c', ...
        
        base_offset_params = 0 # Offset relativo ao SP *atual*
        for i, var in enumerate(var_names):
            offset = base_offset_params + i * 4
            # Define a localização da variável
            self.var_locations[var] = f'[sp, #{offset}]'
            self.emit(f"@ Var '{var}' mapeada para {self.var_locations[var]} (valor do param {len(var_names)-i})")

        new_base_offset_for_temps = len(var_names) * 4
        if new_base_offset_for_temps > self.stack_offset:
             self.stack_offset = new_base_offset_for_temps
             self.emit(f"@ Próximo offset de pilha para temporários: {self.stack_offset}")


    # ============================================
    # MONTAGEM FINAL
    # ============================================
    def assemble_final_code(self):
        from .optimizer import AssemblyOptimizer
        optimizer = AssemblyOptimizer()
        
        final_code = []

        # Diretivas ARM
        final_code.append('.arch armv7-a')
        final_code.append('.arm')
        final_code.append('')

        # Seção .data
        if self.data_section:
            final_code.append('.section .data')
            final_code.extend(self.data_section)
            final_code.append('')

        # Seção .text
        final_code.append('.section .text')
        final_code.append('.global _start')
        final_code.append('')
        
        final_code.append('_start:')
        final_code.append('    @ Ponto de entrada do programa')
        final_code.append('    ldr sp, =0x7000    @ Inicializa SP (topo da pilha)')
        final_code.append('')
        final_code.append('    bl main')
        final_code.append('')
        final_code.append('    @ Exit syscall (ARM Linux) - CPUlator deve interceptar')
        final_code.append('    mov r0, #0         @ Código de saída 0 (sucesso)')
        final_code.append('    mov r7, #1         @ Syscall número 1 (exit)')
        final_code.append('    swi 0              @ Software Interrupt')
        final_code.append('    b .                @ Loop de segurança se SWI não parar') # Segurança
        final_code.append('')

        # Código da 'main'
        final_code.append('main:')
        if self.used_callee_saved_regs:
            # Ordena para consistência (push {r4, r5} vs push {r5, r4})
            sorted_regs = sorted(list(self.used_callee_saved_regs))
            final_code.append(f"    push {{{', '.join(sorted_regs)}}}    @ Salva regs callee-saved (r4-r11)")

        # Otimiza e adiciona o código gerado da main
        optimized_code = optimizer.optimize(self.asm_code)
        final_code.extend(optimized_code) # Adiciona instruções otimizadas

        final_code.append('')
        # 1. Limpa a pilha dos 'param' que não foram limpos por 'call'
        final_code.append('    @ Epílogo: Restaura pilha e registradores')
        if self.stack_pushes > 0:
            final_code.append(f'    add sp, sp, #{self.stack_pushes * 4}  @ Limpa {self.stack_pushes} param(s) da pilha')
        # 2. Restaura registradores callee-saved
        if self.used_callee_saved_regs:
            sorted_regs = sorted(list(self.used_callee_saved_regs))
            final_code.append(f"    pop {{{', '.join(sorted_regs)}}}     @ Restaura regs callee-saved")

        # Retorno padrão da main
        final_code.append('    mov r0, #0         @ Retorno padrão da main (convenção C)')
        final_code.append('    bx lr              @ Retorna para _start')

        return "\n".join(final_code)