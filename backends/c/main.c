#include "lisp_parser.h"

int main() {
    // Create the root environment for our program
    Environment *root_env = create_environment(NULL);

    // Sample input in a Lisp-like dialect.
    const char *input =
        // Wrap in a do block
        "(do"
        // Define a multiply function
        "(def mult ((x y)) (* x y))\n"
        // Define a variable
        "(var answer 42)\n"
        // Call the multiply function
        "(mult answer 2)"
        // End the do block
        ")";

    const char *p = input;

    // Parse the program
    Node *expr = parse_expr(&p);
    if (!expr) {
        printf("Failed to parse program\n");
        return 1;
    }

    // Print the parsed expression
    printf("Parsed: ");
    print_node(expr);
    printf("\n");

    // Evaluate the program
    Value result = eval_node(root_env, expr);

    // Print the result
    printf("Result: ");
    print_value(result);
    printf("\n");

    // Clean up the expression tree
    free_node(expr);

    // TODO: Clean up the environment
    return 0;
} 