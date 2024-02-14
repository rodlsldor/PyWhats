import socket
import threading
import os
import json
import time

class Client:
    def __init__(self, host, port, name, connected=False):
        self.host = host
        self.port = port
        self.name = name
        self.connected=connected
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to_server(self):
        self.client_socket.connect((self.host, self.port))
        self.connected=True
        print(f"Connecté au serveur {self.host}:{self.port}")
        self.client_socket.send(self.name.encode("utf-8"))
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

    def connect(self, username, password):
        if not self.connected:
            self.connect_to_server()
        if self.connected:
            login_info = "/connect "+f"{username}"+" "+f"{password}"
            self.client_socket.send(login_info.encode("utf-8"))
            time.sleep(1)
        else:
            return False

    def change_user(self,username):
        self.disconnect()
        time.sleep(1)
        self.name = username
        self.connect_to_server()

    def send_message(self, message):
        self.client_socket.send(message.encode("utf-8"))

    def send_file(self, recipient_name,file_path):
        if os.path.isfile(file_path):
            filesize =  os.path.getsize(file_path)

            filename = os.path.basename(file_path)
            preamble = f"/file:{recipient_name}:{filename}:{filesize}"
            self.client_socket.send(preamble.encode('utf-8'))
            
            time.sleep(1)

            with open(file_path, "rb") as file:
                while True :
                    bytes_read = file.read(1024)
                    if not bytes_read:
                        break

                    self.client_socket.sendall(bytes_read)

            print(f"Fichier {file_path} envoyé.")
        else:
            print(f"Erreur : Le fichier {file_path} n'existe pas.")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")
                if message.startswith("file:"):
                    # Traitement pour la réception de fichiers
                    _, sender_name, filename, filesize = message.split(":", 3)
                    filesize = int(filesize)
                    
                    # Confirmer la réception du préambule du fichier
                    print(f"Réception du fichier {filename} de {sender_name} de taille {filesize} bytes.")
                    
                    # Préparation à la réception du fichier
                    with open(filename, "wb") as file:
                        bytes_received = 0
                        while bytes_received < filesize:
                            bytes_data = self.client_socket.recv(1024)
                            if not bytes_data:
                                break  # Connexion fermée ou erreur
                            file.write(bytes_data)
                            bytes_received += len(bytes_data)
                    print(f"Fichier {filename} reçu de {sender_name}.")

            except Exception as e:
                print(f"Erreur de réception : {e}")
                break

    def disconnect(self):
        self.client_socket.close()
