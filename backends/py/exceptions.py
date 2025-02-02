class LoopBreak(Exception):
    def __init__(self):
        super().__init__("break is outside loop")

class LoopContinue(Exception):
    def __init__(self):
        super().__init__("continue is outside loop")

class FuncReturn(Exception):
    def __init__(self, val):
        super().__init__("return outside a function")
        self.val = val 