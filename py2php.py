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
        self.src += ';\n'.join( [ get_source(n) for n in node.nodes ])
    
    def visitFunction(self, node):
        print 'function argnames', node.argnames
        print 'function defaults', node.defaults
        self.src += 'function %s (' % node.name
        nb_defaults = len(node.defaults)
        if nb_defaults > 0 : # there are some default args
            simple_args = node.argnames[:len(node.argnames)-nb_defaults]
            assigned_args = node.argnames[len(node.argnames)-nb_defaults:]
            print 'simple_args', simple_args
            print 'assigned_args', assigned_args
            assg_args_w_vals = []
            j = 0
            for assign in assigned_args:
                valu = get_source( node.defaults[j] )
                print '%s = %s' % (assign,valu)
                assg_args_w_vals.append( '%s = %s' % (assign,valu) )
                j+=1
            print simple_args+assg_args_w_vals 
            self.src += ', '.join( ['$%s'%n for n in
            simple_args+assg_args_w_vals ])
        else: 
            self.src += ', '.join( '$%s'%n for n in node.argnames)
        self.src += ') {\n'
        self.src += get_source( node.code )
        self.src += '}\n'

    def visitReturn(self, node):
        self.src += 'return '+get_source(node.value) + ';\n'
    
    def visitName(self, node):
        self.src += '$%s'%node.name

    def visitConst(self, node):
        # Const attributes
        #     value            
        self.src += str(node.value)

    def visitMul(self, node):
        # Mul attributes
        #     left             
        #     right            
        self.src += get_source( node.left ) + ' * ' + get_source( node.right )

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
