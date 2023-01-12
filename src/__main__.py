from .lexer import Lexer
from .parser import Parser
from pprint import pprint as pp
import logging
import sys
from .interpreter import Interpreter, Scope

if __name__ == "__main__":
    
    scope = Scope()
    
    while True:
        lines = []
        while True:
            try:
                line = input(">>> ")
                print(line)
                if not line:
                    break
                elif line == "exit":
                    sys.exit(1)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("Exiting!")
                sys.exit(1)
            else:
                lines.append(line)
        try:
            joint = "\n".join(lines)
            print(repr(joint))
            ip = Interpreter(joint, scope)
            iterator = ip.evaluate()
            for i in iterator:
                print(i)
        except EOFError:
            break
        except Exception as e:
            logging.exception("Exception in REPL: ", exc_info=e)
        
    