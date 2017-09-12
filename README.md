## radius-1xtest
[中文](https://github.com/shanghai-edu/radius-1xtest/blob/master/README-CN.md)
#### Introduction
Simple 802.1x test server, just like [Masarykova univerzita ](https://radius.ics.muni.cz/eduroam-test/eduroam-test.cgi)

Built by Flask

use mscharpv2 for radius challenge

other protocol -- TODO 

#### Install

You need Python 2.7

Clone & Prepare
```
git clone https://github.com/shanghai-edu/radius-1xtest.git
cd radius-1xtest
```

Install dependency
```
yum install python-pip
yum install -y python-devel gcc
yum install libjpeg libjpeg-devel zlib zlib-devel
pip install virtualenv

virtualenv ./env
source env/bin/activate
pip install -r requirement.txt
```

#### Configure
```
cat config.py
# BASIC APP CONFIG
BIND_ADDRESS = '0.0.0.0'
PORT = 81
SECRET_KEY = "session_secret_key" 

# SSID CONFIG
SSID_CONFIG = {
		"test1x":
			{"RADIUS_HOST":"192.168.0.210","RADIUS_SECRET":"802.1x","RADIUS_PORT":1812,"NAS_IP":"192.168.80.5"},
		"eduroam":
			{"RADIUS_HOST":"192.168.0.220","RADIUS_SECRET":"eduroam","RADIUS_PORT":1812,"NAS_IP":"192.168.80.5"},
		}

# API_KEY
API_KEY = "0c8d964e8fbd4cfcd040b5691d119968"
```


#### start

```
chmod +x control
./control start
```

#### stop
```
./control stop
```

#### debug run

```
./env/bin/python run.py
```

#### deploy
use nginx proxy to provide https

#### Screenshots
open ```http://127.0.0.1:81/test/<ssid>``` in your browser.

such as ```http://127.0.0.1:81/test/eduroam```
![](https://i.imgur.com/K7YlzZJ.jpg)

#### API
use API_KEY in config.py for the token
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
