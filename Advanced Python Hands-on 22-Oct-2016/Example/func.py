def multi(a,b):
    return a*b

def testFunc(p, a, b):
    return p(a,b)
    

def square(x, y):
    return (x*x+y*y)

def odd(x):
    return x%2 != 0
if __name__ == '__main__':
##    p = multi
##    print testFunc(p, 1,3)
##    l = [multi]
##    print l[0](3,4)
    #print p(2,3)
##    print map(square, range(10), range(10,20))
    print filter(odd, range(10))
    print map(odd, range(10))
    print reduce(multi,range(1,10))
    print sum(range(1,10))
    







    








