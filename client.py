import requests
ip = input("What IP has the server on it? ")
while True:
    data = input("What program to kill? ")
    requests.post(ip, json={"run": data})