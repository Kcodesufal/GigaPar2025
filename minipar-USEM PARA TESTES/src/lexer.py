# Lexer pseudocode + implementation (simple)
# Pseudocode (also in doc/lexer_pseudocode.txt):
# 1. Define token regex list: NUMBER, STRING, ID, OP, NEWLINE, SKIP, COMMENT
# 2. Scan input left-to-right, matching longest regex, emit tokens
# 3. Map keywords to uppercase token types (SEQ, PAR, chan, send, receive, if, else, while, print)
# 4. Provide iterator interface returning EOF at end.

import re
from collections import namedtuple
Token = namedtuple('Token', ['type','value','line','col'])
KEYWORDS = {'SEQ','PAR','chan','send','receive','if','else','while','print'}
token_spec = [
    ('NUMBER',   r'\d+'),
    ('STRING',   r'"([^"\\]|\\.)*"'),
    ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
    ('OP',       r'==|!=|<=|>=|[+\-*/=<>:,(){}]'),
    ('NEWLINE',  r'\n'),
    ('SKIP',     r'[ \t]+'),
    ('COMMENT',  r'\#.*'),
]
master = re.compile('|'.join('(?P<%s>%s)' % pair for pair in token_spec))
class Lexer:
    def __init__(self, text):
        self.text = text
        self.line = 1; self.col = 1; self.tokens = []; self._tokenize()
    def _tokenize(self):
        for mo in master.finditer(self.text):
            kind = mo.lastgroup; val = mo.group()
            if kind == 'NUMBER':
                tok = Token('NUMBER', int(val), self.line, self.col)
            elif kind == 'STRING':
                tok = Token('STRING', val[1:-1], self.line, self.col)
            elif kind == 'ID':
                if val in KEYWORDS: tok = Token(val.upper(), val, self.line, self.col)
                else: tok = Token('ID', val, self.line, self.col)
            elif kind == 'OP':
                tok = Token('OP', val, self.line, self.col)
            elif kind == 'NEWLINE':
                self.line += 1; self.col = 1; continue
            elif kind == 'SKIP' or kind == 'COMMENT':
                self.col += len(val); continue
            else:
                continue
            self.tokens.append(tok); self.col += len(val)
        self.tokens.append(Token('EOF','',self.line,self.col))
    def __iter__(self):
        return iter(self.tokens)
