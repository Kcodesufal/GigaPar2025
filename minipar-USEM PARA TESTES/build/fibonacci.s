.global _start
.text
_start:
    MOV R4, #5
    LDR R0, =n
    STR R4, [R0]
    MOV R5, #0
    LDR R0, =a
    STR R5, [R0]
    MOV R6, #1
    LDR R0, =b
    STR R6, [R0]
    MOV R7, #0
    LDR R0, =i
    STR R7, [R0]
while0:
    LDR R8, =i
    LDR R8, [R8]
    LDR R9, =n
    LDR R9, [R9]
    CMP R8, R9
    MOVLT R10, #1
    MOVGE R10, #0
    CMP R10, #0
    BEQ endw1
    LDR R11, =a
    LDR R11, [R11]
    LDR R1, =PRINT_OUT_0
    STR R11, [R1]
    B while0
endw1:
    LDR R12, =a
    LDR R12, [R12]
    LDR R12, =b
    LDR R12, [R12]
    ADD R12, R12, R12
    LDR R0, =t
    STR R12, [R0]
    LDR R12, =b
    LDR R12, [R12]
    LDR R0, =a
    STR R12, [R0]
    LDR R12, =t
    LDR R12, [R12]
    LDR R0, =b
    STR R12, [R0]
    LDR R12, =i
    LDR R12, [R12]
    MOV R12, #1
    ADD R12, R12, R12
    LDR R0, =i
    STR R12, [R0]
end_loop:
    B end_loop

.data
a: .word 0
b: .word 0
i: .word 0
n: .word 0
t: .word 0
PRINT_OUT_0: .word 0
PRINT_OUT_1: .word 0
PRINT_OUT_2: .word 0
PRINT_OUT_3: .word 0
PRINT_OUT_4: .word 0
PRINT_OUT_5: .word 0
PRINT_OUT_6: .word 0
PRINT_OUT_7: .word 0
