
def tag(x):
   def trace(f):
      print 'x',x
      def inner(*args):     
         print 'func f called {0}  args'.format(args)
         for arg in args:
            if not isinstance(arg, int):
               raise TypeError('All the values should be Integer type')
         result = f(*args)
         print 'result',result
         return result
      return inner
   return trace


def memotize(f):
   cache = {}
   def wrapper(*args):
      if args in cache:
         print 'in cache'
         return cache[args]
      else:
         print 'not in cache'
         result = f(*args)
         cache[args] = result
         return result
   return wrapper


#@memotize
@tag(1)
def add(a,b):
   return a+b

##@trace(1)
##def mult(a,b):
##   return a*b




if __name__ == '__main__':
   print add(3,4)
   #print mult('k',4)
   #print add(7,4)












