import argparse
from parser import pl_parse_prog, pl_parse_main
from interpreter import pl_eval
from compiler import pl_comp_main
from func import Func
from utils import ir_dump

def main():
    parser = argparse.ArgumentParser(description='Programming Language Processor')
    parser.add_argument('file', nargs='?', help='Input file to process')
    parser.add_argument('--parse', action='store_true', help='Parse the program and show AST')
    parser.add_argument('--compile', action='store_true', help='Compile the program')
    parser.add_argument('--interpret', action='store_true', help='Interpret the program')
    parser.add_argument('--repl', action='store_true', help='Start REPL mode')
    parser.add_argument('--compile-c', action='store_true', help='Compile the program to C')
    parser.add_argument('--compile-asm', action='store_true', help='Compile the program to x86_64 assembly')
    parser.add_argument('--compile-ir', action='store_true', help='Compile the program to IR')

    args = parser.parse_args()

    # Handle REPL mode
    if args.repl:
        print("REPL mode not implemented yet")
        return

    if args.compile_c:
        print("C compilation not implemented yet")
        return

    if args.compile_asm:
        print("x86_64 assembly compilation not implemented yet")
        return

    # If no file is provided and not in REPL mode, show help
    if not args.file and not args.repl:
        parser.print_help()
        return

    # Read the input file
    if args.file:
        try:
            with open(args.file, 'r') as f:
                program = f.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found")
            return
        except Exception as e:
            print(f"Error reading file: {e}")
            return

        # Parse mode
        if args.parse:
            try:
                ast = pl_parse_prog(program)
                print("Parse result:")
                import pprint
                pprint.pprint(ast, indent=2, width=80)
            except Exception as e:
                print(f"Parse error: {e}")
                return

        # Compile mode
        if args.compile:
            print("Compilation not implemented yet")
            return


        if args.compile_ir:
            node = pl_parse_main(program)
            fenv = Func(None)
            pl_comp_main(fenv, node)
            print(ir_dump(fenv))
            return

        # Interpret mode
        if args.interpret:
            try:
                ast = pl_parse_prog(program)
                result = pl_eval((dict(), None), ast)
                if result is not None:
                    print("Result:", result)
            except Exception as e:
                print(f"Runtime error: {e}")
                return

if __name__ == '__main__':
    main()
