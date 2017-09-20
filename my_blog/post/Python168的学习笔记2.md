# Python168的学习笔记2

## 深入循环内部

关于for循环，其实质是利用被循环对象的 __ iter __ ，或者 __ getitem __ 属性接口，由可迭代对象得到迭代器。for循环就是不断调用.next()，直到最终捕获到stop。

```python
import requests
from collections import Iterable,Iterator

class WeatherIterator(Iterator):  # 迭代器
    def __init__(self,cities):
        self.cities = cities
        self.index = 0

    def getweather(self,city):
        r = requests.get(u'http://wthrcdn.etouch.cn/weather_mini?city='+city)  # 这是一个免费的天气api
        data = r.json()['data']['forecast'][0]
        return '%s:%s,%s'%(city,data['low'],data['high'])

    def __next__(self):
        if self.index == len(self.cities):
            raise StopIteration
        city = self.cities[self.index]
        self.index += 1
        return self.getweather(city)
    
    def __iter__(self):
        return self

class WeatherIterable(Iterable):  # 可迭代对象
    def __init__(self,cities):
        self.cities = cities

    def __iter__(self):  # 迭代器接口
        return WeatherIterator(self.cities)

for x in WeatherIterable([u'北京',u'上海',u'广州',u'长春']):
    print x
```

### 序列可以迭代的原因

序列可以迭代的原因是基于 **iter函数** 。当解释器需要迭代一个对象时，他会调用iter(x)。

1. 解释器先去寻找 __ iter __ 方法，有就调用它，获取一个迭代器。
2. 找不到才去找 __ getitem __ ， python自身创建一个迭代器，尝试按顺序，从索引0开始，获取元素。
3. 都找不到就会失败，抛出TypeError的异常。

### 迭代器和可迭代对象

可迭代对象有个 __ iter __ 方法，每次都实例化一个新的迭代器。（不能是自身的迭代器，也就是不能实现 __ next __ 方法）。

迭代器要实现 __ next __ 方法，返回单个元素，此外还要实现 __ iter __ 方法，返回迭代器本身。

### 关于yield

包含`yield`的是生成器，生成器最大的特点是可以无中生有，但是迭代器必须对现有对象操作，这个两者最大的不同。

## 其他杂谈

对list的反序操作，就是list.reverse(),可以得到反序的list，但是这样就是对list进行了操作，原有的顺序改变了。

而list[::-1]，是产生一个新的，反序的list，可能会浪费内存。

所以最好的方法是，去实现list. __ reversed __ 的方法。（正向迭代，就是实现 __ iter __ ；反向迭代，就是实现 __ reversed __ ）。

 

使用itertools.islice可以对迭代器进行切片操作，islice(iter,[start,]end[,step])，不过对迭代对象进行切片操作后，迭代对象的指针会停留在切片的停止的地方，所以如果想要再次用，需要重新申请迭代对象。

关于处理多个迭代对象，并行（同时迭代），用zip函数，zip（ * seq），会返回最短那个迭代对象长度的，由每个迭代对象各个元素组成的子tuple组成的list（ps：用itertools.izip()可以返回iter）；串行（一个接着一个），用itertools.chain,chain( * iter)，直接将所有迭代对象接起来。

注意，所有for对iter的操作，都会使iter的指针去到结尾，需要重新申请迭代对象才能使用。（也就是重新做一个迭代器，或者说在第一次使用时将迭代器list化）。

总的来说，迭代器就只能用一次。然后针对不同的迭代对象，有不同的重置方法，如file操作中的fetch()。