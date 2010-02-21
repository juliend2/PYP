# test
import py2php
import compiler

#unindented_source = py2php.get_source(compiler.parseFile('source.py'))
py2php.PHPVERSION = 5
unindented_source = py2php.get_source(compiler.parse('''
try:
    returned = call_user_func([classname, func])
except Exception,e:
    errors += 1
'''),'''<?php
try {
    $returned = call_user_func(array($classname, $func));
catch (Exception $e) {
    $errors += 1;
}

?>''')

unindented_source = py2php.get_source( compiler.parse("'''module docstring'''\n'''commentaire'''\nresult = mysql_query(self.sql)") )

print py2php.indent_source(py2php.add_semicolons(unindented_source))
