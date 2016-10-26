
class Base(object):
    def __init__(self, a):
        self.a = a
        print 'Base'

    def getMethod_(self):
        self.a = 10
        print 'Base derived getMethod'

    def getValue(self):
        return self.a+10


class Base1(object):
    def __init__(self, c):
        self.c = c
        print 'Base 1'

    def getMethod(self):
        return 'Base1 derived getMethod'

class Derived(Base, Base1):
    def __init__(self, a, b, c):
        #super(Derived, self).__init__(a)
        Base.__init__(self, a)
        Base1.__init__(self, c)
        #superDerived, self).__init__(c)
        self.b = b
        print 'init Derived'
        

    def getMethod_(self):
        return 'Derived'

if __name__ == '__main__':
    d = Derived(1, 2, 3)
    print d.getMethod()
    #print d.getValue()
    










