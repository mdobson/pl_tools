def skip_space(s: str, idx: int):
    while True:
        save = idx
        while idx < len(s) and s[idx].isspace():
            idx += 1
        if idx < len(s) and s[idx] == ';':
            idx += 1
            while idx < len(s) and s[idx] != '\n':
                idx += 1
        if idx == save:
            break
    return idx

def parse_atom(s: str):
    import json
    try:
        return ['val', json.loads(s)]
    except:
        return s

def parse_expr(s: str, idx: int):
    idx = skip_space(s, idx)
    if s[idx] == '(':
        idx+=1
        l = []
        while True:
            idx = skip_space(s, idx)
            if idx >= len(s):
                raise ValueError("Unclosed parenthesis")
            if s[idx] == ')':
                idx += 1
                break
            idx, v = parse_expr(s, idx)
            l.append(v)
        return idx, l
    elif s[idx] == ')':
        raise Exception("Unmatched parenthesis")
    else:
        start = idx
        while idx < len(s) and not s[idx].isspace() and s[idx] not in '()':
            idx += 1
        return idx, parse_atom(s[start:idx])

def pl_parse(s: str):
    idx, node = parse_expr(s, 0)
    idx = skip_space(s, idx)
    if idx < len(s):
        raise ValueError("Unexpected characters at the end of the input")
    return node

def pl_parse_prog(s: str):
    return pl_parse('(do ' + s + ')')

def pl_parse_main(s):
    return pl_parse('(def (main int) () (do ' + s + '))') 