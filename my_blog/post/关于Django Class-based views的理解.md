# 关于Django Class-based views的理解		

Django是mvt模式，其中v就是这个显示逻辑部分，简单来讲，view函数可以说是接收request，然后处理，返回response的主体函数。

对于一些简单的逻辑关系，可以用直接用函数模式来进行处理。

```python
def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)
```

如上，很明显的逻辑，函数接收request为参数，然后随便做点事情，把内容放到response中返回，剩下的事情django都会帮我们做完。view的中心思想就是这样，处理显示部分的逻辑。

当然，当我们写一些复杂的逻辑的时候，或者说要在一个视图函数里处理get和post的时候，用这种函数式的表达方法会很复杂，也不容易日后维护和扩展，这个时候django就推荐我们用class来表达来逻辑了。

首先，要通过现象看本质，这个view的主要思想就是处理和返回请求的，无论使用def还是class。

先看一下这两个在urls.py是怎么样被绑定的：def是可以直接被引用的，而class是需要引用其as_view的方法， 但是我们可以换个角度看，在设置url映射的时候，不就是绑定了一个函数嘛。

然后在view函数中，他们又有什么不同呢。def函数表达方式，非常直观，接收request，返回response；而class则没有那么直观，要解释他的逻辑，要从django提供的基本view类讲起。

django.views.generic.base.view这个函数就是django所有内置类的爸爸，这个view类有三个方法，dispatch(),http_method_not_allowed(),options()和一个类方法as_view()。

其中，dispatch就是用来判断request的method，看接下来将这个request派到哪里method的处理函数那里去（如果要用def函数式来做这一步，就需要写一大堆if request.method == get 之类的判断），

http_method_not_allowed则是用来过滤掉某些特定method的，options就是用来设置response的一些可选参数。as_view可以理解为class的出口函数。

注意，这个view基类是没有渲染功能的，也就是说他不能和template进行交互，所以，我们需要在这个基础去扩展（这里就体现出class的优越性，如果是函数式则需要整体改动，而这里只需要去继承）

除了上面介绍的view，这个generic view class，还有两个基本的mixin类，按我个人的理解，view可以单独拿来用，他本身是完整的，但是mixin不可以，mixin往往只有单个功能，所以需要将mixin作为插件来加到view中。django提供了两个基本mixin class，一个是ContextMixin，这个mixin就只有一个方法，就是get_context_data，简单来讲，他就是接收一些字典类的参数，然后这些字典传到template去；第二个是TemplateResponseMixin，其实页数可以当作只有一个方法，就是render_to_response，没错，这个跟shortcuts里面那个一样，可以理解成返回已经渲染好了的response。

总得来说，这两个mixin，一个获取context，一个负责render，就已经可以帮助我们完成很多很多事情了。

来两个官方的例子

```python
class HomePageView(TemplateView):

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['latest_articles'] = Article.objects.all()[:5]
        return context
```

这个TemplateView也是django内置的，基类，没错，他也是绝大多数内置class的爸爸，当然除了view，他其实就是View，ContextMixin和TemplateResponseMixin的儿子。看一下他的爸爸们，我们很容想到他能干什么，只要为他指定template，然后定义好context的内容，然后就完了，我们就能得到一个渲染好的response了。

看源码可以知道，TemplateView里只有一个方法，就是定义了get()，就没了，也就是说当请求的方式是get，然后这个请求会被View.dispatch传到这个get这里，而这个get要做的也不多，第一步，调用ContextMixi.get_context_data，第二步，将第一步得到的context传到TemplalteResponseMixin.render_to_response，然后就没了。由此可见，其实我们要做的往往就是去调用Django为我们准备好的一些组件。

```python
class ArticleCounterRedirectView(RedirectView):

    permanent = False
    query_string = True
    pattern_name = 'article-detail'

    def get_redirect_url(self, *args, **kwargs):
        article = get_object_or_404(Article, pk=kwargs['pk'])
        article.update_counter()
        return super(ArticleCounterRedirectView, self).get_redirect_url(*args, **kwargs)
```

这个RedirectView的主要作用就是重定向，注意其中使用到shortcuts的get_object_or_404。