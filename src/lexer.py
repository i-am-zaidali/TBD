from .exceptions import LexerException
from typing import Optional
from .lexer_models import *


KEYWORD_TT = {
    "let": KEYWORDS.LET,
    "const": KEYWORDS.CONST,
    "loop": KEYWORDS.LOOP,
    "times": KEYWORDS.TIMES,
    "send": KEYWORDS.SEND,
    "to": KEYWORDS.TO,
    "tag": KEYWORDS.TAG,
    "return": KEYWORDS.RETURN,
    "if": KEYWORDS.IF,
    "else": KEYWORDS.ELSE,
}
"""Keywords linked to their token type"""

A_OPERATOR_TT = {
    "+": OPERATORS.PLUS,
    "-": OPERATORS.MINUS,
    "*": OPERATORS.MULTIPLY,
    "^": OPERATORS.POWER,
    "/": OPERATORS.DIVIDE,
    "%": OPERATORS.REMAINDER,
}
"""Arithmetic Operators linked to their token type"""

AA_OPERATOR_TT = {
    "+=": OPERATORS.PLUS_EQUALS,
    "-=": OPERATORS.MINUS_EQUALS,
    "*=": OPERATORS.MULTIPLY_EQUALS,
    "/=": OPERATORS.DIVIDE_EQUALS,
    "^=": OPERATORS.POWER_EQUALS,
}
"""Arithmetic Assignment Operators linked to their token type"""

L_OPERATOR_TT = {
    "=": OPERATORS.ASSIGNMENT,
    ">": OPERATORS.GREATER_THAN,
    "<": OPERATORS.LESS_THAN,
    ">=": OPERATORS.GTEQUALS,
    "<=": OPERATORS.LTEQUALS,
    "==": OPERATORS.COMPARISON,
    "!=": OPERATORS.NEQUALS,
}
"""Logical Operators linked to their token type"""


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.source_lines = source.splitlines()
        self.tokens = []
        self.row = 1
        self.column = 1
        self.total = len(source)
        self.current = 0

    def tokenize(self):
        while not self._at_end():
            self._scan_token()
            self._advance()

        self._add_token(TokenType.EOF, self.current, self.current, "\0")
        return self.tokens

    def _scan_token(self):
        c = self._peek()
        if c == " ":
            pass
        elif c == "\\":
            next = self._peek_next()
            if next == "t":
                self._add_token(TokenType.TAB, self.current, self.current + 1)
            elif next == "n":
                self._add_token(TokenType.NEWLINE, self.current, self.current + 1)
                self._advance(newline=True)

            self._advance()
        elif c == "\t":
            self._add_token(TokenType.TAB, self.current, self.current)
        elif c == "\n":
            self._add_token(TokenType.NEWLINE, self.current, self.current)
            self._advance(skipline=True)
        elif c == ",":
            self._add_token(TokenType.COMMA, self.current, self.current)
        elif c == ".":
            self._add_token(TokenType.DOT, self.current, self.current)
        elif c == ":":
            self._add_token(TokenType.COLON, self.current, self.current)
        elif c == "(":
            self._add_token(TokenType.LPAREN, self.current, self.current)
        elif c == ")":
            self._add_token(TokenType.RPAREN, self.current, self.current)
        elif c == "[":
            self._add_token(TokenType.LSQUARE, self.current, self.current)
        elif c == "]":
            self._add_token(TokenType.RSQUARE, self.current, self.current)
        elif c == "{":
            self._add_token(TokenType.LCURLY, self.current, self.current)
        elif c == "}":
            self._add_token(TokenType.RCURLY, self.current, self.current)
        elif c in A_OPERATOR_TT:
            if self._peek_next() == "=":

                self._add_token(
                    TokenType.OPERATOR,
                    self.current,
                    self.current + 1,
                    subtype=AA_OPERATOR_TT[c + "="],
                )
                self._advance()
            else:
                self._add_token(
                    TokenType.OPERATOR,
                    self.current,
                    self.current,
                    subtype=A_OPERATOR_TT[c],
                )
        elif c in L_OPERATOR_TT or c == "!" or c == "=":
            if self._peek_next() == "=":
                self._add_token(
                    TokenType.OPERATOR,
                    self.current,
                    self.current + 1,
                    subtype=L_OPERATOR_TT[c + "="],
                )
                self._advance()
            else:
                self._add_token(
                    TokenType.OPERATOR,
                    self.current,
                    self.current,
                    subtype=L_OPERATOR_TT[c],
                )
        elif c == '"' or c == "'":
            self._string(c)
        elif c.isdigit():
            self._number()
        elif self._is_alpha(c):
            self._identifier()
        elif c == "\0":
            self._add_token(TokenType.EOF, self.current, self.current, "\0")
        elif c == "#":
            self._comment()

        else:
            self._error()

    def _string(self, quote: str = '"'):
        start = self.current
        while self._advance() != quote and not self._peek_previous == "\\" and not self._at_end():
            if self._peek() == "\n" and self._peek_previous() != "\\":
                self._error("Unterminated string at end of line {}".format(self.row))

        if self._peek() == quote:
            self._add_token(
                TokenType.LITERAL,
                start,
                self.current,
                self.source[start + 1 : self.current],
                subtype=LITERALS.STRING,
            )

        else:
            self._error("Unterminated string at end of line {}".format(self.row))

    def _number(self):
        start = self.current
        while True:
            if self._peek_next().isdigit():
                self._advance()

            else:
                break

        if self._peek_next() == "." and self._peek(self.current + 2).isdigit():
            self._advance()
            while True:
                if self._peek_next().isdigit():
                    self._advance()

                else:
                    break

        value = self.source[start : self.current + 1]
        self._add_token(
            TokenType.LITERAL,
            start,
            self.current,
            int(value) if value.isdecimal() else float(value),
            subtype=LITERALS.NUMBER,
        )

    def _identifier(self):
        start = self.current
        while self._peek_next().isalnum() or self._peek_next() == "_":
            self._advance()
        value = self.source[start : self.current + 1]
        literal = None
        if value in KEYWORD_TT:
            type_ = TokenType.KEYWORD
            subtype = KEYWORD_TT[value]
        elif value in ("true", "false"):
            type_ = TokenType.LITERAL
            subtype = LITERALS.BOOL
            literal = True if value == "true" else False
        elif value == "null":
            type_ = TokenType.LITERAL
            subtype = LITERALS.NULL
        else:
            type_ = TokenType.IDENTIFIER
            subtype = None

        self._add_token(type_, start, self.current, literal, subtype=subtype)

    def _comment(self):
        start = self.current
        self._advance(skipline=True)
        self._add_token(
            TokenType.COMMENT,
            start,
            self.current,
            self.source[start + 1 : self.current].strip(),
        )

    def _error(self, message: Optional[str] = None):
        message = (
            message
            or f"Unexpected character {self._peek()} at {self.row} row, {self.column} column"
        )
        raise LexerException(message)

    def _add_token(
        self,
        type_: TokenType,
        start: int,
        end: int,
        literal: Optional[str | int | float] = None,
        subtype: Optional[SUBTYPE] = None,
    ):
        lexeme = self.source[start : end + 1]
        tok = Token(type_, subtype, lexeme, literal, self.row, start, end)
        self.tokens.append(tok)
        return tok

    def _peek(self, index: Optional[int] = None):
        index = index or self.current
        if self._at_end(index):
            return "\0"
        return self.source[index]

    def _peek_next(self):
        return self._peek(self.current + 1)

    def _peek_previous(self):
        return self._peek(self.current - 1)

    def _match(self, expected: str):
        return not self._at_end() and self._peek() == expected
        # if self._at_end():
        #     return False
        # if self._peek_next() != expected:
        #     return False
        # return True

    def _advance(self, times=1, skipline=False):
        if self._at_end():
            return "\0"
        if not skipline:
            self.current += times
            self.row, self.column = self._get_rc_from_index(self.current)
        else:
            self.row += 1
            self.column = 0
            self.current = self._get_index_from_rc(self.row, self.column)
        return self._peek()

    def _get_rc_from_index(self, index: int):
        row = self.source.count("\n", 0, index) + 1
        column = index - self.source.rfind("\n", 0, index)
        return row, column

    def _get_index_from_rc(self, row: int, column: int):
        total_len = sum(len(line) + 1 for line in self.source_lines[: row - 1])
        return total_len + (column - 1)

    @staticmethod
    def _is_alpha(c: str):
        return c.isalpha() or c == "_"

    def _at_end(self, index: Optional[int] = None):
        return (index or self.current) >= len(self.source)
