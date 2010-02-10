# test
import py2php
import compiler

#unindented_source = py2php.get_source(compiler.parseFile('source.py'))
py2php.PHPVERSION = 5
unindented_source = py2php.get_source(compiler.parse('''class Joie:
    def __init__(self):
        print 'joie'
    def poulet(self):
        print 'rototo'
'''))

print py2php.indent_source(py2php.add_semicolons(unindented_source))
