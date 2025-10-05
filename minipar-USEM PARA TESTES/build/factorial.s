.global _start
.text
_start:
    MOV R4, #5
    LDR R0, =n
    STR R4, [R0]
    MOV R5, #1
    LDR R0, =f
    STR R5, [R0]
    MOV R6, #1
    LDR R0, =i
    STR R6, [R0]
while0:
    LDR R7, =i
    LDR R7, [R7]
    LDR R8, =n
    LDR R8, [R8]
    CMP R7, R8
    MOVLE R9, #1
    MOVGT R9, #0
    CMP R9, #0
    BEQ endw1
    LDR R10, =f
    LDR R10, [R10]
    LDR R11, =i
    LDR R11, [R11]
    MUL R12, R10, R11
    LDR R0, =f
    STR R12, [R0]
    B while0
endw1:
    LDR R12, =i
    LDR R12, [R12]
    MOV R12, #1
    ADD R12, R12, R12
    LDR R0, =i
    STR R12, [R0]
    LDR R12, =f
    LDR R12, [R12]
    LDR R1, =PRINT_OUT_0
    STR R12, [R1]
end_loop:
    B end_loop

.data
f: .word 0
i: .word 0
n: .word 0
PRINT_OUT_0: .word 0
PRINT_OUT_1: .word 0
PRINT_OUT_2: .word 0
PRINT_OUT_3: .word 0
PRINT_OUT_4: .word 0
PRINT_OUT_5: .word 0
PRINT_OUT_6: .word 0
PRINT_OUT_7: .word 0
