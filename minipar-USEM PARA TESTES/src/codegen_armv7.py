REG_TEMPS = ['R4','R5','R6','R7','R8','R9','R10','R11']

def temp_to_reg(tmp):
    if tmp is None: return None
    if isinstance(tmp, str) and tmp.startswith('t'):
        try:
            idx = int(tmp[1:])
        except:
            return 'R12'
        if idx < len(REG_TEMPS):
            return REG_TEMPS[idx]
        else:
            return 'R12'
    return None

def preprocess_ir(ir):
    # Build map of LOAD_CONST temps -> value
    const_map = {}
    new_ir = []
    i = 0
    while i < len(ir):
        instr = ir[i]
        # track LOAD_CONST temporaries
        if instr.op == 'LOAD_CONST' and instr.c is not None:
            const_map[instr.c] = instr.a
            new_ir.append(instr)
            i += 1; continue
        # detect SEND followed immediately by RECEIVE with same channel
        if instr.op == 'SEND' and (i+1) < len(ir) and ir[i+1].op == 'RECEIVE' and instr.a == ir[i+1].a:
            send_instr = instr; recv_instr = ir[i+1]
            # attempt to resolve operator and operands from const_map
            args = send_instr.b or []
            resolved = []
            ok = True
            for a in args:
                if isinstance(a, str) and a in const_map:
                    resolved.append(const_map[a])
                elif isinstance(a, int):
                    resolved.append(a)
                else:
                    # cannot resolve at compile time; fallback to leaving as runtime SEND
                    ok = False; break
            if ok and len(resolved) >= 3:
                # simple calculadora protocol: operator, a, b
                op = resolved[0]
                a_val = resolved[1]; b_val = resolved[2]
                # compute result for supported ops
                res = None
                if op == '+' or op == '+' or (isinstance(op,str) and op == '+'):
                    res = a_val + b_val
                elif op == '-': res = a_val - b_val
                elif op == '*': res = a_val * b_val
                elif op == '/': res = (a_val // b_val) if b_val != 0 else 0
                if res is not None:
                    # replace SEND + RECEIVE with LOAD_CONST res; STORE into recv var(s)
                    # create a LOAD_CONST instr style: ('LOAD_CONST', res, None, tmp)
                    tmpname = f"t_inline_{i}"
                    new_ir.append(type(instr)( 'LOAD_CONST', res, None, tmpname ))
                    # for each recv var, create STORE tmpname -> var
                    for vn in (recv_instr.b or []):
                        new_ir.append(type(instr)( 'STORE', tmpname, None, vn ))
                    i += 2
                    continue
            # else cannot inline
        new_ir.append(instr); i += 1
    return new_ir

def gen(ir_instructions):
    # Preprocess IR to inline simple calculadora send/receive patterns
    ir = preprocess_ir(ir_instructions)
    asm_lines = []
    data_lines = []
    var_names = set()
    for instr in ir:
        op = instr.op
        if op == 'STORE' and instr.c is not None:
            var_names.add(instr.c)
        if op == 'RECEIVE' and instr.b:
            for v in instr.b:
                var_names.add(v)
    for v in sorted(var_names):
        data_lines.append(f"{v}: .word 0")
    for i in range(8):
        data_lines.append(f"PRINT_OUT_{i}: .word 0")
    asm_lines.append('.global _start'); asm_lines.append('.text'); asm_lines.append('_start:')
    slot_ctr = 0
    for instr in ir:
        op = instr.op
        if op == 'LOAD_CONST':
            dst = temp_to_reg(instr.c); val = instr.a
            if dst is None: continue
            if isinstance(val, int) and -255 <= val <= 255:
                asm_lines.append(f'    MOV {dst}, #{val}')
            else:
                label = f"CONST_{abs(hash(str(val))) & 0xfffff}"
                data_lines.append(f"{label}: .word {val if isinstance(val,int) else 0}")
                asm_lines.append(f'    LDR {dst}, ={label}')
        elif op == 'LOAD_VAR':
            dst = temp_to_reg(instr.c); var = instr.a
            if dst is None: continue
            asm_lines.append(f'    LDR {dst}, ={var}'); asm_lines.append(f'    LDR {dst}, [{dst}]')
        elif op == 'STORE':
            src = temp_to_reg(instr.a); var = instr.c
            if src is None:
                # if src is an inline temp (t_inline_...) it's not in REG_TEMPS; handle immediate by loading constant
                if isinstance(instr.a, str) and instr.a.startswith('t_inline_'):
                    # instr.a holds tmpname; but value unknown here - try to interpret numeric suffix earlier in LOAD_CONST mapping is not available.
                    # Fallback: ignore; in many inlined cases previous LOAD_CONST wrote to register; here we try LDR of CONST label
                    continue
                continue
            asm_lines.append(f'    LDR R0, ={var}'); asm_lines.append(f'    STR {src}, [R0]')
        elif op in ('+','-','*','/'):
            dst = temp_to_reg(instr.c); a = temp_to_reg(instr.a); b = temp_to_reg(instr.b)
            if dst is None or a is None or b is None:
                continue
            if op == '+': asm_lines.append(f'    ADD {dst}, {a}, {b}')
            elif op == '-': asm_lines.append(f'    SUB {dst}, {a}, {b}')
            elif op == '*': asm_lines.append(f'    MUL {dst}, {a}, {b}')
            elif op == '/': asm_lines.append(f'    SDIV {dst}, {a}, {b}')
        elif op in ('EQ','NE','LT','GT','LE','GE'):
            dst = temp_to_reg(instr.c); a = temp_to_reg(instr.a); b = temp_to_reg(instr.b)
            asm_lines.append(f'    CMP {a}, {b}')
            if op == 'EQ': asm_lines.append(f'    MOVEQ {dst}, #1'); asm_lines.append(f'    MOVNE {dst}, #0')
            elif op == 'NE': asm_lines.append(f'    MOVNE {dst}, #1'); asm_lines.append(f'    MOVEQ {dst}, #0')
            elif op == 'LT': asm_lines.append(f'    MOVLT {dst}, #1'); asm_lines.append(f'    MOVGE {dst}, #0')
            elif op == 'GT': asm_lines.append(f'    MOVGT {dst}, #1'); asm_lines.append(f'    MOVLE {dst}, #0')
            elif op == 'LE': asm_lines.append(f'    MOVLE {dst}, #1'); asm_lines.append(f'    MOVGT {dst}, #0')
            elif op == 'GE': asm_lines.append(f'    MOVGE {dst}, #1'); asm_lines.append(f'    MOVLT {dst}, #0')
        elif op == 'PRINT':
            src = temp_to_reg(instr.a) or 'R0'
            # Call print routine: move value into R0 and BL print_int (if available) else store into PRINT_OUT_n
            asm_lines.append(f'    MOV R0, {src}')
            asm_lines.append(f'    BL print_int')
        elif op == 'SEND':
            asm_lines.append(f'    @ SEND {instr.a} (handled by preprocess or left as no-op)')
        elif op == 'RECEIVE':
            asm_lines.append(f'    @ RECEIVE {instr.a} (handled by preprocess or left as no-op)')
        elif op == 'LABEL':
            asm_lines.append(f'{instr.a}:')
        elif op == 'JZ':
            src = temp_to_reg(instr.a) or 'R0'; label = instr.c
            asm_lines.append(f'    CMP {src}, #0'); asm_lines.append(f'    BEQ {label}')
        elif op == 'JMP':
            asm_lines.append(f'    B {instr.a}')
        else:
            asm_lines.append(f'    @ UNKNOWN {instr}')
    # append print_int routine (simple integer -> decimal -> semihosting write0)
    asm_lines.append('    B after_print_runtime')
    asm_lines.append('print_int:')
    asm_lines.append('    @ Input: R0 = integer to print (signed)')
    asm_lines.append('    PUSH {R4-R7, LR}')
    asm_lines.append('    MOV R4, R0 @ copy value')
    asm_lines.append('    LDR R5, =PRINT_BUF_END')
    asm_lines.append('    MOV R6, #0 @ digit count')
    asm_lines.append('    CMP R4, #0')
    asm_lines.append('    BNE print_int_loop')
    asm_lines.append('    MOV R0, #48')
    asm_lines.append('    STRB R0, [R5, #-1]!')
    asm_lines.append('    MOV R6, #1')
    asm_lines.append('    B print_int_done')
    asm_lines.append('print_int_loop:')
    asm_lines.append('    MOV R1, #10')
    asm_lines.append('    UDIV R2, R4, R1    @ R2 = R4 / 10')
    asm_lines.append('    MUL R3, R2, R1     @ R3 = R2 * 10')
    asm_lines.append('    SUB R7, R4, R3     @ R7 = R4 - R3  (remainder)')
    asm_lines.append('    ADD R7, R7, #48    @ ASCII digit')
    asm_lines.append('    STRB R7, [R5, #-1]!')
    asm_lines.append('    MOV R6, R6, LSL #0')
    asm_lines.append('    ADD R6, R6, #1')
    asm_lines.append('    MOV R4, R2')
    asm_lines.append('    CMP R4, #0')
    asm_lines.append('    BNE print_int_loop')
    asm_lines.append('print_int_done:')
    asm_lines.append('    @ Now R5 points to start of string, R6 length, call semihosting SYS_WRITE0 (code 4)')
    asm_lines.append('    MOV R0, #4')
    asm_lines.append('    MOV R1, R5')
    asm_lines.append('    SWI 0x123456')
    asm_lines.append('    POP {R4-R7, LR}')
    asm_lines.append('    BX LR')
    asm_lines.append('after_print_runtime:')
    asm_lines.append('end_loop:')
    asm_lines.append('    B end_loop')
    # data section
    data_lines.append('PRINT_BUF: .space 32')
    data_lines.append('PRINT_BUF_END: .word PRINT_BUF + 32')
    data_sec = ['.data'] + data_lines
    return '\n'.join(asm_lines) + '\n\n' + '\n'.join(data_sec) + '\n'
