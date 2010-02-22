# test
import py2php
import compiler

#unindented_source = py2php.get_source(compiler.parseFile('source.py'))
py2php.PHPVERSION = 4
unindented_source = py2php.get_source(compiler.parse('''
variable = 3 + "str" + 3 + "str"'''))


print py2php.indent_source(py2php.add_semicolons(unindented_source))
