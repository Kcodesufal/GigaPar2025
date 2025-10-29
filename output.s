.arch armv7-a
.arm

.section .data
.STR0: .asciz ""
.STR1: .asciz ""

.section .text
.global _start
.global main

_start:
    ldr sp, =0x8000
    bl main
    b .

.return_exit:
    mov sp, fp
    pop {fp, pc}

    @ Código gerado pelo compilador GigaPar2025
    @ Arquitetura: ARMv7

    @ Função strcmp_func: compara strings r0 e r1, resultado em r2
strcmp_func:
    push {r4, lr}
strcmp_func_loop:
    ldrb r3, [r0], #1
    ldrb r4, [r1], #1
    cmp r3, r4
    bne strcmp_func_false
    cmp r3, #0
    beq strcmp_func_true
    b strcmp_func_loop
strcmp_func_false:
    mov r3, #0
    str r3, [r2]
    b strcmp_func_end
strcmp_func_true:
    mov r3, #1
    str r3, [r2]
strcmp_func_end:
    pop {r4, lr}
    bx lr
    b L0
calcular_fatorial:
func_0:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    mov r0, #1
    str r0, [fp, #-8]
    mov r0, #1
    str r0, [fp, #-12]
L1:
    @ Instrução C3E não reconhecida: t0 = i <= n
    ldr r0, [fp, #-16]
    cmp r0, #0
    beq L2
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-12]
    mul r0, r0, r1
    str r0, [fp, #-20]
    ldr r0, [fp, #-20]
    str r0, [fp, #-8]
    ldr r0, [fp, #-12]
    mov r1, #1
    add r0, r0, r1
    str r0, [fp, #-24]
    ldr r0, [fp, #-24]
    str r0, [fp, #-12]
    b L1
L2:
    ldr r0, =.STR0
    str r0, [fp, #-28]
    ldr r0, [fp, #-36]
    str r0, [fp, #-40]
    ldr r0, [fp, #-8]
    b .return_exit
    b L0
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L0:
    b L3
calcular_fibonacci:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    mov r0, #0
    str r0, [fp, #-8]
    mov r0, #1
    str r0, [fp, #-12]
    mov r0, #0
    str r0, [fp, #-16]
L4:
    ldr r0, [fp, #-16]
    ldr r1, [fp, #-4]
    cmp r0, r1
    movlt r0, #1
    movge r0, #0
    str r0, [fp, #-20]
    ldr r0, [fp, #-20]
    cmp r0, #0
    beq L5
    ldr r0, =.STR1
    str r0, [fp, #-24]
    ldr r0, [fp, #-32]
    str r0, [fp, #-36]
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-12]
    add r0, r0, r1
    str r0, [fp, #-40]
    ldr r0, [fp, #-40]
    str r0, [fp, #-44]
    ldr r0, [fp, #-12]
    str r0, [fp, #-8]
    ldr r0, [fp, #-44]
    str r0, [fp, #-12]
    ldr r0, [fp, #-16]
    mov r1, #1
    add r0, r0, r1
    str r0, [fp, #-48]
    ldr r0, [fp, #-48]
    str r0, [fp, #-16]
    b L4
L5:
    ldr r0, [fp, #-8]
    b .return_exit
    b L3
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L3:
    b L6
main:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    @ INÍCIO DE BLOCO PARALELO
    ldr r0, [fp, #-8]
    str r0, [fp, #-12]
    ldr r0, [fp, #-20]
    str r0, [fp, #-24]
    @ FIM DE BLOCO PARALELO
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L6: