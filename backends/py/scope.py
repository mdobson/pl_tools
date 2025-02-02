class Scope:
    def __init__(self, prev):
        self.prev = prev
        self.nlocal = 0
        self.names = dict()
        self.loop_start = prev.loop_start if prev else -1
        self.loop_end = prev.loop_end if prev else -1 