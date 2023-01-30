# file to define models that will be used in the AST of the language

from .lexer_models import *
from dataclasses import dataclass
import typing

__all__ = (
    "Node",
    "Literal",
    "Statement",
    "IfStatement",
    "FunctionArgument",
    "Expression",
    "BinaryExp",
    "VarDec",
    "ConstDec",
    "Program",
    "UnaryExp",
    "AssignmentExp",
    "Identifier",
    "Property",
    "ObjectExp",
    "FunctionDec",
    "ArrayExp",
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
class IfStatement(Statement):
    condition: Expression
    body: list[Statement]
    _else: list[Statement] | typing.Optional["IfStatement"]


@dataclass
class Literal(Expression):
    value: str | bool | float | int | None | dict | list = None

    def is_arithmetic_compatible(self, other: "Literal"):
        raise NotImplementedError()

    def __add(self, other: "Literal"):
        raise NotImplementedError()

    def __sub(self, other: "Literal"):
        raise NotImplementedError()

    def __mul(self, other: "Literal"):
        raise NotImplementedError()

    def __div(self, other: "Literal"):
        raise NotImplementedError()

    def __mod(self, other: "Literal"):
        raise NotImplementedError()

    def __pow(self, other: "Literal"):
        raise NotImplementedError()

    def __eq(self, other: "Literal"):
        raise NotImplementedError()

    def __access_property(self, property: str):
        raise NotImplementedError()


@dataclass
class Identifier(Expression):
    # yes identifiers are expressions. They do return a value.
    name: str


@dataclass
class BinaryExp(Expression):
    left: Expression
    operator: Token
    right: Expression


@dataclass
class UnaryExp(Expression):
    operator: Token
    operand: Expression


@dataclass
class AssignmentExp(Expression):
    assignee: Expression
    value: Expression


@dataclass
class VarDec(Statement):
    name: str
    value: Expression


class ConstDec(VarDec):
    pass


@dataclass
class FunctionArgument(VarDec):
    pass


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
class ArrayExp(Expression):
    elements: list[Expression]


@dataclass
class FunctionCallExp(Expression):
    # function calls will not be like traditional function calls with paranthesis.
    # they will be like this:
    # { function ...arguments}
    caller: Expression
    arguments: list[FunctionArgument]
    # I only want to support keyword arguments. No positional arguments.
    # so if you try using positional arguments, it will just consider them as keyword arguments.
    # so a function call like this:
    # { function a=a, b}
    # b will be passed as a kwarg with the name "b" and the value of the variable b (if it exists).
    # if literal values are passed, they will be accumulated in a list and passed as a single argument `__args`


@dataclass
class FunctionDec(Statement):
    name: str | None
    body: list[Statement]
    returns: Expression


@dataclass
class MemberExp(Expression):
    object: Expression
    value: Literal | Identifier
    computed: bool
