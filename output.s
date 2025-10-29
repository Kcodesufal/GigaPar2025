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
relu:
func_0:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    @ Instrução C3E não reconhecida: t0 = x >= 0
    ldr r0, [fp, #-8]
    cmp r0, #0
    beq L1
    ldr r0, [fp, #-4]
    b .return_exit
    b L0
    b L2
L1:
    mov r0, #0
    b .return_exit
    b L0
L2:
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L0:
    b L3
pow:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    ldr r0, [fp, #-4]
    str r0, [fp, #-12]
    ldr r0, [fp, #-8]
    mov r1, #0
    cmp r0, r1
    movgt r0, #1
    movle r0, #0
    str r0, [fp, #-16]
    ldr r0, [fp, #-16]
    cmp r0, #0
    beq L4
L6:
    ldr r0, [fp, #-8]
    mov r1, #0
    cmp r0, r1
    movgt r0, #1
    movle r0, #0
    str r0, [fp, #-20]
    ldr r0, [fp, #-20]
    cmp r0, #0
    beq L7
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-12]
    mul r0, r0, r1
    str r0, [fp, #-24]
    ldr r0, [fp, #-24]
    str r0, [fp, #-12]
    ldr r0, [fp, #-8]
    mov r1, #1
    sub r0, r0, r1
    str r0, [fp, #-28]
    ldr r0, [fp, #-28]
    str r0, [fp, #-8]
    b L6
L7:
    b L5
L4:
L8:
    ldr r0, [fp, #-8]
    mov r1, #0
    cmp r0, r1
    movlt r0, #1
    movge r0, #0
    str r0, [fp, #-32]
    ldr r0, [fp, #-32]
    cmp r0, #0
    beq L9
    ldr r0, [fp, #-12]
    ldr r1, [fp, #-4]
    mov r2, #0
    .L_div_103:
    cmp r0, r1
    blt .L_div_done_103
    sub r0, r0, r1
    add r2, r2, #1
    b .L_div_103
    .L_div_done_103:
    mov r0, r2
    str r0, [fp, #-36]
    ldr r0, [fp, #-36]
    str r0, [fp, #-12]
    ldr r0, [fp, #-8]
    mov r1, #1
    add r0, r0, r1
    str r0, [fp, #-40]
    ldr r0, [fp, #-40]
    str r0, [fp, #-8]
    b L8
L9:
L5:
    ldr r0, [fp, #-12]
    b .return_exit
    b L3
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L3:
    b L10
sigmoid:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    mov r0, #2.71828
    str r0, [fp, #-8]
    mov r0, #0
    ldr r1, [fp, #-4]
    sub r0, r0, r1
    str r0, [fp, #-12]
    ldr r0, [fp, #-12]
    str r0, [fp, #-4]
    ldr r0, [fp, #-16]
    str r0, [fp, #-20]
    mov r0, #1
    ldr r1, [fp, #-20]
    add r0, r0, r1
    str r0, [fp, #-24]
    mov r0, #1
    ldr r1, [fp, #-24]
    mov r2, #0
    .L_div_153:
    cmp r0, r1
    blt .L_div_done_153
    sub r0, r0, r1
    add r2, r2, #1
    b .L_div_153
    .L_div_done_153:
    mov r0, r2
    str r0, [fp, #-28]
    ldr r0, [fp, #-28]
    b .return_exit
    b L10
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L10:
    b L11
main:
    push {fp, lr}
    mov fp, sp
    sub sp, sp, #256
    @ Stack frame para func_0
    mov r0, #1
    str r0, [fp, #-4]
    mov r0, #0
    str r0, [fp, #-8]
    mov r0, #1
    str r0, [fp, #-12]
    mov r0, #0
    str r0, [fp, #-16]
    mov r0, #4
    str r0, [fp, #-20]
    mov r0, #3
    str r0, [fp, #-24]
    mov r0, #4
    str r0, [fp, #-28]
    mov r0, #0.5
    str r0, [fp, #-32]
    mov r0, #0.5
    str r0, [fp, #-36]
    mov r0, #0.5
    str r0, [fp, #-40]
    mov r0, #0.5
    str r0, [fp, #-44]
    mov r0, #0.5
    str r0, [fp, #-48]
    mov r0, #0.5
    str r0, [fp, #-52]
    mov r0, #0.5
    str r0, [fp, #-56]
    mov r0, #0.5
    str r0, [fp, #-60]
    mov r0, #0.5
    str r0, [fp, #-64]
    mov r0, #0.5
    str r0, [fp, #-68]
    mov r0, #0.5
    str r0, [fp, #-72]
    mov r0, #0.5
    str r0, [fp, #-76]
    mov r0, #0.5
    str r0, [fp, #-80]
    mov r0, #0.5
    str r0, [fp, #-84]
    mov r0, #0.5
    str r0, [fp, #-88]
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-32]
    mul r0, r0, r1
    str r0, [fp, #-92]
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-44]
    mul r0, r0, r1
    str r0, [fp, #-96]
    ldr r0, [fp, #-92]
    ldr r1, [fp, #-96]
    add r0, r0, r1
    str r0, [fp, #-100]
    ldr r0, [fp, #-12]
    ldr r1, [fp, #-56]
    mul r0, r0, r1
    str r0, [fp, #-104]
    ldr r0, [fp, #-100]
    ldr r1, [fp, #-104]
    add r0, r0, r1
    str r0, [fp, #-108]
    ldr r0, [fp, #-16]
    ldr r1, [fp, #-68]
    mul r0, r0, r1
    str r0, [fp, #-112]
    ldr r0, [fp, #-108]
    ldr r1, [fp, #-112]
    add r0, r0, r1
    str r0, [fp, #-116]
    ldr r0, [fp, #-116]
    ldr r1, [fp, #-80]
    add r0, r0, r1
    str r0, [fp, #-120]
    ldr r0, [fp, #-120]
    str r0, [fp, #-124]
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-36]
    mul r0, r0, r1
    str r0, [fp, #-128]
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-48]
    mul r0, r0, r1
    str r0, [fp, #-132]
    ldr r0, [fp, #-128]
    ldr r1, [fp, #-132]
    add r0, r0, r1
    str r0, [fp, #-136]
    ldr r0, [fp, #-12]
    ldr r1, [fp, #-60]
    mul r0, r0, r1
    str r0, [fp, #-140]
    ldr r0, [fp, #-136]
    ldr r1, [fp, #-140]
    add r0, r0, r1
    str r0, [fp, #-144]
    ldr r0, [fp, #-16]
    ldr r1, [fp, #-72]
    mul r0, r0, r1
    str r0, [fp, #-148]
    ldr r0, [fp, #-144]
    ldr r1, [fp, #-148]
    add r0, r0, r1
    str r0, [fp, #-152]
    ldr r0, [fp, #-152]
    ldr r1, [fp, #-84]
    add r0, r0, r1
    str r0, [fp, #-156]
    ldr r0, [fp, #-156]
    str r0, [fp, #-160]
    ldr r0, [fp, #-4]
    ldr r1, [fp, #-40]
    mul r0, r0, r1
    str r0, [fp, #-164]
    ldr r0, [fp, #-8]
    ldr r1, [fp, #-52]
    mul r0, r0, r1
    str r0, [fp, #-168]
    ldr r0, [fp, #-164]
    ldr r1, [fp, #-168]
    add r0, r0, r1
    str r0, [fp, #-172]
    ldr r0, [fp, #-12]
    ldr r1, [fp, #-64]
    mul r0, r0, r1
    str r0, [fp, #-176]
    ldr r0, [fp, #-172]
    ldr r1, [fp, #-176]
    add r0, r0, r1
    str r0, [fp, #-180]
    ldr r0, [fp, #-16]
    ldr r1, [fp, #-76]
    mul r0, r0, r1
    str r0, [fp, #-184]
    ldr r0, [fp, #-180]
    ldr r1, [fp, #-184]
    add r0, r0, r1
    str r0, [fp, #-188]
    ldr r0, [fp, #-188]
    ldr r1, [fp, #-88]
    add r0, r0, r1
    str r0, [fp, #-192]
    ldr r0, [fp, #-192]
    str r0, [fp, #-196]
    ldr r0, [fp, #-200]
    str r0, [fp, #-204]
    ldr r0, [fp, #-204]
    str r0, [fp, #-208]
    ldr r0, [fp, #-200]
    str r0, [fp, #-212]
    ldr r0, [fp, #-212]
    str r0, [fp, #-216]
    ldr r0, [fp, #-200]
    str r0, [fp, #-220]
    ldr r0, [fp, #-220]
    str r0, [fp, #-224]
    mov r0, #0.5
    str r0, [fp, #-228]
    mov r0, #0.5
    str r0, [fp, #-232]
    mov r0, #0.5
    str r0, [fp, #-236]
    mov r0, #0.5
    str r0, [fp, #-240]
    mov r0, #0.5
    str r0, [fp, #-244]
    mov r0, #0.5
    str r0, [fp, #-248]
    mov r0, #0.5
    str r0, [fp, #-252]
    mov r0, #0.5
    str r0, [fp, #-256]
    mov r0, #0.5
    str r0, [fp, #-260]
    mov r0, #0.5
    str r0, [fp, #-264]
    mov r0, #0.5
    str r0, [fp, #-268]
    mov r0, #0.5
    str r0, [fp, #-272]
    mov r0, #0.5
    str r0, [fp, #-276]
    mov r0, #0.5
    str r0, [fp, #-280]
    mov r0, #0.5
    str r0, [fp, #-284]
    mov r0, #0.5
    str r0, [fp, #-288]
    ldr r0, [fp, #-208]
    ldr r1, [fp, #-228]
    mul r0, r0, r1
    str r0, [fp, #-292]
    ldr r0, [fp, #-216]
    ldr r1, [fp, #-240]
    mul r0, r0, r1
    str r0, [fp, #-296]
    ldr r0, [fp, #-292]
    ldr r1, [fp, #-296]
    add r0, r0, r1
    str r0, [fp, #-300]
    ldr r0, [fp, #-224]
    ldr r1, [fp, #-252]
    mul r0, r0, r1
    str r0, [fp, #-304]
    ldr r0, [fp, #-300]
    ldr r1, [fp, #-304]
    add r0, r0, r1
    str r0, [fp, #-308]
    ldr r0, [fp, #-308]
    ldr r1, [fp, #-276]
    add r0, r0, r1
    str r0, [fp, #-312]
    ldr r0, [fp, #-312]
    str r0, [fp, #-316]
    ldr r0, [fp, #-208]
    ldr r1, [fp, #-232]
    mul r0, r0, r1
    str r0, [fp, #-320]
    ldr r0, [fp, #-216]
    ldr r1, [fp, #-244]
    mul r0, r0, r1
    str r0, [fp, #-324]
    ldr r0, [fp, #-320]
    ldr r1, [fp, #-324]
    add r0, r0, r1
    str r0, [fp, #-328]
    ldr r0, [fp, #-224]
    ldr r1, [fp, #-256]
    mul r0, r0, r1
    str r0, [fp, #-332]
    ldr r0, [fp, #-328]
    ldr r1, [fp, #-332]
    add r0, r0, r1
    str r0, [fp, #-336]
    ldr r0, [fp, #-336]
    ldr r1, [fp, #-280]
    add r0, r0, r1
    str r0, [fp, #-340]
    ldr r0, [fp, #-340]
    str r0, [fp, #-344]
    ldr r0, [fp, #-208]
    ldr r1, [fp, #-236]
    mul r0, r0, r1
    str r0, [fp, #-348]
    ldr r0, [fp, #-216]
    ldr r1, [fp, #-248]
    mul r0, r0, r1
    str r0, [fp, #-352]
    ldr r0, [fp, #-348]
    ldr r1, [fp, #-352]
    add r0, r0, r1
    str r0, [fp, #-356]
    ldr r0, [fp, #-224]
    ldr r1, [fp, #-260]
    mul r0, r0, r1
    str r0, [fp, #-360]
    ldr r0, [fp, #-356]
    ldr r1, [fp, #-360]
    add r0, r0, r1
    str r0, [fp, #-364]
    ldr r0, [fp, #-364]
    ldr r1, [fp, #-284]
    add r0, r0, r1
    str r0, [fp, #-368]
    ldr r0, [fp, #-368]
    str r0, [fp, #-372]
    ldr r0, [fp, #-208]
    ldr r1, [fp, #-236]
    mul r0, r0, r1
    str r0, [fp, #-376]
    ldr r0, [fp, #-216]
    ldr r1, [fp, #-248]
    mul r0, r0, r1
    str r0, [fp, #-380]
    ldr r0, [fp, #-376]
    ldr r1, [fp, #-380]
    add r0, r0, r1
    str r0, [fp, #-384]
    ldr r0, [fp, #-224]
    ldr r1, [fp, #-272]
    mul r0, r0, r1
    str r0, [fp, #-388]
    ldr r0, [fp, #-384]
    ldr r1, [fp, #-388]
    add r0, r0, r1
    str r0, [fp, #-392]
    ldr r0, [fp, #-392]
    ldr r1, [fp, #-288]
    add r0, r0, r1
    str r0, [fp, #-396]
    ldr r0, [fp, #-396]
    str r0, [fp, #-400]
    ldr r0, [fp, #-404]
    str r0, [fp, #-408]
    ldr r0, [fp, #-408]
    str r0, [fp, #-412]
    ldr r0, [fp, #-404]
    str r0, [fp, #-416]
    ldr r0, [fp, #-416]
    str r0, [fp, #-420]
    ldr r0, [fp, #-404]
    str r0, [fp, #-424]
    ldr r0, [fp, #-424]
    str r0, [fp, #-428]
    ldr r0, [fp, #-404]
    str r0, [fp, #-432]
    ldr r0, [fp, #-432]
    str r0, [fp, #-436]
    ldr r0, [fp, #-444]
    str r0, [fp, #-448]
    ldr r0, [fp, #-456]
    str r0, [fp, #-460]
    ldr r0, [fp, #-456]
    str r0, [fp, #-468]
    ldr r0, [fp, #-456]
    str r0, [fp, #-476]
    ldr r0, [fp, #-456]
    str r0, [fp, #-484]
    ldr r0, [fp, #-420]
    mov r1, #0.5
    cmp r0, r1
    movgt r0, #1
    movle r0, #0
    str r0, [fp, #-488]
    ldr r0, [fp, #-488]
    cmp r0, #0
    beq L12
    ldr r0, [fp, #-456]
    str r0, [fp, #-500]
L12:
    ldr r0, [fp, #-436]
    mov r1, #0.5
    cmp r0, r1
    movgt r0, #1
    movle r0, #0
    str r0, [fp, #-504]
    ldr r0, [fp, #-504]
    cmp r0, #0
    beq L13
    ldr r0, [fp, #-456]
    str r0, [fp, #-508]
L13:
    b .return_exit
    add sp, sp, #256
    pop {fp, pc}
L11: