# python日常碎碎念--获取命令行参数

关于取命令行中参数的方法

## sys.argv

这个方法自动获取参数，并split。一般情况下第一个元素是程序的名字。即

```python
python script.py arg1 arg2
```

然后sys.argv返回的list就是[script.y, arg1, arg2]。

如果是用python -c 'command...'，这种args[0]就是'-c'。

如果是直接用python，那argv[0]就是空。

## getopt

```python
>>> import getopt
>>> args = '-a -b -c foo -d bar a1 a2'.split()
>>> args
['-a', '-b', '-cfoo', '-d', 'bar', 'a1', 'a2']
>>> optlist, args = getopt.getopt(args, 'abc:d:')
>>> optlist
[('-a', ''), ('-b', ''), ('-c', 'foo'), ('-d', 'bar')]
>>> args
['a1', 'a2']
```

用法简单明了，getopt接收一个经过split的list，然后根据第二个参数（短参数构成的str，有需要赋值的用:冒号表示)，如上面的c和d，就会跟上相应的值，但是，这种只能用于单字母，也就是shortopts。

如果需要长参数，就用longopts，如下：

```python
>>> s = '--condition=foo --testing --output-file abc.def -x a1 a2'
>>> args = s.split()
>>> args
['--condition=foo', '--testing', '--output-file', 'abc.def', '-x', 'a1', 'a2']
>>> optlist, args = getopt.getopt(args, 'x', [
...     'condition=', 'output-file=', 'testing'])
>>> optlist
[('--condition', 'foo'), ('--testing', ''), ('--output-file', 'abc.def'), ('-x', '')]
>>> args
['a1', 'a2']
```

第三个参数为longopts的列表，并且要注意的是，如果是需要赋值的，就需要带上=

具体的demo

```python
import sys
import getopt

def main():
    try:
        opt, args = getopt.getopt(sys.argv[1:], 'ho:v', ['help', 'output='])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)
    output = None
    verbose = False
    for o, a in opts:
        if o == '-v':
            verbose = True
        elif o in ('-h', '--help'):
            sys.exit()
        elif o in ('-o', '--output'):
            output = a 
        else:
            assert False, 'unhandled option'
            
if __name__ == '__main__':
    main()
```

demo里面处理了h(help), o(output), v这几个参数。

以上例子均来自[官方文档](https://docs.python.org/3.6/library/getopt.html?highlight=getopt#module-getopt)。