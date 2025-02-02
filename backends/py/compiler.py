from func import Func
from utils import move_to, validate_type, scope_get_var

def pl_comp_call(fenv: Func, node):
    _, name, *args = node
    arg_types = []
    for kid in args:
        tp, var = pl_comp_expr(fenv, kid)
        arg_types.append(tp)
        move_to(fenv, var, fenv.tmp())
    fenv.stack -= len(args)

    key = (name, tuple(arg_types))
    _, _, idx = fenv.get_var(key)
    func = fenv.funcs[idx]

    fenv.code.append(('call', idx, fenv.stack, fenv.level, func.level))
    dst = -1

    if func.rtype != ('void',):
        dst = fenv.tmp()
        
    return func.rtype, dst

def pl_comp_return(fenv: Func, node):
    _, *kid = node
    tp, var = ('void,'), -1
    if kid:
        tp, var = pl_comp_expr(fenv, kid[0])
    if tp != fenv.rtype:
        raise ValueError(f"Type mismatch: {tp} != {fenv.rtype}")
    fenv.code.append(('ret', var))
    return tp, var

def pl_comp_cond(fenv: Func, node):
    _, cond, yes, *no = node
    l_true = fenv.new_label()
    l_false = fenv.new_label()
    fenv.scope_enter()

    tp, var = pl_comp_expr(fenv, cond, allow_var=True)
    if tp == ('void',):
        raise ValueError("expected boolean condition")
    
    fenv.code.append(('jmpf', var, l_false))

    t1, a1 = pl_comp_expr(fenv, yes)
    if a1 >= 0:
        move_to(fenv, a1, fenv.stack)

    t2, a2 = ('void',), -1
    if no:
        fenv.code.append(('jmp', l_true))

    fenv.set_label(l_false)
    if no: 
        t2, a2 = pl_comp_expr(fenv, no[0])
        if a2 >= 0:
            move_to(fenv, a2, fenv.stack)

    fenv.set_label(l_true)
    fenv.scope_leave()
    if a1 < 0 or a2 < 0 or t1 != t2:
        return ('void',), -1
    else:
        return t1, fenv.tmp()
    
def pl_comp_loop(fenv: Func, node):
    _, cond, body = node
    fenv.scope.loop_start = fenv.new_label()
    fenv.scope.loop_end = fenv.new_label()

    fenv.scope_enter()
    fenv.set_label(fenv.scope.loop_start)

    _, var = pl_comp_expr(fenv, cond, allow_var=True)
    if var < 0:
        raise ValueError("bad loop condition")
    fenv.code.append(('jmpf', var, fenv.scope.loop_end))

    _, _ = pl_comp_expr(fenv, body)
    fenv.code.append(('jmp', fenv.scope.loop_start))

    fenv.set_label(fenv.scope.loop_end)
    fenv.scope_leave()

    return ('void',), -1


def pl_comp_expr_tmp(fenv: Func, node, *, allow_var=False):

    if not isinstance(node, list):
        return pl_comp_getvar(fenv, node)
    
    if len(node) == 0:
        raise ValueError("Empty list")
    
    if len(node) == 2 and node[0] in ('val', 'val8', 'str'):
        return pl_comp_const(fenv, node)
    
    binops = { '%', '*', '/', '+', '-', 'eq', 'ne', 'lt', 'le', 'gt', 'ge', 'and', 'or' }

    if len(node) == 3 and node[0] in binops:
        return pl_comp_binop(fenv, node)
    
    if len(node) == 2 and node[0] in {'-', 'not'}:
        return pl_comp_unop(fenv, node)

    if node[0] in ('do', 'then', 'else'):
        return pl_comp_scope(fenv, node)
    
    if node[0] == 'var' and len(node) == 3:
        if not allow_var:
            raise ValueError("var is not allowed")
        return pl_comp_newvar(fenv, node)
    
    if node[0] == 'set' and len(node) == 3:
        return pl_comp_setvar(fenv, node)
    
    if node == ['break']:
        if fenv.scope.loop_end < 0:
            raise ValueError("break is outside loop")
        fenv.code.append(('jmp', fenv.scope.loop_end))
        return ('void',), -1
    
    if node == ['continue']:
        if fenv.scope.loop_start < 0:
            raise ValueError("continue is outside loop")
        fenv.code.append(('jmp', fenv.scope.loop_start))
        return ('void',), -1
    
def pl_comp_newvar(fenv: Func, node):
    _, name, kid = node
    tp, var, = pl_comp_expr(fenv, kid)
    if var < 0:
        raise ValueError('bad variable init type')
    dst = fenv.add_var(name, tp)
    return tp, move_to(fenv, var, dst)

def pl_comp_const(fenv: Func, node):
    _, kid = node
    assert isinstance(kid, (int, str))
    dst = fenv.tmp()
    fenv.code.append(('const', kid, dst))
    tp = dict(val='int', val8='byte', str='ptr byte')[node[0]]
    tp = tuple(tp.split())
    return tp, dst

def pl_comp_getvar(fenv: Func, node):
    assert isinstance(node, str)
    flevel, tp, var = fenv.get_var(node)
    if flevel == fenv.level:
        return tp, var
    else:
        dst = fenv.tmp()
        fenv.code.append(('get_env', flevel, var, dst))
        return tp, dst

def pl_comp_setvar(fenv: Func, node):
    _, name, kid = node
    flevel, dst_tp, dst = fenv.get_var(name)
    tp, var = pl_comp_expr(fenv, kid)
    if dst_tp != tp:
        raise ValueError(f"Type mismatch: {dst_tp} != {tp}")
    
    if flevel == fenv.level:
        return dst_tp, move_to(fenv, var, dst)
    else:
        fenv.code.append(('set_env', flevel, dst, var))
        return dst_tp, move_to(fenv, var, fenv.tmp())

def pl_comp_scope(fenv: Func, node):
    fenv.scope_enter()
    tp, var = ('void',), -1

    groups = [[]]
    for kid in node[1:]:
        groups[-1].append(kid)
        if kid[0] == 'var':
            groups.append([])

    for g in groups:
        funcs = [
            pl_scan_func(fenv, kid)
            for kid in g if kid[0] == 'def' and len(kid) == 4
        ]

        for kid in g:
            if kid[0] == 'def' and len(kid) == 4:
                target, *funcs = funcs
                tp, var = pl_comp_func(target, kid)
            else:
                tp, var = pl_comp_expr(fenv, kid, allow_var=True)
    fenv.scope_leave()

    if var >= fenv.stack:
        var = move_to(fenv, var, fenv.tmp())
    return tp, var

def pl_comp_binop(fenv: Func, node):
    op, lhs, rhs = node

    save = fenv.stack
    t1, a1 = pl_comp_expr_tmp(fenv, lhs)
    t2, a2 = pl_comp_expr_tmp(fenv, rhs)
    fenv.stack = save

    if 'ptr' in (t1[0], t2[0]):
        raise NotImplementedError("Pointers")
    
    if not (t1 == t2 and t1[0] in ('int', 'byte')):
        raise ValueError(f"Type mismatch: {t1} != {t2}")

    rtype = t1
    if op in { 'eq', 'ge', 'gt', 'le', 'ne', 'lt' }:
        rtype = ('int',)

    suffix = ''

    if t1 == t2 and t1 == ('byte',):
        suffix = '8'

    dst = fenv.tmp()
    fenv.code.append(('binop' + suffix, op, a1, a2, dst))
    return rtype, dst

def pl_comp_unop(fenv: Func, node):
    op, arg = node
    t1, a1 = pl_comp_expr(fenv, arg)

    suffix = ''
    rtype = t1
    if op == '-':
        if t1[0] not in ('int', 'byte'):
            raise ValueError('bad unop types')
        if t1 == ('byte',):
            suffix = '8'
    elif op == 'not':
        if t1[0] not in ('int', 'byte', 'ptr'):
            raise ValueError('bad unop types')
        rtype = ('int',)    # boolean
    dst = fenv.tmp()
    fenv.code.append(('unop' + suffix, op, a1, dst))
    return rtype, dst

def pl_comp_expr(fenv: Func, node, *, allow_var=False):
    if allow_var:
        assert fenv.stack == fenv.nvar
    save = fenv.stack

    tp, var = pl_comp_expr_tmp(fenv, node, allow_var=allow_var)
    assert var < fenv.stack
    

    if allow_var:
        fenv.stack = fenv.nvar
    else:
        fenv.stack = save
    
    assert var <= fenv.stack
    return tp, var

def pl_scan_func(fenv: Func, node):
    _, (name, *rtype), args, _ = node
    rtype = validate_type(rtype)

    arg_type_list = tuple(validate_type(arg_type) for _, *arg_type in args)
    key = (name, arg_type_list)
    if key in fenv.scope.names:
        raise ValueError(f"Function {name} already defined")
    fenv.scope.names[key] = (rtype, len(fenv.funcs))
    func = Func(fenv)
    func.rtype = rtype
    fenv.funcs.append(func)
    return func

def pl_comp_func(fenv: Func, node):
    _, _, args, body = node

    for arg_name, *arg_type in args:
        if not isinstance(arg_name, str):
            raise ValueError("invalid argument name")
        arg_type = validate_type(arg_type)
        if arg_type == 'void':
            raise ValueError(f"{arg_type} is not allowed")
        fenv.add_var(arg_name, arg_type)
    assert fenv.stack == len(args)

    body_type, var = pl_comp_expr(fenv, body)
    if fenv.rtypep != ('void',) and fenv.rtype != body_type:
        raise ValueError(f"Bad body type: {body_type}")
    if fenv.rtype == ('void',):
        var = -1
    fenv.code.append(('ret', var))
    return ('void',), -1

def pl_comp_main(fenv: Func, node):
    assert node[:3] == ['def', ['main', 'int'], []]
    func = pl_scan_func(fenv, node)
    return pl_comp_func(func, node)
