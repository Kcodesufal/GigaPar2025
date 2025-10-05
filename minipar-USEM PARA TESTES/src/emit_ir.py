import src.ast as AST
from src.ir import IRBuilder
class Generator:
    def __init__(self):
        self.irb = IRBuilder()
    def gen_program(self, prog: AST.Program):
        for b in prog.blocks:
            self.gen_seq(b)
        return self.irb.code
    def gen_seq(self, seq: AST.SeqBlock):
        for s in seq.stmts: self.gen_stmt(s)
    def gen_stmt(self, stmt):
        if isinstance(stmt, AST.Assign):
            src = self.gen_expr(stmt.expr)
            if isinstance(src, tuple) and src[0] == 'const':
                tmp = self.irb.newtmp(); self.irb.emit('LOAD_CONST', src[1], None, tmp); self.irb.emit('STORE', tmp, None, stmt.target)
            else:
                self.irb.emit('STORE', src, None, stmt.target)
        elif isinstance(stmt, AST.Print):
            v = self.gen_expr(stmt.expr)
            if isinstance(v, tuple) and v[0] == 'const':
                tmp = self.irb.newtmp(); self.irb.emit('LOAD_CONST', v[1], None, tmp); self.irb.emit('PRINT', tmp)
            else:
                self.irb.emit('PRINT', v)
        elif isinstance(stmt, AST.If):
            cond = self.gen_expr(stmt.cond)
            else_label = self.irb.newlabel('else'); end_label = self.irb.newlabel('endif')
            if isinstance(cond, tuple) and cond[0]=='const':
                tmpc=self.irb.newtmp(); self.irb.emit('LOAD_CONST', cond[1], None, tmpc); self.irb.emit('JZ', tmpc, None, else_label)
            else:
                self.irb.emit('JZ', cond, None, else_label)
            if isinstance(stmt.then_branch, AST.SeqBlock): self.gen_seq(stmt.then_branch)
            else: self.gen_stmt(stmt.then_branch)
            self.irb.emit('JMP', end_label); self.irb.emit('LABEL', else_label)
            if stmt.else_branch:
                if isinstance(stmt.else_branch, AST.SeqBlock): self.gen_seq(stmt.else_branch)
                else: self.gen_stmt(stmt.else_branch)
            self.irb.emit('LABEL', end_label)
        elif isinstance(stmt, AST.While):
            start = self.irb.newlabel('while'); end = self.irb.newlabel('endw')
            self.irb.emit('LABEL', start)
            cond = self.gen_expr(stmt.cond)
            if isinstance(cond, tuple) and cond[0] == 'const':
                tmpc = self.irb.newtmp(); self.irb.emit('LOAD_CONST', cond[1], None, tmpc); self.irb.emit('JZ', tmpc, None, end)
            else:
                self.irb.emit('JZ', cond, None, end)
            if isinstance(stmt.body, AST.SeqBlock): self.gen_seq(stmt.body)
            else: self.gen_stmt(stmt.body)
            self.irb.emit('JMP', start); self.irb.emit('LABEL', end)
        elif isinstance(stmt, AST.Send):
            args = [self.gen_expr(a) for a in stmt.args]; arg_temps = []
            for a in args:
                if isinstance(a, tuple) and a[0]=='const':
                    ta = self.irb.newtmp(); self.irb.emit('LOAD_CONST', a[1], None, ta); arg_temps.append(ta)
                else:
                    arg_temps.append(a)
            self.irb.emit('SEND', stmt.channel, arg_temps, None)
        elif isinstance(stmt, AST.Receive):
            self.irb.emit('RECEIVE', stmt.channel, stmt.vars, None)
        else:
            if isinstance(stmt, AST.BinaryOp): self.gen_expr(stmt)
    def gen_expr(self, expr):
        if isinstance(expr, AST.Number): return ('const', expr.value)
        if isinstance(expr, AST.String): return ('const', expr.value)
        if isinstance(expr, AST.Var):
            tmp = self.irb.newtmp(); self.irb.emit('LOAD_VAR', expr.name, None, tmp); return tmp
        if isinstance(expr, AST.BinaryOp):
            a = self.gen_expr(expr.left); b = self.gen_expr(expr.right)
            if isinstance(a, tuple) and a[0] == 'const':
                ta = self.irb.newtmp(); self.irb.emit('LOAD_CONST', a[1], None, ta); a = ta
            if isinstance(b, tuple) and b[0] == 'const':
                tb = self.irb.newtmp(); self.irb.emit('LOAD_CONST', b[1], None, tb); b = tb
            res = self.irb.newtmp(); op = expr.op
            if op in ('+','-','*','/'): self.irb.emit(op, a, b, res)
            elif op in ('==','!=','<','>','<=','>='):
                opmap = {'==':'EQ','!=':'NE','<':'LT','>':'GT','<=':'LE','>=':'GE'}; self.irb.emit(opmap[op], a, b, res)
            else: raise Exception('Unknown binary op: ' + op)
            return res
        raise Exception('Unknown expr')
