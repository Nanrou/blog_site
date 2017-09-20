# Celery入门指北

其实本文就是我看完Celery的官方文档指南的读书笔记。然后由于我的懒，只看完了那些入门指南，原文地址：[First Steps with Celery](http://docs.celeryproject.org/en/master/getting-started/first-steps-with-celery.html)，[Next Steps](http://docs.celeryproject.org/en/master/getting-started/next-steps.html)，[Using Celery with Django](http://docs.celeryproject.org/en/master/django/first-steps-with-django.html)。ps：本文基于celery版本4.0.2

## First Steps with Celery

其实先要理解Celery是干什么的，在我的个人理解里，他是用来管理消息队列的，具体一点讲就是，有一百个任务要分给十个人做，Celery就是负责分这一部分的工作。

在这个入门指南里，官方文档给出了存放这这一百个任务的最佳储存方式，就是`RabbitMQ`，其次的话就是`Redis`。

安装的话就直接用万能的`pip`就可以了。

在具体声明任务，调用任务这一块，文档给了非常简单的例子，个人感觉还要找其他稍微复杂一点的例子才能更好地理解是怎么用的。

而关于保存任务运行结果，也是可以放在`RebbitMQ`里或者其他数据库里。

至于配置文件，在刚入门这个情况下，只用默认就够了。

## Next Steps

这一章也只是简单地介绍一些celery的特性，想要更详细的必须要看使用指南。

比如如何在我们的应用里用Celery，在我们应用的根目录下，创建`celery.py`和`tasks.py`，前者负责生成和配置一个celery的实例，后者则是负责声明任务，任务的形式与声明普通函数类似，就是要在这些函数上面加上一个特定的装饰器。

那么如何调用这个 celery这个实例呢，文档给出的示例是用命令行启动。而调用任务的话，就是用任务的`delay()`方法。

在调用任务这部分，celery提供了一些有用的API，比如延时功能，偏函数赋值功能（就是先给一部分参数，后面再给另外一部分参数）。

celery还内置了一些基础的任务基元（不懂翻译这个），就是辅助我们构造出复杂的工作流程的工具。

任务路由方面，可以在配置文件中定制，在可以在命令行运行的时候以参数形式传入。

远程控制这部分暂时跳过。

时区设置，可以在配置文件中设置。

优化方面，默认配置是针对普通情况的，想要进一步优化就要看优化文档。不过如果有使用`RabbitMQ`的话，可以用`librabbitmq`这个库。

## Using Celery with Django

Django和Celery是有特殊的合作方式的。

* 先在`project`的文件夹下创建`celery.py`文件，如前文所讲，这个文件的任务就是配置并实例化celery。
* 然后也是在这个文件夹下，更改`__init__.py`，目的是为了启动项目时候，会导入`celery.py`。
* 然后就是在app的文件夹下创建`tasks.py`来声明任务，值得注意的就是，这些任务需要用到`@shared_task`这个装饰器。

具体的话可以看官方的[例子](https://github.com/celery/celery/tree/master/examples/django)