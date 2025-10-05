import src.ast as AST
class SemanticError(Exception): pass
class SemanticAnalyzer:
    def __init__(self): self.vars = set()
    def analyze(self, program: AST.Program):
        for block in program.blocks: self._analyze_seq(block)
    def _analyze_seq(self, seq: AST.SeqBlock):
        for stmt in seq.stmts: self._analyze_stmt(stmt)
    def _analyze_stmt(self, stmt):
        if isinstance(stmt, AST.Assign):
            self._analyze_expr(stmt.expr); self.vars.add(stmt.target)
        elif isinstance(stmt, AST.Print):
            self._analyze_expr(stmt.expr)
        elif isinstance(stmt, AST.While):
            self._analyze_expr(stmt.cond)
            if isinstance(stmt.body, AST.SeqBlock):
                for s in stmt.body.stmts: self._analyze_stmt(s)
            else:
                self._analyze_stmt(stmt.body)
        elif isinstance(stmt, AST.Send):
            for a in stmt.args: self._analyze_expr(a)
        elif isinstance(stmt, AST.Receive):
            for v in stmt.vars:
                if v not in self.vars: self.vars.add(v)
        elif isinstance(stmt, AST.If):
            self._analyze_expr(stmt.cond)
            if isinstance(stmt.then_branch, AST.SeqBlock):
                for s in stmt.then_branch.stmts: self._analyze_stmt(s)
            else:
                self._analyze_stmt(stmt.then_branch)
            if stmt.else_branch:
                if isinstance(stmt.else_branch, AST.SeqBlock):
                    for s in stmt.else_branch.stmts: self._analyze_stmt(s)
                else:
                    self._analyze_stmt(stmt.else_branch)
        elif isinstance(stmt, AST.BinaryOp):
            self._analyze_expr(stmt)
    def _analyze_expr(self, expr):
        if isinstance(expr, AST.Number): return
        if isinstance(expr, AST.String): return
        if isinstance(expr, AST.Var):
            if expr.name not in self.vars:
                raise SemanticError(f"Variable '{expr.name}' used before assignment")
        if isinstance(expr, AST.BinaryOp):
            self._analyze_expr(expr.left); self._analyze_expr(expr.right)
