.arch armv7-a
.arm

.section .data
.STR0: .asciz "+"

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
    mov r0, #50000
    str r0, [fp, #-4]
    mov r0, #50001
    str r0, [fp, #-8]
    @ Declaração de canal ignorada: channel_decl calculadora, computador_1, computador_2
    b L0
calcular:
func_0:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    @ Instrução C3E não reconhecida: t0 = operacao == "+"
    ldr r0, [fp, #-16]
    cmp r0, #0
    beq L1
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-12]
    add r0, r0, r1
    str r0, [fp, #-20]
    ldr r0, [fp, #-20]
    b .return_exit
    b L0
    b L2
L1:
    @ Instrução C3E não reconhecida: t2 = operacao == "-"
    ldr r0, [fp, #-24]
    cmp r0, #0
    beq L3
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-12]
    sub r0, r0, r1
    str r0, [fp, #-28]
    ldr r0, [fp, #-28]
    b .return_exit
    b L0
    b L4
L3:
    @ Instrução C3E não reconhecida: t4 = operacao == "*"
    ldr r0, [fp, #-32]
    cmp r0, #0
    beq L5
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-12]
    mul r0, r0, r1
    str r0, [fp, #-36]
    ldr r0, [fp, #-36]
    b .return_exit
    b L0
    b L6
L5:
    ldr r0, [fp, #-44]
    str r0, [fp, #-48]
    mov r0, #0
    b .return_exit
    b L0
L6:
L4:
L2:
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L0:
    @ INÍCIO DE BLOCO SEQUENCIAL
    b L7
main:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    ldr r0, [fp, #-8]
    str r0, [fp, #-12]
    ldr r0, =.STR0
    str r0, [fp, #-16]
    mov r0, #10
    str r0, [fp, #-20]
    mov r0, #5
    str r0, [fp, #-24]
    @ Operação de envio: send calculadora, 4
    nop
    ldr r0, [fp, #-8]
    str r0, [fp, #-44]
    @ Operação de recepção: receive calculadora, operacao, valor1, valor2, resultado
    nop
    ldr r0, [fp, #-56]
    str r0, [fp, #-60]
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L7:
    @ FIM DE BLOCO SEQUENCIAL