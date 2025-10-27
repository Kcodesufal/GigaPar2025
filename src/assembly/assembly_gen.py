class AssemblyGenerator:
    """
    Gera código Assembly x86-64 a partir de Código de 3 Endereços (C3E).
    """

    def __init__(self):
        self.asm_code = []  # Lista de instruções assembly
        self.data_section = []  # Seção .data (strings, constantes)
        self.var_locations = {}  # Mapa: variável -> localização (registrador ou memória)
        self.stack_offset = 0  # Offset atual na pilha
        self.string_counter = 0  # Contador para labels de strings
        self.channels = {}  # Informações sobre canais declarados

        # Registradores disponíveis para variáveis temporárias
        # Seguindo convenção x86-64 System V ABI
        self.temp_registers = ['r10', 'r11', 'r12', 'r13', 'r14', 'r15']
        self.reg_index = 0

        # Registradores para parâmetros (primeiros 6 parâmetros)
        self.param_registers = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

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
        self.asm_code.append(f"    ; {comment}")

    def allocate_register(self, var_name):
        """Aloca um registrador para uma variável temporária."""
        if var_name not in self.var_locations:
            if self.reg_index < len(self.temp_registers):
                reg = self.temp_registers[self.reg_index]
                self.var_locations[var_name] = reg
                self.reg_index += 1
            else:
                # Se acabaram os registradores, usa a pilha (spilling)
                self.stack_offset += 8
                self.var_locations[var_name] = f"-{self.stack_offset}(%rbp)"
        return self.var_locations[var_name]

    def get_location(self, operand):
        """Retorna a localização de um operando (registrador, memória ou imediato)."""
        # Se for número literal
        if operand.lstrip('-').replace('.', '', 1).isdigit():
            return f"${operand}"

        # Se for variável temporária (t0, t1, ...)
        if operand.startswith('t') and operand[1:].isdigit():
            return self.allocate_register(operand)

        # Se for variável regular
        if operand in self.var_locations:
            return self.var_locations[operand]

        # Aloca na pilha se não existir
        self.stack_offset += 8
        self.var_locations[operand] = f"-{self.stack_offset}(%rbp)"
        return self.var_locations[operand]

    def add_string_literal(self, string_value):
        """Adiciona uma string literal na seção .data."""
        label = f".STR{self.string_counter}"
        self.string_counter += 1
        # Remove aspas da string
        clean_string = string_value.strip('"')
        self.data_section.append(f'{label}: .string "{clean_string}"')
        return label

    # ============================================
    # GERAÇÃO PRINCIPAL
    # ============================================
    def generate(self, c3e_instructions):
        """Ponto de entrada: gera assembly a partir das instruções C3E."""
        self.emit_comment("Código gerado pelo compilador GigaPar2025")
        self.emit_comment("Arquitetura: x86-64")
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

        dest_loc = self.get_location(dest)

        # Operações binárias
        if any(op in right for op in
               [' + ', ' - ', ' * ', ' / ', ' == ', ' != ', ' < ', ' > ', ' <= ', ' >= ', ' and ', ' or ']):
            self.handle_binary_op(dest_loc, right)

        # Operações unárias
        elif right.startswith('not ') or right.startswith('- '):
            self.handle_unary_op(dest_loc, right)

        # Atribuição simples
        else:
            src_loc = self.get_location(right)

            # Move o valor para o destino
            if src_loc.startswith('$'):  # Imediato
                self.emit(f"movq {src_loc}, %rax")
                self.emit(f"movq %rax, {dest_loc}")
            elif dest_loc.startswith('-') and src_loc.startswith('-'):  # Ambos na pilha
                self.emit(f"movq {src_loc}, %rax")
                self.emit(f"movq %rax, {dest_loc}")
            else:  # Registrador para registrador ou registrador para memória
                self.emit(f"movq {src_loc}, %rax")
                self.emit(f"movq %rax, {dest_loc}")

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

        left_loc = self.get_location(left)
        right_loc = self.get_location(right)

        # Carrega operandos em registradores
        self.emit(f"movq {left_loc}, %rax")
        self.emit(f"movq {right_loc}, %rbx")

        # Executa operação
        if op == '+':
            self.emit("addq %rbx, %rax")
        elif op == '-':
            self.emit("subq %rbx, %rax")
        elif op == '*':
            self.emit("imulq %rbx, %rax")
        elif op == '/':
            self.emit("cqto")  # Estende sinal de rax para rdx:rax
            self.emit("idivq %rbx")
        elif op in ['==', '!=', '<', '>', '<=', '>=']:
            self.emit("cmpq %rbx, %rax")
            if op == '==':
                self.emit("sete %al")
            elif op == '!=':
                self.emit("setne %al")
            elif op == '<':
                self.emit("setl %al")
            elif op == '>':
                self.emit("setg %al")
            elif op == '<=':
                self.emit("setle %al")
            elif op == '>=':
                self.emit("setge %al")
            self.emit("movzbq %al, %rax")  # Zero-extend para 64 bits
        elif op == 'and':
            self.emit("andq %rbx, %rax")
        elif op == 'or':
            self.emit("orq %rbx, %rax")

        # Salva resultado
        self.emit(f"movq %rax, {dest}")

    def handle_unary_op(self, dest, expr):
        """Gera código para operações unárias."""
        if expr.startswith('not '):
            operand = expr[4:].strip()
            op_loc = self.get_location(operand)
            self.emit(f"movq {op_loc}, %rax")
            self.emit("notq %rax")
            self.emit(f"movq %rax, {dest}")
        elif expr.startswith('- '):
            operand = expr[2:].strip()
            op_loc = self.get_location(operand)
            self.emit(f"movq {op_loc}, %rax")
            self.emit("negq %rax")
            self.emit(f"movq %rax, {dest}")

    def handle_if_false(self, parts):
        """Gera código para desvio condicional."""
        # Formato: if_false condition goto label
        condition = parts[1]
        label = parts[3]

        cond_loc = self.get_location(condition)
        self.emit(f"movq {cond_loc}, %rax")
        self.emit("cmpq $0, %rax")
        self.emit(f"je {label}")

    def handle_goto(self, parts):
        """Gera código para salto incondicional."""
        label = parts[1]
        self.emit(f"jmp {label}")

    def handle_param(self, parts):
        """Prepara parâmetro para chamada de função (empilha)."""
        param = parts[1]
        param_loc = self.get_location(param)

        if param_loc.startswith('$'):
            self.emit(f"movq {param_loc}, %rax")
            self.emit("pushq %rax")
        else:
            self.emit(f"pushq {param_loc}")

    def handle_call(self, instruction):
        """Gera código para chamada de função."""
        # Formato: result = call func_name, n_args
        left, right = instruction.split('=', 1)
        result = left.strip()

        parts = right.strip().split()
        func_name = parts[1].rstrip(',')
        n_args = int(parts[2])

        # Chama a função
        self.emit(f"call {func_name}")

        # Limpa pilha (n_args * 8 bytes)
        if n_args > 0:
            self.emit(f"addq ${n_args * 8}, %rsp")

        # Salva valor de retorno
        result_loc = self.get_location(result)
        self.emit(f"movq %rax, {result_loc}")

    def handle_begin_func(self):
        """Prólogo de função."""
        self.emit("pushq %rbp")
        self.emit("movq %rsp, %rbp")
        # Espaço para variáveis locais será ajustado dinamicamente

    def handle_end_func(self):
        """Epílogo de função."""
        self.emit("movq %rbp, %rsp")
        self.emit("popq %rbp")
        self.emit("ret")

    def handle_get_param(self, parts):
        """Recebe parâmetro de função."""
        param_name = parts[1]
        # Parâmetros estão na pilha (convenção de chamada)
        param_loc = self.get_location(param_name)
        # Simplificação: assume que parâmetros vêm em ordem
        self.emit(f"movq 16(%rbp), %rax")  # Primeiro parâmetro
        self.emit(f"movq %rax, {param_loc}")

    def handle_return(self, parts):
        """Gera código para return."""
        if len(parts) > 1:
            ret_value = parts[1]
            ret_loc = self.get_location(ret_value)
            self.emit(f"movq {ret_loc}, %rax")
        self.emit("jmp .FUNC_END")  # Pula para epílogo

    def handle_send(self, instruction):
        """Simula envio de dados por canal."""
        # Formato: send channel, n_params
        self.emit_comment(f"Operação de envio: {instruction}")
        # Implementação simplificada - na prática precisaria de syscalls ou runtime
        self.emit("nop  ; send operation")

    def handle_receive(self, instruction):
        """Simula recepção de dados por canal."""
        # Formato: receive channel, var1, var2, ...
        self.emit_comment(f"Operação de recepção: {instruction}")
        # Implementação simplificada
        self.emit("nop  ; receive operation")

    # ============================================
    # MONTAGEM FINAL
    # ============================================
    def assemble_final_code(self):
        """Monta o código assembly completo com seções."""
        final_code = []

        # Seção .data
        if self.data_section:
            final_code.append(".section .data")
            final_code.extend(self.data_section)
            final_code.append("")

        # Seção .text
        final_code.append(".section .text")
        final_code.append(".globl _start")
        final_code.append("")
        final_code.append("_start:")
        final_code.append("    ; Ponto de entrada do programa")
        final_code.append("    call main")
        final_code.append("    ; Exit syscall")
        final_code.append("    movq $60, %rax")
        final_code.append("    xorq %rdi, %rdi")
        final_code.append("    syscall")
        final_code.append("")
        final_code.append("main:")

        # Adiciona o código gerado
        final_code.extend(self.asm_code)

        # Retorno da main
        final_code.append("")
        final_code.append("    ; Retorno da main")
        final_code.append("    movq $0, %rax")
        final_code.append("    ret")

        return "\n".join(final_code)