# TBD
A scripting language for use inside discord through bots.

## Features

- [x] Basic arithmetic (add +, subtract -, multiply *, divide /, remainder (modulus) %, power ^)
- [x] Variables and Constants (let, const)
- [x] Functions (tag)
- [x] Data types (Number (ints and floats), String, Bool, Array, Dict)
- [x] Property access (obj.prop or obj["prop"])

Examples can be found in the [examples](examples) folder.

## How to run

Discord bot implementation hasnt been added yet but you can use this as a standalone script interpreter.

To run:

1. Clone the repository
2. Open a terminal
3. Run the command `python3 -m src` (You can optionally pass a file to run as an argument with the `-f`/`--file` flag.)

That's it! A REPL will be activated, however it's a shitty REPL and doesn't really REPL.
You write multiple lines of code and it reads them then after an empty line, evaluates all the lines together.

I know it's shitty ok.