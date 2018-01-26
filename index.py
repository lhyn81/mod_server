from flask import Flask, render_template, request, send_file
from model.test import modinfo_test, modx_test, mody_test
from model.cyclone import modinfo_cyclone, modx_cyclone, mody_cyclone
from model.steam import modinfo_steam, modx_steam, mody_steam
from model.utils import export_docx


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/show/<mod_name>', methods=['GET'])
def show(mod_name):
    if mod_name == 'test':
        return render_template("pages/02.html", info=modinfo_test(), var=modx_test(), mod_name=mod_name)
    if mod_name == 'cyclone':
        return render_template("show.html", info=modinfo_cyclone(), var=modx_cyclone(), mod_name=mod_name)
    if mod_name == 'steam':
        return render_template("show.html", info=modinfo_steam(), var=modx_steam(), mod_name=mod_name)


@app.route('/do/<mod_name>', methods=['POST'])
def do(mod_name):
    if mod_name == 'test':
        x = request.form.to_dict()
        y = mody_test(x)
        fn = export_docx(y)
        return y.__str__()
        return render_template("do.html", var=y, fn=fn)
    if mod_name == 'cyclone':
        x = request.form.to_dict()
        y = mody_cyclone(x)
        fn = export_docx(y)
        return render_template("do.html", var=y, fn=fn)
    if mod_name == 'steam':
        x = request.form.to_dict()
        y = mody_steam(x)
        fn = export_docx(y)
        return render_template("do.html", var=y, fn=fn)


@app.route('/download/<fn>')
def download(fn):
    filename = 'static/results/'+fn
    return send_file(filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
