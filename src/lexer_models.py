from enum import Enum
from dataclasses import dataclass

__all__ = ("Token", "TokenType", "SUBTYPE", "KEYWORDS", "OPERATORS", "LITERALS")


class TokenType(Enum):
    KEYWORD = "KEYWORD"
    LITERAL = "LITERAL"
    COLON = "COLON"
    COMMA = "COMMA"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LSQUARE = "LSQUARE"
    RSQUARE = "RSQUARE"
    LCURLY = "LCURLY"
    RCURLY = "RCURLY"
    OPERATOR = "OPERATOR"
    DOT = "DOT"
    BACKSLASH = "BACKSLASH"
    IDENTIFIER = "IDENTIFIER"
    NEWLINE = "NEWLINE"
    TAB = "TAB"
    EOF = "EOF"
    INVALID = "INVALID"
    HASH = "HASH"
    COMMENT = "COMMENT"

    def __str__(self):
        return self.value


class SUBTYPE(Enum):
    def __str__(self) -> str:
        return self.value


class LITERALS(SUBTYPE):
    STRING = "STRING"
    NUMBER = "NUMBER"
    BOOL = "BOOL"
    NULL = "NULL"


class KEYWORDS(SUBTYPE):
    LET = "let"
    CONST = "const"
    LOOP = "loop"
    TIMES = "times"
    SEND = "send"
    TO = "to"
    TAG = "tag"
    RETURN = "return"
    IF = "if"
    ELSE = "else"


class OPERATORS(SUBTYPE):
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    POWER = "^"
    DIVIDE = "/"
    REMAINDER = "%"
    ASSIGNMENT = "="
    PLUS_EQUALS = getattr(PLUS, "value", "+") + getattr(ASSIGNMENT, "value", "=")
    MINUS_EQUALS = getattr(MINUS, "value", "-") + getattr(ASSIGNMENT, "value", "=")
    MULTIPLY_EQUALS = getattr(MULTIPLY, "value", "*") + getattr(ASSIGNMENT, "value", "=")
    DIVIDE_EQUALS = getattr(DIVIDE, "value", "/") + getattr(ASSIGNMENT, "value", "=")
    POWER_EQUALS = getattr(POWER, "value", "^") + getattr(ASSIGNMENT, "value", "=")
    COMPARISON = "=="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GTEQUALS = getattr(GREATER_THAN, "value", ">") + getattr(ASSIGNMENT, "value", "=")
    LTEQUALS = getattr(LESS_THAN, "value", "<") + getattr(ASSIGNMENT, "value", "=")
    NEQUALS = "!" + getattr(ASSIGNMENT, "value", "=")


@dataclass
class Token:
    type: TokenType
    subtype: SUBTYPE | None
    lexeme: str
    literal: str | None | int | float
    line: int
    start_position: int
    end_position: int
