# WX小程序碎碎念--初入门

对button组件的例子中，JS代码的一点理解

```javascript
for (var i = 0; i < types.length; ++i) {
  (function(type) {  // 循环构建目标函数
    pageObject[type] = function(e) {  // duck类赋方法
      var key = type + 'Size'
      var changedData = {}
      changedData[key] =
        this.data[key] === 'default' ? 'mini' : 'default'
      this.setData(changedData)
    }
  })(types[i])  // 将此作为迭代对象
}
```

JS中，`let`，`var`，`const`的区分。

首先，三者都是用来声明变量的（用惯python这种动态语言真是好不习惯）。

`const`定义的变量不可变，且声明时必须赋值。

首先，`let`需要在`strict`模式下才能用，然后`le`t定义的变量必须赋值后才能用，不然会报错（`var`声明的变量如果未赋值，运行时会自动赋予`undefined`，不会有问题）；

`let`只能对同一变量声明一次；`let`声明的变量有严格的作用域（这是好的方面，如果是`var`的话，后声明的可能会覆盖掉前面声明的）

=> es6中的`arrow function`（卧槽这个语法真是厉害）

`(x) => x + 6`就会等于

```javascript
function(x){
    return x + 6;
}
```

有种lambda有感觉。