.global _start
.text
_start:
    LDR R4, =CONST_341996
    MOV R5, #4
    MOV R6, #5
    @ SEND calculadora (no-op in assembly)
    @ RECEIVE calculadora (no-op in assembly)
    LDR R7, =resultado
    LDR R7, [R7]
    LDR R1, =PRINT_OUT_0
    STR R7, [R1]
end_loop:
    B end_loop

.data
resultado: .word 0
PRINT_OUT_0: .word 0
PRINT_OUT_1: .word 0
PRINT_OUT_2: .word 0
PRINT_OUT_3: .word 0
PRINT_OUT_4: .word 0
PRINT_OUT_5: .word 0
PRINT_OUT_6: .word 0
PRINT_OUT_7: .word 0
CONST_341996: .word 0
