import re

from translator.isa import Term, AddressingMode, Opcode
from translator.lex import *


# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

        self.integers = {}
        self.strings = {}
        self.loop_ind = 0
        self.if_ind = 0
        self.exp_ind = 0
        self.instructions = []
        self.stack = []

        self.labels = {}
        self.var_labels = {}
        self.variables = []

        self.curToken = None
        self.peekToken = None
        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort("Expected " + kind.name + ", got " + self.curToken.kind.name)
        self.nextToken()

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
        sys.exit("Error. " + message)

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(
            TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(
            TokenType.NOTEQ)

    def isEqOperator(self):
        return self.checkToken(TokenType.EQ) or self.checkToken(TokenType.ASTERISKEQ) or self.checkToken(
            TokenType.MODEQ) or self.checkToken(TokenType.SLASHEQ) or self.checkToken(TokenType.MINUSEQ) or self.checkToken(
            TokenType.PLUSEQ)

    @staticmethod
    def loop_begin(number):
        return 'loop' + str(number)

    @staticmethod
    def loop_end(number):
        return 'end_loop' + str(number)

    @staticmethod
    def if_done(number):
        return 'if_done' + str(number)

    @staticmethod
    def exp_op(number):
        return 'exp_op' + str(number)

    @staticmethod
    def mk_ptr(label):
        return str(label) + 'ptr'

    @staticmethod
    def label(label, body):
        return str(label) + ': ' + str(body)

    def addVariables(self):
        for lb in self.integers:
            self.var_labels[lb] = len(self.variables)
            self.variables.append(
                {'opcode': Opcode.DATA, 'term': Term(len(self.variables), self.integers[lb], AddressingMode.DIRECT)})
        for lb in self.strings:
            self.var_labels[self.mk_ptr(lb)] = len(self.variables)
            self.variables.append(
                {'opcode': Opcode.DATA, 'term': Term(len(self.variables), len(self.variables) + 1, AddressingMode.ABSOLUTE)})
            self.var_labels[lb] = len(self.variables)
            self.variables.append(
                {'opcode': Opcode.DATA,
                 'term': Term(len(self.variables), ord(self.strings[lb][0]), AddressingMode.DIRECT)})
            for i in range(1, len(self.strings[lb])):
                letter = self.strings[lb][i]
                self.variables.append(
                    {'opcode': Opcode.DATA,
                     'term': Term(len(self.variables), ord(letter), AddressingMode.DIRECT)})
            self.variables.append(
                {'opcode': Opcode.DATA,
                 'term': Term(len(self.variables), 0, AddressingMode.DIRECT)})

    def create_exp_op(self):
        self.exp_ind += 1
        exp = self.exp_op(self.exp_ind)
        self.var_labels[exp] = len(self.variables)
        self.variables.append({'opcode': Opcode.DATA, 'term': Term(len(self.variables), 0, AddressingMode.DIRECT)})
        return exp

    def create_and_save_exp_op(self):
        exp = self.create_exp_op()
        self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), exp, AddressingMode.ABSOLUTE)})
        return exp

    def create_exp_evaluation(self, opcode, exp1, exp2, exp_res):
        self.instructions.append({'opcode': Opcode.LD, 'term': Term(len(self.instructions), exp1, AddressingMode.ABSOLUTE)})
        self.instructions.append({'opcode': opcode, 'term': Term(len(self.instructions), exp2, AddressingMode.ABSOLUTE)})
        if exp_res is not None:
            self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), exp_res, AddressingMode.ABSOLUTE)})

    def create_code_arr(self):
        code = []
        code += self.variables

        for instr in self.instructions:
            # print(instr)
            term_line = len(code)
            term_arg = str(instr['term'][1])
            term_mode = instr['term'][2]
            if re.search('[a-zA-Z]', str(term_arg)):
                if term_arg in self.labels:
                    term_arg = self.labels[term_arg] + len(self.variables)
                elif term_arg in self.var_labels:
                    term_arg = self.var_labels[term_arg]

            instr['term'] = Term(term_line, term_arg, term_mode)
            code.append(instr)
        return code

    # Production rules.

    # program ::= {statement}
    def program(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement()

        self.instructions.append({'opcode': Opcode.HLT, 'term': Term(len(self.instructions), 0, AddressingMode.DIRECT)})

        self.addVariables()
        return self.create_code_arr()

    def statement(self):

        # "PRINT" "(" ident ")"
        if self.checkToken(TokenType.PRINT):
            self.nextToken()
            self.match(TokenType.OPEN_PAREN_ROUND)

            ident = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.CLOSE_PAREN_ROUND)

            if ident in self.integers:
                self.instructions.append({'opcode': Opcode.LD, 'term': Term(len(self.instructions), ident, AddressingMode.ABSOLUTE)})
                self.instructions.append({'opcode': Opcode.OUT, 'term': Term(len(self.instructions), 0, AddressingMode.DIRECT)})
            elif ident in self.strings:
                self.loop_ind += 1
                l_begin = self.loop_begin(self.loop_ind)
                l_end = self.loop_end(self.loop_ind)
                ptr = self.mk_ptr(ident)
                self.labels[l_begin] = len(self.instructions)
                self.instructions.append({'opcode': Opcode.LD, 'term': Term(len(self.instructions), ptr, AddressingMode.RELATIVE)})
                self.instructions.append({'opcode': Opcode.BEQ, 'term': Term(len(self.instructions), l_end, AddressingMode.DIRECT)})

                self.instructions.append({'opcode': Opcode.OUT, 'term': Term(len(self.instructions), 0, AddressingMode.DIRECT)})
                self.instructions.append({'opcode': Opcode.LD, 'term': Term(len(self.instructions), ptr, AddressingMode.ABSOLUTE)})
                self.instructions.append({'opcode': Opcode.INC, 'term': Term(len(self.instructions), 0, AddressingMode.DIRECT)})
                self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), ptr, AddressingMode.ABSOLUTE)})
                self.instructions.append({'opcode': Opcode.JUMP, 'term': Term(len(self.instructions), l_begin, AddressingMode.DIRECT)})
                self.labels[l_end] = len(self.instructions)

        # "IF" "(" comparison ")" {statement} "ENDIF"
        elif self.checkToken(TokenType.IF):
            self.nextToken()
            self.match(TokenType.OPEN_PAREN_ROUND)

            self.if_ind += 1
            if_end = self.if_done(self.if_ind)

            self.comparison()
            self.match(TokenType.CLOSE_PAREN_ROUND)
            self.nl()
            opcode = self.stack.pop()
            self.instructions.append({'opcode': opcode, 'term': Term(len(self.instructions), if_end, AddressingMode.DIRECT)})

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.labels[if_end] = len(self.instructions)

        # "WHILE" "(" comparison ")" {statement} "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            self.nextToken()
            self.match(TokenType.OPEN_PAREN_ROUND)

            self.loop_ind += 1
            l_begin = self.loop_begin(self.loop_ind)
            l_end = self.loop_end(self.loop_ind)

            self.labels[l_begin] = len(self.instructions)
            self.comparison()
            self.match(TokenType.CLOSE_PAREN_ROUND)
            self.nl()
            opcode = self.stack.pop()
            self.instructions.append({'opcode': opcode, 'term': Term(len(self.instructions), l_end, AddressingMode.DIRECT)})

            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.instructions.append({'opcode': Opcode.JUMP, 'term': Term(len(self.instructions), l_begin, AddressingMode.DIRECT)})
            self.labels[l_end] = len(self.instructions)

        # "INT" ident "=" expression
        elif self.checkToken(TokenType.INT):
            self.nextToken()
            ident = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)
            self.integers[ident] = self.evaluate_expression()

        # "STRING" ident "=" word
        elif self.checkToken(TokenType.STRING):
            self.nextToken()
            ident = self.curToken.text
            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            word = self.curToken.text
            self.strings[ident] = word
            self.nextToken()

        # ident "[ + | - | / | % ]=" expression (for int only)
        elif self.checkToken(TokenType.IDENT):
            ident1 = self.curToken.text
            self.nextToken()
            operator = self.curToken.kind
            if self.isEqOperator():
                self.nextToken()
                self.expression()
                if operator == TokenType.EQ:
                    self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), ident1, AddressingMode.ABSOLUTE)})
                else:
                    exp = self.create_and_save_exp_op()
                    if operator == TokenType.PLUSEQ:
                        self.create_exp_evaluation(Opcode.ADD, ident1, exp, ident1)
                    elif operator == TokenType.MINUSEQ:
                        self.create_exp_evaluation(Opcode.SUB, ident1, exp, ident1)
                    elif operator == TokenType.SLASHEQ:
                        self.create_exp_evaluation(Opcode.DIV, ident1, exp, ident1)
                    elif operator == TokenType.ASTERISKEQ:
                        self.create_exp_evaluation(Opcode.MUL, ident1, exp, ident1)
                    elif operator == TokenType.MODEQ:
                        self.create_exp_evaluation(Opcode.MOD, ident1, exp, ident1)
            else:
                self.abort('Invalid operation ' + self.curToken.text)

        # "INPUT" "(" ident ")"
        elif self.checkToken(TokenType.INPUT):
            self.nextToken()
            self.match(TokenType.OPEN_PAREN_ROUND)

            ident = self.curToken.text

            self.match(TokenType.IDENT)
            self.instructions.append({'opcode': Opcode.IN, 'term': Term(len(self.instructions), 0, AddressingMode.DIRECT)})
            self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), ident, AddressingMode.ABSOLUTE)})

            self.match(TokenType.CLOSE_PAREN_ROUND)

        # This is not a valid statement. Error!
        else:
            self.abort("Invalid statement at " + self.curToken.text + " (" + self.curToken.kind.name + ")")

        # Newline.
        self.nl()

    # nl ::= '\n'+
    def nl(self):
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    # comparison ::= expression | (expression ("==" | "!=" | ">" | ">=" | "<" | "<=") expression)
    def comparison(self):
        self.expression()

        if self.isComparisonOperator():
            exp_id1 = self.create_and_save_exp_op()
            operator = self.curToken.text
            self.nextToken()
            self.expression()
            exp_id2 = self.create_and_save_exp_op()
            self.create_exp_evaluation(Opcode.CMP, exp_id1, exp_id2, None)
            if operator == "==":
                self.stack.append(Opcode.BNE)
            elif operator == "!=":
                self.stack.append(Opcode.BEQ)
            elif operator == ">=":
                self.stack.append(Opcode.BL)
            elif operator == "<=":
                self.stack.append(Opcode.BG)
            elif operator == "<":
                self.stack.append(Opcode.BGE)
            elif operator == ">":
                self.stack.append(Opcode.BLE)
        else:
            self.abort("Expected comparison operator at: " + self.curToken.text)

    # expression ::= term {( "-" | "+" ) term}
    def expression(self):
        self.term()

        # Can have 0 or more +/- and expressions.
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            exp1 = self.create_exp_op()
            while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
                self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), exp1, AddressingMode.ABSOLUTE)})
                operator = self.curToken.text
                self.nextToken()
                self.term()
                exp2 = self.create_and_save_exp_op()
                if operator == '+':
                    self.create_exp_evaluation(Opcode.ADD, exp1, exp2, None)
                elif operator == '-':
                    self.create_exp_evaluation(Opcode.SUB, exp1, exp2, None)

    def evaluate_expression(self):
        res = self.evaluate_term()

        # Can have 0 or more +/- and expressions.
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
                operator = self.curToken.text
                self.nextToken()
                b = self.evaluate_term()
                if operator == '+':
                    res = res + b
                elif operator == '-':
                    res = res - b
        return res

    # term ::= unary {( "/" | "*" | "%" ) unary}
    def term(self):
        self.unary()
        # Can have 0 or more */% and expressions.
        if self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.MOD):
            exp1 = self.create_exp_op()
            while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(
                    TokenType.MOD):
                self.instructions.append({'opcode': Opcode.ST, 'term': Term(len(self.instructions), exp1, AddressingMode.ABSOLUTE)})
                operator = self.curToken.text
                self.nextToken()
                self.unary()
                exp2 = self.create_and_save_exp_op()
                if operator == "/":
                    self.create_exp_evaluation(Opcode.DIV, exp1, exp2, None)
                elif operator == "*":
                    self.create_exp_evaluation(Opcode.MUL, exp1, exp2, None)
                elif operator == '%':
                    self.create_exp_evaluation(Opcode.MOD, exp1, exp2, None)

    def evaluate_term(self):
        res = self.evaluate_unary()
        # Can have 0 or more *// and expressions.
        if self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.MOD):
            while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(
                    TokenType.MOD):
                operator = self.curToken.text
                self.nextToken()
                b = self.evaluate_unary()
                if operator == "/":
                    res = res // b
                elif operator == "*":
                    res = res * b
                elif operator == '%':
                    res = res % b
        return res

    # unary ::= ["+" | "-"] primary
    def unary(self):
        # Optional unary +/-
        token = None
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            token = '-'
            self.nextToken()
        self.primary()
        if token == '-':
            self.instructions.append({'opcode': Opcode.NEG, 'term': Term(len(self.instructions), 0, AddressingMode.DIRECT)})

    def evaluate_unary(self):
        # Optional unary +/-
        sign = 1
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            if self.checkToken(TokenType.MINUS):
                sign = -1
            self.nextToken()
        return self.evaluate_primary() * sign

    # primary ::= number | ident
    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.instructions.append({'opcode': Opcode.LD, 'term': Term(len(self.instructions), self.curToken.text, AddressingMode.DIRECT)})
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.integers:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            self.instructions.append(
                {'opcode': Opcode.LD, 'term': Term(len(self.instructions), self.curToken.text, AddressingMode.ABSOLUTE)})
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

    def evaluate_primary(self):
        if self.checkToken(TokenType.NUMBER):
            res = int(self.curToken.text)
            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            # Ensure the variable already exists.
            if self.curToken.text not in self.integers:
                self.abort("Referencing variable before assignment: " + self.curToken.text)

            res = int(self.integers[self.curToken.text])
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)
        return res

