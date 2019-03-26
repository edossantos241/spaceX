import threading
import re
import socket
import sys
from socket import *

server = socket(AF_INET, SOCK_STREAM)
server.bind(('localhost', int(sys.argv[1])))
server.listen(4)

if len(sys.argv) != 3:
    print("Usage: {} <port> <répertoire>".format(sys.argv[0]))
    sys.exit(1)

list = []

def connect(match, isconnected, list):
    str = ","
    var = match.group("variable")
    req = re.compile(r"^?P<variable>[a-zA-Z0-9_]{1,15}+")
    matchReq = re.match(req, var)
    if (match.group("variable") is None):
        answer = "403"
    elif (matchReq is None):
        answer = "408"
    elif (match.group("variable") in list):
        answer = "405"
    elif (isconnected == True):
        answer = "400"
    else:
        answer = "200"
        informationAllClient = "*" + match.group("variable") + " CONNECT"
        informationClient = "*" + list
        list += match.group("variable")
        isconnected = True
        pseudo = match.group("variable")
    return answer, informationAllClient, informationClient

def sendAllClients(message, list):
    for client in list :
        client.send(message)

def treat_client(sock_client):
    isconnected = False
    pseudo = ""
    status = ""
    data = sock_client.recv(1024)
    data = data.decode()
    request = re.compile(r"^(?P<command>[A-Z]+)(?P<variable> \w+)*")
    match = re.match(request, data)
    if (match is not None):
        answer = ""
        informationAllClient = ""
        informationClient = ""
        if(match.group("command") == "CONNECT"):
            answer, informationAllClient, informationClient = connect(match, isconnected, list)
        elif(match.group("command") == "QUIT"):
            answer, information = quit(match, isconnected, list, pseudo)
        elif(match.group("command") == "MESSAGE"):
            answer, information = message(match, isconnected, pseudo, status)
        elif(match.group("command") == "WHISPER"):
            answer, information2, listMessagePrivate = whisper(match, isconnected, pseudo, list)
        elif(match.group("command") == "MUTE"):
            answer, information2, listMessagePrivate = mute(match, isconnected, pseudo, list)
        else:
            pass
        sock_client.send(answer.encode())
        sock_client.sendAllClients(informationAllClient.encode())
        sock_client.sendAllClients(informationClient.encode())
        #sock_client.sendAllClients(information2.encode(), listMessagePrivate)


while True:
    try:
        sock_client, adr_client = server.accept()
        print("connection de : "+adr_client[0])
        threading.Thread(target=treat_client, args=(sock_client,)).start()
    except KeyboardInterrupt:
        break
