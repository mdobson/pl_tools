from func import Func

def move_to(fenv: Func, var, dst):
    if dst != var:
        fenv.code.append(('mov', var, dst))
    return dst

def scope_get_var(scope, name):
    while scope:
        if name in scope.names:
            return scope.names[name]
        scope = scope.prev
    return None, -1

def validate_type(tp):
    tp = tuple(tp)
    if tp not in {('void',), ('int',), ('byte',)}:
        raise ValueError('unknown type')
    return tp 