from flask import *
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import os
import subprocess
import sys
import platform
import time
from threading import Thread


def closeprocessfunc(name: str) -> int:
    if platform.system() == "Windows":
        if not name.endswith(".exe"):
            name += ".exe"
        num = os.system(f"taskkill /im {name} /f > nul")
    elif platform.system() in ["Darwin", "Linux"]:
        num = os.system(f"killall {name} > /dev/null")
    return num


class CloseWindowThread(Thread):
    def __init__(self, time: int, wintoclose: str):
        Thread.__init__(self)
        self.time = time
        self.wintoclose = wintoclose

    def run(self):
        while self.time > 0:
            top_windows = pywinauto.Desktop(backend="uia").windows()
            for window in top_windows:
                if self.wintoclose in window.window_text():
                    window.close()
            self.time -= 1
            time.sleep(1)


class CloseProcessThread(Thread):
    def __init__(self, time: int, process: str):
        Thread.__init__(self)
        self.time = time
        self.process = process

    def run(self):
        while self.time > 0:
            closeprocessfunc(self.process)
            self.time -= 1
            time.sleep(1)


ph = PasswordHasher()
if platform.system() == "Windows":
    try:
        import pywinauto
    except ImportError:
        print("Not using windows features.")
        usingWinFeatures = False
debugmode = os.getenv("DEBUG") != None and os.getenv("DEBUG").lower() == "true"
app = Flask(__name__)


def firsttimepass():
    password = input("What would you like to choose as a password? ")
    hash = ph.hash(password)
    with open("password.txt", "w") as f:
        f.write(hash)


if os.path.isfile("password.txt"):
    with open("password.txt", "r") as f:
        hash = f.read()
    try:
        if ph.check_needs_rehash(hash):
            # invalid hash
            os.remove("password.txt")
            firsttimepass()
    except InvalidHash:
        os.remove("password.txt")
        firsttimepass()
else:
    firsttimepass()


def verify(hash, passw):
    try:
        ph.verify(hash, passw)
    except Exception as e:
        if isinstance(e, VerifyMismatchError) or not isinstance(e, InvalidHash):
            return False
        os.remove("password.txt")
        firsttimepass()
        return False
    return True


@app.route("/", methods=["GET", "POST"])
def closeprocess():
    if request.method == "GET":
        return (
            "Remote Access Software was installed correctly.",
            200,
            {"ContentType": "application/text"},
        )
    data = json.loads(request.data)
    if not verify(hash, data["password"]):
        return json.dumps({"success": False}), 401, {"ContentType": "application/json"}
    num = closeprocessfunc(data["wintoclose"])

    return (
        json.dumps({"success": num is 0}),
        200 if num is 0 else 400,
        {"ContentType": "application/json"},
    )


@app.route("/getprocesses", methods=["GET"])
def getprocesses():
    process = subprocess.check_output(
        ["tasklist"] if platform.system() == "Windows" else ["ps", "-ax"]
    )
    process = process.decode(sys.getdefaultencoding())
    return (
        str(process),
        200,
        {"ContentType": "application/text", "charset": sys.getdefaultencoding()},
    )


@app.route("/closewindow", methods=["POST"])
def closewindow():
    data = json.loads(request.data)
    if not verify(hash, data["password"]):
        return json.dumps({"success": False}), 401, {"ContentType": "application/json"}
    if platform.system() != "Windows" or not usingWinFeatures:
        return json.dumps({"success": False}), 501, {"ContentType": "application/json"}
    top_windows = pywinauto.Desktop(backend="uia").windows()
    success = False
    for window in top_windows:
        if data["wintoclose"] in window.window_text():
            window.close()
            success = True
    return (
        json.dumps({"success": success}),
        200 if success else 400,
        {"ContentType": "application/json"},
    )


@app.route("/getwindows", methods=["GET"])
def getwindows():
    if platform.system() != "Windows" or not usingWinFeatures:
        return json.dumps({"success": False}), 501, {"ContentType": "application/json"}
    top_windows = pywinauto.Desktop(backend="uia").windows()
    returnitem = [window.window_text() for window in top_windows]
    return "\n".join(returnitem), 200, {"ContentType": "application/text"}


@app.route("/blockwindow", methods=["POST"])
def blockwindow():
    if platform.system() != "Windows" or not usingWinFeatures:
        return json.dumps({"success": False}), 501, {"ContentType": "application/json"}
    data = json.loads(request.data)
    t = CloseWindowThread(data["time"], data["wintoclose"])
    t.start()


@app.route("/blockprocess", methods=["POST"])
def blockprocess():
    data = json.loads(request.data)
    t = CloseProcessThread(data["time"], data["wintoclose"])
    t.start()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=debugmode, ssl_context="adhoc")
