

def fonction(argu, argu2, defaut=8):
    if argu == 2 > 3 or argu == 4:
        argu += 3
        return argu * 2
    elif argu == 3:
        return 'trois'
    else:
        return argu

class Joie(base):
    def __init__(self, prop1, prop2, prop3='verbe'):
        self.prop1 = prop1
        self.prop2 = prop2
        self.prop3 = prop3

    def Crier(self):
        return self.prop1+' '+self.prop2

