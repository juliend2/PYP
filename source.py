"""Doc string pour le module"""

for key,value in list:
    dosomething()
    print 'joie'

for val in list:
    var = doshit(val,attr)
    print 'joie'

def fonction(argu, argu2, defaut=8):
    '''doc string pour la fonction'''
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
    '''doc string pour la classe'''
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

print 2 + 3
print 4 / 2
print 3.8 / 4
print ( 4 + 4 ) / 3
print 2 - 1
print 3 + 3
print 3 ^ 3

array1 = ['elem1', 'elem2', variab, 23]
array2 = {
    'key1':'value',
    key2:value2
    }
print array1[0]
print array2['key1']
print array2['key1'][0]

print 20 != '20'
print 20 > 23
print 30 < 2
print 32 <= 32
print 32 >= 32
var *= 1
var /= 1
var = False
var = True
print True
print False
print None

if not value:
    print 'hoy'

global var1, var2
