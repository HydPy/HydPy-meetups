class Ops(object):
    ''' this sample class'''
    VAR = 10
    def __init__(self, a, b):
        self.a = a
        self.b = b
        
    def add(self):
        print self.x
        return self.a+self.b
        

    def sub():
        print 'ff'
##        self.x =  10
##        return self.x-self.b
    
    @classmethod
    def clsMethod(cls):
        print cls.VAR
        print 'Class Method'

    @staticmethod
    def stcMethod():        
        print 'static method'
        

if __name__ == '__main__':
##    ops = Ops(1,2)    
##    print ops.sub()
##    print ops.add()
##
##    setattr(ops, 'y', 80)
##    print 'after adding y ',ops.y
##    print dir(ops)
##    print ops.__doc__

##    print Ops.VAR
##    print Ops.clsMethod()
    print Ops.stcMethod()
    print Ops.sub()
















    
    