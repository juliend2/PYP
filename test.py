# test
import py2php
import compiler

#unindented_source = py2php.get_source(compiler.parseFile('source.py'))
py2php.PHPVERSION = 5
unindented_source = py2php.get_source(compiler.parse('''
var = '5'+'4'+'7'+'32'
var += '5' + '3' + "43" + '2'
var += 5 + 4 + 4 + 5
'''))

print py2php.indent_source(py2php.add_semicolons(unindented_source))
