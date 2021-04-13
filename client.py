import requests
ip = input("What IP has the server on it? ")
if ":" not in ip:
    ip += ":5000"
if "http" not in ip:
    ip = "http://" + ip
while True:
    data = input("What program to kill? Get Processes to get the current processes running. ")
    if data.lower() == "Get Processes".lower():
        r = requests.get(ip + "/getprocesses")
        print(r.text)
    else:
        requests.post(ip, json={"run": data})