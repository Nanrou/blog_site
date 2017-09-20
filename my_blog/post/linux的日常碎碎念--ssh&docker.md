# linux的日常碎碎念--ssh&docker

## ssh

刚弄了个腾讯云的服务器，开通了ssh key登陆

根据下载的私匙，用puttygen来生成私匙文件，然后将其导入配置，就可以登陆了。

注意的是，用户下面都要有authorized_keys才能够通过ssh来登陆，所以就去有的地方，复制过来即可。

## docker

写在前面，为什么用docker。

因为配置环境真得很烦啊，所以打算直接做一个自己想要的镜像，然后用就好了。

 

在ubuntu16.04(64位)下，直接按照官方文档安装就可以了。

1，首先，如果有旧版本的docker，就用 `sudo apt-get remove docker docker-engine`

2，然后官方推荐的方法是Install using the reprository，就是在源(仓库)来安装，而不是自己编译安装，接着按照文档说的做，先更新apt源

　　`sudo apt-get install apt-transport-https ca-certificates curl software-properties-common  安装一个软件，让apt能够用https来下载`

　　`curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -  添加官方公匙`

　　`sudo apt-key fingerprint 0EBFCD88  确认公匙`

　　`sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"  添加官方的镜像仓库`

3，开始安装docker

　　`sudo apt-get update  使刚才的更改生效`

　　`sudo apt-get install docker-ce  通过apt下载安装，CE是社区版，EE是专业版`

　　官方建议在实际生产环境中，不一定要用最新的版本，可以自己指定想要的版本

　　`apt-cache madison docker-ce  查看所下载的docker的版本信息`

　　`sudo apt-get install docker-ce=<VERSION>  可以指定版本下载`

　　通过apt下载安装之后，docker daemon应该会自动运行。如无意外，应该就是可以用了

　　`sudo docker run hello-world`  起码我可以用了。。

4，我安装中遇到的问题

　　- 普通用户运行时，显示连接不上docker daemon

　　解决方法：将普通用户添加到docker的用户组中去

　　-运行过程中老是提醒不能打开config文件，说权限不允许

 　　我是直接把config那个文件夹和文件改成当前用户，和755，后面就没有提示了

　　-记录一下docker run的指令

　　docker run -it -d --name in_you_like -p 80:80 -v /home/usr/code:/home/usr/code image /bin/bash

