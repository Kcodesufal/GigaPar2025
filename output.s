.arch armv7-a
.arm

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

    b L0
calcular:
func_0:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    @ Instrução C3E não reconhecida: t0 = operacao == "soma"
    ldr r0, [fp, #-16]
    cmp r0, #0
    beq L1
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-8]
    add r0, r0, r1
    str r0, [fp, #-20]
    ldr r0, [fp, #-28]
    str r0, [fp, #-32]
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-8]
    add r0, r0, r1
    str r0, [fp, #-36]
    ldr r0, [fp, #-36]
    b .return_exit
    b L0
    b L2
L1:
    ldr r0, [fp, #-44]
    str r0, [fp, #-48]
L2:
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L0:
    @ Declaração de canal ignorada: channel_decl calculadora, computador1, computador2
    b L3
main:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    mov r0, #25
    str r0, [fp, #-4]
    mov r0, #17
    str r0, [fp, #-8]
    ldr r0, [fp, #-16]
    str r0, [fp, #-20]
    ldr r0, [fp, #-20]
    mov r1, #15
    mul r0, r0, r1
    str r0, [fp, #-24]
    ldr r0, [fp, #-24]
    str r0, [fp, #-28]
    mov r0, #0
    str r0, [fp, #-32]
L4:
    ldr r0, [fp, #-32]
    mov r1, #3
    cmp r0, r1
    movlt r0, #1
    movge r0, #0
    str r0, [fp, #-36]
    ldr r0, [fp, #-36]
    cmp r0, #0
    beq L5
    ldr r0, [fp, #-40]
    str r0, [fp, #-44]
    ldr r0, [fp, #-32]
    mov r1, #1
    add r0, r0, r1
    str r0, [fp, #-48]
    ldr r0, [fp, #-48]
    str r0, [fp, #-32]
    b L4
L5:
    @ INÍCIO DE BLOCO PARALELO
    ldr r0, [fp, #-40]
    str r0, [fp, #-52]
    ldr r0, [fp, #-40]
    str r0, [fp, #-56]
    @ FIM DE BLOCO PARALELO
    ldr r0, [fp, #-40]
    str r0, [fp, #-64]
    mov r0, #1
    str r0, [fp, #-28]
    ldr r0, [fp, #-40]
    str r0, [fp, #-68]
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-28]
    sub r0, r0, r1
    str r0, [fp, #-72]
    ldr r0, [fp, #-4]
    mov r1, #2
    mov r2, #0
    .L_div_95:
    cmp r0, r1
    blt .L_div_done_95
    sub r0, r0, r1
    add r2, r2, #1
    b .L_div_95
    .L_div_done_95:
    mov r0, r2
    str r0, [fp, #-76]
    ldr r0, [fp, #-72]
    ldr r1, [fp, #-76]
    add r0, r0, r1
    str r0, [fp, #-80]
    ldr r0, [fp, #-80]
    str r0, [fp, #-8]
    @ Declaração de canal ignorada: channel_decl serverclient, c1, c2
    @ Operação de envio: send c1, 5
    nop
    @ Operação de recepção: receive c2, y, i, j, k, l
    ldr r0, [fp, #-40]
    str r0, [fp, #-124]
    ldr r0, [fp, #-40]
    str r0, [fp, #-132]
    mov r0, #1
    b .return_exit
    b L3
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L3:
    @ Operação de envio: send calculadora, 3
    nop
    @ Operação de recepção: receive calculadora, a, b, c
    ldr r0, [fp, #-4]
    mov r1, #2
    add r0, r0, r1
    str r0, [fp, #-144]
    ldr r0, [fp, #-144]
    str r0, [fp, #-4]
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-4]
    add r0, r0, r1
    str r0, [fp, #-148]
    ldr r0, [fp, #-148]
    str r0, [fp, #-8]