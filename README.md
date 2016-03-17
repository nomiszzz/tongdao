# tongdao




## 部署相关环境

* Linux
* python 2.7
* mysql
* redis
* nginx

## 部署

默认部署在用户根目录,假设用户为 work,即部署再 /home/work


### 获取项目源码

    $ cd ~ && git clone https://github.com/rsj217/tongdao

### 创建python虚拟环境

    $ cd tongdao
    $ virtualenv venv

### 安装依赖

    $ source venv/bin/activate
    $ pip install -r requirements.txt

### 服务配置

    $ mv conf/nginx.conf  /etc/nginx/site-enable/
    $ mv conf/supervisor.conf /etc/

### 启动服务

    $ sudo supervisorctl -c /etc/supervisor.conf status
    $ sudo supervisorctl -c /etc/supervisor.conf restart tongdao

### 访问

    使用手机微信访问链接地址:

    https://example.com/



