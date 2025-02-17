#include "lisp_parser.h"

// Forward declaration for scope management
typedef struct Scope Scope;

// A scope is a hashtable of variable bindings
struct Scope {
    struct {
        char *name;
        Value value;
    } *bindings;
    size_t capacity;
    size_t size;
};

// Environment is a linked list of scopes (for lexical scoping)
struct Environment {
    Scope *scope;
    Environment *parent;
};

// Create a new scope
Scope *create_scope(size_t initial_capacity) {
    Scope *scope = malloc(sizeof(Scope));
    if (!scope) {
        perror("Failed to allocate scope");
        exit(EXIT_FAILURE);
    }
    scope->capacity = initial_capacity;
    scope->size = 0;
    scope->bindings = calloc(initial_capacity, sizeof(*scope->bindings));
    if (!scope->bindings) {
        perror("Failed to allocate bindings");
        exit(EXIT_FAILURE);
    }
    return scope;
}

// Create a new environment with a parent
Environment *create_environment(Environment *parent) {
    Environment *env = malloc(sizeof(Environment));
    if (!env) {
        perror("Failed to allocate environment");
        exit(EXIT_FAILURE);
    }
    env->scope = create_scope(16);  // Start with space for 16 bindings
    env->parent = parent;
    return env;
}

// Look up a variable in the environment chain
Value *lookup_variable(Environment *env, const char *name) {
    while (env) {
        // Search current scope
        for (size_t i = 0; i < env->scope->size; i++) {
            if (strcmp(env->scope->bindings[i].name, name) == 0) {
                return &env->scope->bindings[i].value;
            }
        }
        env = env->parent;
    }
    return NULL;
}

// Define a new variable in the current scope
void define_variable(Environment *env, const char *name, Value value) {
    Scope *scope = env->scope;
    
    // Check if we need to resize
    if (scope->size >= scope->capacity) {
        size_t new_capacity = scope->capacity * 2;
        scope->bindings = realloc(scope->bindings, 
                                new_capacity * sizeof(*scope->bindings));
        if (!scope->bindings) {
            perror("Failed to resize scope");
            exit(EXIT_FAILURE);
        }
        scope->capacity = new_capacity;
    }
    
    // Add new binding
    scope->bindings[scope->size].name = strdup(name);
    scope->bindings[scope->size].value = value;
    scope->size++;
}

// Create integer value
Value create_integer(int n) {
    Value v = {.type = VAL_INTEGER, .data.integer = n};
    return v;
}

// Create string value
Value create_string(const char *s) {
    Value v = {.type = VAL_STRING, .data.string = strdup(s)};
    return v;
}

// Create boolean value
Value create_boolean(bool b) {
    Value v = {.type = VAL_BOOLEAN, .data.boolean = b};
    return v;
}

// Create null value
Value create_null(void) {
    Value v = {.type = VAL_NULL};
    return v;
}

// Evaluate an atom node
Value eval_atom(Environment *env, Node *node) {
    assert(node->type == NODE_ATOM);
    
    switch (node->data.atom.atom_type) {
        case ATOM_INTEGER: {
            // Convert string to integer
            char *endptr;
            int value = strtol(node->data.atom.value, &endptr, 10);
            if (*endptr != '\0') {
                fprintf(stderr, "Invalid integer: %s\n", node->data.atom.value);
                exit(EXIT_FAILURE);
            }
            return create_integer(value);
        }
        
        case ATOM_STRING:
            return create_string(node->data.atom.value);
            
        case ATOM_IDENTIFIER: {
            // Look up variable in environment
            Value *value = lookup_variable(env, node->data.atom.value);
            if (!value) {
                fprintf(stderr, "Undefined variable: %s\n", node->data.atom.value);
                exit(EXIT_FAILURE);
            }
            return *value;
        }
        
        default:
            fprintf(stderr, "Unsupported atom type\n");
            exit(EXIT_FAILURE);
    }
}

// Forward declaration for mutual recursion
Value eval_node(Environment *env, Node *node);

// Evaluate a list node (function call or special form)
Value eval_list(Environment *env, Node *node) {
    assert(node->type == NODE_LIST);
    
    // Empty list is an error
    if (!node->data.list) {
        fprintf(stderr, "Empty list in evaluation\n");
        exit(EXIT_FAILURE);
    }
    
    // Get the first element (operator)
    Node *op = node->data.list->node;
    if (op->type != NODE_ATOM) {
        fprintf(stderr, "Operator must be an atom\n");
        exit(EXIT_FAILURE);
    }
    
    // Handle special forms
    if (strcmp(op->data.atom.value, "def") == 0) {
        // Function definition
        // (def name (args) body)
        NodeList *rest = node->data.list->next;
        if (!rest || !rest->next || !rest->next->next) {
            fprintf(stderr, "Malformed def\n");
            exit(EXIT_FAILURE);
        }
        
        // Extract function name
        Node *name_node = rest->node;
        if (name_node->type != NODE_ATOM) {
            fprintf(stderr, "Function name must be an atom\n");
            exit(EXIT_FAILURE);
        }
        
        // Create function value
        Value func = {
            .type = VAL_FUNCTION,
            .data.function = {
                .params = rest->next->node->data.list,  // Parameter list
                .body = rest->next->next->node,         // Function body
                .env = env                              // Capture current environment
            }
        };
        
        // Define the function in current environment
        define_variable(env, name_node->data.atom.value, func);
        return create_null();
    }
    
    if (strcmp(op->data.atom.value, "var") == 0) {
        // Variable definition
        // (var name value)
        NodeList *rest = node->data.list->next;
        if (!rest || !rest->next) {
            fprintf(stderr, "Malformed var\n");
            exit(EXIT_FAILURE);
        }
        
        Node *name_node = rest->node;
        if (name_node->type != NODE_ATOM) {
            fprintf(stderr, "Variable name must be an atom\n");
            exit(EXIT_FAILURE);
        }
        
        // Evaluate the value and define it
        Value value = eval_node(env, rest->next->node);
        define_variable(env, name_node->data.atom.value, value);
        return value;
    }
    
    // TODO: Add more special forms (if, loop, etc.)
    
    // Otherwise, treat as function call
    // First evaluate the operator to get the function
    Value func = eval_node(env, op);
    if (func.type != VAL_FUNCTION) {
        fprintf(stderr, "Attempting to call non-function\n");
        exit(EXIT_FAILURE);
    }
    
    // Create new environment for function call
    Environment *call_env = create_environment(func.data.function.env);
    
    // Evaluate arguments and bind to parameters
    NodeList *arg = node->data.list->next;
    NodeList *param = func.data.function.params;
    while (arg && param) {
        Value arg_val = eval_node(env, arg->node);
        define_variable(call_env, param->node->data.atom.value, arg_val);
        arg = arg->next;
        param = param->next;
    }
    
    if (arg || param) {
        fprintf(stderr, "Wrong number of arguments\n");
        exit(EXIT_FAILURE);
    }
    
    // Evaluate function body in new environment
    return eval_node(call_env, func.data.function.body);
}

// Main evaluation function
Value eval_node(Environment *env, Node *node) {
    if (node->type == NODE_ATOM) {
        return eval_atom(env, node);
    } else {
        return eval_list(env, node);
    }
}

// Helper function to print a value
void print_value(Value value) {
    switch (value.type) {
        case VAL_INTEGER:
            printf("%d", value.data.integer);
            break;
        case VAL_STRING:
            printf("\"%s\"", value.data.string);
            break;
        case VAL_BOOLEAN:
            printf("%s", value.data.boolean ? "true" : "false");
            break;
        case VAL_NULL:
            printf("null");
            break;
        case VAL_FUNCTION:
            printf("<function>");
            break;
    }
} 