#linux的日常碎碎念--python&vim&crontab

## 关于安装软件的三连击

在很久之前，我就知道了linux下面，安装软件要./configure，make，make install这三步，现在来记录一下为什么要用这三连击

首先，docker的ubuntu镜像里面真是可以说什么都没有的，但是幸好，还是有apt的，所以下载gcc，make，zlib1g-dev这些软件也不会太难，要注意的是，在创建容器的时候，把国内源的文件放进去就好了

`docker run -it -v /local/host/file/path:/container/file/path --name whatever ubuntu /bin/bash`

指令解释：

　　run 就是用根据指定镜像创建容器

　　-it 就是交互式的控制台模式

　　-v 挂载宿主机的文件

　　--name 给容器命名

　　ubuntu 用到的镜像

　　/bin/bash 指定进入容器的入口？好吧，这个具体含义暂时还不清楚

将本地的源替换掉容器中的源之后，下载速度快得飞起，嘿嘿嘿。

回到正题，configure是安装文件自带的，用来检测安装环境是否可用，这个指令可以带上参数，用--help去看，但是无论是否需要自定义，都建议加上--prefix=/usr/local/filename，将文件都安装到一个指定的文件夹内，最主要是方便日后管理

make 和 make all 是一样的，作用是生成安装文件

make install就是安装

 

## python

apt源现在还是3.5，但是3.6出了新的协程关键字，所以肯定要用新的啊

可以去官方找下载地址，然后用wget来下载

在下载python前，先把其他包给安装了，包括但不限libbz2-dev，libsqlite3-dev，python3-dev，libxml2-dev，libxslt1，libffi-dev，libsll-dev，个人建议是，先装了再说

之后就是安装文件三连击

 

## 关于安装vim

apt源的版本是7.4，用wget去下载最新的8.0

在安装之前，记得下python3-dev等，防止安装后才发现没支持

在configure的时候，要注意开启插件支持，如--enable-pythoninerp，不然后面ycm这些就用不了

关于.vimrc的配置，我也都是抄网上的，抄最简单的就行，因为一般你是不会在服务器上写太多的

而关于vim插件的安装，按照网上大多数教程推荐的，先用git下载vundle，然后再用vundle去下载其他插件

但是在我的实际情况，vundle下载插件真是慢得，不知道怎么讲，所以可以用git来辅助下载

如我下载YCM的时候，就用了git来辅助

`git submodule update --init --recursive ` 在ycm目录下，敲这个，如果不完整就会自动下载，真棒！

 

## 关于crontab

安装配置crontab是不难的，但是我设置好后不运行，又找不到日志，那就很烦了

一开始我是直接使用 cmd: python script  这个类型做设置任务的，后来想重定向输入相关日志时很麻烦（主要是我不懂）

所以再写一个sh文件来执行，注意的是，无论是程序还是目标文件，最好都是用绝对地址，然后cmd写成 xx.sh >> /var/log/out.log 2>&1 & 就可以了重定向错误信息到标准输出，然后保存到out.log里面了

可以下载rsyslog这个应用，然后在/etc/rsyslog.d/具体什么我忘了，不过目录下只有一个默认文件，取消cron前面的注释，那么在cron的运行日志就会自动保存在/var/log/下了

当我都搞完这些后，就看到cron的确按我的要求定时运行了，然后从out.log里面发现运行权限不够。

所以要把那个sh文件和script文件 chmod +x，如果还不行，就把crontab 放到root组里，并chmod u+x。而我做到这一步就行了。

不过两天之后我上服务器一看，怎么脚本输出日志是空的，然后排查测试了好久，最后发现是脚本输出日志的地址错了，一定要注意输出地址时写的绝对地址还是相对地址