#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "expr.h"
#include "types.h"

char* read_file_to_string(const char* filename) {
    FILE* file = fopen(filename, "r");
    if (file == NULL) {
        fprintf(stderr, "Could not open file %s\n", filename);
        return NULL;
    }

    // Get file size
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    rewind(file);

    // Allocate buffer
    char* buffer = (char*)malloc(file_size + 1);
    if (buffer == NULL) {
        fprintf(stderr, "Memory allocation failed\n");
        fclose(file);
        return NULL;
    }

    // Read file into buffer
    size_t read_size = fread(buffer, 1, file_size, file);
    buffer[read_size] = '\0';

    fclose(file);
    return buffer;
}


int skip_space(const char* s, int idx) {
    while (1) {
        int save = idx;
        
        // Skip whitespace
        while (s[idx] != '\0' && (s[idx] == ' ' || s[idx] == '\t' || s[idx] == '\n' || s[idx] == '\r')) {
            idx++;
        }

        // Skip comments
        if (s[idx] == ';') {
            idx++;
            while (s[idx] != '\0' && s[idx] != '\n') {
                idx++;
            }
        }

        if (idx == save) {
            break;
        }
    }
    return idx;
}


Expr* parse_atom(char* s) {
    Expr* expr = (Expr*)malloc(sizeof(Expr));
    expr->type = ATOM;
    expr->value = s;
    return expr;
}

Expr* parse_expr(char* s) {
    int idx = 0;
    idx = skip_space(s, idx);

    if (s[idx] == '(') {
        idx++;
        Expr* expr = (Expr*)malloc(sizeof(Expr));
        expr->type = EXPR;
        expr->value = s + idx;

        while (1) {
            idx = skip_space(s, idx);
            if (s[idx] == '\0') {
                free(expr);
                return NULL; // Unclosed parenthesis
            }
            if (s[idx] == ')') {
                idx++;
                break;
            }
            Expr* sub_expr = parse_expr(s + idx);
            if (sub_expr == NULL) {
                free(expr);
                return NULL;
            }
            // TODO: Add sub_expr to list
            idx += (sub_expr->value - (s + idx));
            free(sub_expr);
        }
        return expr;
    }
    else if (s[idx] == ')') {
        return NULL; // Unmatched parenthesis
    }
    else {
        int start = idx;
        while (s[idx] != '\0' && !isspace(s[idx]) && s[idx] != '(' && s[idx] != ')') {
            idx++;
        }
        char* atom = (char*)malloc(idx - start + 1);
        strncpy(atom, s + start, idx - start);
        atom[idx - start] = '\0';
        return parse_atom(atom);
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <filename>\n", argv[0]);
        return 1;
    }

    char* content = read_file_to_string(argv[1]);
    if (content == NULL) {
        return 1;
    }

    printf("%s", content);
    free(content);
    return 0;
}
