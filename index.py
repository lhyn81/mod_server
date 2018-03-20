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

#--------------------主程序---------------------------

if __name__ == '__main__':
    app.secret_key="19811015"
    # toolbar = DebugToolbarExtension(app)

    app.run(host='0.0.0.0', port=5000, debug=True)
