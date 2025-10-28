class AssemblyOptimizer:
    """
    Otimizador de código Assembly ARMv7.
    Implementa várias estratégias de otimização para melhorar a qualidade do código gerado.
    """

    def __init__(self):
        self.live_vars = {}  # Rastreamento de variáveis vivas
        self.reg_graph = {}  # Grafo de interferência para alocação de registradores
        self.const_values = {}  # Cache de valores constantes

    def optimize(self, asm_instructions):
        """
        Aplica todas as otimizações disponíveis ao código assembly.
        """
        instructions = asm_instructions.copy()
        
        for _ in range(2): # Executa o ciclo de otimização 2 vezes
            instructions = self.eliminate_redundant_moves(instructions)
            instructions = self.optimize_arithmetic(instructions)
            instructions = self.optimize_branches(instructions)
            instructions = self.eliminate_dead_code(instructions)
        
        return instructions

    def eliminate_redundant_moves(self, instructions):
        """
        Elimina instruções MOV redundantes, como:
        - mov r0, r0
        """
        result = []
        for instr_line in instructions:
            instr = instr_line.strip()
            
            if instr.startswith('mov'):
                # Tenta extrair 'mov REG, REG'
                # Remove vírgula e divide: 'mov r0, r0' -> ['mov', 'r0', 'r0']
                parts = instr.replace(',', ' ').split() 
                if len(parts) == 3:
                    dest = parts[1]
                    src = parts[2]
                    if dest == src:
                        # É um 'mov rX, rX'. Marca como otimizado e pula.
                        result.append(f"    @ Optim-out (mov rX, rX): {instr_line.strip()}")
                        continue 
            result.append(instr_line)
        
        return result

    def optimize_arithmetic(self, instructions):
        """
        Otimiza operações aritméticas, como:
        - Substituir multiplicação por 2 por shift left
        - Combinar operações aritméticas consecutivas
        """
        result = []
        
        for instr in instructions:
            if 'mul' in instr and ', #2' in instr:
                parts = instr.split(',')
                reg_dest = parts[0].split()[-1]
                reg_src = parts[1].strip()
                result.append(f"    lsl {reg_dest}, {reg_src}, #1")
            else:
                result.append(instr)
                
        return result

    def optimize_branches(self, instructions):
        """
        Otimiza desvios condicionais:
        - Remove desvios para a próxima instrução (pulando comentários/brancos)
        """
        result = []
        
        for i in range(len(instructions)):
            instr_line = instructions[i]
            curr = instr_line.strip()
            
            if curr.startswith('b ') and not curr.startswith('bl '):
                branch_target = curr.split()[-1]
                
                next_real_line = None
                for j in range(i + 1, len(instructions)):
                    next_line_candidate = instructions[j].strip()
                    # Se for uma linha de código ou um label
                    if next_line_candidate and not next_line_candidate.startswith('@'):
                        next_real_line = next_line_candidate
                        break
                
                if next_real_line and next_real_line.rstrip(':') == branch_target:
                    # O desvio é para a próxima instrução. Remove o desvio.
                    result.append(f"    @ Optim-out (b to next line): {instr_line.strip()}")
                    continue # Não adiciona o 'b'
            
            result.append(instr_line)
            
        return result

    def eliminate_dead_code(self, instructions):
        """
        Elimina código morto:
        - Instruções após retorno incondicional
        - Código inacessível
        """

        result = []
        in_dead_code = False
        
        for instr in instructions:
            if instr.strip().endswith(':'):
                in_dead_code = False
            
            if not in_dead_code:
                result.append(instr)
                
            # Marca código após retorno como morto
            if instr.strip().startswith('b ') or instr.strip() == 'bx lr' or 'pop {' in instr and 'pc}' in instr:
                in_dead_code = True
                
        return result

    def analyze_live_ranges(self, instructions):
        """
        Analisa o tempo de vida das variáveis para melhor alocação de registradores.
        """
        self.live_vars = {}
        current_live = set()
        
        for instr in reversed(instructions):
            parts = instr.strip().split()
            if not parts:
                continue
                
            # Análise básica de definição/uso de registradores
            if parts[0] in ['mov', 'add', 'sub', 'mul', 'div']:
                dest_reg = parts[1].rstrip(',')
                current_live.discard(dest_reg)  # Definição mata variável
                
                # Adiciona registradores usados como vivos
                for part in parts[2:]:
                    reg = part.rstrip(',')
                    if reg.startswith('r'):
                        current_live.add(reg)
                        
            self.live_vars[instr] = current_live.copy()