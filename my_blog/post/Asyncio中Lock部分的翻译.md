# Asyncio中Lock部分的翻译

## Locks

### class asyncio.Lock(*, loop=None)

原始锁的对象。

 这个基础的锁是一个同步化的组件，当它上锁的时候就不属于典型的协程了（译者住：我的理解是因为上锁会阻塞住运行，所以协程也得停下来）。这个锁有两个状态，`locked`和`unlocked`。

新创建的锁的初始状态是`unlocked`。锁有两个基本方法，`acquire()`和`release()`。当锁的状态是`unlocked()`的时候，`acquire()`就会改变锁状态，也就是上锁，然后会立刻返回。当锁的状态是`locked`的时候，如果这个时候调用`acquire()`，`acquire()`会阻塞着，一直等到其他协程调用`release()`来释放锁，然后再立刻上锁，接着返回。`release()`方法只应该在锁是`locked()`的时候调用，它会释放锁并立刻返回，如果对`unlocked`状态的锁调用其`release()`方法，会抛出`RuntimeError`异常。

当有多个协程的`acquire()`都在等待释放锁的时候，那么在释放锁的时候，也只会有一个协程会成功拿到锁，而且是第一个调用`acquire()`的协程会被执行（译者注：也就是FIFO罗）。

`acquire()`是一个协程操作，所以必须用`yield from`（译者注：现在是`await`了）。

Locks也支持上下文管理机制，`yield from lock`应该作为上下文管理中的表达方式。

这个LOCK类不是线程安全的。

举个栗子

```python
lock = Lock()
...
yield from lock
try:
    ...
finally:
    lock.release()    
```

举个上下文管理的栗子：

```python
lock = Lock()
with (yield from lock):
    ...
```

锁对象的状态能够用来进行判断：

```python
if not lock.locked():
    yield from lock
else:
    # lock is acquired
    ...
```

### locked()

当锁被拿到的时候，返回`True`（译者注：其实就是锁是上锁状态的时候返回真）。

### acquire()

拿锁，申请锁，要去拿锁。

这个方法会阻塞到锁被释放，然后又把锁上锁，并返回真。

这个方法是协程，要记得用`await`。

### release()

释放锁，开锁。

当锁是上锁状态时，会释放锁，然后返回。如果其他的协程都在等待锁被释放，那么只会选择它们其中一个来获得锁（就是最早申请锁的那个）。

当没上锁的锁调用这个方法的时候，会抛出`RuntimeError`异常。

这个方法没有返回值。