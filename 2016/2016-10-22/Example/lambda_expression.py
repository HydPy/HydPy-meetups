
# lambda args : expression

def last(x):
    return x[-1]
print sorted( [('a',3),('c',1),('b',2)], key=last)

print 'with lambda',sorted( [('a',3),('c',1),('b',2)],
              key=lambda x:x[-1])

p = lambda x,y : x**y
print p(2,3)

p = lambda x: x*x if x > 5 else (x**3 if x<3 else x)

print p(6)
print p(2)
print p(5)
















