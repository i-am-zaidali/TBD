# file to define models that will be used in the AST of the language

from .lexer_models import *
from dataclasses import dataclass, field
import typing

__all__ = (
    "Node",
    "Literal",
    "String",
    "Number",
    "Bool",
    "Null",
    "Statement",
    "Expression",
    "BinaryExp",
    "VarDec",
    "ConstDec",
    "Program",
    "literals",
    "UnaryExp",
    "AssignmentExp",
    "Identifier",
    "Dict",
    "Property",
    "ObjectExp",
    "FunctionCallExp",
    "MemberExp",
)


class Node:
    pass  # base class for all nodes in the AST


class Statement(Node):
    pass


class Expression(Statement):
    pass


@dataclass
class Literal(Expression):
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


@dataclass
class Identifier(Expression):
    # yes identifiers are expressions. They do return a value.
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
    body: list[Statement | Token | Expression]


@dataclass
class Property(Expression):
    name: Identifier
    value: Expression


@dataclass
class ObjectExp(Expression):
    properties: list[Property]


@dataclass
class FunctionCallExp(Expression):
    # function calls will not be like traditional function calls with paranthesis.
    # they will be like this:
    # { function ...arguments}
    caller: Expression
    arguments: list[AssignmentExp]
    # I only want to support keyword arguments. No positional arguments.
    # so if you try using positional arguments, it will just consider them as keyword arguments.
    # so a function call like this:
    # { function a=a, b}
    # b will be passed as a kwarg with the name "b" and the value of the variable b (if it exists).


@dataclass
class MemberExp(Expression):
    object: Expression
    value: Expression
    computed: bool


literals: dict[
    typing.Type[int | float | str | bool] | typing.Literal["null"], Literal
] = {
    int: Number,
    float: Number,
    str: String,
    bool: Bool,
    "null": Null,
}
