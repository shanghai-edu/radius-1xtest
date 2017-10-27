#coding=utf-8
import jinja2
import json
from time import time
from flask import request,jsonify,render_template,make_response,session,url_for
from app import app
from utils import radius_challenge
from utils import create_validate_code
from functools import wraps

def require_appkey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-KEY') and request.headers.get('X-API-KEY') == app.config["API_KEY"]:
            return view_function(*args, **kwargs)
        else:
            result = {"sucess":False,"msg":"missing API-KEY or KEY is Wrong"}
            return jsonify(result=result),403
    return decorated_function

@app.route('/api/v1/<string:ssid>', methods=['POST'])
@require_appkey
def radius1x_api(ssid):
	ssid_config = app.config['SSID_CONFIG']
	if ssid not in ssid_config:
		return "404 page not found",404
        data = request.get_json()
        if not data or not 'username' in data or not 'password' in data:
                result = {"success":False,"msg":"username or password not found"}
                return jsonify(result=result),400
        username = data["username"].encode("utf-8")
        password = data["password"].encode("utf-8")
	tsStart = time()
        try:
		res = radius_challenge(username, password, ssid_config[ssid]['RADIUS_HOST'], ssid_config[ssid]['RADIUS_SECRET'], ssid_config[ssid]['RADIUS_PORT'], ssid_config[ssid]['NAS_IP'],False)
        	t = time() - tsStart
        	result = {"username":username,"method":"mscharpv2","time":t,"success":res}
        	return jsonify(result=result),200
	except:
		t = time() - tsStart
		result = {"username":username,"method":"mscharpv2","time":t,"success":False}
		return jsonify(result=result),200

@app.route('/code', methods=['GET'])
def code():
    """生成验证码
    """
    from io import BytesIO

    output = BytesIO()
    code_img, code_str = create_validate_code()
    code_img.save(output, 'jpeg')
    img_data=output.getvalue()
    output.close()
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/jpg'
    session['code_text'] = code_str
    return response   

@app.route('/test/<string:ssid>', methods=['GET','POST'])
def radius_test(ssid):
        ssid_config = app.config['SSID_CONFIG']
        if ssid not in ssid_config:
                return "404 page not found",404
	if request.method == 'GET':
		return render_template('radius1x.html',ssid=ssid)
	
	username = request.form['username'].encode("utf-8")
	password = request.form['password'].encode("utf-8")
	verify_code = request.form['verify_code']
	if 'code_text' in session and verify_code.lower() != session['code_text'].lower():
		return render_template('radius1x.html',ssid=ssid,verify_error=True)
       	tsStart = time()
       	try:
               	res = radius_challenge(username, password, ssid_config[ssid]['RADIUS_HOST'], ssid_config[ssid]['RADIUS_SECRET'], ssid_config[ssid]['RADIUS_PORT'], ssid_config[ssid]['NAS_IP'],False)
       		t= time() - tsStart
		result = {"username":username,"method":"mscharpv2","time":t,"success":res}
		if result["success"]:
       	        	access = "Access-Accept"
       		else:
               		access = "Access-Reject"
       	 	timeusage = ("%.2f" % result['time'])
       		timeusage = str(timeusage) + "s"
       		return render_template('radius1x.html', ssid=ssid,username=result['username'], method=result['method'], timeusage=timeusage, success=result['success'], access=access)
	except:
               	t = time() - tsStart
		result = {"username":username,"method":"mscharpv2","time":t,"success":False}
		if result["success"]:
			access = "Access-Accept"
		else:
			access = "Access-Reject"
		timeusage = ("%.2f" % result['time'])
		timeusage = str(timeusage) + "s"
		return render_template('radius1x.html', ssid=ssid,username=result['username'], method=result['method'], timeusage=timeusage, success=result['success'], access=access)
