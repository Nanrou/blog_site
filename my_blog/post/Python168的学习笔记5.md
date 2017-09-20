# Python168的学习笔记5

## 对csv文件的操作

标准库中有操作csv的库，可以直接用。

```python
import csv

with open('pingan.csv','rb') as rf:
    reader = csv.reader(rf)  # 读操作
    with open('pingan2.csv','wb') as wf:
        writer = csv.writer(wf)
        headers = reader.next()
        writer.writerow(headers)  # 写操作
        for row in reader:
            if row[0] < '2016-01-01':  # 满足条件就退出循环
                break　　　　　　　　　　　　
            if int(row[5]) >= 50000000:  # 对特定数据的判断
                writer.writerow(row)
```

## 对json文件的操作

标准库中也有操作json的库，同样可以直接使用。

```python
import json

l = (1,2,'abc',{'name':'john','age':18})

with open('demo.json','wb') as f:
    json.dump(l,f)
    
with open('demo.json','rb') as f:
    r = json.load(f)
```

## 对xml文件的操作

```python
from xml.etree.ElementTree import parse

f = open('demo.xml')
et = parse(f)

root = et.getroot()  # 根节点

for child in root:  # 子节点
    print child.get('name')
    
for e in root.iterfind('country'):  # 跟上面结果一样，只是用了迭代
    print e.get('name')
    
print list(root.iter('rank'))  # 找孙子节点

print root.findall('country/*')  # 某些语法特点
print root.findall('.//rank')
```

## csv与xml的交互处理

```python
from xml.etree.ElementTree import ElementTree,Element  # 由element构成elementtree
import csv
from test_retractxml import pretty

def csvToxml(fname):
    with open(fname,'rb') as f:
        reader = csv.reader(f)
        headers = reader.next()  # 读取了第一行
        
        root = Element('Data')  # 构建了根节点
        for row in reader:  # 这里指针已经去到数据行了
            eRow = Element('Row')  # 创建子节点
            root.append(eRow)  # 将子节点插入根节点
            for tag,text in zip(headers,row):  # 迭代字典，就是将csv首行和数据行打包成字典，然后循环赋值
                e = Element(tag)
                e.text = text
                eRow.append(e)  # 将孙子节点插入到子节点
    pretty(root)
    return ElementTree(root)

et = csvToxml('pingan2.csv')
et.write('pingan.xml')
```

由于ElementTree自带的写入方法不能对格式进行操作，所以可以自己写个缩进的方法。

```python
def pretty(e,level=0):
    if len(e)>0:
        e.text='\n'+'\t'*(level+1)  # 先换行，然后给level个Tab
        for child in e:
            pretty(child,level+1)  # 递归给tab
        child.tail = child.tail[:-1]  # tail不懂（尾部的意思），这是对倒数第二行(子节点结尾)进行操作
        # 如果不操作，子节点结尾就会跟孙子节点一样缩进了
    e.tail = '\n' +'\t' *level  # 这是对最后一行进行操作
```

