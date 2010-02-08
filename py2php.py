import compiler
from types import TupleType

class visitor:
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

    def visitModule(self,t):
        self.src += '<?php\n' + get_source(t.getChildNodes()[0])
    
    def visitStmt(self,node):
        #print '***stmt nodes****',len(node.nodes), node.nodes
        self.src += '\n'.join( [ get_source(n) for n in node.nodes ]) + '\n'

    def visitClass(self, node):
        # Class attributes
        #     name             the name of the class, a string
        #     bases            a list of base classes
        #     doc              doc string, a string or <code>None</code>
        #     code             the body of the class statement
        if node.doc != None:
            self.src += '/* ' + node.doc + ' */' 
        self.src += 'class %s ' % node.name
        if len(node.bases) > 0:
            self.src += 'extends %s' % get_source( node.bases[0] )[1:] # php has no multiple inheritance
        self.src += ' {\n'
        self.src += get_source( node.code )
        self.src += '}\n'

    def visitFunction(self, node):
        # Function attributes
        #     name             name used in def, a string
        #     argnames         list of argument names, as strings
        #     defaults         list of default values
        #     flags            xxx
        #     doc              doc string, a string or <code>None</code>
        #     code             the body of the function
        #print 'node.code',node.code
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
        if node.flags == 'OP_ASSIGN':
            self.src += ' = '

    def visitReturn(self, node):
        self.src += 'return '+get_source(node.value)

    def visitName(self, node):
        if node.name == 'self':
            self.src += '$this'
        else:
            self.src += '$%s'%node.name

    def visitConst(self, node):
        # Const attributes
        #     value            
        if type(node.value) is str:
            self.src += "'%s'" % node.value
        else:
            self.src += str(node.value)

    def visitMul(self, node):
        # Mul attributes
        #     left             
        #     right            
        self.src += get_source( node.left ) + ' * ' + get_source( node.right )

    def visitAdd(self, node):
        # Add attributes
        #     left             left operand
        #     right            right operand
        self.src += get_source( node.left ) + ' + ' + get_source( node.right )

    def visitAugAssign(self, node):
        # AugAssign attributes
        #     node             
        #     op               
        #     expr             
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

    def visitCompare(self, node):
        # Compare attributes
        #     expr             
        #     ops              
        self.src +=  get_source( node.expr )
        for comp in node.ops:
            self.src += comp[0] + get_source( comp[1] )

    def visitIf(self, node):
        # if attributes
        #     tests            
        #     else_            
        i = 0
        for test in node.tests:
            if i==0:
                self.src += 'if ('
                # for compare in test:
                print 'test',test[0]
                self.src += get_source( test[0] )
                self.src += ') {\n'
                print 'ici le bloc', test[1:]
                self.src += ''.join( [ get_source(n) for n in test[1:] ] )
                self.src += '}\n'
            i+= 1

    def visitList(self,t):
        self.src += ','.join ( [ get_source(n) for n in t.nodes ])

 
def get_source(node):
    """Return the source code of the node, built by an instance of
    ge_visitor"""
    return compiler.walk(node,visitor()).src

 
if __name__ == '__main__':
    print get_source(compiler.parseFile('source.py'))
