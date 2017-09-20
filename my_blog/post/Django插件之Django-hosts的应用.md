# Django插件之Django-hosts的应用

## 前因

网站移动端的域名是m.example.com，最开始只是在nginx做了映射，将m.example.com映射到example.com/m/下面，的确是可以访问到，但是后面发现这样做的坏处就是浏览器在浏览的时候，浏览器上面的URL会是example.com/m/xxxxx这样的，而不是按预想的二级域名那样，而且看了一些关于seo优化的，移动适配方面是不建议把移动站的页面作为PC站网站中的一个子目录来配置的，所以必须做出改变。

## 解决方法

现在养成个好习惯就是，有问题除了先搜为敬之外，还会回官方文档看有没有相关的解释。回到官网一看，官网文档部分的页面就是用了二级域名的，因为官网的源码是开源的，所以立刻上gayhub，就发现这个功能是用Django-hosts来实现的。

## 简单使用说明

Django-hosts的[官方文档](https://django-hosts.readthedocs.io/en/latest/index.html)。

个人理解：这个插件的作用其实是类似我们项目中的`urls.py`，也是做路由，只不过他是用中间件形式，在相对更外面一层，分析整个URL，而我们的`urls.py`在相对里面一点，只分析主域名后面的路径。

### 下载安装

直接用万能的`pip`就可以了。

### 配置

1. 把`django_hosts`加到`mysite.settings`的`INSTALLED_APPS`中。
2. 把`django_hosts.middleware.HostsRequestMiddleware`加到`MIDDLEWARE`的开头。
3. 把`django_hosts.middleware.HostsResponseMiddleware`加到`MIDDLEWARE`的结尾。
4. 创建`hosts.py`文件，直接放在`mysite`下面就好了。
5. 在`mysite.settings`中加上`ROOT_HOSTCONF = mysite.hosts`，注意后面的这个值取决于你第四步创建文件的位置。
6. 在`mysite.settings`中加上`DEFAULT_HOST = xxx`，就是设置路由的首选项，这个可以后面再回来看，拿下面这个例子来讲，一般就是设成`DEFAULT_HOST = 'www'`。

官网的`hosts.py`例子：

```python
from django.conf import settings
from django_hosts import patterns, host

host_patterns = patterns('',
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'(\w+)', 'path.to.custom_urls', name='wildcard'),
)
```

这个`host_patterns`的形式其实是跟`url_patterns`是很像的，第一个`host`的意思就是，以`www`开头的，也就是`www.example.com`形式的，是用`settings.ROOT_URLCONF`来进行路由，而这个`settings.ROOT_URLCONF`的默认值就是`mysite.urls`，是不是感觉到什么了，没错，这个hosts文件和项目`urls.py`文件的关系就像项目`urls.py`和app的`urls.py`的关系那样，逐层路由，最后的`name`参数就是为这个规则命名而已。

第二个`host`是用了正则匹配来匹配URL开头，然后第二个参数是URL配置文件的路径。

这个插件中实现了一个自定义的`template tag`，在模板文件里可以直接`{load hosts}`，后面调用`{% host_url 'view_name' host 'host_name'%}`就可以生成对应host的URL。

而在python文件里，这个插件提供了个跟Django内置`reverse()`一样的接口

```python
from django.shortcuts import render
from django_hosts.resolvers import reverse

def homepage(request):
    homepage_url = reverse('homepage', host='www')
    return render(request, 'homepage.html', {'homepage_url': homepage_url})
```

用法与内置的几乎一致，只不过是要多添加一个`host`的参数来指明要用哪个host。

### 遇到的问题

#### 关于路径参数

就是对应APP的URL配置文件的地址，记住这个APP要在`settings`里注册。

#### 关于本地调试

在运行本地调试的时候，`m.127.0.0.1:8000`是访问不到的啊。。我到现在也没找到解决方法，所以说没办法进行本地调试，只能直接上服务器调。

#### URL的概念

URL的核心是协议加地址，也就是说必须是要以`http`或者`https`这些开头的，而不是`www`。这设置转发的时候，要注意，一开始就是只设置`www`开头的，导致转发不成功。