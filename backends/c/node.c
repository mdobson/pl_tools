#include "lisp_parser.h"

// free_node
// Recursively frees all memory allocated for the parse tree.
void free_node(Node *node) {
    if (!node)
        return;
    if (node->type == NODE_ATOM) {
        free(node->data.atom.value);
    } else if (node->type == NODE_LIST) {
        NodeList *child = node->data.list;
        while (child) {
            NodeList *next = child->next;
            free_node(child->node);
            free(child);
            child = next;
        }
    }
    free(node);
} 