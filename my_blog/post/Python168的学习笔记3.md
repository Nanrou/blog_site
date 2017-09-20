# Python168的学习笔记3

## 扩展列表

list.extend(),可以拓展list,a=(0,1),b=(2,3) a.extend(b),a就变成（0,1,2,3）

## 分割字符串

分割字符串（除去字符串中的,\/;之类的），如果用str.split()，默认是除去空格，然后返回处理过后的list，可以输入特定值如split(';')，但缺点是一次只能处理一个特定的。

```python
#coding:utf8
def mySplit(s,ds):
    res = [s]
    
    for d in ds:
        t = []
        map(lambda x : t.extend(x.split(d)),res)
        #实际上就是res.split(d),然后将处理后的list全部加到t中
        res = t
        
    return [x for x in res if x]#除去空的

s = 'ab;cd|efg;hi..jk\\mn\top'
print mySplit(s,',;|.\\\t')

>>>'abcdefghijkmnop'
```

如上，就是通过循环使用可以达到最终效果。

在处理复杂情况时使用正则表达式会更简单。

```python
import re
s = 'ab;cd|efg;hi..jk\\mn\top'
print re.split(r'[,;.\t\\|]+',s)
```

就可以得到上面那种结果。

## 字符串替换

内置有replace方法来替换，进阶可以用re.sub可以做到字符串调换，先利用正则表达式来做到捕获各个组，然后在替换字符串中调整各个捕获组的位置。如将2016-11-06变成11/06/2016这样。

```python
import re

datas = ('2015-06-19','2015-06-20','2015-06-30')

for data in datas:
    print re.sub(r'(\d{4})-(\d{2})-(\d{2})',r'\2/\3/\1',data)
    print re.sub(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})',r'\g<month>/\g<day>/\g<year>',data)  # 用了命名语法
```

## 字符串拼接

拼接字符串用str.join()方法，'[]'.join(iter)(就是指每个元素中间可以选择加关键字)但是注意方法接收的对象，如果有数字需要转换为字符，而在这里，我们最好用()来传入迭代器而不是只用一次的list。

## 字符串对齐

关于对字符串的对齐操作，可以用str.ljust(),str.rjust(),str.center()之类的，如a = kkk, a.ljust(20,[=])就是会输出20个字符kkk在最左边，然后填充17个=进去。

用format()，传入'<' ,'>', '^'这些参数也跟上面那种方法一样。

## 删除特定字符串

```python
s = '-------abc+++++++++'
print s.strip('+-')  # 还有lstrip,rstrip,缺点在于只能去掉左右两端的

s = 'abc:123'
print s[:3] + s[4:]  # 切片有很大的局限性

s = 'abc\tdef\tghc123\t'
print s.replace('\t', '')  # 只能替换单个

import re
s = 'abc\td\ref\tghc\n123\t'
print re.sub('[\t\r\n]','',s)  # 用正则应该是最好的
# s.translate(table[,deletechars])table可以是一个字典，里面对应着映射关系表；或者传入None,然后再传入要删除的关键字。

import string
s = 'abc123xyz'
print s.translate(string.maketrans('abcxyz', 'xyzabc'))  # 用maketrans()可以直接建立映射表
print s.translate(None,'123')
```

