# Language Specification

pl is a lisp-like language that is designed to be easy to understand and use.

## Grammar

```antlr
grammar PlLang;

program
    : expr* EOF
    ;

expr
    : literal
    | IDENTIFIER
    | function_def
    | call
    | var_decl
    | return_stmt
    | print_stmt
    | file_expr
    | do_block
    | arith_expr
    | list_expr
    ;

function_def
    : '(' DEF (function_signature_with_type | IDENTIFIER) param_list func_body ')'
    ;

function_signature_with_type
    : '(' IDENTIFIER type ')'
    ;

param_list
    : '(' parameter* ')'
    ;

parameter
    : IDENTIFIER
    | '(' IDENTIFIER type ')'
    ;

func_body
    : do_block
    | expr
    ;

do_block
    : '(' DO expr+ ')'
    ;

call
    : '(' CALL IDENTIFIER expr* ')'
    ;

var_decl
    : '(' VAR IDENTIFIER expr ')'
    ;

return_stmt
    : '(' RETURN expr ')'
    ;

print_stmt
    : '(' PRINT expr ')'
    ;

file_expr
    : '(' FILE STRING ')'
    ;

arith_expr
    : '(' arith_operator expr+ ')'
    ;

arith_operator
    : '+'
    | '-'
    | '*'
    | '/'
    ;

list_expr
    : '(' expr* ')'
    ;

literal
    : INTEGER
    | STRING
    ;

type
    : IDENTIFIER
    ;

DEF    : 'def';
DO     : 'do';
CALL   : 'call';
VAR    : 'var';
RETURN : 'return';
PRINT  : 'print';
FILE   : 'file';

INTEGER
    : [0-9]+
    ;

STRING
    : '"' (~["\\] | '\\' . )* '"'
    ;

IDENTIFIER
    : [a-zA-Z_][a-zA-Z0-9_]*
    ;

WS
    : [ \t\r\n]+ -> skip
    ;
```
