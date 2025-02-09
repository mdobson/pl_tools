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
        raise ValueError(f'unknown type of {tp}')
    return tp 

def ir_dump(root: Func):
    out = []
    for i, func in enumerate(root.funcs):
        out.append(f'func{i}:')
        pos2labels = dict()
        for label, pos in enumerate(func.labels):
            pos2labels.setdefault(pos, []).append(label)
        for pos, instr in enumerate(func.code):
            for label in pos2labels.get(pos, []):
                out.append(f'L{label}:')
            if instr[0].startswith('jmp'):
                instr = instr[:-1] + (f'L{instr[-1]}',)
            if instr[0] == 'const' and isinstance(instr[1], str):
                import json
                instr = list(instr)
                instr[1] = json.dumps(instr[1])
            out.append('    ' + ' '.join(map(str, instr)))
        out.append('')

    return '\n'.join(out)