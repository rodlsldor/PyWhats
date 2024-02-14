from client import Client
import time
import socket


def update_gui(message):
    print(f"Nouveau message: {message}")

if __name__ == "__main__":
    # Paramètres du serveur
    host = "127.0.0.1"  # ou l'adresse IP du serveur auquel vous souhaitez vous connecter
    port = 12345  # le port sur lequel le serveur écoute

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    username = input("Username : ")
    password = input("Password : ")
    couille = username+":"+password
    client_socket.send(couille.encode('utf-8'))
    time.sleep(1)
    rep = client_socket.recv(1024).decode('utf-8')

    if (rep == "oui") :
        print("ID success")
    else :
        print("couldn't authenticate")
        client_socket.close()
        exit()
    
    
    while rep!="Goodbye" :
        req = input("Pour envoyer un message tapez 'pseudo':'message'")
        client_socket.send(req.encode('utf-8'))
        rep = client_socket.recv(1024).decode('utf-8')

        #Et la tu fout ton process de requetes
        print("I received", rep, " UwU")
