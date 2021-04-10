from flask import *
import os
app = Flask(__name__)

@app.route('/', methods = ['POST'])
def home():
    """Renders the home page."""
    data = json.loads(request.data)
    os.system(f"taskkill /im {data['run']} /f")
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

if __name__ == "__main__":
    app.run()
