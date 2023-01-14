# pyright: reportShadowedImports=false

from .lexer_models import *
from .parser_models import *
from .lexer import AA_OPERATOR_TT, A_OPERATOR_TT
from .exceptions import ParserException
from typing import List, Optional


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.index = 0
        self.ast = []

    def match(self, type: TokenType, subtype: Optional[SUBTYPE] = None) -> bool:
        to_check = self.lookahead()
        if to_check.type is type:
            if subtype is not None and to_check.subtype is subtype:
                return True
            return True
        return False

    def peek(self):
        return self.tokens[self.index]

    def peek_match(self, type: TokenType, subtype: Optional[SUBTYPE] = None) -> bool:
        to_check = self.peek()
        if to_check.type is type:
            if subtype is not None:
                if not to_check.subtype is subtype:
                    return False
            return True
        return False

    def lookahead(self):
        if self.at_end():
            return None
        return self.tokens[self.index + 1]

    def consume(self) -> Token:
        self.index += 1
        return self.tokens[self.index]

    def at_end(self) -> bool:
        return self.index > (len(self.tokens) - 1) or self.peek_match(TokenType.EOF)

    def parse(self) -> Program:
        while not self.at_end():
            result = self.statement()
            if result is None:
                continue
            self.ast.append(result)

        prog = Program(self.ast)
        return prog

    def statement(self) -> Node:
        if self.peek_match(TokenType.KEYWORD, KEYWORDS.LET):
            return self.let_stmt()
        elif self.peek_match(TokenType.KEYWORD, KEYWORDS.CONST):
            return self.const_stmt()
        elif self.peek_match(TokenType.NEWLINE):
            self.consume()
            return literals["null"]
        # elif self.match(TokenType.KEYWORD, KEYWORDS.LOOP):
        #     return self.loop_stmt()
        # elif self.match(TokenType.KEYWORD, KEYWORDS.SEND):
        #     return self.send_stmt()
        # elif self.match(TokenType.KEYWORD, KEYWORDS.IF):
        #     return self.if_stmt()
        # else:
        return self.expr_stmt()

    def expr_stmt(self) -> Expression:
        return self.parse_assignment_expr()

    def parse_assignment_expr(self):
        left = self.parse_additive_expr()

        if self.peek_match(TokenType.OPERATOR, OPERATORS.ASSIGNMENT):
            self.consume()

            right = self.expr_stmt()

            return AssignmentExp(left, right)

        elif (
            self.peek_match(TokenType.OPERATOR)
            and self.peek().subtype in AA_OPERATOR_TT.values()
        ):
            if not isinstance(left, Identifier):
                raise ParserException(
                    "Cannot perform arithmetic assignment on non-identifier"
                )
            op = self.peek()

            self.consume()

            right = self.expr_stmt()
            op = Token(
                TokenType.OPERATOR,
                A_OPERATOR_TT[op.lexeme[0]],
                op.lexeme[0],
                None,
                op.line,
                op.start_position,
                op.end_position,
            )

            return AssignmentExp(left, BinaryExp(left, op, right))
        return left

    def parse_additive_expr(self):

        left = self.parse_multiplicative_expr()

        while (
            not self.at_end()
            and self.peek_match(TokenType.OPERATOR)
            and self.peek().subtype in (OPERATORS.PLUS, OPERATORS.MINUS)
        ):
            operator = self.peek()
            self.consume()
            right = self.parse_multiplicative_expr()
            left = BinaryExp(left, operator, right)
        return left

    def parse_multiplicative_expr(self):

        left = self.parse_member_expr()
        while (
            not self.at_end()
            and self.peek_match(TokenType.OPERATOR)
            and self.peek().subtype
            in (
                OPERATORS.MULTIPLY,
                OPERATORS.POWER,
                OPERATORS.REMAINDER,
                OPERATORS.DIVIDE,
            )
        ):
            operator = self.peek()
            self.consume()
            right = self.parse_member_expr()
            left = BinaryExp(left, operator, right)

        return left

    def parse_member_expr(self):
        # member expressions can be either of the form:
        # object.property or object[property]

        obj = self.parse_function_call_expr()
        if self.peek_match(TokenType.DOT):
            self.consume()
            prop = self.parse_function_call_expr()
            if not isinstance(prop, Identifier):
                raise ParserException("DOt property accessors must be identifiers!")
            return MemberExp(obj, prop, False)
        elif self.peek_match(TokenType.LSQUARE):
            self.consume()
            prop = self.parse_function_call_expr()
            self.consume()
            return MemberExp(obj, prop, True)
        return obj

    def parse_function_call_expr(self):
        # function call: {function_name argument=value, argument2=value2}
        # {function_name} is also a valid function calls
        # We can allow as many arguments as we want
        # function definitions will not define arguments

        if not self.peek_match(TokenType.LCURLY):
            return self.parse_primary_expr()

        self.consume()  # consume the {
        if (
            self.peek_match(TokenType.IDENTIFIER) and self.match(TokenType.COLON)
        ) or self.peek_match(TokenType.RCURLY):
            return self.parse_object_expr()

        caller = self.expr_stmt()

        arguments = list[AssignmentExp]()

        while True:
            if self.peek_match(TokenType.RCURLY):
                break
            arg = self.parse_assignment_expr()
            if isinstance(arg, Identifier):
                arg = AssignmentExp(arg, arg)
            elif not isinstance(arg, AssignmentExp):
                raise ParserException(
                    "Function arguments must be either identifiers or assignments!"
                )
            arguments.append(arg)
            if self.peek_match(TokenType.COMMA):
                self.consume()

        self.consume()

        return FunctionCallExp(caller, arguments)

    def parse_object_expr(self):
        properties = list[Property]()
        while not self.peek_match(TokenType.RCURLY):
            properties.append(self.parse_property())

        self.consume()

        return ObjectExp(properties)

    def parse_primary_expr(self):
        curr = self.peek()

        if curr.type in [TokenType.IDENTIFIER, TokenType.LITERAL]:
            self.consume()
            return (
                literals[type(curr.literal)](curr.literal)
                if curr.type is TokenType.LITERAL
                else Identifier(curr.lexeme)
            )

        elif curr.type is TokenType.LPAREN:
            self.consume()
            value = self.expr_stmt()
            if not self.peek().type is TokenType.RPAREN:
                raise ParserException(
                    "Expected closing parenthesis, found {}".format(self.lookahead())
                )
            self.consume()
            return value

        else:
            raise ParserException(f"Unexpected token found during parsing: {curr}")

    def parse_property(self):
        if not self.peek_match(TokenType.IDENTIFIER) and not self.peek_match(
            TokenType.LITERAL, LITERALS.STRING
        ):
            raise ParserException(
                "Expected identifier or string literal, found {}".format(self.peek())
            )

        name = self.peek()

        self.consume()

        if not self.peek_match(TokenType.COLON):
            raise ParserException(
                "Expected ':' after property name, found {}".format(self.lookahead())
            )

        self.consume()

        value = self.expr_stmt()

        if isinstance(value, AssignmentExp):
            raise ParserException(
                "Cannot have an assignment expression as a property value"
            )

        if self.peek_match(TokenType.RCURLY):
            return Property(Identifier(name.lexeme), value)

        elif not self.peek_match(TokenType.COMMA):
            raise ParserException(
                "Expected ',' after property value, found {}".format(self.lookahead())
            )

        self.consume()

        return Property(
            Identifier(
                name.lexeme if name.type is TokenType.IDENTIFIER else name.literal
            ),
            value,
        )

    def let_stmt(self):
        ident = self.consume()  # consume the "let" keyword
        if not self.peek_match(TokenType.IDENTIFIER):
            raise ParserException(
                "Expected identifier after 'let', found {}".format(self.lookahead())
            )

        self.consume()  # consume the identifier

        if not self.peek_match(TokenType.OPERATOR, OPERATORS.ASSIGNMENT):
            raise ParserException(
                "Expected '=' after identifier, found {}".format(self.lookahead())
            )

        self.consume()  # consume the '='

        val = self.expr_stmt()

        return VarDec(ident.lexeme, val)

    def const_stmt(self):
        var = self.let_stmt()
        return ConstDec(var.name, var.value)  # shortcut :p
