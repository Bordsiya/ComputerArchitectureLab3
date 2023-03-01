import enum

from exceptions import TranslationException


class Token:
    def __init__(self, token_text, token_kind):
        self.text = token_text  # The token's actual text. Used for identifiers, strings, and numbers
        self.kind = token_kind  # The TokenType that this token is classified as

    @staticmethod
    def checkIfKeyword(token_text):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX
            if kind.name == token_text.upper() and 100 <= kind.value < 200:
                return kind
        return None


# TokenType is our enum for all the types of tokens
class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    WORD = 3
    OPEN_PAREN_ROUND = 4
    CLOSE_PAREN_ROUND = 5
    # Keywords.
    PRINT = 100
    INPUT = 101
    IF = 102
    ENDIF = 103
    WHILE = 104
    ENDWHILE = 105
    INT = 106
    STRING = 107
    # Operators.
    EQ = 200
    PLUS = 201
    MINUS = 202
    ASTERISK = 203
    SLASH = 204
    EQEQ = 205
    NOTEQ = 206
    LT = 207
    LTEQ = 208
    GT = 209
    GTEQ = 210
    MOD = 211
    PLUSEQ = 212
    MINUSEQ = 213
    ASTERISKEQ = 214
    SLASHEQ = 215
    MODEQ = 216


class Lexer:
    def __init__(self, input):
        self.source = input + '\n'
        self.cur_char = ''
        self.cur_pos = -1
        self.next_char()

    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos >= len(self.source):
            self.cur_char = '\0'  # EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    def peek(self):
        if self.cur_pos + 1 >= len(self.source):
            return '\0'
        return self.source[self.cur_pos + 1]

    def skip_whitespace(self):
        while self.cur_char == ' ' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()

    def skip_comment(self):
        if self.cur_char == '/' and self.peek() == '/':
            while self.cur_char != '\n':
                self.next_char()

    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()

        token = None
        if self.cur_char == '+':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.PLUSEQ)
            else:
                token = Token(self.cur_char, TokenType.PLUS)

        elif self.cur_char == '-':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.MINUSEQ)
            else:
                token = Token(self.cur_char, TokenType.MINUS)

        elif self.cur_char == '*':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.ASTERISKEQ)
            else:
                token = Token(self.cur_char, TokenType.ASTERISK)

        elif self.cur_char == '/':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.SLASHEQ)
            else:
                token = Token(self.cur_char, TokenType.SLASH)

        elif self.cur_char == '%':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.MODEQ)
            else:
                token = Token(self.cur_char, TokenType.MOD)

        elif self.cur_char == '=':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.EQEQ)
            else:
                token = Token(self.cur_char, TokenType.EQ)

        elif self.cur_char == '>':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.GTEQ)
            else:
                token = Token(self.cur_char, TokenType.GT)

        elif self.cur_char == '<':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.LTEQ)
            else:
                token = Token(self.cur_char, TokenType.LT)

        elif self.cur_char == '!':
            if self.peek() == '=':
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.NOTEQ)
            else:
                raise TranslationException("Expected !=, got !" + self.peek())

        elif self.cur_char == '(':
            token = Token(self.cur_char, TokenType.OPEN_PAREN_ROUND)

        elif self.cur_char == ')':
            token = Token(self.cur_char, TokenType.CLOSE_PAREN_ROUND)

        elif self.cur_char == '\"':
            # Get characters between quotations
            self.next_char()
            start_pos = self.cur_pos

            while self.cur_char != '\"':
                # Don't allow special characters in the string. No escape characters, newlines, tabs, or %
                if self.cur_char == '\r' or self.cur_char == '\n' or self.cur_char == '\t' \
                        or self.cur_char == '\\' or self.cur_char == '%':
                    raise TranslationException("Illegal character in string")
                self.next_char()

            tok_text = self.source[start_pos:self.cur_pos]
            token = Token(tok_text, TokenType.WORD)

        elif self.cur_char.isdigit():
            # Leading character is a digit, so this must be a number
            start_pos = self.cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == '.':
                raise TranslationException("Only integers allowed")

            tok_text = self.source[start_pos: self.cur_pos + 1]
            token = Token(tok_text, TokenType.NUMBER)

        elif self.cur_char.isalpha():
            # Leading character is a letter, so this must be an identifier or a keyword
            start_pos = self.cur_pos
            while self.peek().isalnum():
                self.next_char()

            # Check if the token is in the list of keywords
            tok_text = self.source[start_pos: self.cur_pos + 1]
            keyword = Token.checkIfKeyword(tok_text)
            if keyword is None:
                token = Token(tok_text, TokenType.IDENT)
            else:
                token = Token(tok_text, keyword)

        elif self.cur_char == '\n':
            token = Token(self.cur_char, TokenType.NEWLINE)

        elif self.cur_char == '\0':
            token = Token('', TokenType.EOF)

        else:
            raise TranslationException("Unknown token: " + self.cur_char)

        self.next_char()
        return token
