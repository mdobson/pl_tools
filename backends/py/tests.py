from interpreter import pl_eval
from parser import pl_parse_prog

def test_eval():
    def f(s):
        parse_result = pl_parse_prog(s)
        #print(parse_result)
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

    print(f('''
        (def add (n) (do
            (var r "1")
            (return (+ r n))
        ))
        (call add "foo")
    '''))

if __name__ == '__main__':
    test_eval() 