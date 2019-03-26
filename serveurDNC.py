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
    if (len(match.group("variable")) > 10) and (match.group("variable")[0] == "@") and (str.find(match.group("variable")) != -1):
        answer = "ERR_INVALIDNICKNAME"
    elif (match.group("variable") is None):
        answer = "ERR_NOTENOUGHARGS"
    elif (match.group("variable") in list):
        answer = "ERR_NICKNAMEINUSE"
    elif (isconnected == True):
        answer = "ERR_ALREADYCONNECTED"
    else:
        answer = "100 RPL_DONE"
        information = ":" + match.group("variable") + " CONNECT"
        list += match.group("variable")
        isconnected = True
        pseudo = match.group("variable")
    return answer, information

def quit(match, isconnected, list, pseudo):
    if(isconnected == False):
        answer = "ERR_NOTCONNECTED"
    else:
        answer = "100 RPL_DONE"
        if(match.group("variable") is not None):
            information = ":" + pseudo + " QUIT " + match.group("variable")
        else:
            information = ":" + pseudo + " QUIT"
        list -= pseudo
    return answer, information

def message(match, isconnected, pseudo, status):
    if(isconnected == False):
        answer = "ERR_NOTCONNECTED"
    elif (match.group("variable") is None):
        answer = "ERR_NOTENOUGHARGS"
    elif (status == "AWAY"):
        answer = "ERR_BADSTATUS"
    else:
        answer = "100 RPL_DONE"
        information = ":" + pseudo + " MESSAGE " + match.group("variable")
    return answer, information

def sendAllClients(message, list): 
    for client in list : 
        client.send(message)

def whisper(match, isconnected, pseudo, list):
    listMessagePrivate = []
    if(isconnected == False):
        answer = "ERR_NOTCONNECTED"
    elif ((match.group("variable") not in list) || (match.group("variable2") not in list)):
        answer = "ERR_NICKNAMENOTEXIST"
    elif ((match.group("variable") is None) || (match.group("variable3") is None)):
        answer = "ERR_NOTENOUGHARGS"
    else:
        answer = "100 RPL_DONE"
        information = ":" + pseudo + " WHISPER " + match.group("variable3")
        listMessagePrivate += pseudo
        listMessagePrivate += (match.group("variable3")
    return answer, information, listMessagePrivate


def treat_client(sock_client):
    isconnected = False
    pseudo = ""
    status = ""
    data = sock_client.recv(1024)
    data = data.decode()
    request = re.compile(r"^(?P<command>[A-Z]+) (?P<variable>[a-zA-Z0-9_]{1,10}+) (?P<variable2>[a-zA-Z0-9_]{1,10}+)? (?P<variable3>[a-zA-Z0-9_]{1,10}+)?")
    match = re.match(request, data)
    if (match is not None):
        answer = ""
        information = ""
        if(match.group("command") == "CONNECT"):
            answer, information = connect(match, isconnected, list)
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
        sock_client.sendAllClients(information.encode(), list)
        sock_client.sendAllClients(information2.encode(), listMessagePrivate)


while True:
    try:
        sock_client, adr_client = server.accept()
        print("connection de : "+adr_client[0])
        threading.Thread(target=treat_client, args=(sock_client,)).start()
    except KeyboardInterrupt:
        break
