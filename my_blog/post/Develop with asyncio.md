# Develop with asyncio

异步程序和普通的连续程序（也就是同步程序）是很不一样的，这里会列出一些常见的陷阱，并介绍如何去避开他们。

## Debug mode of asyncio

我们用`asyncio`就是为了提高性能，而为了更容易去开发编写异步的代码，我们需要开启`debug`模式

在应用中开启调试模式：

* 全局开启异步的调试模式，可以通过设置环境变量`PYTHONASYNCIODEBUG=1`，或者直接调用`AbstractEventLoop.set_debug()`
* 设置`asynico logger`的日志等级为DEBUG，如在代码开头`logging.basicConfig(level=logging.DEBUG)`
* 配置`warnings`模块去显示`ResourceWarning`警告，如在命令行中添加`-Wdefault`这个选项去启动python来显示这些

## Cancellation

取消任务（执行）这个操作对于普通的程序来讲并不常见，但是在异步程序中，这不仅是个很普通的事情，而且我们还需要去准备好去处理它们。

可以直接用`Future.cancel()`这个方法去取消掉`Future`类和`tasks`类，而`wait_for`这个方法则是直接在超时的时候取消掉这些任务。以下是一些间接取消任务的情况

如果在`Future`被取消之后调用它的`set_result()`或者`set_exception()`，它将会被一个异常导致执行失败（后半句原句为: it would fail with an exception）

```python
if not fut.cancelled():
    fut.set_result('done')
```

不要直接通过`AbstractEventLoop.call_soon()`去安排`future`类调用`set_result()`或者`set_exception()`，因为这个`future`类可以在调用这些方法前被取消掉

如果你等待一个`future`类的返回，那么就应该提早检查这个`future`类是否被取消了，这样可以避免无用的操作

```python
@coroutine
def slow_operation(fut):
    if fut.cancelled():
        return
    # ... slow computtaion ...
    yield from fut
    # ...
```

`shield()`方法能够用来忽略取消操作

## Concurrency and multithreading

一个事件循环是跑在一个线程上面的，它所有的回溯函数和任务也是执行在这个线程上的。当事件循环里面跑着一个任务的时候，不会有其他任务同时跑在同一个线程里，但是当这个任务用了`yield from`之后，那么这个任务将会被挂起，并而事件循环会去执行下一个任务。

在不是同一线程的时候，应该用`AbstractEventLoop.call_soon_threadsafe()`方法来安排回溯。

```python
loop.call_soon_threadsafe(callback, *args)
```

大多数`asyncio`对象都不是线程安全的。所以需要注意的是是否有在事件循环之外调用这些对象。举个栗子，要取消一个`future`类的时候，不应该直接调用`Future.cancel()`，而是`loop.call_soon_threadsafe(fut.cancel)`

为了控制信号和执行子进程，事件循环必须运行在主线程。

在不同线程安排回溯对象时，应该用`run_coroutine_threadsafe()`，它会返回一个`concurrent.futures.Future`对象去拿到结果

```python
future = asyncio.run_coroutine_threadsafe(coro_func(), loop)
result = future.result(timeout)  # wait for the result with a timeout 
```

`AbstractEventLoop.run_in_executor()`能够用来作为线程池的执行者，在不同的线程里去执行回溯，而且不会阻塞当前线程的事件循环。

## Handle blocking functions correctly

阻塞函数不应该被直接调用。举个栗子，如果一个函数被阻塞了一秒，那么其他任务都会被延迟一秒，这会产生很大的影响。

在网络和子进程方面，`asynico`提供了高级的API如协议。

`AbstractEventLoop.run_in_executor()`方法能够在不阻塞当前线程的事件循环的前提下，去调用其他线程或者进程的任务。

## Logging

`asyncio`模块的日志信息在`logging`模块的`asyncio`实例里

默认的日志等级是info，可以根据自己的需要改变

`logging.getLogger('asyncio').setLevel(logging.WARNING)`

## Detect coroutine objects never scheduled

当一个协程函数被调用，然后如果它的返回值没有传给`ensure_future()`或者`AbstractEvenLoop.create_task()`

的话，执行这个操作的协程对象将永远不会被安排执行，这可能就是一个bug，可以开启调试模式去通过warning信息找到它。

举个栗子

```python
import asyncio
@asyncio.coroutine
def test():
    print('never scheduled')
   
test()
```

在调试模式下会输出

```
Coroutine test() at test.py:3 was never yielded from
Coroutine object create at (most recent call last):
	File 'test.py', line 7, in <module>
	  test()
```

解决方法就是去调用`ensure_future()`函数或者通过协程对象去调用`AbstractEventLoop.create_task()`

## Detect exceptions never consumed

python经常会调用`sys.displayhook()`来处理那些未经处理过的异常。如果`Future.set_exception()`被调用，那么这个异常将不会被消耗掉（处理掉），`sys.displayhook()`也不会被调用。取而代之的是，当这个`future`类被垃圾回收机制删除的时候，日志将会输出这个异常的相关错误信息。

举个栗子，unhandled exception

```python
import asyncio

@asyncio.coroutine
def bug():
    raise Exception('not consumed')
    
loop = asyncio.get_event_loop()
asyncio.ensure_future(bug())
loop.run_forever()
loop.close()
```

输出将是

```python
Task exception was never retrieved
future: <Task finished coro=<coro() done, defined at asyncio/coroutines.py:139> exception=Exception('not consumed',)>
Traceback (most recent call last):
  File "asyncio/tasks.py", line 237, in _step
    result = next(coro)
  File "asyncio/coroutines.py", line 141, in coro
    res = func(*args, **kw)
  File "test.py", line 5, in bug
    raise Exception("not consumed")
Exception: not consumed
```

开启`asyncio`的调试模式后，会得到具体位置的错误信息

```python
Task exception was never retrieved
future: <Task finished coro=<bug() done, defined at test.py:3> exception=Exception('not consumed',) created at test.py:8>
source_traceback: Object created at (most recent call last):
  File "test.py", line 8, in <module>
    asyncio.ensure_future(bug())
Traceback (most recent call last):
  File "asyncio/tasks.py", line 237, in _step
    result = next(coro)
  File "asyncio/coroutines.py", line 79, in __next__
    return next(self.gen)
  File "asyncio/coroutines.py", line 141, in coro
    res = func(*args, **kw)
  File "test.py", line 5, in bug
    raise Exception("not consumed")
Exception: not consumed
```

可以看到第二行那里，指出了抛出异常的位置

以下提供了几个方法来解决这个问题。第一个方法就是将这个协程链到另外一个协程并使用try/except去捕捉

```python
@asyncio.coroutine
def handle_exception():
    try:
        yield from bug()
    except Exception:
        print("exception consumed")

loop = asyncio.get_event_loop()
asyncio.ensure_future(handle_exception())
loop.run_forever()
loop.close()
```

第二个方法就是用`AbstractEventLoop.run_until_complete()`

```python
task = asyncio.ensure_future(bug())
try:
    loop.run_until_complete(task)
except Exception:
    print("exception consumed")
```

## Chain corotuines correctly

当一个协程函数被另外一个协程函数（任务）调用，他们之间应该明确地用`yield from `链接起来，不然的话，执行顺序不一定和预想一致。

举个栗子，用`asyncio.sleep()`模仿的慢操作导致的bug

```python
import asyncio

@asyncio.coroutine
def create():
    yield from asyncio.sleep(3.0)
    print('(1) create file')
    
@asyncio.coroutine
def write():
    yield from asyncio.sleep(1.0)
    print('(2) write into file')
    
@asyncio.coroutine
def close():
    print('(3) close file')
    
@asyncio.coroutine
def test():
    asyncio.ensure_future(create())
    asyncio.ensure_future(write())
    asyncio.ensure_future(close())
    yield from asyncio.sleep(2.0)
    loop.stop()
    
loop = asyncio.get_event_loop()
asyncio.ensure_future(test())
loop.run_forever()
print('Pending tasks at exit: %s' % asyncio.Task.all_tasks(loop))
loop.close()
```

预想的输出为

```
(1) create file
(2) write into file
(3) close file
Pending tasks at exit: set()
```

实际的输出为

```
(3) close file
(2) write into file
Pending tasks at exit: {<Task pending create() at test.py:7 wait_for=<Future pending cb=[Task._wakeup()]>>}
Task was destroyed but it is pending!
task: <Task pending create() done at test.py:5 wait_for=<Future pending cb=[Task._wakeup()]>>
```

事件循环在`create()`完成前就已经停止掉了，而且`close()`在`write()`之前被调用，然而我们所希望调用这些函数的顺序为`create()`，`write()`，`close()`

为了解决这个问题，必须要用`yield from`来处理这些任务

```python
@asyncio.corotine
def test():
    yield from asyncio.ensure_future(create())
    yield from asyncio.ensure_future(write())
    yield from asyncio.ensure_future(close())
    yield from asyncio.sleep(2.0)
    loop.stop()
```

或者可以不要`asyncio.ensure_future()`

```python
@asyncio.coroutine
def test():
    yield from create()
    yield from write()
    yield from close()
    yield from asyncio.sleep(2.0)
    loop.stop()
```

## Pending task destroyed

如果挂起的任务被摧毁掉的话，那么包裹它的协程的执行操作将不会完成。这很有可能就是个bug，所以会被warning级别日志记录到

举个栗子，相关的日志

```
Task was destroyed but it is pending!
task: <Task pending coro=<kill_me() done, defined at test.py:5> wait_for=<Future pending cb=[Task._wakeup()]>>
```

开启`asyncio`的调试模式就可以拿到在任务被创建出来的具体位置的错误信息，开启调试模式后的相关日志

```
Task was destroyed but it is pending!
source_traceback: Object created at (most recent call last):
  File "test.py", line 15, in <module>
    task = asyncio.ensure_future(coro, loop=loop)
task: <Task pending coro=<kill_me() done, defined at test.py:5> wait_for=<Future pending cb=[Task._wakeup()] created at test.py:7> created at test.py:15>
```

## Close transports and event loops

当一个传输（交互）不再需要的时候，调用它自身的`close()`方法来释放内存，事件循环也必须明确地关闭掉（也就是要调用事件循环自身的`close()`）

如果`transport`或者`event loop`没有被显示地关闭掉，`ResourceWarning`的警告信息会传给负责摧毁它的那个执行构件。默认情况下，`ResourceWarning`的警告信息会被忽略掉。