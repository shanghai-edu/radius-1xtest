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
