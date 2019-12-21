class MagicMethod(object):
    def __init__(self, a):
        self.a = a
        #self.b = b

    def __len__(self):
        return len(self.a)

##    def __eq__(self, other):        
##        return self.__dict__ == other.__dict__
##
##    def __cmp__(self, other):
##        return self.a > other.a

if __name__ == '__main__':
    m1 = MagicMethod([3, 2])
    print len(m1)
##    m2 = MagicMethod(1, 2)    
##    print m1 == m2
##    print m1 > m2








