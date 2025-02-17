#include "lisp_parser.h"

// print_node_internal
// Internal helper function that handles indentation level
void print_node_internal(const Node *node, int indent_level) {
    // Print indentation for everything except the first level
    if (indent_level > 0) {
        printf("\n%*s", indent_level * 2, "");
    }

    if (node->type == NODE_ATOM) {
        // Print atom value with appropriate color coding and type annotation
        const char *type_str;
        switch (node->data.atom.atom_type) {
            case ATOM_INTEGER:
                type_str = "\033[33m<int>\033[0m";   // yellow for numbers
                break;
            case ATOM_STRING:
                type_str = "\033[32m<str>\033[0m";   // green for strings
                break;
            case ATOM_KEYWORD:
                type_str = "\033[36m<kw>\033[0m";    // cyan for keywords
                break;
            case ATOM_IDENTIFIER:
                type_str = "\033[35m<id>\033[0m";    // magenta for identifiers
                break;
            default:
                type_str = "<unknown>";
        }
        printf("%s %s", node->data.atom.value, type_str);
    } else if (node->type == NODE_LIST) {
        printf("(");  // Opening parenthesis for list
        
        NodeList *child = node->data.list;
        int first = 1;
        
        while (child) {
            if (!first) {
                // Don't add space after opening parenthesis
                printf(" ");
            }
            // Increase indent level for nested elements
            print_node_internal(child->node, indent_level + 1);
            first = 0;
            child = child->next;
        }
        
        // If this was a multi-line list, print closing parenthesis on new line
        if (!first && node->data.list && node->data.list->next) {
            printf("\n%*s", indent_level * 2, "");
        }
        printf(")");
    }
}

// print_node
// Recursively prints the parse tree with pretty formatting
void print_node(const Node *node) {
    print_node_internal(node, 0);
    printf("\n");  // Add final newline
} 