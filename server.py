from flask import *
import os
import subprocess
import sys

app = Flask(__name__)

@app.route('/', methods = ['POST'])
def home():
    """Renders the home page."""
    data = json.loads(request.data)
    os.system(f"taskkill /im {data['run']} /f")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

@app.route('/getprocesses', methods = ['GET'])
def getprocesses():
    process = subprocess.check_output(["tasklist"])
    process = process.decode(sys.stdout.encoding)
    print(str(process))
    return str(process), 200, {"ContentType":"application/text"}
    
if __name__ == "__main__":
    debug = False
    if os.getenv("DEBUG") != None and os.getenv("DEBUG").lower() == "true":
        debug = True 
    app.run(host='0.0.0.0', debug=debug)
