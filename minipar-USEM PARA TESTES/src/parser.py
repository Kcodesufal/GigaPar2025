# Parser pseudocode in doc/parser_pseudocode.txt
from src.lexer import Lexer, Token
import src.ast as AST
class ParseError(Exception): pass
class Parser:
    def __init__(self, text):
        self.tokens = list(Lexer(text)); self.pos = 0
    def peek(self):
        if self.pos < len(self.tokens): return self.tokens[self.pos]
        return Token('EOF','',0,0)
    def advance(self): t = self.peek(); self.pos += 1; return t
    def expect(self, typ, val=None):
        t = self.peek()
        if t.type != typ and (val is None or t.value != val):
            raise ParseError(f'Expected {typ} {val}, got {t}')
        return self.advance()
    def parse(self):
        blocks = []
        while self.peek().type != 'EOF':
            if self.peek().type == 'SEQ': blocks.append(self.parse_seq())
            else: blocks.append(self.parse_seq())
        return AST.Program(blocks)
    def parse_seq(self):
        if self.peek().type == 'SEQ': self.advance()
        stmts = []
        while self.peek().type not in ('EOF','PAR','SEQ'):
            if (self.peek().type == 'ID' and self.peek().value == 'chan') or (self.peek().type == 'ID' and self.peek().value == 'c_channel'):
                self.advance(); self.expect('ID'); self.expect('ID'); self.expect('ID'); continue
            stmts.append(self.parse_stmt())
        return AST.SeqBlock(stmts)
    def parse_stmt(self):
        t = self.peek()
        if t.type == 'PRINT':
            self.advance(); self.expect('OP','('); expr = self.parse_expr(); self.expect('OP',')'); return AST.Print(expr)
        if t.type == 'WHILE': return self.parse_while()
        if t.type == 'IF': return self.parse_if()
        if t.type == 'SEND' or (t.type == 'ID' and t.value == 'send'): return self.parse_send()
        if t.type == 'RECEIVE' or (t.type == 'ID' and t.value == 'receive'): return self.parse_receive()
        if t.type == 'ID':
            if self.pos+1 < len(self.tokens) and self.tokens[self.pos+1].value == '=':
                return self.parse_assign()
            else:
                return self.parse_expr()
        raise ParseError(f'Unexpected token in statement: {t}')
    def parse_assign(self):
        name = self.expect('ID').value; self.expect('OP','='); expr = self.parse_expr(); return AST.Assign(name, expr)
    def parse_while(self):
        self.expect('WHILE'); self.expect('OP','('); cond = self.parse_expr(); self.expect('OP',')'); body = self.parse_stmt_or_block(); return AST.While(cond, body)
    def parse_if(self):
        self.expect('IF'); self.expect('OP','('); cond = self.parse_expr(); self.expect('OP',')'); then_branch = self.parse_stmt_or_block(); else_branch = None
        if self.peek().type == 'ELSE': self.advance(); else_branch = self.parse_stmt_or_block()
        return AST.If(cond, then_branch, else_branch)
    def parse_send(self):
        if self.peek().type == 'SEND': self.advance()
        else: self.expect('ID')
        self.expect('OP','(')
        if self.peek().type not in ('ID','STRING'): raise ParseError('Expected channel identifier in send')
        ch = self.expect(self.peek().type).value
        args = []
        while self.peek().value == ',': self.expect('OP',','); args.append(self.parse_expr())
        self.expect('OP',')'); return AST.Send(ch, args)
    def parse_receive(self):
        if self.peek().type == 'RECEIVE': self.advance()
        else: self.expect('ID')
        self.expect('OP','(')
        if self.peek().type != 'ID': raise ParseError('Expected channel id in receive')
        ch = self.expect('ID').value; vars = []
        while self.peek().value == ',': self.expect('OP',','); vars.append(self.expect('ID').value)
        self.expect('OP',')'); return AST.Receive(ch, vars)
    def parse_stmt_or_block(self):
        if self.peek().type == 'SEQ': return self.parse_seq()
        else: return self.parse_stmt()
    def parse_expr(self, min_prec=0):
        t = self.peek()
        if t.type == 'NUMBER': left = AST.Number(self.advance().value)
        elif t.type == 'STRING': left = AST.String(self.advance().value)
        elif t.type == 'ID': left = AST.Var(self.advance().value)
        elif t.type == 'OP' and t.value == '(':
            self.advance(); left = self.parse_expr(); self.expect('OP',')')
        else:
            raise ParseError(f'Unexpected token in expression: {t}')
        while True:
            tok = self.peek()
            if tok.type == 'OP' and tok.value in ('+','-','*','/','==','!=','<','>','<=','>='):
                prec = self._prec(tok.value)
                if prec < min_prec: break
                op = self.advance().value
                right = self.parse_expr(prec+1)
                left = AST.BinaryOp(op, left, right)
            else:
                break
        return left
    def _prec(self, op):
        if op in ('*','/'): return 20
        if op in ('+','-'): return 10
        if op in ('==','!=','<','>','<=','>='): return 5
        return 0
