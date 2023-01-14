from .lexer_models import *
from .lexer import Lexer
from .parser import Parser
from .parser_models import *
from .exceptions import InterpreterException
from typing import Any, Optional
from dataclasses import dataclass, field

binops = {
    OPERATORS.PLUS: lambda l, r: l + r,
    OPERATORS.MINUS: lambda l, r: l - r,
    OPERATORS.MULTIPLY: lambda l, r: l * r,
    OPERATORS.DIVIDE: lambda l, r: l / r,
    OPERATORS.REMAINDER: lambda l, r: l % r,
    OPERATORS.POWER: lambda l, r: l**r,
    OPERATORS.COMPARISON: lambda l, r: l == r,
    OPERATORS.NEQUALS: lambda l, r: l != r,
    OPERATORS.GREATER_THAN: lambda l, r: l > r,
    OPERATORS.LESS_THAN: lambda l, r: l < r,
    OPERATORS.GTEQUALS: lambda l, r: l >= r,
    OPERATORS.LTEQUALS: lambda l, r: l <= r,
}


@dataclass
class Scope:
    parent: Optional["Scope"] = None
    variables: dict = field(default_factory=dict)
    constants: dict = field(default_factory=dict)

    def resolve_var_scope(self, name: str) -> "Scope":
        if name in self.variables or name in self.constants:
            return self

        if self.parent is not None:
            return self.parent.resolve_var_scope(name)

        raise InterpreterException(f"Variable {name} is not defined!")

    def get_var(self, name: str) -> Literal | None:
        scope = self.resolve_var_scope(name)
        return scope.variables.get(name, self.constants.get(name, None))

    def declare_var(self, name: str, value: Any, constant: bool = False):
        if name in self.variables or name in self.constants:
            raise InterpreterException(f"Variable {name} is already defined!")
        if constant:
            self.constants[name] = value
            return
        self.variables[name] = value

    def assign_var(self, name: str, value: Any):
        scope = self.resolve_var_scope(name)
        if name in scope.constants:
            raise InterpreterException(
                f"Variable {name} is a constant and cannot be reassigned!"
            )
        scope.variables[name] = value

    def is_constant(self, name: str) -> bool:
        scope = self.resolve_var_scope(name)
        return name in scope.constants


class Interpreter:
    def __init__(self, source: str, scope: Scope = None) -> None:
        self.source = source
        self._lexer = Lexer(source)
        self._tokens = self._lexer.tokenize()
        self._parser = Parser(self._tokens)
        self.ast = self._parser.parse()
        self.index = 0

        self.global_scope = scope or Scope()

    def evaluate(self):
        while not self.at_end():
            yield self._eval_node(self.current())
            self.advance()

    def advance(self):
        self.index += 1
        if self.at_end():
            return None
        return self.ast.body[self.index]

    def at_end(self):
        return (
            self.index > (len(self.ast.body) - 1)
            or getattr(self.current(), "type", None) is TokenType.EOF
        )

    def current(self):
        return self.ast.body[self.index]

    def _eval_node(self, node: Node | Token, scope: Scope = None):
        scope = scope or self.global_scope
        if isinstance(node, BinaryExp):
            return self._eval_binop(node, scope)

        elif isinstance(node, (VarDec, ConstDec)):
            is_const = isinstance(node, ConstDec)
            return self._eval_vardec(node, is_const, scope)

        elif isinstance(node, AssignmentExp):
            return self._eval_assignment(node, scope)

        elif isinstance(node, Literal):
            return node

        elif isinstance(node, Token):
            if node.type is TokenType.NEWLINE:
                return

        elif isinstance(node, Identifier):
            return self._eval_identifier(node, scope)

        elif isinstance(node, ObjectExp):
            return self._eval_object(node, scope)

        else:
            return "Not implemented: {}".format(node)

    def _eval_binop(self, node: BinaryExp, scope: Scope = None):
        scope = scope or self.global_scope
        left: Literal = self._eval_node(node.left, scope)
        right: Literal = self._eval_node(node.right, scope)

        if not left.is_arithmetic_compatible(right):
            raise InterpreterException(
                "Incompatible types for arithmetic operation: {} and {}".format(
                    left, right
                )
            )

        l, r = left.value, right.value
        if node.operator.subtype in binops:
            result: int | float | str = binops[node.operator.subtype](l, r)
            tr = type(result)
            return literals[tr](result)

        else:
            raise InterpreterException(f"Invalid operator {node.operator.subtype}")

    def _eval_vardec(self, node: VarDec, constant: bool = False, scope: Scope = None):
        scope = scope or self.global_scope
        try:
            scope.get_var(node.name)
        except InterpreterException:
            pass
        else:
            raise InterpreterException(
                f"Variables cannot be redeclared with the let/const keyword!"
            )

        val = self._eval_node(node.value, scope)

        if isinstance(val, Token) and val.type is TokenType.IDENTIFIER:
            raise InterpreterException(f"Variable {val.lexeme} is not defined.")

        scope.declare_var(node.name, val, constant)
        return Null()

    def _eval_assignment(self, node: AssignmentExp, scope=None):
        scope = scope or self.global_scope

        print(node)
        try:
            name = None
            if isinstance(node.assignee, Identifier):
                name = node.assignee.name

            if scope.is_constant(name):
                raise InterpreterException(
                    f"Variable {name} is a constant and cannot be reassigned!"
                )

        except InterpreterException:
            raise InterpreterException(
                f"Variable {name} needs to be defined first with the let/const keyword!"
            )

        else:
            res = self._eval_node(node.value, scope)
            scope.assign_var(name, res)
            return res

    def _eval_object(self, node: ObjectExp, scope: Scope = None):
        _d = Dict()
        _d.values.update(
            {
                prop.name.name: self._eval_node(prop.value, scope)
                for prop in node.properties
            }
        )
        return _d

    def _eval_identifier(self, node: Identifier, scope: Scope = None):
        scope = scope or self.global_scope
        try:
            return scope.get_var(node.name)
        except InterpreterException:
            raise InterpreterException(f"Variable {node.name} is not defined.")
