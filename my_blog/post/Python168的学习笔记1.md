# Python168的学习笔记1

##对常见数据结构的操作

在对list的条件选择有两种常用方法，直接使用filter函数，就是filter(func,sequence);另外一种就是迭代操作，类似 x for x in sequence func。这两种方法，迭代操作比filter函数快一倍左右。

xrange与range的区别，xrange是类，生成器；然后range是直接返回list，所以多用xrange好。当然现在python3就只有range了。

timeit 后面接上操作语句，可以得到操作语句的用时。

对字典dict的筛选操作也类似，同样可以运用迭代的方法{k:v for k,v in dict.iteritems() func}

对set的操作也类似，同样的{x for x in set func}

 ## 细节

关于为元组的元素命名，增加程序可读性。

eg:user=('john',16,'male')

1，是通过关键字=常量,如：name=0,然后user[name]就可以访问john了

2，通过collection.namedtuple，在创建tuple的时候就定义每个元素的名字，如：user = namedtuple('user',['name','age','sex'])

namedtuple就是tuple的一个子类，其实也就是用一个类的生成器来生成tuple，访问时可以直接用类对象user.name就得到john了。

生成随机list的时候，注意语法 data = [randint(0,10) for _ in xrange(8)]这个 _ 用得好。

用预设值生成dict的时候，可以用dict.fromkeys(seq[,values])来生成，就是用预设的键，如

```python
seq = ('name', 'age', 'sex')

dict_ = dict.fromkeys(seq)
print("new dict: %s" % str(dict_))

dict_ = dict.fromkeys(seq, 10)
print("new dict: %s" % str(dict_))

>>> new dict: {'a': None, 'b': None, 'c': None}
>>> new dict: {'a': 10, 'b': 10, 'c': 10}
```

## 统计出现次数

利用collections库可以更高效地统计，首先利用Counter,就可以生成列表中，每个元素对应出现次数的dict。

然后用Counter.most_common(n),就可以得到出现频度最高的n个元素。

##正则分割文章

在对英语文本进行操作时，需要用到正则表达式。

import re，然后利用re.split('\W+',object),就可以在非字母处都进行分割。

##sorted排序

排序用内置函数sorted。但如果直接用sorted对dict操作，操作的对象是key，无法直接得到我们想要的效果。

1，用zip函数构造我们想要的元组来比较，zip（dict.values(),dict.keys()）可以得到value和key组成的元组。

而针对内存的使用，用迭代的方法更加节省内存，所以用zip(dict.itervalues(),dict.iterkeys())会更好。

ps：对元组元素进行排序时，先进行元组的第一个元素比较，然后再进行第二个，如此类推。

2，为sorted函数输入关键字比较，sorted(dict.items(),key=lambda x : x[1])

dict.items()返回的是(key,value),而后面关键字key等于x元组的第二个元素，也就是value,所以这样就直接对value就行比较了。

##随机取样

random.sample随机取样。sample(seq,n)在seq中随机取n个值。

##用交集提取公共键

找到多个字典的公共键，首先用dict.keys()获取当前dict的key,这个函数是返回一个set。然后用&（与操作），就可以得到多个dict的公共键了。

语法为 reduce(lambda a,b : a&b,map(dict.keys,[dict1,dict2,dict3...]))

##一些内置的数据类型

当对dict有顺序要求时，可以利用collections的OrderedDict,OrderedDict是按进入字典的顺序来进行排序的。

双端循环队列可以采用collections中的deque.

##pickle存储

存储文件，可以用序列化工具pickle库中的dump，dump（object，file），将目标序列化到文件。反序列化操作就是pickle.load(file)。注意在反序列化时，要提供相应类的定义。