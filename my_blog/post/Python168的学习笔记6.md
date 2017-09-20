# Python168的学习笔记6

## 关于元类

99%情况下都不需要用这个，暂时来讲知道这个特性主要由 __ new __ 方法实现就行了。

## 节约内存

关于使用__slots__，的确是可以节省内存，但是一般情况下也是不需要用到的。

## 上下文管理

关于上下文管理，也就是在class中设置 __ enter __ ， __ exit __ 属性，这样就可以配合with使用了。也就是说，在with这个块中，无论如何都会执行exit方法。

在设置 __ enter __ 属性时，要注意返回的对象是不是self，一般来说都是。

在设置 __ exit __ 属性时，要注意接收的参数， def  __ exit __ (self,exc_type,exc_val,exc_tab)，需要接收异常信息。

注意，如果在exit中设置了return Ture。则错误会被包在with中而不传回给最上层。

## 类中特殊的三个装饰器方法

property，staticmethod， classmethod这三兄弟是使用在类中的特殊方法。

* property：将装饰的属性方法（attribute）变为特性（property）。（这个说法摘自fluent python的19章）
* staticmethod：将装饰的方法变为静态方法，也就是普通函数，只不过刚好在类中定义体中。个人认为完全可以将这个函数放到外面去。
* classmethod： 将装饰的attribute变成类方法。（本来的都是实例方法）

## 定义比较运算符

类与类之所以能够相互比较，就是因为实现了 __ lt __ , __ le __ , __ gt __ , __ ge __ , __ eq __ , __ ne __ 这些magic method。实际进行比较，就等于是调用这些方法。我们当然可以全部实现这6个方法，不过也可以调用functools.total_ordering这个方法，将其作为装饰器，装饰整个类，然后只用实现 __ lt __ 和 __ eq __ 就可以实现6个属性的比较了。

```python
from functools import total_ordering
from abc import abstractmethod,ABCMeta

@total_ordering
class Shape(object):  # python3的话可以将object变成metaclass=abc.ABCMeta
    __metaclass__ = ABCMeta  # 定义这个类为抽象类，不可以被实例化，这是python2的语法
    @abstractmethod  # 声明定义抽象方法，让各个子类去完善
    def area(self):
        pass
    
    def __lt__(self,obj):
        if not isinstance(obj,Shape):
            raise TypeError('obj is not shape.')
        return self.area() <obj.area()
    
    def __eq__(self,obj):
        if not isinstance(obj,Shape):
            raise TypeError('obj is not shape.')
        return self.area() == obj.area()


class Rectangle(Shape):
    def __init__(self,w,h):
        self.w = w
        self.h = h
        
    def area(self):
        return self.w *self.h
    

class Circle(Shape):
    def __init__(self,r):
        self.r = r
        
    def area(self):
        return self.r ** 2 *3.14
    
r1 = Rectangle(3,5)    
r2 = Rectangle(5,5)   
c1 = Circle(5) 
print r1 > r2
print c1 > r1
```

## 定于操作符

这里自定义了__set__方法

```python
class Attr(object):
    def __init__(self,name,type_):
        self.name = name
        self.type_ = type_
        
    def __get__(self,instance,cls):
        return instance.__dict__[self.name]
    
    def __set__(self,instance,value):
        if not isinstance(value,self.type_):
            raise TypeError('expected an %s' % self.type_)
        instance.__dict__[self.name] = value
        
    def __delete__(self,instance):
        del instance.__dict__[self.name]

class Person(object):
    name =  Attr('name',str)
    age = Attr('age',int)
    height = Attr('height',float)
    
p = Person()

p.age = '17' 
print p.age  # 这里就会报错
```

## 简单了解弱引用

首先要讲一下python的删除机制，当一个对象的引用次数为零时，这个对象就回被删除，回收这一部分的内存。而我们平常要引用一个对象，这个对象的引用次数就会对应地增加1，而弱引用的特点就是，虽然引用了这个对象，但是不增加他的引用次数。对象存在时，当然可以取回这个对象的值，而对象不存在时，则返回None。

```python
import weakref

class Data(object):
    def __init__(self,value,owner):
        self.owner = weakref.ref(owner)  # 如果不是弱引用，则删除实例也不会回收
        self.value = value
        
    def __del__(self):  # 回收函数，正常情况下不应该手动调用这个方法。
        print 'in Data.__del__'
      
class Node(object):
    def __init__(self,value):
        self.data = Data(value,self)
    
    def __del__(self):
        print 'in Node.__del__'
        
node = Node(100)
del node
```

## 用getattr，hasattr来对实例进行方法的判断

```python
class s1(object):
    def A(self):
        return 'A'

class s2(object):
    def B(self):
        return 'B'

class s3(object):
    def C(self):
        return 'C'
    
def getS(s):
    for name in ('A','B','C'):
        f = getattr(s, name,None)  # 在这里寻找对应的方法，如果找不到就返回none
        if f:
            return f()
        
a = s1()
b = s2()
c = s3()
t = [a,b,c]
print map(getS,t)
```

