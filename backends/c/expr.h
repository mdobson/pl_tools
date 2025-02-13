#ifndef EXPR_H
#define EXPR_H

typedef struct Expr {
    int type;
    char *value;
} Expr;

Expr* parse_atom(char* s);
Expr* parse_expr(char* s);

#endif
