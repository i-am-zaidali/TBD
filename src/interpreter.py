from .lexer_models import *
from .lexer import Lexer
from .parser import Parser
from .parser_models import *
from .builtin_models import *
from .exceptions import InterpreterException
from typing import Any, Optional
from dataclasses import dataclass, field
from pprint import pprint

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


class Interpreter:
    def __init__(self, source: str, scope: Optional[Scope] = None) -> None:
        self.source = source
        self._lexer = Lexer(source)
        self._tokens = self._lexer.tokenize()
        self._parser = Parser(self._tokens)
        self.ast = self._parser.parse()
        # pprint(self.ast)
        self.index = 0

        self.global_scope = scope or Scope()
        # self._populate_builtins()

    def _populate_builtins(self):
        self.global_scope.declare_var("print", BuiltInFunction(print))

    def evaluate(self):
        while not self.at_end():
            res = self._eval_node(self.current())
            self.advance()
            if res is None:
                continue

            yield res

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

    def _eval_node(self, node: Node | Token, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        if isinstance(node, BinaryExp):
            return self._eval_binop(node, scope)

        elif isinstance(node, UnaryExp):
            return self._eval_unary(node, scope)

        elif isinstance(node, (VarDec, ConstDec)):
            is_const = isinstance(node, ConstDec)
            return self._eval_vardec(node, is_const, scope)

        elif isinstance(node, Null):
            return None

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

        elif isinstance(node, FunctionCallExp):
            return self._eval_function_call(node, scope)

        elif isinstance(node, ArrayExp):
            return self._eval_array(node, scope)

        elif isinstance(node, FunctionDec):
            return self._eval_function_dec(node, scope)

        elif isinstance(node, MemberExp):
            return self._eval_member_exp(node, scope)

        elif isinstance(node, IfStatement):
            return self._eval_if_statement(node, scope)

        else:
            return "Not implemented: {}".format(node)

    def _eval_binop(self, node: BinaryExp, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        left: Literal = self._eval_node(node.left, scope)
        right: Literal = self._eval_node(node.right, scope)

        if not left.is_arithmetic_compatible(right):
            raise InterpreterException(
                "Incompatible types for arithmetic operation: {} and {}".format(left, right)
            )

        l, r = left.value, right.value
        if node.operator.subtype in binops:
            result: int | float | str = binops[node.operator.subtype](l, r)
            tr = type(result)
            return literals[tr](result)

        else:
            raise InterpreterException(f"Invalid operator {node.operator.subtype}")

    def _eval_unary(self, node: UnaryExp, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        operand = self._eval_node(node.operand, scope)
        if node.operator.subtype in (OPERATORS.PLUS, OPERATORS.MINUS) and not isinstance(
            operand, Number
        ):
            raise InterpreterException(
                "Unary operator {} can only be applied to numbers!".format(node.operator.subtype)
            )

        if node.operator.subtype is OPERATORS.MINUS:
            return literals[type(operand.value)](-operand.value)

        return operand

    def _eval_vardec(self, node: VarDec, constant: bool = False, scope: Optional[Scope] = None):
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

    def _eval_assignment(self, node: AssignmentExp, scope: Optional[Scope] = None):
        scope = scope or self.global_scope

        name = None
        if isinstance(node.assignee, Identifier):
            name = node.assignee.name

        is_constant = scope.is_constant(name)
        if is_constant:
            raise InterpreterException(f"Variable {name} is a constant and cannot be reassigned!")

        res = self._eval_node(node.value, scope)
        scope.assign_var(name, res)
        return res

    def _eval_object(self, node: ObjectExp, scope: Optional[Scope] = None):
        _d = Dict()
        _d.value.update(
            {prop.name.name: self._eval_node(prop.value, scope) for prop in node.properties}
        )
        return _d

    def _eval_identifier(self, node: Identifier, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        try:
            return scope.get_var(node.name)
        except InterpreterException:
            raise InterpreterException(f"Variable {node.name} is not defined.")

    def _eval_member_exp(self, node: MemberExp, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        obj = self._eval_node(node.object, scope)
        if not isinstance(obj, (Dict, Array)) and node.computed:
            raise InterpreterException(f"Object {obj} is not subscriptable.")
        return obj._access_property(getattr(node.value, "name", node.value.value))

    def _eval_function_call(self, node: FunctionCallExp, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        function = self._eval_node(node.caller, scope)
        if isinstance(function, BuiltInFunction):
            subscope = Scope(parent=scope)
            args = {arg.name: self._eval_argument(arg, subscope) for arg in node.arguments}
            return function.python_function(args)

        elif isinstance(function, Function):
            subscope = Scope(parent=function.declarative_scope)
            # we need to loop through the arguments and params and assign them to the subscope
            # if we have a param that wasn't passed in, we need to assign it to Null
            # we also need to assign the extra arguments to the subscope anyways.

            for param in function.parameters:
                subscope.force_assign_var(param.name, Null())  # assign the param to Null

            for arg in node.arguments:
                subscope.force_assign_var(arg.name, self._eval_argument(arg, subscope))
                # assign the arg to the value
                # dual looping allows us to properly assign all arguments and parameters to the subscope

            for node in function.body:
                self._eval_node(node, subscope)

            return self._eval_node(function.returns, subscope)

        else:
            raise InterpreterException(f"{node.caller} is not callable")

    def _eval_function_dec(self, node: FunctionDec, scope: Optional[Scope] = None):
        scope = scope or self.global_scope

        def filter_probable_parameters(node: Node):
            if isinstance(node, Identifier):
                try:
                    scope.get_var(node.name)

                except InterpreterException:
                    return True

            return False

        parameters = list[Identifier](filter(filter_probable_parameters, node.body))
        func = Function(node.name, parameters, node.body, node.returns, scope)
        if node.name:
            scope.force_assign_var(node.name, func)
        else:
            return func

    def _eval_if_statement(self, node: IfStatement, scope: Scope):
        cond = self._eval_node(node.condition, scope)
        res = Null()
        if self._check_truthiness(cond):
            for node in node.body:
                res = self._eval_node(node, scope)

            return res

        else:
            if isinstance(node._else, IfStatement):
                return self._eval_if_statement(node._else, scope)

            else:
                for node in node._else:
                    res = self._eval_node(node, scope)

                return res

    def _check_truthiness(self, node: Literal) -> bool:
        if isinstance(node, Null):
            return False
        elif isinstance(node, Bool):
            return node.value
        elif isinstance(node, Number):
            return node.value != 0
        elif isinstance(node, String):
            return node.value != ""
        elif isinstance(node, Array):
            return len(node.value) != 0
        elif isinstance(node, Dict):
            return len(node.value) != 0
        else:
            return True

    def _eval_argument(self, node: FunctionArgument, scope: Scope) -> Literal:
        val = self._eval_node(node.value, scope)
        scope.force_assign_var(node.name, val)
        return val

    def _eval_array(self, node: ArrayExp, scope: Optional[Scope] = None):
        scope = scope or self.global_scope
        _a = Array()
        _a.value.extend([self._eval_node(element, scope) for element in node.elements])
        return _a
