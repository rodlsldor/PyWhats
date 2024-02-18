import socket
import threading
import os
import bcrypt
import base64
import json
import user
import msg

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}
        self.start_server()

    def start_server(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Serveur en attente de connexions sur {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Connexion établie avec {client_address}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

    def handle_client(self, client_socket):
        client_data = client_socket.recv(1024).decode("utf-8")
        client_name = client_data.split(':')[0]
        client_password = client_data.split(':')[1]
        if self.authentification(client_name,client_password) :
            client_socket.send(client_name.encode("utf-8"))
            self.clients[client_name] = {"socket": client_socket, "messages": []}
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break

                    command = data.decode("utf-8")
                    if command.startswith("/"):
                        command = command.replace("/","")
                        if command.startswith("add") or command.startswith("remove") or command.startswith("modify") or command.startswith("request") or command.startswith("get") or command.startswith("confirm") :
                            self.receive_command(command, client_name)
                        elif command.startswith("file"):
                            self.handle_file_transfer(client_socket,command)
                        elif command.startswith("exit"):
                            break
                        elif command.startswith("help"):
                            command = f"{client_name}: "+ self.help_command()
                            self.handle_message(f"{client_name}", command)
                        else:
                            command= f"{client_name}: Erreur commande"
                            self.handle_message(f"{client_name}", command)
                    else:
                        self.handle_message(client_name, command)
                except ConnectionResetError:
                    break
        else :
            client_socket.send("nope!".encode("utf-8"))
            client_socket.close()          
        print(f"Connexion avec {client_name} fermée.")
        if f"{client_name}" in self.clients:
            del self.clients[client_name]
        client_socket.close()

    def handle_message(self, sender_name, message):
        # Vérifier si le message contient le caractère ':', qui sépare le nom du destinataire et le message
        if ':' in message:
            recipient_name, message_content = message.split(':', 1)
            recipient_socket = self.clients.get(recipient_name, None)
            if recipient_socket:
                # Si le destinataire existe, envoyer le message
                recipient_socket["socket"].send(f"{sender_name}: {message_content}".encode("utf-8"))
                self.clients[recipient_name]["messages"].append(f"{sender_name}: {message_content}")
                msg.comm_save(f"{sender_name}",f"{recipient_name}", f"{sender_name}"+":"+message_content+"\n")
            else:
                # Si le destinataire n'existe pas, informer l'expéditeur
                self.clients[sender_name]["socket"].send("Destinataire non trouvé.".encode("utf-8"))
        else:
            # Si le message ne suit pas le format attendu, informer l'expéditeur
            self.clients[sender_name]["socket"].send("Format de message invalide. Utilisez '@recipient:message'.".encode("utf-8"))


    def handle_file_transfer(self, client_socket, command):
        # Extrait les informations nécessaires de la commande
        _, recipient_name, filename, filesize = command.split(';', 4)
        filesize = int(filesize)
        recipient_socket_info = self.clients.get(recipient_name, None)
        print(recipient_socket_info)
        if recipient_socket_info:
            recipient_socket = recipient_socket_info["socket"]
            # Envoyer les métadonnées de fichier au destinataire
            file_metadata = f"file:{filename}:{filesize}"
            recipient_socket.send(file_metadata.encode("utf-8"))
            
            # Commencez à transférer le fichier
            bytes_sent = 0
            while bytes_sent < filesize:
                chunk = client_socket.recv(1024)
                recipient_socket.send(chunk)
                bytes_sent += len(chunk)

    def broadcast(self, message, sender_socket):
        for client in self.clients.values():
            if client["socket"] != sender_socket:
                try:
                    client["socket"].send(message.encode("utf-8"))
                except:
                    continue

    def validate_credentials(self, username, password):
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents", f"{username}.json")  # Chemin vers le fichier de l'utilisateur
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user_data = json.load(file)
                hashed_password_base64 = user_data["password"]
                # Décodage du mot de passe base64
                hashed_password = base64.b64decode(hashed_password_base64)
                return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        return False
    
    def receive_valid(self,username,password):
        if self.validate_credentials(username,password) :
            self.server_socket.send("True".encode("utf-8"))

    def receive_command(self, command, username):
        command_parts = command.split(' ')
        action = command_parts[0]
        if action == "add":
            return self.add_command(command_parts, username)
        elif action == "get":
            return self.get_command(command_parts,username)
        elif action == "remove":
            return self.remove_command(command_parts, username)
        elif action == "modify":
            return self.modify_command(command_parts, username)
        elif action == "request":
            return self.request_command(command_parts, username)
        elif action == "confirm" :
            return self.confirm_command(command_parts,username)
        elif action == "connect" :
            return self.authentification(command_parts[1], command_parts[2])
        elif action == "help":
            return self.help_command()
        else:
            return False

    def help_command(self):
        return "Bienvenue sur PyWhats\nVoici les commandes possibles\n\tadd\n\tmodify\n\tremove\naurevoir"

    def add_command(self, command_parts, username):
        if command_parts[1] == "friend":
            if command_parts[2] == username:
                return user.ajouterAmi(username, command_parts[2])
        elif command_parts[1] == "user":
            return user.addUser(*command_parts[2:])
        
        command= f"{username}: Erreur commande"
        self.handle_message(f"{username}", command)

    def get_command(self,command_parts,username):
        if command_parts[1] == "friends" :
            if command_parts[2] == username :
                return user.getAmis(username)
            else:
                return user.getAmis(command_parts[2])
        elif command_parts[1] == "user":
            if command_parts[2] == username :
                return user.getUserInfo(username)
            else:
                return user.getUserInfo(command_parts[2])
        command= f"{username}: Erreur commande"
        self.handle_message(f"{username}", command)

    def remove_command(self, command_parts, username):
        if command_parts[1] == "friend":
            return user.enleverAmi(command_parts[2], command_parts[3])
        elif command_parts[1] == "user":
            if command_parts[2] == f"{username}" or command_parts[3] == "admin" :
                return user.removeUser(command_parts[2])
        elif command_parts[1] == "request":
            if command_parts[2] == "friend":
                if command_parts[3] == username :
                    user.enleverDemandeAmi(username, command_parts[4])
        command= f"{username}: Erreur commande"
        self.handle_message(f"{username}", command)

    def modify_command(self, command_parts,username):
        field = command_parts[1]
        if field == "password":
            if command_parts[2] == username:
                return user.modifierPassword(username, command_parts[3], command_parts[4])
        elif field == "phoneNumber":
            if command_parts[2] == username:
                return user.modifierPhoneNumber(username, command_parts[3])
        command= f"{username}: Erreur commande"
        self.handle_message(f"{username}", command)
        
    def request_command(self, command_parts, username):
        field = command_parts[1]
        if field == "friend" :
            return user.requestFriend(username, command_parts[3])
        command= f"{username}: Erreur commande"
        self.handle_message(f"{username}", command)
    
    def confirm_command(self,command_parts,username):
        field = command_parts[1]
        if field == "friend" :
            return user.confirmRequestFriend(command_parts[2], command_parts[3])
        command= f"{username}: Erreur commande"
        self.handle_message(f"{username}", command)

    def authentification(self,username,password): 
        if not user.checkExistingUser(username) :
            print("Cet utilisateur n'existe pas.")
            return False
        try :
            if os.path.exists(user.user_file_path(username)):
                with open(user.user_file_path(username), 'r') as fichierProfile:
                    user_data = json.load(fichierProfile)
                hashed_password_base64 = user_data["password"]
                hashed_password = base64.b64decode(hashed_password_base64)
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                    return True
                else:
                    return False
        except IOError as e:
            print("Erreur de connexion : {e}")
            return False 