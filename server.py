from flask import *
import os
import subprocess
import sys
import platform
if platform.system() == "Windows":
    import pywinauto

app = Flask(__name__)
password = None
args = sys.argv
args = args.pop(0)
if len(args) == 0:
    print("No password was passed in after the script name, assuming no password.")
else:
    password = args[0]
@app.route('/', methods = ['POST'])
def closeprocess():
    data = json.loads(request.data)
    if password is not None and data['password'] != password:
        return json.dumps({'success': False}), 401, {"ContentType": 'application/json'}
    if platform.system() == "Windows":
        num = os.system(f"taskkill /im {data['run']} /f")
    elif platform.system() == "Darwin":
        num = os.system(f"killall {data['run']}")

    return (
        json.dumps({'success': num is 0}),
        200 if num is 0 else 400,
        {'ContentType': 'application/json'},
    ) 

@app.route('/getprocesses', methods = ['GET'])
def getprocesses():
    process = subprocess.check_output(["tasklist"] if platform.system == "Windows" else ["ps", "-ax"])
    process = process.decode(sys.getdefaultencoding())
    return str(process), 200, {"ContentType":"application/text", "charset": sys.getdefaultencoding()}
    
@app.route("/closewindow", methods = ['POST'])
def closewindow():
    if password is not None and data['password'] != password:
        return json.dumps({'success': False}), 401, {"ContentType": 'application/json'}
    data = json.loads(request.data)
    if platform.system() != "Windows":
        return json.dumps({'success': False}), 501, {'ContentType': 'application/json'}
    top_windows = pywinauto.Desktop(backend="uia").windows()
    success = False
    for window in top_windows:
        if data['wintoclose'] in window.window_text():
            window.close()
            success = True
    return json.dumps({'success': success}), 200 if success else 400, {'ContentType': 'application/json'}
    
@app.route('/getwindows', methods = ['GET'])
def getwindows():
    if platform.system() != "Windows":
        return json.dumps({'success': False}), 501, {'ContentType': 'application/json'}
    top_windows = pywinauto.Desktop(backend="uia").windows()
    returnitem = []
    for window in top_windows:
        returnitem.append(window.window_text())
    return '\n'.join(returnitem), 200, {'ContentType': 'application/text'}

if __name__ == "__main__":
    debug = False
    if os.getenv("DEBUG") != None and os.getenv("DEBUG").lower() == "true":
        debug = True 
    app.run(host='0.0.0.0', debug=debug)
