# pyright: reportShadowedImports=false

from .lexer_models import *
from .parser_models import *
from .exceptions import ParserException
from typing import List, Optional

class Parser:
    # grammar for the language:
    # statement -> expr_stmt | let_stmt | const_stmt | loop_stmt | send_stmt | if_stmt
    # expr_stmt -> expr NEWLINE
    # let_stmt -> "let" IDENTIFIER EQUALS expr_stmt
    # const_stmt -> "const" IDENTIFIER EQUALS expr_stmt
    # loop_stmt -> "loop" expr_Stmt "times" COLON [NEWLINE TAB] expr_stmt
    # send_stmt -> "send" expr ["to" expr] NEWLINE
    # if_stmt -> "if" expr COLON [NEWLINE TAB] expr_stmt
    # expr -> IDENTIFIER | NUMBER | STRING | "true" | "false"| expr OPERATOR expr | expr DOT IDENTIFIER | LPAREN expr RPAREN expr
    
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
    
    def peek_match(self, type: TokenType, subtype: Optional[SUBTYPE]=None) -> bool:
        to_check = self.peek()
        if to_check.type is type:
            if subtype is not None and to_check.subtype is subtype:
                return True
            return True
        return False
    
    def lookahead(self):
        if self.at_end():
            return None
        return self.tokens[self.index+1]
    
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
        return self.object_expr()
    
    def object_expr(self):
        if not self.peek_match(TokenType.LCURLY):
            return self.assignment_expr()
            
        self.consume()
        properties = list[Property]()    
        while not self.peek_match(TokenType.RCURLY):
            properties.append(self.parse_property())
            
        self.consume()
            
        return ObjectExp(properties)
            
    
    def assignment_expr(self):
        left = self.parse_additive_expr()
        if self.peek_match(TokenType.OPERATOR, OPERATORS.ASSIGNMENT):
            self.consume()
            right = self.expr_stmt()
            return AssignmentExp(left, right)
        return left
    
    def parse_additive_expr(self):
        left = self.parse_multiplicative_expr()
        while not self.at_end() and self.peek_match(TokenType.OPERATOR) and self.peek().subtype in (OPERATORS.PLUS, OPERATORS.MINUS):
            operator = self.peek()
            self.consume()
            right = self.parse_multiplicative_expr()
            left = BinaryExp(left, operator, right)
        return left
    
    def parse_multiplicative_expr(self):
        left = self.parse_primary_expr()
        while not self.at_end() and self.peek().type is TokenType.OPERATOR and self.peek().subtype in (OPERATORS.MULTIPLY, OPERATORS.POWER, OPERATORS.REMAINDER, OPERATORS.DIVIDE):
            operator = self.peek()
            self.consume()
            right = self.parse_primary_expr()
            left = BinaryExp(left, operator, right)
            
        return left
    
    def parse_primary_expr(self):
        curr = self.peek()
        
        if curr.type in [TokenType.IDENTIFIER, TokenType.LITERAL]:
            self.consume()
            return literals[type(curr.literal)](curr.literal) if curr.type is TokenType.LITERAL else Identifier(curr.lexeme)
        
        elif curr.type is TokenType.LPAREN:
            self.consume()
            value = self.expr_stmt()
            if not self.peek().type is TokenType.RPAREN:
                raise ParserException("Expected closing parenthesis, found {}".format(self.lookahead()))
            self.consume()
            return value
        
        else:
            raise ParserException(f"Unexpected token found during parsing: {curr}")
        
    def parse_property(self):
        if not self.peek_match(TokenType.IDENTIFIER) and not self.peek_match(TokenType.LITERAL, LITERALS.STRING):
            raise ParserException("Expected identifier or string literal, found {}".format(self.peek()))
        
        name = self.peek()
        
        self.consume()
        
        if not self.peek_match(TokenType.COLON):
            raise ParserException("Expected ':' after property name, found {}".format(self.lookahead()))
        
        self.consume()
        
        value = self.expr_stmt()
        
        if isinstance(value, AssignmentExp):
            raise ParserException("Cannot have an assignment expression as a property value")
        
        if self.peek_match(TokenType.RCURLY):
            return Property(Identifier(name.lexeme), value)
        
        elif not self.peek_match(TokenType.COMMA):
            raise ParserException("Expected ',' after property value, found {}".format(self.lookahead()))
        
        self.consume()
        
        return Property(Identifier(name.lexeme if name.type is TokenType.IDENTIFIER else name.literal), value)
        
        
    def let_stmt(self):
        ident = self.consume() # consume the "let" keyword
        if not self.peek_match(TokenType.IDENTIFIER):
            raise ParserException("Expected identifier after 'let', found {}".format(self.lookahead()))
        
        self.consume() # consume the identifier
        
        if not self.peek_match(TokenType.OPERATOR, OPERATORS.ASSIGNMENT):
            raise ParserException("Expected '=' after identifier, found {}".format(self.lookahead()))
        
        self.consume() # consume the '='
        
        val = self.expr_stmt()
        
        return VarDec(ident.lexeme, val)
    
    def const_stmt(self):
        var = self.let_stmt()
        return ConstDec(var.name, var.value) # shortcut :p
        