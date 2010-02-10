import py2php
import unittest
import compiler

def parsepyp(pypsource):
    unindented_source = py2php.get_source(compiler.parse(pypsource))
    return py2php.indent_source(py2php.add_semicolons(unindented_source))

class TestAssignation(unittest.TestCase):
    
    def testAssignNumber(self):
        self.assertEqual(parsepyp('deux = 2'), '''<?php
$deux = 2;
?>''')
        
    def testAssignEndOfLine(self):
        self.assertEqual(parsepyp('float = 3.4\n'), '''<?php
$float = 3.4;
?>''')
        
    def testAssignDoubleQuotedStringEndOfLine(self):
        self.assertEqual(parsepyp('float = "3.4"\n'), '''<?php
$float = "3.4";
?>''')
        
    def testAssign2IdentifiersEndOfLine(self):
        self.assertEqual(parsepyp('deux = joie\ntrois = banane\n'), '''<?php
$deux = $joie;
$trois = $banane;
?>''')
        
    def testAssignFunctionCallEndOfLine(self):
        self.assertEqual(parsepyp('deux = poulet()\n'), '''<?php
$deux = poulet();
?>''')

    def testAssignMethodCallEndOfLine(self):
        self.assertEqual(parsepyp('deux = obj.poulet()\n'), '''<?php
$deux = $obj->poulet();
?>''')

    def testAssignMethodPlusArgsCallEndOfLine(self):
        self.assertEqual(parsepyp('deux = obj.poulet(ab, cd)\n'), '''<?php
$deux = $obj->poulet($ab, $cd);
?>''')
        
    def testAssign2MethodPlusArgsCallEndOfLine(self):
        self.assertEqual(parsepyp('deux = obj.poulet(ab, cd)\ntrois = obj.poutine(vw, xy)\n'), '''<?php
$deux = $obj->poulet($ab, $cd);
$trois = $obj->poutine($vw, $xy);
?>''')
        
class TestCall(unittest.TestCase):

    def testSimpleFuncCallEndOfLine(self):
        self.assertEqual(parsepyp('prout()\n'), '''<?php
prout();
?>''')
    
    def testSimpleMethodCallEndOfLine(self):
        self.assertEqual(parsepyp('obj.prout()\n'), '''<?php
$obj->prout();
?>''')


class TestDefBlock(unittest.TestCase):
    
    def testDef(self):
        self.assertEqual(parsepyp('''\
def mafonction(): 
    poulet()
'''),'''<?php
function mafonction () {
    poulet();
}

?>''')
    def testDefAssign(self):
        self.assertEqual(parsepyp('''\
def mafonction(): 
    mavar = poulet()
'''),'''<?php
function mafonction () {
    $mavar = poulet();
}

?>''')

    def testDefPassArguments(self):
        self.assertEqual(parsepyp('''\
def mafonction(argument): 
    mavar = argument
'''),'''<?php
function mafonction ($argument) {
    $mavar = $argument;
}

?>''')

    def testDefPassDefaultArguments(self):
        self.assertEqual(parsepyp('''\
def mafonction(argument = 'valeur par defaut'):
    mavar = argument
'''),'''<?php
function mafonction ($argument = "valeur par defaut") {
    $mavar = $argument;
}

?>''')

    def testDefPass2DefaultArguments(self):
        self.assertEqual(parsepyp('''\
def mafonction(argument = 'valeur par defaut', argument2 = 'valeur par defaut 2'): 
    mavar = argument
'''),'''<?php
function mafonction ($argument = "valeur par defaut", $argument2 = "valeur par defaut 2") {
    $mavar = $argument;
}

?>''')

    def testDefPass1ArgPlus2DefaultArgs(self):
        self.assertEqual(parsepyp('''\
def mafonction(nombre, argument = 'valeur par defaut', argument2 = 'valeur par defaut 2'):
    mavar = argument
'''),'''<?php
function mafonction ($nombre, $argument = "valeur par defaut", $argument2 = "valeur par defaut 2") {
    $mavar = $argument;
}

?>''')

    def testDefPass2Arguments(self):
        self.assertEqual(parsepyp('''\
def mafonction(argument, bonsoir): 
    mavar = argument
    arg2 = bonsoir

'''),'''<?php
function mafonction ($argument, $bonsoir) {
    $mavar = $argument;
    $arg2 = $bonsoir;
}

?>''')

    def testDefAssign2Lines(self):
        self.assertEqual(parsepyp('''\
def mafonction(): 
    mavar = poulet()
    trois = valeur
'''),'''<?php
function mafonction () {
    $mavar = poulet();
    $trois = $valeur;
}

?>''')

    def testIfInDef(self):
        self.assertEqual(parsepyp('''\
def mafonction():
    if (drole):
        joie = cool
'''),'''<?php
function mafonction () {
    if ($drole) {
        $joie = $cool;
    }
}

?>''')

class TestIfBlock(unittest.TestCase):
    
    def testIf(self):
        self.assertEqual(parsepyp('''\
if (variable) :
    poulet()
'''),'''<?php
if ($variable) {
    poulet();
}

?>''')

    def testIfDefaultArg(self):
        self.assertEqual(parsepyp('''\
if (variable == 2): 
    poulet()
'''),'''<?php
if ($variable === 2) {
    poulet();
}

?>''')

    def testIfElse(self):
        self.assertEqual(parsepyp('''\
if (variable) :
    poulet()
else:
    pouletfrit()
'''),'''<?php
if ($variable) {
    poulet();
}
else {
    pouletfrit();
}

?>''')

    def testIf2Lines(self):
        self.assertEqual(parsepyp('''\
if (variable) :
    val = vari()
    valeur = fonc()
'''),'''<?php
if ($variable) {
    $val = vari();
    $valeur = fonc();
}

?>''')

    def testElseIf2Lines(self):
        self.assertEqual(parsepyp('''\
if (variable) :
    val = vari()
    valeur = fonc()
elif (valeur2): 
    drole = rire
'''),'''<?php
if ($variable) {
    $val = vari();
    $valeur = fonc();
}
elseif ($valeur2) {
    $drole = $rire;
}

?>''')

    def testDoubleElseIf(self):
        self.assertEqual(parsepyp('''\
if (variable): 
    val = vari()
    valeur = fonc()
elif (valeur2):
    drole = rire
elif (valeur3):
    drolefou = rirefou
'''),'''<?php
if ($variable) {
    $val = vari();
    $valeur = fonc();
}
elseif ($valeur2) {
    $drole = $rire;
}
elseif ($valeur3) {
    $drolefou = $rirefou;
}

?>''')

    def testNestedIfs(self):
        self.assertEqual(parsepyp('''\
if (variable) :
    val = vari()
    valeur = fonc()
    if (autre):
        joa = trucmalade
'''),'''<?php
if ($variable) {
    $val = vari();
    $valeur = fonc();
    if ($autre) {
        $joa = $trucmalade;
    }
}

?>''')

class TestForBlock(unittest.TestCase):
    
    def testFor(self):
        self.assertEqual(parsepyp('''\
for truc in machins: 
    print(truc)
'''),'''<?php
foreach ($machins as $truc) {
    print $truc;
}

?>''')

    def testForKeyValue(self):
        self.assertEqual(parsepyp('''\
for cle,valeur in machins:
    print(cle)
'''),'''<?php
foreach ($machins as $cle => $valeur) {
    print $cle;
}

?>''')


class TestOperators(unittest.TestCase):
    
        
    def testFor(self):
        self.assertEqual(parsepyp('var = 3 + 2'),'''<?php
$var = (3 + 2);
?>''')

if __name__ == '__main__':
    unittest.main()



