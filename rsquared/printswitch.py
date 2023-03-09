class Switch:
    def __init__(self):
        self.print = True
switch = Switch()

def PRINTS(*args, **kwargs):
    if switch.print:
        print(*args, **kwargs)