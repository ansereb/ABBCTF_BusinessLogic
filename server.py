import flask
import configparser
import equations
import base64
from flask_session import Session
import json
from urllib import parse
from Cryptodome.Hash import SHA256

app = flask.Flask(__name__)

flag="Abbflagis{[A-z0-9_]*}"

@app.route('/', methods = ['GET', 'POST'])
def root():
    if flask.request.method=='POST':
        stringData=base64.b64decode(flask.request.data).decode('utf-8')
        dictData=dict(parse.parse_qsl(stringData))
        params=stringData[:stringData.index('&checkSum')]
        #check hash of request
        if (SHA256.new(params.encode('utf-8')).hexdigest() == dictData['checkSum']):
            flask.session['tasksCount']=int(dictData['taskNumber'])
            #is result right
            if (int(dictData['x'])==flask.session['solutions'][0] and int(dictData['y'])==flask.session['solutions'][1] and int(dictData['z'])==flask.session['solutions'][2]):
                #if task number is 10000 return the flag
                if (flask.session['tasksCount']==10000):
                    return flask.Response(json.dumps({'result': True, 'tasksToSolve': 10000-flask.session['tasksCount'], 'flag': flag}))
                else:
                    flask.session['tasksCount']+=1
                    return flask.Response(json.dumps({'result': True, 'tasksToSolve': 10000-flask.session['tasksCount']}))
            else:
                return flask.Response(json.dumps({'result': False, 'tasksToSolve': 10000-flask.session['tasksCount']}))
        else:
            return flask.Response(status=400)
    return flask.send_from_directory('.', 'static/index.html')

@app.route('/js/<path:path>')
def send_js(path):
    return flask.send_from_directory('static/js', path)

@app.route('/css/<path:path>')
def send_css(path):
    return flask.send_from_directory('static/css', path)

#return base64 encoded image of generated system of linear equations
@app.route('/generateEquation')
def generateEquation():
    system=equations.generateSystem()
    flask.session['solutions']=system['solutions']
    return flask.Response(base64.b64encode(equations.createSystemImageFromText(equations.createSystemTextFromDict(system))))

if __name__ == "__main__":
    parser = configparser.ConfigParser()
    parser.read_file(open("config/config.ini", "r"))
    with open("config/" + parser.get("Crypto", "SESSION_KEY"), 'r') as f:
        sessionKey = f.read()
    app.config['SECRET_KEY']=sessionKey
    app.config['SESSION_TYPE']='filesystem'
    sess = Session()
    sess.init_app(app)
    app.run(host=parser.get("Common", "HOST"), port=parser.get("Common", "PORT"))