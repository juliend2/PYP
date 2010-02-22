#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import types
import compiler
import visitor_base
from types import StringType

INDENT = '    '
LINEEND = ';'
PHPVERSION = 5
# used for php4 constructor function name (that is the same as the class name
current_class_name = ''
is_parsing_class = False

class visitor(visitor_base.VisitorSkeleton):
    """Instances of ge_visitor are used as the visitor argument to 
    compiler.walk(tree,visitor) where tree is an AST tree built by
    compiler.parse
    The instance has a src attribute which looks like the source
    code from which the tree was built
    Only a few of the visitNodeType are implemented, those likely to appear
    in a database query. Can be easily extended
    """

    def __init__(self):
        self.src = ''
        self.comment_start = '/*\n'
        self.comment_end = '\n*/\n'
        self.funcs_to_replace = {
            'str':'strval',
            'int':'intval',
            'float':'floatval',
        }
        self.magic_constants = ['__FILE__', '__LINE__', '__FUNCTION__',
        '__CLASS__','__METHOD__']

    def visitModule(self,t):
        # Module attributes
        #     doc              doc string, a string or <code>None</code>
        #     node             body of the module, a <tt class="class">Stmt</tt>
        self.src += '<?php\n' 
        if t.doc:
            self.src += self.comment_start + t.doc + self.comment_end
        self.src += get_source(t.getChildNodes()[0])
        self.src += '?>'
    
    def visitStmt(self,node):
        #print '***stmt nodes****',len(node.nodes), node.nodes
        self.src += '\n'.join( [ get_source(n) for n in node.nodes ]) + '\n'

    def visitClass(self, node):
        # Class attributes
        #     name             the name of the class, a string
        #     bases            a list of base classes
        #     doc              doc string, a string or <code>None</code>
        #     code             the body of the class statement
        global current_class_name, is_parsing_class
        is_parsing_class = True # important, must be in the beginning !
        current_class_name = node.name
        if node.doc != None:
            self.src += self.comment_start + node.doc + self.comment_end
        self.src += 'class %s ' % node.name
        if len(node.bases) > 0:
            self.src += 'extends %s' % get_source( node.bases[0] )[1:] # php has no multiple inheritance
        self.src += ' {\n'
        self.src += get_source( node.code )
        self.src += '}\n'
        is_parsing_class = False # important, must be at the end!

    def visitFunction(self, node):
        # Function attributes
        #     name             name used in def, a string
        #     argnames         list of argument names, as strings
        #     defaults         list of default values
        #     flags            xxx
        #     doc              doc string, a string or <code>None</code>
        #     code             the body of the function
        global current_class_name, is_parsing_class
        if is_parsing_class: # if class method, delete the Python's self argument
            node.argnames = node.argnames[1:]
        if node.doc != None:
            self.src += self.comment_start + node.doc + self.comment_end
        if (PHPVERSION == 5 and 
        node.name == '__init__' and 
        is_parsing_class):
            node.name = '__construct'
        elif (PHPVERSION == 4 and
        node.name == '__init__' and
        is_parsing_class and
        current_class_name != ''):
            node.name = current_class_name
        self.src += 'function %s (' % node.name
        nb_defaults = len(node.defaults)
        if nb_defaults > 0 : # there are some default args
            simple_args = node.argnames[:len(node.argnames)-nb_defaults]
            assigned_args = node.argnames[len(node.argnames)-nb_defaults:]
            assg_args_w_vals = []
            j = 0
            for assign in assigned_args:
                valu = get_source( node.defaults[j] )
                assg_args_w_vals.append( '%s = %s' % (assign,valu) )
                j+=1
            self.src += ', '.join( ['$%s'%n for n in
            simple_args+assg_args_w_vals ])
        else: 
            self.src += ', '.join( '$%s'%n for n in node.argnames)
        self.src += ') {\n'
        self.src += get_source( node.code )
        self.src += '}\n'

    def visitGetattr(self, node):
        # Getattr attributes
        #     expr             
        #     attrname         
        self.src += get_source( node.expr ) + '->' + node.attrname
        
    def visitAssAttr(self, node):
        # AssAttr attributes
        #     expr             expression on the left-hand side of the dot
        #     attrname         the attribute name, a string
        #     flags            XXX
        self.src += get_source( node.expr ) + '->'
        self.src += node.attrname

    def visitDiscard(self, node):
        # Discard attributes
        #     expr             
        if node.expr.__class__ is compiler.ast.Const :
            self.src += '/* ' + get_source( node.expr )[1:-1] + ' */'
        else:
            self.src += get_source( node.expr )

    def visitReturn(self, node):
        self.src += 'return '+get_source(node.value)

    def visitContinue(self, node):
        # Continue attributes
        self.src += 'continue'

    def visitBreak(self, node):
        # Break attributes
        self.src += 'break'

    def visitPrintnl(self, node):
        # Printnl attributes
        #     nodes            
        #     dest             
        # PHP print statement takes only one parameter so we take the first one :
        self.src += 'print '+ get_source( node.nodes[0] ) 

    def visitName(self, node):
        if node.name == 'self':
            self.src += '$this'
        elif node.name == 'False':
            self.src += 'false'
        elif node.name == 'True':
            self.src += 'true'
        elif node.name == 'None':
            self.src += 'null'
        elif re.match( '^[A-Z][_A-Z]*$', node.name ): # it's a constant if ALL CAPS
            self.src += node.name
        elif (node.name in self.magic_constants):
            self.src += node.name
        else:
            self.src += '$%s'%node.name

    def visitConst(self, node):
        # Const attributes
        #     value            
        if type(node.value) is str:
            self.src += '"%s"' % node.value
        else:
            self.src += str(node.value)

    def visitMod(self, node):
        # Mod attributes
        #     left             
        #     right            
        left = get_source( node.left )
        if '%' in left and type(left) is str and left.startswith('"'):
            # sprintf
            self.src += 'sprintf(' + left + ', '
            if node.right.__class__ is compiler.ast.Tuple:
                self.src += ', '.join( [ get_source(n) for n in node.right ] )
            else:
                self.src +=  get_source(node.right)
            self.src += ')'
        else:
            # modulo normal
            self.src += '('+get_source( node.left ) + ' % ' + get_source(
            node.right )+')'
            pass

    def visitMul(self, node):
        # Mul attributes
        #     left             
        #     right            
        self.src += '('+get_source( node.left ) + ' * ' + get_source(
        node.right )+')'

    def visitDiv(self, node):
        # Div attributes
        #     left             
        #     right            
        self.src += '('+get_source( node.left ) + ' / ' + get_source(
        node.right )+')'

    def visitAdd(self, node):
        # Add attributes
        #     left             left operand
        #     right            right operand
        print 'left', node.left
        print 'right', node.right
        if (
        (node.left.__class__ is compiler.ast.Const and 
        type(node.left.getChildren()[0]) is str) or
        (node.right.__class__ is compiler.ast.Const and
        type(node.right.getChildren()[0]) is str)
        ):
            self.src += get_source(node.left) + ' . ' + get_source(node.right)
        else: 
            self.src += '('+get_source( node.left ) + ' + ' + get_source(
            node.right )+')'

    def visitSub(self, node):
        # Sub attributes
        #     left             
        #     right            
        self.src += '('+get_source( node.left ) + ' - ' + get_source(
        node.right )+')'

    def visitUnaryAdd(self, node):
        # UnaryAdd attributes
        #     expr             
        self.src += '+'+get_source( node.expr )

    def visitUnarySub(self, node):
        # UnarySub attributes
        #     expr             
        self.src += '-'+get_source( node.expr )

    def visitAssign(self, node):
        # Assign attributes
        #     nodes            a list of assignment targets, one per equal sign
        #     expr             the value being assigned
        parsed_expr = get_source( node.expr )
        if ( len(node.nodes)==1 and 
            type(node.nodes[0].getChildren()[0]) is StringType and 
            re.match('^[A-Z][_A-Z]*$', node.nodes[0].getChildren()[0]) ):
            self.src += 'define("'+node.nodes[0].getChildren()[0]+'", '+parsed_expr+')' 
        else:
            self.src += ', '.join( [get_source( n ) for n in node.nodes ] ) + ' = ' 
            self.src += parsed_expr

    def visitAugAssign(self, node):
        # AugAssign attributes
        #     node             
        #     op               
        #     expr             
        def nodeLoop(node):
            try:
                if node.getChildren()[0].__class__ is compiler.ast.Add:
                    return nodeLoop(node.getChildren()[0])
                elif node.getChildren()[0].__class__ is compiler.ast.Const:
                    return node.getChildren()[0]
                else:
                    return node
            except Exception, e:
                return node
                    
        if (node.op == '+=' and
        node.expr.__class__ is compiler.ast.Const and
        type(node.expr.getChildren()[0]) is str):
            self.src += get_source( node.node )
            self.src += ' .= '
            self.src += get_source( node.expr )
        else:
            try:
                if (nodeLoop(node.expr).__class__ is compiler.ast.Const and
                type(nodeLoop(node.expr).getChildren()[0]) is str):
                    node.op = '.='
            except Exception, e:
                pass
            self.src += get_source( node.node )
            self.src += ' '+node.op+' '
            self.src += get_source( node.expr )

    def visitOr(self, node):
        # Or attributes
        #     nodes            
        self.src += ' || '.join( [ get_source( n ) for n in node.nodes ] )
    
    def visitAnd(self, node):
        # And attributes
        #     nodes            list of operands
        self.src += ' && '.join( [ get_source( n ) for n in node.nodes ] )

    def visitNot(self, node):
        # Not attributes
        #     expr             
        self.src += '!%s' % get_source(node.expr)

    def visitGlobal(self, node):
        # Global attributes
        #     names            
        self.src += 'global '+ ( ', '.join( ['$%s' % name for name in node.names ] ) )

    def visitCompare(self, node):
        # Compare attributes
        #     expr             
        #     ops              
        self.src +=  get_source( node.expr )
        for comp in node.ops:
            if comp[0] == '!=':
                operator = '!=='
            elif comp[0] == '==':
                operator = '==='
            elif comp[0] == 'is':
                raise visitor_base.NotImplementedException('IS keyword')
            else:
                operator = comp[0]
            self.src += ' '+operator+' ' + get_source( comp[1] )

    def visitIf(self, node):
        # if attributes
        #     tests            
        #     else_            
        i = 0
        for test in node.tests:
            if i==0:
                self.src += 'if ('
            else:
                self.src += 'elseif ('
            # for compare in test:
            self.src += get_source( test[0] )
            self.src += ') {\n'
            self.src += ''.join( [ get_source(n) for n in test[1:] ] )
            self.src += '}\n'
            i+= 1
        if node.else_:
            self.src += 'else {\n'
            self.src += get_source( node.else_ )
            self.src += '}\n'

    def visitTryExcept(self, node):
        # TryExcept attributes
        #     body             
        #     handlers         
        #     else_            
        self.src += 'try {\n'
        self.src += get_source( node.body )
        self.src += '}\n' 
        for handler in node.handlers:
            self.src += 'catch ('
            if handler[1] == None:
                self.src += 'Exception '+get_source(handler[0])
            else:
                self.src += handler[0].getChildren()[0] + ' '
                self.src += get_source( handler[1] )
            self.src += ') {\n'
            self.src += get_source( handler[2] )
            self.src += '}\n'

    def visitFor(self, node):
        # For attributes
        #     assign           
        #     list             
        #     body             
        #     else_            
        self.src += 'foreach ('+get_source(node.list)+' as '
        self.src += get_source( node.assign ) + ') {\n'
        self.src += get_source( node.body )
        self.src += '}\n'

    def visitWhile(self, node):
        # While attributes
        #     test             
        #     body             
        #     else_            
        self.src += 'while ('
        self.src += get_source( node.test )
        self.src += ') {\n'
        self.src += get_source( node.body )
        self.src += '}\n'

    def visitCallFunc(self, node):
        # CallFunc attributes
        #     node             expression for the callee
        #     args             a list of arguments
        #     star_args        the extended *-arg value
        #     dstar_args       the extended **-arg value
        # call a function :
        if type(node.node.getChildren()[0]) is str:
            # if it's an instanciation:
            if re.match('^[A-Z]', node.node.getChildren()[0] ):
                self.src += 'new ' + node.node.getChildren()[0]  + '('
            else: # we have a function:
                funcname = node.node.getChildren()[0]
                if self.funcs_to_replace.has_key(funcname):
                    funcname = self.funcs_to_replace[funcname]
                self.src += funcname + '('
        else: # call a method :
            if len( node.node.getChildren() ) == 2 :
                self.src += get_source( node.node.getChildren()[0] )
                self.src += '->' + node.node.getChildren()[1] + '('
        self.src += ', '.join( [get_source(n) for n in node.args ] )
        self.src += ')'

    def visitAssName(self, node):
        # AssName attributes
        #     name             name being assigned to
        #     flags            XXX
        if re.match( '^[A-Z][_A-Z]*$', node.name ): # it's a constant if ALL CAPS
            self.src += node.name
        elif (node.name in self.magic_constants):
            self.src += node.name
        else:
            self.src += '$%s' % node.name

    def visitAssTuple(self, node):
        # AssTuple attributes
        #     nodes            list of tuple elements being assigned to
        # ** Tuple assignment does not exist in PHP so i'm gonna use it for the
        # foreach key => value pair, or value only if there is only one element
        if len(node.nodes) == 2:
            self.src += get_source(node.nodes[0]) + ' => ' 
            self.src += get_source(node.nodes[1])
        elif len(node.nodes) == 1:
            self.src += get_source(node.nodes[0])
        else:
            raise visitor_base.NotImplementedException('Tuple assignment does not exist in PHP')

    def visitList(self,t):
        self.src += 'array('
        self.src += ', '.join ( [ get_source(n) for n in t.nodes ])
        self.src += ')'

    def visitDict(self, node):
        # Dict attributes
        #     items            
        self.src += 'array('
        self.src += ', '.join( [get_source(k)+'=>'+get_source(v) for k,v in
        node.items] )
        self.src += ')'

    def visitSubscript(self, node):
        # Subscript attributes
        #     expr             
        #     flags            
        #     subs             
        if node.flags == 'OP_ASSIGN' or node.flags == 'OP_APPLY':
            self.src += get_source(node.expr) +'['
            self.src += get_source(node.subs[0]) # [0] parce qu'on ne peut faire de [0:2] en PHP
            self.src += ']'

    def visitPass(self, node):
        pass
 
def get_source(node):
    """Return the source code of the node, built by an instance of
    ge_visitor"""
    return compiler.walk(node,visitor()).src

def add_semicolons(code):
    global LINEEND
    lines_list = code.split('\n')
    in_comment = False
    new_lines = []
    for line in lines_list:
        if line.startswith('/*') and not line.endswith('*/'):
            in_comment = True
        elif line.endswith('*/'):
            in_comment = False
        if (line.strip() != '<?php' and
            line.strip() != '?>' and
            line.strip() != '' and 
            not in_comment and 
            not (
                line.endswith('}') or
                line.endswith('{') or 
                line.endswith('*/')
            )
        ):
            new_lines.append( line + LINEEND )
        else:
            new_lines.append( line )
    return '\n'.join(new_lines)


def indent_source(code):
    global INDENT
    lines_list = code.split('\n')
    tab_count = 0
    new_lines = []
    for line in lines_list:
        if line == '}':
            tab_count -= 1
        val = (INDENT*tab_count) + line
        indentation = INDENT*tab_count
        if not (line.strip() == '' and tab_count != 0):
            new_lines.append( val )
        if line.endswith('{'):
            tab_count += 1
    return '\n'.join(new_lines)

if __name__ == '__main__':
    unindented_source = get_source(compiler.parseFile('source.py'))
    print indent_source(add_semicolons(unindented_source))
