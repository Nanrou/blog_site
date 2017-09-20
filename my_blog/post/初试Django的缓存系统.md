# 初试Django的缓存系统

现在我网页的逻辑是，响应请求，查找数据库相关信息，渲染模版生成最终页面，最后返回。使用缓存后就是将这个页面保存一段时间，在有响应请求相同页面的时候，可以直接返回，不用再做那么多步。

## Django-redis

直接在`settings.py`中设置要使用的缓存形式，和添加一些特定的参数来自定义。

我选择的是用redis来做缓存数据库，而现在就有一个非常好的插件`django-redis`，可以直接用。下载库之后直接设置为`caches`的后端就行了，简单配置如下：

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PICKLE_VERSION": -1,
            "IGNORE_EXCEPTIONS": True,
        }
    }
}
```

设置完之后，在对应的视图函数`views.py`用`cache`装饰器去装饰对应的函数型视图函数，或者在`urls.py`中，用直接用`cache`这个函数去处理对应视图函数。

在`views.py`

```python
from django.views.decorators.cache import cache_page

@cache_page
def foo(request):
    ***
    return response
```

在`urls.py`

```python
from django.views.decorators.cache import cache_page

urlpatterns = [
    url(r'^$', cache_page(60 * 15)(views.HomeView.as_view()), name='home'),
]
```

还可以在模版文件中，缓存某部分页面（个人感觉主要去缓存那些要与数据库交互的部分就好了）

```python
{% load cache %}

{% cache 60 some_part}
*********
{% endcache %}

```

### 关于一些对cache的直接操作

其实`cache`的储存方式可以理解成类似于字典，都是键值对应的。

在导入`cache`之后，直接按字典型操作，就可以取到缓存中的值了。

```python
>>> from django.core.cache import cache
>>> cache.set("foo", "value", timeout=25)
>>> cache.ttl("foo")
25
>>> cache.ttl("not-existent")
0
```

以上例子来自`django-redis`的文档。



## 下载安装redis

在官方文档下载完压缩包后，解压，然后就`make test`，通过之后就可以`make --prefix=/usr/redis`，`make  install`。

完成安装后，去到目录下，测试`server`是否能成功启动。

配置方面，我暂时就只设置了守护进程，日志等级，存放位置，储存上限，满上限后的删除规则。