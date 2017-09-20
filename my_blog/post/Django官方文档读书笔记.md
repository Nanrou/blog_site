# Django官方文档读书笔记

## 写在前面

这算是第二次读英文原文文档，第一次是读scrapy，感觉还是要做笔记，好记性不如烂笔头，现在已经忘了scrapy文档讲了什么了，心疼。以后要多读多写

## 关于Django

经过半年的基础学习（懒，拖延）终于来到web开发这一步，当时买了董大的web实战，准备是用flask来实现的，但是后面在逼乎上找到某培训班的django视频资源，所以最终还是决定用django。

看过各种对django的评价之后，个人总结django是一个已经高度框架化的框架了，他的每一部分M,V,T都已经帮用户分好了，用户可自主选择不多，但是我也是相信一个理念，就是不需要给用户过多的选择，而且在现阶段，用django准备好给我的就已经够了。 

最开始先是完成了官方给新手准备好的tutorial，这个入门练习里带着我去实现一个在带有投票功能的小widget（网站？），主题功能就是可以投票，然后显示票数（whatever），这都不是重点，重点是介绍了M部分，就是DATA的管理，V部分，逻辑的管理，T部分，网页模板的管理，然后介绍了django有自带admin后台模块，还要让我们知道单元测试的重要性，至于最后的打包，复用，我就跳过了。

##一些细节部分

### model layer

分而治之是程序设计的基本理念，model层就是一个只处理数据的层，django提供好了orm，我们需要做的就是将我们想要创建的表（列），用python语言表达出来就行了。比如一个表，就是一个类，类中的属性就是表里面列。

```python
from django.db import models

class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)

class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    num_stars = models.IntegerField()
```

这是文档中的example，通过例子可以很直观地理解到model的用法。要注意，如果我们定义表时，未指定主键，django会自动创建主键。

列的名字可以通过field的参数指定，如果不指定，django会以属性名来做列名。

关系型数据库，django是有提供了一对多，多对一，多对多的feild。PS：一开始我是没有明白这些对应关系的，由于数据库基础不扎实。不过只要弄懂一个，其他就都明白了。比如拿foreignkey来讲，他是外键约束，就是多对一，比如以上例子，一个musician可以有多个album，所以musician就是album的外键。而具体到往album插入数据时，必须指明是关联到哪个musician才能插入。例子中foreignkey的on_delete参数的意思是外键被删除的时候关联的数据也会被删除。

在model里再增加一个class meta可以自定义一些metadata（这个不知道怎么翻译，我理解成是一些参数规则，文档的原文是anything that's not a feild，除了feild之外可以是任何东西，比如排列order的顺序是按列来排的，表的名字（不在class meta里面定义verbose_name的话，object会自动命名成class的名字），代理模式（就是用一个继承父类的子类class（这个class只有class meta；proxy=True和各种方法）去操作父类的数据，这样就不用重新对父类进行更改））。

我们可以为model这个class添加自定义的方法，当然这些方法最好都只是针对数据的，而不是其他。django是为我们提供了很多方法，但是在文档中提到有两个方法我们应该重写的，就是__str__，和get_absolute_url，前者帮助我们阅读，后者是告诉django如何生成object对应的url。要注意的是，无论重写哪个方法，都不要忘记去执行他本来的功能，也就是最好在重写方法时加上SUPER（特指save()那些涉及数据库操作的函数）。

model的继承，跟普通class的继承一样，但是要注意的一点，如果在model中的加了class meta，且abstrct=True的话，表明这个model是抽象类，不会被实例化，也就是说在migrate的时候，是不会为这个model创建表的。至于多重继承及要注意的地方，暂时跳过。

index 索引部分，跳过跳过。其实在关键部分选择生成index就好，说到底就是一个空间换时间的东西。

model的自带属性中最重要的可以说是manager了，他是db查询方法是实现，默认名字objects，使用example如下：

```python
Entry.objects.filter(pub_date__lte='2006-01-01')  # Entry.objects.all().filter(pub_date__lte='2006-01-01') 两者等价
```

等价的sql就是：SELECT * FROM blog_entry WHERE pub_date<='2016-01-01';

查询是可以链式查询的，具体实现还是可以到时查api。但是这里引入了两个新语法，就是F()和Q()，其中F()的用法就是类似一个指针，举个例子，我们有一个这样的表，表中是记录着小明和他小伙伴的身高，现在我们要取出比小明高的人的数据，那么我们就先要取出小明的身高，然后再用这个数值来做过滤器的参数，再去取出目标数据，那么这将执行两次sql语句；如果用F()方法，就是可以将F（小明身高）这个直接作为过滤器的参数，从而减少操作的次数。Q()语句则是复杂查询的实现，如下:

```python
Poll.objects.get(
    Q(question__startswith='Who'),
    Q(pub_date=date(2005, 5, 2)) | Q(pub_date=date(2005, 5, 6))
)
```

等价sql: SELECT * from polls WHERE question LIKE 'Who%' AND (pub_date = '2005-05-02' OR pub_date = '2005-05-06')   ps: how marvelous

 当我们要创建新表，修改，删除时，需要用到以下几个命令：makemigrations，migrate。暂时来讲这两个已经够我用了，makemigrations就是生成修改文件，可做版本管理的功能，migrate就是实操，直接对DB进行操作。一般流程就是，编好model之后，先makemigrations,然后migrate,DB中就会有对应的表了。

剩下部分都是进阶运用了，以后再重新看吧，现在用不上。

### View layer

与MVC模式不同的是，django框架是由V来进行逻辑处理。这一层的具体实现可以说是由urls.py和view.py组成。前者规定了url和view函数的对应关系，后者则负责相关的逻辑处理。

urls.py的具体实现，其实也就是用了django内置的url函数，url函数可以接收正则表达式来匹配，并可以将捕获到的参数传给view函数。

```python
url(r'^articles/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/(?P<day>[0-9]{2})/$', views.article_detail)
```

以上例子说明url的使用方法，接收正则，传year,month,day这三个参数到后面view.article_detail这个函数中去。要注意的地方正则的开头不需要匹配'/'但结尾的时候需要(index除外，index的话直接是r'^$'就行了)。

在构造url的方面，有两个很好用的方法:include，reverse。

```python
extra_patterns = [url(r'^reports/$', credit_views.report),]
urlpatterns = [url(r'^credit/', include(extra_patterns)),]
```

include个人理解为可以减少重复子域的编写。而reverse的作用是构建url，一般情况下，往reverse中传入url或者url的名字，和参数的dict，就可以生成目标url了。

关于命名空间namespace，个人的理解就是在文件中加上app_name这个参数，并在每个文件夹（如templates）再创建app名字的文件夹来避免引用时产生冲突，当然在template中引用变量时最好也加上app的名字。

关于request和response。django中这两个都是object，内置了许多属性和方法，其中request.meta是包含请求头信息的类dict；而response分为两种，httpresponse是类dict，可以向处理dict那样添加数据，这个是一个static（静态）结构，为什么这么讲呢，因为这个response一旦生成，就不能被装饰器或者中间件修改了；而templateResponse则是动态的，在render之前他都可以受装饰器和中间件的修改。要注意的是，django中，url和view处理函数是一一对应的，所以说无论是get还是post或者其他方法，都是会对应到那一个函数上面去的。

对于view中的逻辑处理，逻辑函数可以写成方法，或者类形式。django中内置了很多基础view class来帮助开发，等于是有很多个基础组件来让我们使用，或者组合使用。

剩下的就跳过了。

### template layer

这一层是关于前端显示的，暂时对于我的水平来讲，还是用内置的dtl就好了。

 

感觉以上已经够做一个只展示内容的网站，就先到这里吧。

