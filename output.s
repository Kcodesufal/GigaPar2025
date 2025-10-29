.arch armv7-a
.arm

.section .text
.global _start

_start:
    @ Ponto de entrada do programa
    push {r4, r5, r6, r7, r8, fp, lr}
    mov fp, sp
    sub sp, sp, #12
    @ Código gerado pelo compilador GigaPar2025
    @ Arquitetura: ARMv7

    @ Canal declarado: calculadora entre computador1 e computador2
    mov r0, #10
    push {r0}
    mov r0, #2
    push {r0}
    mov r0, #1
    push {r0}
    @ Operação de envio: send calculadora, 3
    nop  @ send operation
    add sp, sp, #12
    @ Operação de recepção: receive calculadora, a, b, c
    @ SIMULANDO receive(a, b, c) <- (1, 2, 10)
    mov r0, #1
    str r0, [fp, #-4]
    mov r0, #2
    str r0, [fp, #-8]
    mov r0, #10
    str r0, [fp, #-12]
    @ BEGIN PARALLEL BLOCK
    ldr r0, [fp, #-4]
    mov r1, #2
    add r0, r0, r1
    mov r4, r0
    mov r0, r4
    str r0, [fp, #-4]
    ldr r0, [fp, #-8]
    mov r1, #3
    mul r0, r0, r1
    mov r5, r0
    mov r0, r5
    str r0, [fp, #-8]
    ldr r0, [fp, #-12]
    mov r1, #5
    sub r0, r0, r1
    mov r6, r0
    mov r0, r6
    str r0, [fp, #-12]
    @ END PARALLEL BLOCK
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-8]
    add r0, r0, r1
    mov r7, r0
    mov r0, r7
    ldr r1, [fp, #-12]
    add r0, r0, r1
    mov r8, r0
    mov r0, r8
    str r0, [fp, #-4]

    @ Fim do script, preparando para sair
    mov r0, #0
    mov sp, fp
    pop {r4, r5, r6, r7, r8, fp, lr}
    @ Exit syscall (ARM Linux)
    mov r7, #1      @ syscall number for exit
    swi 0           @ software interrupt