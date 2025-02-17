#ifndef LISP_PARSER_H
#define LISP_PARSER_H

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <stdbool.h>
#include <assert.h>

// Type Definitions
typedef enum {
    NODE_ATOM,
    NODE_LIST
} NodeType;

typedef enum {
    ATOM_IDENTIFIER,  // Variable/function names
    ATOM_INTEGER,     // Integer literals
    ATOM_STRING,      // String literals
    ATOM_KEYWORD      // Language keywords (def, do, call, etc)
} AtomType;

typedef struct Node Node;
typedef struct NodeList NodeList;

struct NodeList {
    Node *node;
    struct NodeList *next;
};

struct Node {
    NodeType type;
    union {
        struct {
            AtomType atom_type;
            char *value;
        } atom;      // valid when type == NODE_ATOM
        NodeList *list;  // valid when type == NODE_LIST
    } data;
};

// Node Functions
void free_node(Node *node);

// Parser Functions
void skip_whitespace(const char **input);
char* parse_atom(const char **input);
AtomType determine_atom_type(const char *token);
Node* parse_expr(const char **input);

// Printer Functions
void print_node(const Node *node);
void print_node_internal(const Node *node, int indent_level);

// Interpreter Types
typedef enum {
    VAL_INTEGER,
    VAL_STRING,
    VAL_BOOLEAN,
    VAL_NULL,
    VAL_FUNCTION
} ValueType;

typedef struct Environment Environment;  // Forward declaration

// Value type that can hold any type of value
typedef struct Value {
    ValueType type;
    union {
        int integer;
        char *string;
        bool boolean;
        struct {
            NodeList *params;    // Parameter list
            Node *body;          // Function body
            Environment *env;    // Closure environment
        } function;
    } data;
} Value;

// Interpreter Functions
Environment *create_environment(Environment *parent);
Value eval_node(Environment *env, Node *node);
void print_value(Value value);

#endif // LISP_PARSER_H 