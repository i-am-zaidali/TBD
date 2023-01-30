from pprint import pprint as pp
import logging
import sys
from .interpreter import Interpreter, Scope
from .builtin_models import BuiltInFunction
import argparse
import pathlib


def __handle_print(args):
    if not args["__args"].value:
        del args["__args"]

    else:
        [print(a, end=" ") for a in args["__args"].value]
        del args["__args"]
    print(*args.values())


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", "-f", default=None, dest="file")
    return parser


def get_default_scope():
    scope = Scope()
    scope.declare_var("print", BuiltInFunction(__handle_print))
    return scope


def error(message: str = "", REPL=False):
    if message:
        print("Error: {}".format(message))

    print(f"Exiting{' REPL' if REPL else ''}.")
    sys.exit(1)


def start_repl():
    scope = get_default_scope()
    while True:
        lines = []
        while True:
            try:
                line = input(">>> ")
                if not line:
                    break
                elif line == "exit":
                    error(REPL=True)
            except EOFError:
                break
            except KeyboardInterrupt:
                error("Keyboard Interrupt detected. Exiting.")
            else:
                lines.append(line)
        try:
            joint = "\n".join(lines)
            ip = Interpreter(joint, scope)
            iterator = ip.evaluate()
            for i in iterator:
                print(i)
        except EOFError:
            break
        except Exception as e:
            logging.exception("Exception in REPL: ", exc_info=e)


if __name__ == "__main__":
    parser = create_parser()

    flags = vars(parser.parse_args())

    if fn := flags.get("file"):
        path = pathlib.Path(fn)
        if not path.is_file():
            error("Filename is not a valid file!")

        else:
            with path.open("r") as file:
                text = file.read()

            ip = Interpreter(text, get_default_scope())
            for res in ip.evaluate():
                print(res)
            error()

    else:
        start_repl()
