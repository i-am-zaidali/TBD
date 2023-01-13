# file to define models that will be used in the AST of the language

from .lexer_models import *
from dataclasses import dataclass, field
import typing

__all__ = ("Node", "Literal", "String", "Number", "Bool", "Null", "Statement", "Expression", "BinaryExp", "VarDec", "ConstDec", "Program", "literals", "UnaryExp", "AssignmentExp", "Identifier", "Dict", "Property", "ObjectExp")

class Node:
    pass # base class for all nodes in the AST

@dataclass
class Literal(Node):    
    def is_arithmetic_compatible(self, other: "Literal"):
        raise NotImplementedError()

@dataclass
class String(Literal):
    value: str
    def is_arithmetic_compatible(self, other: "Literal"):
        return isinstance(other, String)

@dataclass    
class Number(Literal):
    value: int | float
    def is_arithmetic_compatible(self, other: "Literal"):
        return isinstance(other, Number) or isinstance(other, Bool)

@dataclass    
class Bool(Literal):
    value: bool
    def is_arithmetic_compatible(self, other: "Literal"):
        return isinstance(other, Number) or isinstance(other, Bool)

@dataclass    
class Null(Literal):
    value: None = None
    def is_arithmetic_compatible(self, other: "Literal"):
        return False
    
@dataclass
class Dict(Literal):
    values: dict[str, Literal] = field(default_factory=dict[str, Literal])

class Statement(Node):
    pass
    
class Expression(Statement):
    pass

@dataclass
class Identifier(Expression): # yes identifiers are expressions. They do return a value.
    name: str
    
@dataclass
class BinaryExp(Expression):
    left: typing.Union[Token, "BinaryExp"]
    operator: Token
    right: typing.Union[Token, "BinaryExp"]
    
@dataclass
class UnaryExp(Expression):
    operator: Token
    operand: typing.Union[Token, "UnaryExp"]
    
@dataclass
class AssignmentExp(Expression):
    assignee: Expression
    value: Expression
    
@dataclass
class VarDec(Statement):
    name: str
    value: Expression
    
@dataclass
class ConstDec(Statement):
    name: str
    value: Expression

@dataclass
class Program(Node):
    body: list[Statement|Token|Expression]

@dataclass
class Property(Expression):
    name: Identifier
    value: Expression
    
@dataclass
class ObjectExp(Expression):
    properties: list[Property]
    
    
literals: dict[typing.Type[int | float | str | bool] | typing.Literal["null"], Literal] = {
    int: Number,
    float: Number,
    str: String,
    bool: Bool,
    "null": Null,
}
    