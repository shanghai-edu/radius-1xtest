## radius-1xtest
#### 简介
一个简单的 802.1x 测试服务，类似于 [Masarykova 大学 ](https://radius.ics.muni.cz/eduroam-test/eduroam-test.cgi)的这个 eduroam 测试站点

基于 Flask，轻量级

使用 mscharpv2 发起 radius 挑战报文，其他协议之后考虑增加

#### 安装

需要 Python 2.7 以上版本

克隆代码
```
git clone https://github.com/shanghai-edu/radius-1xtest.git
cd radius-1xtest
```

安装依赖
```
yum install python-pip
yum install -y python-devel
yum install libjpeg libjpeg-devel zlib zlib-devel
pip install virtualenv

virtualenv ./env
source env/bin/activate
pip install -r requirement.txt
```

#### 配置
```
cat config.py
# BASIC APP CONFIG
BIND_ADDRESS = '0.0.0.0'
PORT = 81
SECRET_KEY = "session_secret_key"  # 建立 session 所使用的 key，session 用来存验证码

# SSID CONFIG
SSID_CONFIG = {
		"test1x":
			{"RADIUS_HOST":"192.168.0.210","RADIUS_SECRET":"802.1x","RADIUS_PORT":1812,"NAS_IP":"192.168.80.5"},
		"eduroam":
			{"RADIUS_HOST":"192.168.0.220","RADIUS_SECRET":"eduroam","RADIUS_PORT":1812,"NAS_IP":"192.168.80.5"},
		}
# 字典的 key 将作为 url 的路径，例如 https://test.edu.cn/test/eduroam

# API_KEY
API_KEY = "0c8d964e8fbd4cfcd040b5691d119968"
```

#### 启动

```
chmod +x control
./control start
```

#### 停止
```
./control stop
```

#### debug 模式运行

```
./env/bin/python run.py
```

#### 部署
建议再套一层 nginx 做反向代理，以开启 https

#### 运行截图

![](https://i.imgur.com/K7YlzZJ.jpg)


#### API
配置文件中的 API_KEY 即为 API 所需的 token，示例如下：
```
[root@host ~]# curl -H "Content-Type: application/json" -d '{"username":"test01@test.edu.cn","password":"test123","token":"0c8d964e8fbd4cfcd040b5691d119968"}' "https://test.edu.cn/api/v1/eduroam"
{
  "result": {
    "method": "mscharpv2", 
    "success": true, 
    "time": 0.36426687240600586, 
    "username": "test01@test.edu.cn"
  }
}
```