from scope import Scope

class Func:
    def __init__(self, prev):
        self.prev = prev
        self.level = (prev.level + 1) if prev else 0
        self.rtype = None
        self.funcs = prev.funcs if prev else []
        self.scope = Scope(None)
        self.code = []
        self.nvar = 0
        self.stack = 0
        self.labels = []

    def new_label(self):
        l = len(self.labels)
        self.labels.append(None)
        return l
    
    def set_label(self, l):
        assert l < len(self.labels)
        self.labels[l] = len(self.code)
    
    def tmp(self):
        dst = self.stack
        self.stack += 1
        return dst
    
    def add_var(self, name, tp):
        if name in self.scope.names:
            raise ValueError(f"Name {name} already defined")
        self.scope.names[name] = (tp, self.nvar)
        self.scope.nlocal += 1

        assert self.stack == self.nvar
        dst = self.stack
        self.stack += 1
        self.nvar += 1
        return dst

    def get_var(self, name):
        from utils import scope_get_var
        tp, var = scope_get_var(self.scope, name)
        if var >= 0:
            return self.level, tp, var
        if not self.prev:
            raise ValueError(f"Variable {name} not defined")
        return self.prev.get_var(name)
    
    def scope_enter(self):
        self.scope = Scope(self.scope)
        self.scope.save = self.stack
    
    def scope_leave(self):
        self.stack = self.scope.save
        self.nvar -= self.scope.nlocal
        self.scope = self.scope.prev 