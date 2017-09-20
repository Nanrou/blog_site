# 关于Gevent的使用指北

只是看了[入门指南](http://sdiehl.github.io/gevent-tutorial/)，和一个[翻译文档](http://xlambda.com/gevent-tutorial/)。写一下个人读书心得。

其实看完之后，第一个反映就是`asyncio`这个系统库，感觉`gevent`现在所做的一些事情是与`asyncio`很像的，但是他自己有一个非常可怕的黑科技，就是`monkey`补丁。

使用`gevent`的过程可以简单地概括为，将一个任务（函数）放到`gevent.spawn()`中，将它变成`Greenlets`类，这一步个人感觉是与`asyncio`中，将一个函数变成`future`类或者`task`类是一个作用，然后就阻塞到全部注册的任务完成。在这个过程中，这些任务会同时执行，也就是并发。然后`gevent`也是提供了各种类似`threading`的接口，和数据结构。

至于黑科技`monkey`，就是直接替换了系统库，将系统库变成支持协程的，好处就是，只要导入这个，整个程序就支持协程了，不过最大的问题就是，这是个黑箱操作，在调试方面可能是个噩梦。

而我为什么要用`gevent`呢，因为我要用`gunicorn`，一开始我以为`gunicorn`的异步模式会很麻烦，要改很多东西，然后我就发现，只需要在`gunicorn`的配置文件中，打上`monkey`补丁，然后工人类型设为`gevent`，就可以了，没错，就是这么简单暴力。