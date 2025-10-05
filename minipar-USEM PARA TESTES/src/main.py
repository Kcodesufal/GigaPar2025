# main utility to compile source -> IR and to emit ARM .s using codegen_armv7
import os, sys
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.emit_ir import Generator
from src.codegen_armv7 import gen as gen_arm
def compile_to_ir(text):
    p = Parser(text); prog = p.parse()
    sa = SemanticAnalyzer(); sa.analyze(prog)
    gen = Generator(); ir = gen.gen_program(prog)
    return ir
def emit_arm_from_source(text):
    ir = compile_to_ir(text)
    asm = gen_arm(ir)
    return asm
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python -m src.main tests/file.minipar'); sys.exit(1)
    infile = sys.argv[1]; text = open(infile).read()
    asm = emit_arm_from_source(text)
    out = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build', os.path.basename(infile).replace('.minipar', '.s'))
    with open(out, 'w') as f: f.write(asm)
    print('Wrote', out)
