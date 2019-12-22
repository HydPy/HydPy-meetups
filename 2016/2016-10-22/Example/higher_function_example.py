
class linear(object):
   def __init__(self, a, b):
       self.a, self.b = a,b
   def __call__(self, x):
       return self.a * x + self.b


if __name__ == '__main__':
    l = linear(2,3)
    print l(2)