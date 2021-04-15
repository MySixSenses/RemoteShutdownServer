import requests
ip = input("What IP has the server on it? ")
if ":" not in ip:
    ip += ":5000"
if "http" not in ip:
    ip = "http://" + ip
password = input("What password is used for authentication? You can skip this part if the target server does not implement a password. ")
                 
while True:
    data = input("Pick one of the following: \n\t[1] Get Processes\n\t[2] Get Windows\n\t[3] Close Process\n\t[4]Close Window")
    try:
        data = int(data)
    except ValueError:
        print("You did not input a number, please enter 1, 2, 3, or 4")
        continue
    if data not in [1, 2, 3, 4]:
        print("You did not input a number, please enter 1, 2, 3, or 4")
        continue
    if data == 1:
        r = requests.get(f"{ip}/getprocesses")
        print(r.text)
    elif data == 2:
        r = requests.get(f"{ip}/getwindows")
        if r.status_code == 501:
            print("The server cannot handle the request, likely because the server isn't a Windows computer")
        print(r.text)
    elif data == 3:
        process = input("What process to kill? ")
        r = requests.post(ip, json = {'run': process, 'password': password})
        if r.status_code == 401:
            print("The server understood your request, but could not do it because you didn't enter the correct password")
        if r.status_code == 400:
            print("Unsuccessful because there was no process to close, if you're on Windows this is likely because you did not append .exe to the end of the string")
            continue
        print(f"Succesfully closed {process}")
    else:
        window = input("What window to close? ")
        r = requests.post(f"{ip}/closewindow" json = {'wintoclose': window, 'password': password})
        if r.status_code == 401:
            print("The server understood your request, but could not do it because you didn't enter the correct password")
        if r.status_code == 501:
            print("The server cannot handle the request, likely because the server isn't a Windows computer")
            continue
        if r.status_code == 400:
            print("Unsuccessful because there was no process to close, if you're on Windows this is likely because you did not append .exe to the end of the string")
            continue
        print(f"Succesfully closed all windows with names containing: {process}")


