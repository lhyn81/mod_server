from flask import Flask, render_template, request, send_file, jsonify, session
from model.cyclone import  mody_cyclone
from model.steam import mody_steam
from model.aspen_01 import mody_aspen
from model.fuelmixer import mody_fuelmixer
from model.stock import ts_get_stock
from model.utils import export_docx
from model.blue import modGroup, modItems 
from flaskext.markdown import Markdown
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import *
import hashlib
import lxml
from xml.etree import ElementTree as ET
import time
import urllib
import string
import json
import xlrd

app = Flask(__name__)
CORS(app,supports_credentials=True)
app.debug = True
Markdown(app)


#--------------------电脑端---------------------------

# Show the main page, and load sidebar menus from blue
@app.route('/')
def index():
    return render_template("home.html",groupinfo=modGroup,modinfo=modItems)

# Show the specified module page in the same format and style. Display the module information
# and make ajax link pointing to the do/name page, which is the real calculation.
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=="GET":
        return render_template("pages/login.html")
    else:
        user = request.form.to_dict()
        userid = user['user']
        pw = user['pwd']
        session['user']=userid
        return "Welcome " + session['user'] + "!"

@app.route('/show/<mod_name>', methods=['GET'])
def show(mod_name):
    if modItems[mod_name]['modType']=='normal':
        return render_template("show.html",groupinfo=modGroup,modinfo=modItems,info=modItems[mod_name])
    elif modItems[mod_name]['modType']=='custom':
        return render_template("pages/show-"+mod_name+".html",groupinfo=modGroup,modinfo=modItems,info=modItems[mod_name])
    else:
        return "mod type error!"

# From AJAX request. No html page need to load.
@app.route('/do/<mod_name>', methods=['GET', 'POST'])
def do(mod_name):
    if mod_name=='stock':
        # stockid = request.form.get('stockid')
        x = request.form.to_dict()
        y = ts_get_stock(x)
        lenth = len(y[1])
        rlt = {'total': lenth, 'rows':y[1], 'stockname':y[0], 'fn':y[2]}
        rlt = jsonify(rlt)
        return rlt
    else:
        x = request.form.to_dict()
        Calculator = modItems[mod_name]['modCalculator']
        print(Calculator)
        y = globals()[Calculator](x)
        lenth = len(y)
        rlt = {'total': lenth, 'rows':y}
        rlt = jsonify(rlt)
        return rlt

# For VIP user to download the report.
@app.route('/download/<fn>')
def download(fn):
    filename = 'static/results/'+fn
    return send_file(filename, as_attachment=True)

#--------------------移动端---------------------------

@app.route('/mobile')
def mobile_index():
    return render_template("mobile/base.html")

@app.route('/mobile/login')
def mobile_login():
    pass

@app.route('/mobile/show/<mod_name>')
def mobile_show(mod_name):
    # if mod_name=="steam":
    rlt = modItems[mod_name]
    return jsonify(rlt)

@app.route('/mobile/do/<mod_name>')
def mobile_do(mod_name):
    pass

@app.route('/mobile/test')
def mobile_test():
    return render_template("mobile/content.html")

#--------------------微信端---------------------------

@app.route('/wx',methods=['GET','POST'])
def wx_index():
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

#--------------------主程序---------------------------

if __name__ == '__main__':
    app.secret_key="19811015"
    # toolbar = DebugToolbarExtension(app)

    app.run(host='0.0.0.0', port=5000, debug=True)
