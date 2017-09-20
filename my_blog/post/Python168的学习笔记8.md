# Python168的学习笔记8

## 装饰器的初步应用

```python
# 斐波那契数列，第三项起，每一项都等于前两项之和

def memo(func):
    cache = {}  # 闭包，做缓存用
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap

@memo
def fibonacci(n):
    if n<=1:
        return 1
    return fibonacci(n-1)+fibonacci(n-2)

# 上楼梯算法，总过n个台阶，一次只能迈a-b个台阶，不能后退，问有几种走法
@memo
def climb(n,steps):  # steps=[a, b+1]范围
    count = 0
    if n in [0, 1]:
        count = 1
    elif n > 1:
        for step in steps:
            count += climb(n-step,steps)
    return count

# 先要找到边界，也就是当台阶<=1时，只有1种走法。而剩下的就是往这个条件靠，也就是((((n-1)-1)-1)...)(当步数为1时)，以此不断逼近边界。
```

这里主要是要理解这两个递归算法。

## 装饰器对原函数的影响

关于函数的元数据，如：f. __ name __ ,指的是def时指定的名字；f. __ doc __ ,指的是函数文档字符串；f. __ moudle __ ,指的是函数所属模块;f. __ default __ ,指的是函数默认值；f. __ dict __ ,指的是属性字典；f. __ closure __ ,指的是函数的闭包。。。这些元数据都是func的属性。

使用装饰器会改变func的元数据。有三种方法将其改回来，当然推荐用的是wraps。

```python
from functools import update_wrapper,wraps,WRAPPER_ASSIGNMENTS,WRAPPER_UPDATES

def mydecorator(func):
    @wraps(func)  # 第一种
    def wrapper(*args,**kw):
        '''wrapper function'''
        print 'In wrapper'
        func(*args,**kw)
    # wrapper.__name__ = func.__name__  第二种
    # update_wrapper(wrapper,func,('__name__','__doc__'),('__dict__',))#第四个参数是将func的属性更新到wrap
    # 第三种：update_wrapper后两个的默认参数分别是('__module__', '__name__', '__doc__')；('__dict__',)
    return wrapper

@mydecorator
def example():
    '''example function'''
    print 'In example'
```

## 带参的装饰器

```python
import time
import functools

DEFAULT_FMT = '[{elased:0.8f}s] {name} ({args} {kwargs}) -> {result}'

def clock(fmt=DEFAULT_FMT):
    def dcorate(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            t0 = time.time()
            _res = func(*args, **kwargs)
            elapsed = time.timte() - t0
            name = func.__name__
            args = ', '.join(repr(arg) for arg in args)
            kwargs = ', '.join(repr(kwarg) for arg in kwargs)
            result = repr(_res)
            print(fmt.format(**local))  # 这个用法是为了在fmt中引用clocked的局部变量，不用一个个传进去
            return _res
        return wrapper
    return decorate
```

可以为装饰器添加函数来达到动态改参的目的。

```python
import time
from functools import wraps
import logging

def warn(timeout):
    timeout = [timeout]  # 将参数设为只有一个数的list
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kw):
            start = time.time()
            res = func(*args,**kw)
            used = time.time()-start
            if used > timeout[0]:
                msg = '%s : %s >%s' % (func.__name__,used,timeout[0])
                logging.warn(msg)
            return res
        def setTimeout(k):  # 注意这里
            timeout[0] = k
        wrapper.setTimeout = setTimeout
        return wrapper
    return decorator

from random import randint
@warn(0.5)
def test():
    print 'In test'
    while randint(0,1):
        print 'I am sleep'
        time.sleep(1)
        
for _ in range(10):
    test()
    
test.setTimeout(1)
for _ in range(10):
    test()
```

## 用类来实现装饰器

```python
import logging
from time import localtime,time,strftime,sleep

class CallingInfo(object):
    def __init__(self,name):
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)  # 设置等级
        fh = logging.FileHandler(name+'.log')  # 设置文件处理方法
        log.addHandler(fh)  # 绑定方法到log上
        log.info('Start'.center(50,'-'))  # 添加log文本的头部
        self.log= log  # 绑定到类的属性上
        self.formatter = '%(func)s ->[%(time)s - %(used)s -%(ncalls)s]'  # 定义了输出模板
        
    def info(self,func):  # 这个就是平常的装饰器
        def wrapper(*args,**kw):
            wrapper.ncalls +=1
            lt = localtime()  # 返回当地时间
            start = time()
            res = func(*args,**kw)
            used = time() - start
            
            info = {}  # 建立info的字典
            info['func'] = func.__name__
            info['time'] = strftime('%x %X',lt)
            info['used'] = used
            info['ncalls'] = wrapper.ncalls

            msg = self.formatter % info  # 将字典映射到输入模板上
            self.log.info(msg)  # 输出字符串
            return res
        wrapper.ncalls = 0  # 这个语句需要在这个位置的解释有待完善
        return wrapper
    
    def setFromatter(self,formatter):
        self.formatter = formatter
        
    def turnOn(self):
        self.log.setLevel(logging.INFO)
        
    def turnOff(self):
        self.log.setLevel(logging.WARN)  # 级别提高就不在那里输出了    
        
cinfo1 = CallingInfo('mylog1')
cinfo2 = CallingInfo('mylog2')

cinfo1.setFromatter('%(func)s ->[%(time)s  -%(ncalls)s]')
cinfo2.turnOff()  # 这里可以看到是很方便地修改装饰器

@cinfo1.info    
def f():
    print 'in f'
    
@cinfo1.info
def h():
    print 'in h'

@cinfo2.info 
def g():
    print 'in g'
    
    
from random import choice
for _ in xrange(10):
    choice([f,g,h])()
    sleep(choice([0.5,1,1.5]))
```

在fluent python中，推荐是通过类的 __ call __ 方法来实现装饰器功能。