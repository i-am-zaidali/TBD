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
    SQUARER = "SQUARER"
    SQUAREL = "SQUAREL"
    OPERATOR = "OPERATOR"
    DOT = "DOT"
    BACKSLASH = "BACKSLASH"
    IDENTIFIER = "IDENTIFIER"
    NEWLINE = "NEWLINE"
    TAB = "TAB"
    EOF = "EOF"
    INVALID = "INVALID"
    
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
    # TAG = "tag"
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
    PLUS_EQUALS = PLUS + ASSIGNMENT
    MINUS_EQUALS = MINUS + ASSIGNMENT
    MULTIPLY_EQUALS = MULTIPLY + ASSIGNMENT
    DIVIDE_EQUALS = DIVIDE + ASSIGNMENT
    POWER_EQUALS = POWER + ASSIGNMENT
    COMPARISON = "=="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GTEQUALS = GREATER_THAN + ASSIGNMENT
    LTEQUALS = LESS_THAN + ASSIGNMENT
    NEQUALS = "!"+ASSIGNMENT

@dataclass
class Token:
    type: TokenType
    subtype: SUBTYPE | None
    lexeme: str
    literal: str | None | int | float
    line: int
    start_position: int
    end_position: int