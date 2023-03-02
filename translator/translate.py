# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import sys

from isa import write_code
from translator.lex import Lexer
from translator.parse import Parser, TranslationException


def main(args):
    assert len(args) == 2, "Wrong arguments: translate.py <input_file> <target_file>"
    source, target = args

    with open(source, "rt", encoding="utf-8") as f:
        source = f.read()

    lexer = Lexer(source)
    parser = Parser(lexer)

    try:
        code = parser.program()
        print("source LoC:", len(source.split("\n")), "| code instr:", len(code))
        write_code(target, code)
    except TranslationException as exception:
        print(exception.get_msg())


if __name__ == '__main__':
    main(sys.argv[1:])
