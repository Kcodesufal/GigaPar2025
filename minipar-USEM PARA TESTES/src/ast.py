from dataclasses import dataclass
from typing import List, Optional
@dataclass
class Node: pass
@dataclass
class Program(Node):
    blocks: List[Node]
@dataclass
class SeqBlock(Node):
    stmts: List[Node]
@dataclass
class Assign(Node):
    target: str
    expr: Node
@dataclass
class While(Node):
    cond: Node
    body: Node
@dataclass
class BinaryOp(Node):
    op: str
    left: Node
    right: Node
@dataclass
class Number(Node):
    value: int
@dataclass
class String(Node):
    value: str
@dataclass
class Var(Node):
    name: str
@dataclass
class Print(Node):
    expr: Node
@dataclass
class If(Node):
    cond: Node
    then_branch: Node
    else_branch: Optional[Node] = None
@dataclass
class Send(Node):
    channel: str
    args: list
@dataclass
class Receive(Node):
    channel: str
    vars: list
