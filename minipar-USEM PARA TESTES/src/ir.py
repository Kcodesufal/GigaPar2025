class Instr:
    def __init__(self, op, a=None, b=None, c=None):
        self.op = op; self.a = a; self.b = b; self.c = c
    def __repr__(self):
        parts=[self.op]
        for x in (self.a,self.b,self.c):
            if x is not None: parts.append(str(x))
        return ' '.join(parts)
class IRBuilder:
    def __init__(self): self.code=[]; self.tmpcnt=0; self.labelcnt=0
    def newtmp(self):
        t = f"t{self.tmpcnt}"; self.tmpcnt+=1; return t
    def newlabel(self,prefix='L'):
        l = f"{prefix}{self.labelcnt}"; self.labelcnt+=1; return l
    def emit(self, op, a=None, b=None, c=None):
        instr=Instr(op,a,b,c); self.code.append(instr); return instr
