# Django关于设置自定义404和安装debug-toolbar的笔记

# 关于设置404

先做好404页面，然后在`views.py`文件中做好映射，最后是在`urls.py`做好路由，而这个`urls.py`必须是项目里的那个，我放到了app的里面，弄了好久都没出来，官网也只是讲了放到urlconf中，但是哪个没有讲明白。

```python
handler404 = 'app.views.your_page_not_found'
```

记住，一定要是项目的`urls.py`。

## 关于安装debug-toolbar

安装方法很简单，官网给了很详细的解释，用万能的pip下载完后，根据官网介绍的，在项目下的`urls.py`加上

```python
from django.conf import settings

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
```

然后在`settings.py`中加上

```python
if DEBUG:
    try:
        import debug_toolbar
    except ImportError:
        pass
    else:
        DEBUG_TOOLBAR_CONFIG = {
            'JQUERY_URL': r"http://code.jquery.com/jquery-2.1.1.min.js",
        }
        INSTALLED_APPS.append('debug_toolbar')
        INTERNAL_IPS = ['127.0.0.1']
        MIDDLEWARE.insert(
            MIDDLEWARE.index('django.middleware.common.CommonMiddleware') + 1,
            'debug_toolbar.middleware.DebugToolbarMiddleware'
        )
```

这个用法我是直接从Django官网的源码抄下来的，又学习了。其中那个config是把jquery的引用网址改回国内。