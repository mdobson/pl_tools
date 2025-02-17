#include "lisp_parser.h"

// skip_whitespace
// Advances the input pointer past any whitespace characters.
void skip_whitespace(const char **input) {
    while (**input && isspace(**input))
        (*input)++;
}

// parse_atom
// Reads an atomic token from the input, stopping at whitespace or parentheses.
char* parse_atom(const char **input) {
    const char *start = *input;
    while (**input && !isspace(**input) && **input != '(' && **input != ')')
        (*input)++;
    size_t len = *input - start;
    char *token = malloc(len + 1);
    if (!token) {
        perror("malloc failed");
        exit(EXIT_FAILURE);
    }
    strncpy(token, start, len);
    token[len] = '\0';
    return token;
}

// determine_atom_type
// Analyzes a token string and determines its AtomType
AtomType determine_atom_type(const char *token) {
    if (!token) return ATOM_IDENTIFIER;  // Default for NULL tokens
    
    // Check if it's a number (integer)
    int is_number = 1;
    for (const char *p = token; *p != '\0'; p++) {
        if (!isdigit(*p)) {
            is_number = 0;
            break;
        }
    }
    if (is_number) return ATOM_INTEGER;
    
    // Check for keywords
    const char *keywords[] = {"def", "do", "call", "return", "var", NULL};
    for (const char **kw = keywords; *kw != NULL; kw++) {
        if (strcmp(token, *kw) == 0) {
            return ATOM_KEYWORD;
        }
    }
    
    // Check if it's a string (surrounded by quotes)
    size_t len = strlen(token);
    if (len >= 2 && token[0] == '"' && token[len-1] == '"') {
        return ATOM_STRING;
    }
    
    // Default case: it's an identifier
    return ATOM_IDENTIFIER;
}

// parse_expr
// Recursively parses an expression. An expression can be:
//   - A list: begins with '(' and continues until its matching ')'.
//   - An atom: any token other than a parenthesis.
Node* parse_expr(const char **input) {
    skip_whitespace(input);
    if (**input == '\0')
        return NULL;

    if (**input == '(') {
        // Begin a list.
        (*input)++; // consume '('
        Node *node = malloc(sizeof(Node));
        if (!node) {
            perror("malloc failed");
            exit(EXIT_FAILURE);
        }
        node->type = NODE_LIST;
        node->data.list = NULL;
        NodeList *last = NULL;

        // Parse each sub-expression until we hit the closing ')'.
        while (1) {
            skip_whitespace(input);
            if (**input == ')') {
                (*input)++; // consume ')'
                break;
            }
            Node *child = parse_expr(input);
            if (!child)
                break;

            // Wrap the child in a linked list node.
            NodeList *child_node = malloc(sizeof(NodeList));
            if (!child_node) {
                perror("malloc failed");
                exit(EXIT_FAILURE);
            }
            child_node->node = child;
            child_node->next = NULL;
            if (node->data.list == NULL)
                node->data.list = child_node;
            else
                last->next = child_node;
            last = child_node;
        }
        return node;
    } else if (**input == ')') {
        // Encountering a closing parenthesis here indicates an error.
        fprintf(stderr, "Unexpected closing parenthesis.\n");
        exit(EXIT_FAILURE);
    } else {
        // Parse an atomic token.
        char *token = parse_atom(input);
        Node *node = malloc(sizeof(Node));
        if (!node) {
            perror("malloc failed");
            exit(EXIT_FAILURE);
        }
        node->type = NODE_ATOM;
        node->data.atom.value = token;
        node->data.atom.atom_type = determine_atom_type(token);
        return node;
    }
} 