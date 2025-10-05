MiniPar Compiler - Final Delivery (matches PDF requirements)
------------------------------------------------------------
Included:
- src/: lexer, parser, semantic, IR generator, ARMv7 code generator (componentized).
- tests/: Minipar test programs (factorial, fibonacci, channel_calc).
- build/: output assembly .s will be generated here by running the pipeline.
- doc/: pseudocode required by the PDF (lexer, parser, semantic, symbol table, IR, ARM codegen).

What matches the PDF (Tema1 - Projeto1 - MiniPar 2025.1):
- Implements lexical, syntactic and semantic analyzers, symbol table pseudocode, 3-address IR and a generator to ARMv7 assembly.
- Emits ARMv7 .s files for the test programs; these .s files are suitable for the CPUlator emulator (see examples in the PDF). PDF reference: see original PDF included in the submission. fileciteturn0file0

Limitations and notes:
- PRINT in generated assembly stores results into memory labels PRINT_OUT_n so you can inspect values using CPUlator Memory view (this follows the examples in the PDF where results are stored into memory labels like RESULT, FIB_MEM, etc.).
- PAR (parallel) and channel network communication (send/receive across hosts via sockets) are part of the language specification in the PDF. For CPUlator execution, full socket-based channel runtime is environment-dependent; this package emits markers for SEND/RECEIVE in the ARM code. If you want a concrete ARM runtime implementation (for example using semihosting, UART, or a simulated memory mailbox) I can add that — tell me which approach you want.
- The project contains pseudocode files requested in the PDF (lexer, parser, semantic, symbol table, IR, ARM codegen) and a README mapping deliverables to the PDF.

How to generate assembly:
1) From project root:
   python -m src.main tests/factorial.minipar
   Output: build/factorial.s

2) Load the generated .s into CPUlator (paste into the Code window or upload) and Assemble+Run.
3) Inspect memory symbols (PRINT_OUT_0, etc.) in CPUlator Memory panel to see printed values (or RESULT / FIB_MEM in examples).

If you want, I will now:
- (A) Add semihosting/puts so `print` appears on CPUlator console, OR
- (B) Implement a simple ARM runtime to emulate channel send/receive for the `calculadora` example (so server/client can be simulated), OR
- (C) Produce a PDF-style report + UML diagrams.

Tell me which of A/B/C to do next and I'll update the ZIP immediately.


Updates: semihosting print routine added (print_int) using SWI; simple calculadora SEND+RECEIVE patterns are inlined at compile time when args are constants.
