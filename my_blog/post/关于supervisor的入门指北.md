# 关于supervisor的入门指北

在目前这个时间点（2017/07/25），supervisor还是仅支持python2，所以我们要用版本管理pyenv来隔离环境。

## pyenv

根据官方文档的讲解，pyenv的主要思路是修改环境变量，将想要用的那个版本的路径插到环境变量中的最前面去。

下载安装的话，直接

`curl -L https://raw.githubusercontent.com/pyenv/pyenv-installer/master/bin/pyenv-installer | bash`

然后再根据自己的需求去用`pyenv install xxxxx`来安装想要用的版本。

关于使用方面，`pyenv local 2.7.13`，就是指在本目录内，用python2这个解释器。

`pyenv global 2.7.13`就是全局了。

## supervisor

根据上文安装好pyenv后，新建一个文件夹`py2-supervisor`，然后在这个文件内声明`pyenv local 2.7.13`，接着`pip install supervisor`，安装完后输入`echo_supervisord_conf`，如果能看到配置信息就是安装成功了。

先生成默认的配置文件`echo_supervisord_conf > /etc/supervisor/supervisor.conf`，然后在这个目录下再创建一个`conf.d/`的文件夹，在这里面放我们具体的程序的配置文件。

如创建一个`gunicron.ini`文件，具体配置如下

```ini
[program:gunicorn]
directory = /home/nan/code/novel_site/mysite
command = gunicorn -c gunicorn.conf.py mysite.wsgi
autostart = true
redirect_stderr = true
stdout_logfile_maxbytes = 20MB
stdout_logfile_backups = 20
stdout_logfile = /home/log/gunicorn-supervisor.log
```

在主配置文件`supervisor.conf`中导入这个文件夹下的配置文件

```ini
[includes]
files = ./conf.d/*ini
```

完成之后，在`py2-supervisor`文件夹下`supervisor -c /etc/supervisor/supervisor.conf`就可以跑起来了

## supervisorctl

按上述那样运行的话，supervisor会在后台跑起来，这个时候我们可以用交互模式来访问

`supervisorctl -c supervisor.conf`，进入交互模式后，就可以用`start stop restart`这种非常人性化地去操作我们的相关任务