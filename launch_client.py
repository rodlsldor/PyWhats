from fileinput import filename
import time
import socket
import threading
import tkinter as tk
import os
from tkinter import filedialog

save_path_dir=os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "Files_received")

def listen_for_messages(client_socket):
    while True:
        try:
            header = client_socket.recv(1024).decode('utf-8')
            if header.startswith("file:"):
                # Extrait les informations du fichier
                _, filename, filesize = header.split(':')
                print("yes1")
                filesize = int(filesize)
                # Prépare le chemin de sauvegarde
                save_path = os.path.join(save_path_dir, filename)
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                client_socket.send("OK".encode())
                time.sleep(1)
                # Commence à recevoir le fichier
                with open(save_path, 'wb') as file:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break  # Connexion fermée
                        file.write(chunk)
                        bytes_received += len(chunk)
                print(f"\nFichier reçu et sauvegardé dans : {save_path}")
            else:
                print(f"{header}")
        except Exception as e:
            print("Une erreur est survenue lors de la réception d'un message.")
            print(e)
            break

if __name__ == "__main__":
    
    host = "127.0.0.1"
    port = 12345  

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    if not os.path.exists(save_path_dir):
        os.makedirs(save_path_dir)

    username = input("Username : ")
    password = input("Password : ")
    logins= username+":"+password
    client_socket.send(logins.encode('utf-8'))
    time.sleep(1)
    rep = client_socket.recv(1024).decode('utf-8')
    if rep == username:
        listening_thread = threading.Thread(target=listen_for_messages, args=(client_socket,))
        listening_thread.daemon = True
        listening_thread.start()
        while True:
            req = input("Votre message (pseudo_destinataire:votre_message. Si c'est un fichier, remplacez ':' par ';'.): \n")
            if req.lower() == '**exit**': 
                break
            if req.startswith("/file"):
                tmp = req.split(";")
                root = tk.Tk()
                root.withdraw()
                filename = filedialog.askopenfilename()
                tmp.append(filename)
                print(tmp)
                filesize = os.path.getsize(tmp[2])
                tmp.append(str(filesize))
                req = ";".join(tmp)
            print(req)
            client_socket.send(req.encode('utf-8'))
            time.sleep(1)
    else :
        print("couldn't authenticate")
        client_socket.close()
        exit()
    
    
