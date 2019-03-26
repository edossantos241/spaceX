import socket
import sys

HOST = 'localhost'
PORT = int(sys.argv[1])

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Connexion vers " + HOST + ":" + str(PORT) + " reussie.")

message = input("Requete : ")
message = str(message)
print('Envoi de : ' + str(message))
n = client.send(b'message')
if (n != len(message)):
        print('Erreur envoi.')
else:
        print('Envoi ok.')

print('Reception...')
donnees = client.recv(1024)
print('Recu :', donnees)

print('Deconnexion.')
client.close()
