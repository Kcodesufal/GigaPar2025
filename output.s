.arch armv7-a
.arm

.section .text
.global _start

_start:
    @ Ponto de entrada do programa
    ldr sp, =0x7000    @ Inicializa SP (topo da pilha)

    bl main

    @ Exit syscall (ARM Linux) - CPUlator deve interceptar
    mov r0, #0         @ Código de saída 0 (sucesso)
    mov r7, #1         @ Syscall número 1 (exit)
    swi 0              @ Software Interrupt
    b .                @ Loop de segurança se SWI não parar

main:
    push {r4, r5, r6, r7, r8}    @ Salva regs callee-saved (r4-r11)
    @ Código gerado pelo compilador GigaPar2025
    @ Arquitetura: ARMv7

    @ Canal declarado: calculadora entre computador1 e computador2
    mov r0, #10
    push {r0}
    mov r0, #2
    push {r0}
    mov r0, #1
    push {r0}
    @ Operação de envio (NOP): send calculadora, 3
    nop  @ send operation
    @ Operação de recepção: receive calculadora, a, b, c
    @ Var 'a' mapeada para [sp, #0] (valor do param 3)
    @ Var 'b' mapeada para [sp, #4] (valor do param 2)
    @ Var 'c' mapeada para [sp, #8] (valor do param 1)
    @ Próximo offset de pilha para temporários: 12
    @ BEGIN PARALLEL BLOCK
    ldr r0, [sp, #0]
    mov r1, #2
    add r0, r0, r1
    @ Variável 't0' não encontrada, alocando na pilha...
    mov r4, r0
    mov r0, r4
    str r0, [sp, #0]
    ldr r0, [sp, #4]
    mov r1, #3
    mul r0, r0, r1
    @ Variável 't1' não encontrada, alocando na pilha...
    mov r5, r0
    mov r0, r5
    str r0, [sp, #4]
    ldr r0, [sp, #8]
    mov r1, #5
    sub r0, r0, r1
    @ Variável 't2' não encontrada, alocando na pilha...
    mov r6, r0
    mov r0, r6
    str r0, [sp, #8]
    @ END PARALLEL BLOCK
    ldr r0, [sp, #0]
    ldr r1, [sp, #4]
    add r0, r0, r1
    @ Variável 't3' não encontrada, alocando na pilha...
    mov r7, r0
    mov r0, r7
    ldr r1, [sp, #8]
    add r0, r0, r1
    @ Variável 't4' não encontrada, alocando na pilha...
    mov r8, r0
    mov r0, r8
    str r0, [sp, #0]

    @ Epílogo: Restaura pilha e registradores
    add sp, sp, #12  @ Limpa 3 param(s) da pilha
    pop {r4, r5, r6, r7, r8}     @ Restaura regs callee-saved
    mov r0, #0         @ Retorno padrão da main (convenção C)
    bx lr              @ Retorna para _start