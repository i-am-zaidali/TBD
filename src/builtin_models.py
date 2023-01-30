from .parser_models import Expression, Literal, Identifier
from .exceptions import NotSupported, PropertyNotFound, InterpreterException
from dataclasses import dataclass, field
import typing

__all__ = (
    "Scope",
    "String",
    "Number",
    "Bool",
    "Null",
    "Dict",
    "BuiltInFunction",
    "Function",
    "Array",
    "literals",
)


@dataclass
class Scope:
    parent: typing.Optional["Scope"] = None
    variables: dict = field(default_factory=dict)
    constants: dict = field(default_factory=dict)

    def resolve_var_scope(self, name: str) -> typing.Optional["Scope"]:
        if name in self.variables or name in self.constants:
            return self

        if self.parent is not None:
            return self.parent.resolve_var_scope(name)

        return None

    def get_var(self, name: str) -> Literal | None:
        scope = self.resolve_var_scope(name)
        if scope is None:
            raise InterpreterException(f"Variable {name} is not defined!")
        return scope.variables.get(name, self.constants.get(name, None))

    def declare_var(self, name: str, value: typing.Any, constant: bool = False):
        if self.resolve_var_scope(name) is self:
            raise InterpreterException(f"Variable {name} is already defined!")
        if constant:
            self.constants[name] = value
            return
        self.variables[name] = value

    def assign_var(self, name: str, value: typing.Any):
        scope = self.resolve_var_scope(name)
        if scope is None:
            raise InterpreterException(f"Variable {name} is not defined!")
        if name in scope.constants:
            raise InterpreterException(f"Variable {name} is a constant and cannot be reassigned!")
        scope.variables[name] = value

    def force_assign_var(self, name: str, value: typing.Any, constant: bool = False):
        """This method is used to assign variables forcefully, bypassing scope checks and whether the variable exists or not."""
        if not constant:
            self.variables[name] = value
            return
        self.constants[name] = value

    def is_constant(self, name: str) -> bool:
        scope = self.resolve_var_scope(name)
        if not scope:
            raise InterpreterException(f"Variable {name} is not defined!")
        return name in scope.constants


@dataclass
class String(Literal):
    value: str

    _PROPERTIES = {
        "length": lambda self: Number(len(self.value)),
        "upper": lambda self: String(self.value.upper()),
        "lower": lambda self: String(self.value.lower()),
        "capitalize": lambda self: String(self.value.capitalize()),
        "title": lambda self: String(self.value.title()),
        "strip": lambda self: String(self.value.strip()),
    }

    def is_arithmetic_compatible(self, other: Literal):
        return isinstance(other, String)

    def __add(self, other: Literal):
        if self.is_arithmetic_compatible(other):
            return String(self.value + other.value)

        raise NotSupported(f"Cannot add {self} and {other}")

    def __sub(self, other: Literal):
        raise NotSupported(f"Cannot subtract {self} and {other}")

    def __mul(self, other: Literal):
        if isinstance(other, Number):
            return String(self.value * other.value)
        raise NotSupported(f"Cannot multiply {self} and {other}")

    def __div(self, other: "Literal"):
        raise NotSupported(f"Cannot divide {self} and {other}")

    def __mod(self, other: "Literal"):
        raise NotSupported(f"Cannot mod {self} and {other}")

    def __eq(self, other: "Literal"):
        if self.is_arithmetic_compatible(other):
            return Bool(self.value == other.value)
        raise NotSupported(f"Cannot compare {self} and {other}")

    def _access_property(self, property: str):
        if property in self._PROPERTIES:
            return self._PROPERTIES[property]

        raise PropertyNotFound(f"Property {property} not found in {self}")


@dataclass
class Number(Literal):
    value: int | float

    def is_arithmetic_compatible(self, other: Literal):
        return isinstance(other, Number) or isinstance(other, Bool)


@dataclass
class Bool(Literal):
    value: bool

    def is_arithmetic_compatible(self, other: Literal):
        return isinstance(other, Number) or isinstance(other, Bool)


@dataclass
class Null(Literal):
    value: None = None

    def is_arithmetic_compatible(self, other: Literal):
        return False


@dataclass
class Dict(Literal):
    value: dict[str, Literal] = field(default_factory=dict[str, Literal])

    def _access_property(self, property: str):
        return self.value.get(property, Null())


@dataclass
class Array(Literal):
    value: list[Literal] = field(default_factory=list[Literal])

    def _access_property(self, property: str):
        if property == "length":
            return Number(len(self.value))

        return self.value[int(property)]


@dataclass
class BuiltInFunction(Expression):
    python_function: typing.Callable[[typing.Dict[str, Literal]], typing.Any]
    # a callback function that takes a list of arguments and returns a value


@dataclass
class Function(Expression):
    name: str
    parameters: list[Identifier]
    body: list[Expression]
    returns: Expression
    declarative_scope: Scope


literals: dict[
    typing.Type[int | float | str | bool | None] | typing.Literal["null"],
    typing.Type[Literal],
] = {
    int: Number,
    float: Number,
    str: String,
    bool: Bool,
    "null": Null,
    type(None): Null,
}
