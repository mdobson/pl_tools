from exceptions import LoopBreak, LoopContinue, FuncReturn
from parser import pl_parse_prog

def name_lookup(env, key):
    while env:
        current, env = env
        if key in current:
            return current
    raise ValueError(f"Name {key} not found")

def pl_eval(env, node):
    if not isinstance(node, list):
        assert isinstance(node, str)
        return name_lookup(env, node)[node]

    if len(node) == 0:
        raise ValueError("Empty list")
    
    import operator
    binary_ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        'eq': operator.eq,
        'ne': operator.ne,
        'lt': operator.lt,
        'le': operator.le,
        'gt': operator.gt,
        'ge': operator.ge,
        'and': operator.and_,
        'or': operator.or_
    }
    
    if len(node) == 3 and node[0] in binary_ops:
        op = binary_ops[node[0]]
        opret = op(pl_eval(env, node[1]), pl_eval(env, node[2]))
        return opret
    
    unops = {
        'neg': operator.neg,
        'not': operator.not_
    }

    if len(node) == 2 and node[0] in unops:
        op = unops[node[0]]
        return op(pl_eval(env, node[1]))
    
    if len(node) in (3,4) and node[0] in ('?', 'if'):
        _, cond, yes, *no = node
        no = no[0] if no else ['val', None]
        new_env = (dict(), env)
        if pl_eval(new_env, cond):
            return pl_eval(new_env, yes)
        else:
            return pl_eval(new_env, no)

    if node[0] == 'print':
        return print(*(pl_eval(env, val) for val in node[1:]))
    
    if node[0] in ('do', 'then', 'else') and len(node) > 1:
        new_env = (dict(), env)
        for val in node[1:]:
            val = pl_eval(new_env, val)
        return val
    
    if node[0] == 'var':
        _, name, val = node
        scope, _ = env
        if name in scope:
            raise ValueError(f"Name {name} already defined")
        val = pl_eval(env, val)
        scope[name] = val
        return val
    
    if node[0] == 'set' and len(node) == 3:
        _, name, val = node
        scope = name_lookup(env, name)
        val = pl_eval(env, val)
        scope[name] = val
        return val
    
    if node[0] == 'loop' and len(node) == 3:
        _, cond, body = node
        ret = None
        while True:
            new_env = (dict(), env)
            if not pl_eval(new_env, cond):
                break
            try:
                ret = pl_eval(new_env, body)
            except LoopBreak:
                break
            except LoopContinue:
                continue
        return ret
    
    if node[0] == 'def' and len(node) == 4:
        _, name, args, body = node
        for arg_name in args:
            if not isinstance(arg_name, str):
                raise ValueError("invalid argument name")
        if len(args) != len(set(args)):
            raise ValueError("duplicate argument name")
        dct, _ = env
        key = (name, len(args))
        if key in dct:
            raise ValueError("function already defined")
        dct[key] = (args, body, env)
        return 
    
    if node[0] == 'call' and len(node) >= 2:
        _, name, *args = node
        key = (name, len(args))
        fargs, fbody, fenv = name_lookup(env, key)[key]
        new_env = dict()
        for arg_name, arg_val in zip(fargs, args):
            new_env[arg_name] = pl_eval(env, arg_val)
        try:
            return pl_eval((new_env, fenv), fbody)
        except FuncReturn as ret:
            return ret.val
    
    if node[0] == 'break' and len(node) == 1:
        raise LoopBreak
    
    if node[0] == 'continue' and len(node) == 1:
        raise LoopContinue
    
    if node[0] == 'return' and len(node) == 1:
        raise FuncReturn(None)
    
    if node[0] == 'return' and len(node) == 2:
        _, val = node
        raise FuncReturn(pl_eval(env, val))
    
    if len(node) == 2:
        return node[1]

    raise ValueError("Invalid node")

def test_eval():
    def f(s):
        parse_result = pl_parse_prog(s)
        result = pl_eval(None, parse_result)
        return result
    assert f('''
        (def fib (n)
            (if (le n 0)
                (then 0)
                (else (+ n (call fib (- n 1))))))
        (call fib 5)
    ''') == 5 + 4 + 3 + 2 + 1

    assert f('''
        (def fib (n) (do
            (var r 0)
            (loop (gt n 0) (do
                (set r (+ r n))
                (set n (- n 1))
            ))
            (return r)
        ))
        (call fib 5)
    ''') == 5 + 4 + 3 + 2 + 1

    assert f('''
        (def add (n) (do
            (var r 1)
            (return (+ r n))
        ))
        (call add 5)
    ''') == 6
if __name__ == '__main__':
    test_eval() 