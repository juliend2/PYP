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
        self.src += '\n'.join( [ get_source(n) for n in node.nodes ])
    
    def visitFunction(self, node):
        self.src += 'function %s (' % node.name
        self.src += ', '.join( '$%s'%n for n in node.argnames)
        self.src += ') {'
        self.src += get_source( node.code )
        self.src += '}'

    def visitReturn(self, node):
        self.src += 'return '+get_source(node.value) + ';'
    
    def visitName(self, node):
        self.src += '$%s'%node.name

    def visitConst(self, node):
        # Const attributes
        #     value            
        self.src += str(node.value)

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
            print 'comp', comp
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
                self.src += ') {'
                print 'ici le bloc', test[1:]
                self.src += '}'
            i+= 1

    def visitList(self,t):
        self.src += ','.join ( [ get_source(n) for n in t.nodes ])

 
def get_source(node):
    """Return the source code of the node, built by an instance of
    ge_visitor"""
    return compiler.walk(node,visitor()).src

 
if __name__ == '__main__':
    print get_source(compiler.parseFile('source.py'))
