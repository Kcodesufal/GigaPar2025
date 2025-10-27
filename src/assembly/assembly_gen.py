class AssemblyGenerator:
    """
    Gera código Assembly ARMv7 a partir de Código de 3 Endereços (C3E).
    """

    def __init__(self):
        self.asm_code = []  # Lista de instruções assembly
        self.data_section = []  # Seção .data (strings, constantes)
        self.var_locations = {}  # Mapa: variável -> localização (registrador ou memória)
        self.stack_offset = 0  # Offset atual na pilha
        self.string_counter = 0  # Contador para labels de strings
        self.channels = {}  # Informações sobre canais declarados

        # Registradores disponíveis para variáveis temporárias
        # ARMv7: r4-r11 são preservados (callee-saved)
        self.temp_registers = ['r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11']
        self.reg_index = 0

        # Registradores para parâmetros (primeiros 4 parâmetros)
        # ARMv7 AAPCS: r0-r3 para argumentos
        self.param_registers = ['r0', 'r1', 'r2', 'r3']

    # ============================================
    # MÉTODOS UTILITÁRIOS
    # ============================================
    def emit(self, instruction):
        """Adiciona uma instrução assembly."""
        self.asm_code.append(f"    {instruction}")

    def emit_label(self, label):
        """Adiciona um label."""
        self.asm_code.append(f"{label}:")

    def emit_comment(self, comment):
        """Adiciona um comentário."""
        self.asm_code.append(f"    @ {comment}")

    def allocate_register(self, var_name):
        """Aloca um registrador para uma variável temporária."""
        if var_name not in self.var_locations:
            if self.reg_index < len(self.temp_registers):
                reg = self.temp_registers[self.reg_index]
                self.var_locations[var_name] = reg
                self.reg_index += 1
            else:
                # Se acabaram os registradores, usa a pilha (spilling)
                self.stack_offset += 4  # ARM usa palavras de 4 bytes
                self.var_locations[var_name] = f"[sp, #{self.stack_offset}]"
        return self.var_locations[var_name]

    def get_location(self, operand):
        """Retorna a localização de um operando (registrador, memória ou imediato)."""
        # Se for número literal
        if operand.lstrip('-').replace('.', '', 1).isdigit():
            return f"#{operand}"

        # Se for variável temporária (t0, t1, ...)
        if operand.startswith('t') and operand[1:].isdigit():
            return self.allocate_register(operand)

        # Se for variável regular
        if operand in self.var_locations:
            return self.var_locations[operand]

        # Aloca na pilha se não existir
        self.stack_offset += 4
        self.var_locations[operand] = f"[sp, #{self.stack_offset}]"
        return self.var_locations[operand]

    def add_string_literal(self, string_value):
        """Adiciona uma string literal na seção .data."""
        label = f".STR{self.string_counter}"
        self.string_counter += 1
        # Remove aspas da string
        clean_string = string_value.strip('"')
        self.data_section.append(f'{label}: .asciz "{clean_string}"')
        return label

    def load_to_register(self, operand, register):
        """Carrega um operando para um registrador."""
        loc = self.get_location(operand)

        if loc.startswith('#'):  # Imediato
            # Verifica se o imediato cabe em uma instrução MOV
            value = int(loc[1:])
            if -256 <= value <= 255 or (0 <= value <= 65535):
                self.emit(f"mov {register}, {loc}")
            else:
                # Usa movw/movt para valores maiores
                self.emit(f"movw {register}, #{value & 0xFFFF}")
                if value > 65535:
                    self.emit(f"movt {register}, #{(value >> 16) & 0xFFFF}")
        elif loc.startswith('['):  # Memória (pilha)
            self.emit(f"ldr {register}, {loc}")
        else:  # Registrador
            if loc != register:
                self.emit(f"mov {register}, {loc}")

    def store_from_register(self, register, dest):
        """Armazena de um registrador para destino."""
        loc = self.get_location(dest)

        if loc.startswith('['):  # Memória (pilha)
            self.emit(f"str {register}, {loc}")
        else:  # Registrador
            if loc != register:
                self.emit(f"mov {loc}, {register}")

    # ============================================
    # GERAÇÃO PRINCIPAL
    # ============================================
    def generate(self, c3e_instructions):
        """Ponto de entrada: gera assembly a partir das instruções C3E."""
        self.emit_comment("Código gerado pelo compilador GigaPar2025")
        self.emit_comment("Arquitetura: ARMv7")
        self.asm_code.append("")

        # Processa cada instrução C3E
        for instruction in c3e_instructions:
            self.process_instruction(instruction)

        # Monta o código final
        return self.assemble_final_code()

    def process_instruction(self, instruction):
        """Processa uma instrução C3E e gera assembly correspondente."""
        parts = instruction.strip().split()

        if not parts:
            return

        # Comentários
        if parts[0].startswith('#'):
            self.emit_comment(' '.join(parts[1:]))
            return

        # Declaração de canal
        if parts[0] == "channel_decl":
            self.handle_channel_decl(instruction)

        # Atribuições (var = expr)
        elif '=' in instruction and not any(x in instruction for x in ['==', '!=', '<=', '>=']):
            self.handle_assignment(instruction)

        # Desvios condicionais
        elif parts[0] == "if_false":
            self.handle_if_false(parts)

        # Saltos incondicionais
        elif parts[0] == "goto":
            self.handle_goto(parts)

        # Labels
        elif instruction.endswith(':'):
            self.emit_label(instruction.rstrip(':'))

        # Chamadas de função
        elif parts[0] == "param":
            self.handle_param(parts)
        elif "call" in instruction and '=' in instruction:
            self.handle_call(instruction)

        # Funções
        elif parts[0] == "begin_func":
            self.handle_begin_func()
        elif parts[0] == "end_func":
            self.handle_end_func()
        elif parts[0] == "get_param":
            self.handle_get_param(parts)
        elif parts[0] == "return":
            self.handle_return(parts)

        # Operações de canal
        elif parts[0] == "send":
            self.handle_send(instruction)
        elif parts[0] == "receive":
            self.handle_receive(instruction)

        # BEGIN/END parallel blocks
        elif "BEGIN PARALLEL" in instruction:
            self.emit_comment("INÍCIO DE BLOCO PARALELO")
        elif "END PARALLEL" in instruction:
            self.emit_comment("FIM DE BLOCO PARALELO")

    # ============================================
    # HANDLERS PARA DIFERENTES INSTRUÇÕES
    # ============================================
    def handle_channel_decl(self, instruction):
        """Declara um canal de comunicação."""
        # Formato: channel_decl canal, comp1, comp2
        parts = instruction.replace(',', '').split()
        if len(parts) >= 4:
            channel_name = parts[1]
            comp1 = parts[2]
            comp2 = parts[3]
            self.channels[channel_name] = {'comp1': comp1, 'comp2': comp2}
            self.emit_comment(f"Canal declarado: {channel_name} entre {comp1} e {comp2}")

    def handle_assignment(self, instruction):
        """Gera código para atribuições."""
        # Formato: dest = operand1 op operand2  OU  dest = operand
        left, right = instruction.split('=', 1)
        dest = left.strip()
        right = right.strip()

        # Operações binárias
        if any(op in right for op in
               [' + ', ' - ', ' * ', ' / ', ' == ', ' != ', ' < ', ' > ', ' <= ', ' >= ', ' and ', ' or ']):
            self.handle_binary_op(dest, right)

        # Operações unárias
        elif right.startswith('not ') or right.startswith('- '):
            self.handle_unary_op(dest, right)

        # Atribuição simples
        else:
            self.load_to_register(right, 'r0')
            self.store_from_register('r0', dest)

    def handle_binary_op(self, dest, expr):
        """Gera código para operações binárias."""
        # Detecta o operador
        operators = [' + ', ' - ', ' * ', ' / ', ' == ', ' != ', ' < ', ' > ', ' <= ', ' >= ', ' and ', ' or ']
        op = None
        for operator in operators:
            if operator in expr:
                op = operator.strip()
                left, right = expr.split(operator, 1)
                break

        if not op:
            return

        left = left.strip()
        right = right.strip()

        # Carrega operandos
        self.load_to_register(left, 'r0')
        self.load_to_register(right, 'r1')

        # Executa operação
        if op == '+':
            self.emit("add r0, r0, r1")
        elif op == '-':
            self.emit("sub r0, r0, r1")
        elif op == '*':
            self.emit("mul r0, r0, r1")
        elif op == '/':
            # Divisão em ARM requer chamada de função ou instrução SDIV (ARMv7-A)
            self.emit("sdiv r0, r0, r1")
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            self.emit("cmp r0, r1")
            if op == '==':
                self.emit("moveq r0, #1")
                self.emit("movne r0, #0")
            elif op == '!=':
                self.emit("movne r0, #1")
                self.emit("moveq r0, #0")
            elif op == '<':
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
        elif op == 'and':
            self.emit("and r0, r0, r1")
        elif op == 'or':
            self.emit("orr r0, r0, r1")

        # Salva resultado
        self.store_from_register('r0', dest)

    def handle_unary_op(self, dest, expr):
        """Gera código para operações unárias."""
        if expr.startswith('not '):
            operand = expr[4:].strip()
            self.load_to_register(operand, 'r0')
            self.emit("mvn r0, r0")  # MVN = bitwise NOT
            self.store_from_register('r0', dest)
        elif expr.startswith('- '):
            operand = expr[2:].strip()
            self.load_to_register(operand, 'r0')
            self.emit("rsb r0, r0, #0")  # RSB = reverse subtract (0 - r0)
            self.store_from_register('r0', dest)

    def handle_if_false(self, parts):
        """Gera código para desvio condicional."""
        # Formato: if_false condition goto label
        condition = parts[1]
        label = parts[3]

        self.load_to_register(condition, 'r0')
        self.emit("cmp r0, #0")
        self.emit(f"beq {label}")

    def handle_goto(self, parts):
        """Gera código para salto incondicional."""
        label = parts[1]
        self.emit(f"b {label}")

    def handle_param(self, parts):
        """Prepara parâmetro para chamada de função (empilha)."""
        param = parts[1]
        self.load_to_register(param, 'r0')
        self.emit("push {r0}")

    def handle_call(self, instruction):
        """Gera código para chamada de função."""
        # Formato: result = call func_name, n_args
        left, right = instruction.split('=', 1)
        result = left.strip()

        parts = right.strip().split()
        func_name = parts[1].rstrip(',')
        n_args = int(parts[2])

        # Chama a função
        self.emit(f"bl {func_name}")

        # Limpa pilha (n_args * 4 bytes)
        if n_args > 0:
            self.emit(f"add sp, sp, #{n_args * 4}")

        # Salva valor de retorno (r0)
        self.store_from_register('r0', result)

    def handle_begin_func(self):
        """Prólogo de função (ARM AAPCS)."""
        self.emit("push {fp, lr}")  # Salva frame pointer e link register
        self.emit("mov fp, sp")  # Setup frame pointer
        # Espaço para variáveis locais será ajustado dinamicamente

    def handle_end_func(self):
        """Epílogo de função."""
        self.emit("mov sp, fp")
        self.emit("pop {fp, pc}")  # Restaura FP e retorna (PC = LR)

    def handle_get_param(self, parts):
        """Recebe parâmetro de função."""
        param_name = parts[1]
        # Parâmetros estão na pilha ou em r0-r3
        # Simplificação: assume que vêm da pilha
        self.emit(f"ldr r0, [fp, #8]")  # Primeiro parâmetro
        self.store_from_register('r0', param_name)

    def handle_return(self, parts):
        """Gera código para return."""
        if len(parts) > 1:
            ret_value = parts[1]
            self.load_to_register(ret_value, 'r0')
        self.emit("b .FUNC_END")  # Pula para epílogo

    def handle_send(self, instruction):
        """Simula envio de dados por canal."""
        # Formato: send channel, n_params
        self.emit_comment(f"Operação de envio: {instruction}")
        # Implementação simplificada - na prática precisaria de syscalls ou runtime
        self.emit("nop  @ send operation")

    def handle_receive(self, instruction):
        """Simula recepção de dados por canal."""
        # Formato: receive channel, var1, var2, ...
        self.emit_comment(f"Operação de recepção: {instruction}")
        # Implementação simplificada
        self.emit("nop  @ receive operation")

    # ============================================
    # MONTAGEM FINAL
    # ============================================
    def assemble_final_code(self):
        """Monta o código assembly completo com seções."""
        final_code = []

        # Diretivas ARM
        final_code.append(".arch armv7-a")
        final_code.append(".arm")
        final_code.append("")

        # Seção .data
        if self.data_section:
            final_code.append(".section .data")
            final_code.extend(self.data_section)
            final_code.append("")

        # Seção .text
        final_code.append(".section .text")
        final_code.append(".global _start")
        final_code.append("")
        final_code.append("_start:")
        final_code.append("    @ Ponto de entrada do programa")
        final_code.append("    bl main")
        final_code.append("    @ Exit syscall (ARM Linux)")
        final_code.append("    mov r0, #0")
        final_code.append("    mov r7, #1      @ syscall number for exit")
        final_code.append("    swi 0           @ software interrupt")
        final_code.append("")
        final_code.append("main:")

        # Adiciona o código gerado
        final_code.extend(self.asm_code)

        # Retorno da main
        final_code.append("")
        final_code.append("    @ Retorno da main")
        final_code.append("    mov r0, #0")
        final_code.append("    bx lr")

        return "\n".join(final_code)