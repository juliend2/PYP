# Prerequisites :

- Python 2.6 on Mac or Linux (haven't tested on Windows)


# Usage :

1. cd into the directory that contains this script (py2php.py, watch.py, etc)<br/>
example : cd ~/myscripts/PYP/

2. python watch.py &lt;pyp sources directory&gt; &lt;php destination directory&gt;<br/>
example : python watch.py ./ /var/www/projectname/


# TODO :

- Fix the issue about the quote excaping.
- Convert Class attributes
- Convert Class methods
- Parse some of the Python methods into their PHP versions. <br/>
Example :    
    * ', '.join(list) would become : implode(', ', $list) 
    * str.split('-', 1) would become : explode('-', $str, 1)
    * list.append('element') would become : array_push($list, 'element')

# Nice to have:

- passing by reference (&$variable , =& , etc)
- $this-&gt;{'property name'}-&gt;method();

# Known issues :
- the strings that are generated in PHP have double quotes, because i haven't find a way to detect the kind of quoting of a Python string.
- Therefore, if you need to write a doublequote in your string (") you will need to escape it using \\" (yes, two backslashes).
- The previous issue is caused by the python script that interprets the string and therefore "eats" the first backslash.
- Don't push your luck too much with the "+" operator for concatening strings. It does not know when a variable is a string or a digit. For strings and digits it is obvious but for variables, it will not check the type. The compiler will check if one of the operands are a string by checking if they are quoted and will transform the "+" into a "." (concatenation in PHP) operator when needed. When in doubt, use "%s%s" % (string1, string2) to concatenate (it will generate a sprintf() in PHP).
- The same applies for "+=" and therefore .= operators
