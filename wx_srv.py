from flask import Flask, render_template, request, send_file, jsonify, session
import json
import hashlib
import lxml
from xml.etree import ElementTree as ET
import time
import urllib
import string
from model.steam import mody_steam

app = Flask(__name__)

# Show the main page, and load sidebar menus from blue
@app.route('/wx',methods=['GET','POST'])
def index():
	if request.method=='GET':
		data = request.args
		signature = data.get('signature')
		timestamp = data.get('timestamp')
		nonce = data.get('nonce')
		echostr = data.get('echostr')
		token = "lh1981" 
		list = [token, timestamp, nonce]
		list.sort()
		sha1 = hashlib.sha1()
		map(sha1.update, list)
		hashcode = sha1.hexdigest()
		if hashcode == signature:
			return echostr
		else:
			return echostr
	elif request.method=='POST':
		data=request.get_data()
		xml=ET.fromstring(data)
		msgType=xml.findtext('.//MsgType')
		ToUserName=xml.findtext('.//ToUserName')
		FromUserName=xml.findtext('.//FromUserName')
		CreateTime=xml.findtext('.//CreateTime')
		MsgId=xml.findtext('.//MsgId')
		if msgType=="text":
			steampara=xml.findtext('.//Content')
			steampara=steampara.split()
			# Content=steampara[0]+':'+steampara[1]
			if steampara[0].isnumeric() and steampara[1].isnumeric():
				x={'T':steampara[0],'P':steampara[1]}
				y=mody_steam(x)
				Content=''
				for item in y:
					Content=Content+item['varName']+':'+item['varVal']+' '+item['varUnit']+'\n'
			else:
				Content='''交互功能如下：
1.水蒸气参数查询
	查询方式：文本输入
	查询格式：温度（空格）压力
	备注：如查询饱和态，温度（或压力）请用0代替。
2.中国城市PM2.5查询
	查询方式：语音说出城市名称
	备注：无法识别区、县城、乡镇、农村等非城市名称'''
		elif msgType=="image":
			# url='https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxd2796a79e37b6b50&secret=85afc42ef6c81dfa8e120bf737486e9c'
			# tokenStr = urllib.request.urlopen(url).read().decode('UTF-8')
			# tokenData = json.loads(tokenStr)
			# token=tokenData['access_token']
			# url='https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token='+token
			# data={"type":'image',"offset":0,"count":1}
			# data=json.dumps(data)
			# data=bytes(data,'utf8')  
			# req = urllib.request.Request(url)
			# rsp = urllib.request.urlopen(req,data).read().decode('UTF-8')
			# data = json.loads(rsp)
			# print(data)
			# media_id=data['item'][0]['media_id']
			Content="微信没认证，没法发图，哈哈"
		elif msgType=="voice":
			city=xml.findtext('.//Recognition')
			city=city[:-1]
			url='http://web.juhe.cn:8080/environment/air/cityair?city='+city+'&key=fc0cf3af4fff1f1dab76ec1516045ace'
			url=urllib.parse.quote(url,safe=string.printable)
			jsonStr = urllib.request.urlopen(url).read().decode('UTF-8')
			data = json.loads(jsonStr)
			if data['error_code']==0:
				Content='''您查询的城市为:%s
日期:%s
PM2.5为:%s
空气质量为:%s'''%(city,data['result'][0]['citynow']['date'],data['result'][0]['citynow']['AQI'],data['result'][0]['citynow']['quality'])
			else:
				Content='你确定你说的是中国的某个城市？'


# construct response
		# print(Content)
		response='''<xml>
<ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%s]]></Content>
<MsgId>%s</MsgId>
</xml>'''%(FromUserName,ToUserName,time.time(),Content,MsgId)
		# print(response)
		return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
