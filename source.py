for key,value in list:
    dosomething()
    print 'joie'

for val in list:
    var = doshit(val,attr)
    print 'joie'

def fonction(argu, argu2, defaut=8):
    if argu == 2 > 3 or argu == 4:
        argu += 3
        return argu * 2
    elif argu == 3:
        return 'trois'
    elif argu == 4:
        return 'quatre'
    else:
        return argu

class Joie(base):
    def __init__(self, prop1, prop2, prop3='verbe'):
        self.prop1 = prop1
        self.prop2 = prop2
        self.prop3 = prop3

    def Crier(self, joie):
        if joie:
            print 3 % 3
            return '%s %s' % (self.prop1, self.prop2)
        else:
            return '%d' % self.prop1
        return self.prop1+' '+self.prop2

obj = Joie('prop1', 'prop2', 'prop3')
print obj.Crier('joie')
print obj.prop1.Crier('torp')
