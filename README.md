# Prerequisites :

- Python 2.6 on Linux (haven't tested on Mac or Windows)


# Usage :

1. cd into the directory that contains this script (py2php.py, watch.py, etc)
example : cd ~/myscripts/pyp/
2. python watch.py <pyp sources directory> <php destination directory>
example : python watch.py ./ /var/www/projectname/


# TODO :

- permettre ce truc : =& (??)
- parser les quelques methodes cool du python dans leur equivalent en fonction
php. Genre :
    * ', '.join(list) deviandrait implode(', ', $list) 
    * str.split('-', 1) deviendrait explode('-', $str, 1)
    * list.append('element') deviendrait array_push($list, 'element')


# Nice to have:

- $this->{'nom de propriete'}->methode();
- un setting pour determiner la version de PHP que l'on compile. Si c'est 4 ou 5
- permettre d'acceder a des attributs de classe comme
parent::ParentClassMethod() (*** N'EXISTE PAS EN PYTHON***)

# Known issues :
- the strings that are generated in PHP have double quotes, because i haven't find a way to detect the kind of quoting of a Python string.
- Therefore, if you need to write a doublequote in your string (") you will need to escape it using \\" (yes, two backslashes).
- The previous issue is caused by the python script that interprets the string and therefore "eats" the first backslash.
- Don't push your luck too much with the "+" operator for concatening strings. It does not know when a variable is a string or a digit. For strings and digits it is obvious but for variables, it will not check the type. The compiler will check if one of the operands are a string by checking if they are quoted and will transform the "+" into a "." (concatenation in PHP) operator when needed. When in doubt, use "%s%s" % (string1, string2) to concatenate (it will generate a sprintf() in PHP).
- The same applies for "+=" and therefore .= operators
