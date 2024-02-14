# from asyncio.windows_events import NULL
# from contextlib import nullcontext
# from msilib.schema import CreateFolder
import os
import json
# from xmlrpc.client import FastMarshaller
import bcrypt
import base64
import re

# Fonction pour vérifier si un utilisateur existe déjà
def checkExistingUser(username):
    dir_path = os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "Users")
    try:
        for fichier in os.listdir(dir_path):
            if username in fichier:
                return True
    except FileNotFoundError :
        print(f"Le dossier {username}  n'a pas été créé")
        return False

def createFolder():
    try:
        os.makedirs(user_folder_path())
        return True
    except IOError :
        return False

def creerProfile(name: str, lastname: str, username: str, password: str, phoneNumber: str):
    if os.path.exists(user_folder_path()):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_base64 = base64.b64encode(hashed_password).decode()
        user_data = {
            "name": name,
            "lastname": lastname,
            "username": username,
            "password": hashed_password_base64,  # Store the base64 encoded hashed password
            "phoneNumber": phoneNumber,
            "amis": [],
            "demandeAmi":[]
        }

        with open(user_file_path(username),"w+") as fichierProfile:
            json.dump(user_data,fichierProfile, indent=4)
    else:
        try:
            if createFolder():
                creerProfile(name, lastname, username, password, phoneNumber)
            else :
                print("Impossible de créer le répertoire souhaité")
        except FileExistsError :
            print("Dossier existant")

# Fonction pour obtenir le chemin du fichier de l'utilisateur
def user_file_path(username):
    return os.path.join(os.path.expanduser("~"), "Documents","PyWhats", "Users",f"{username}.json")

def user_folder_path():
    return os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "Users")

# Fonction pour supprimer un profil utilisateur
def supprimerProfile(username):
    try:
        if os.path.exists(user_file_path(username)):
            os.remove(user_file_path(username))
    except IOError as e:
        print(f"Erreur de fichier : {e}")

#Modifier les mots de passe
def modifierPassword(username, old_password, new_password):
    try:
        if os.path.exists(user_file_path(username)):
            with open(user_file_path(username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            stored_password_hash = base64.b64decode(user_data["password"])
            if bcrypt.checkpw(old_password.encode(), stored_password_hash):
                new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                new_password_base64 = base64.b64encode(new_hashed_password).decode('utf-8')
                user_data["password"] = new_password_base64
                with open(user_file_path(username), 'w') as fichierProfile:
                    json.dump(user_data, fichierProfile)
                return True
            else:
                return False
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return False


# Fonction pour modifier le numéro de téléphone de l'utilisateur
def modifierPhoneNumber(username, new_phoneNumber):
    try:
        if os.path.exists(user_file_path(username)):
            with open(user_file_path(username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            user_data["phoneNumber"] = new_phoneNumber
            with open(user_file_path(username), 'w') as fichierProfile:
                json.dump(user_data, fichierProfile)
        return 0
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return 1

# Fonction pour ajouter un utilisateur
def addUser(name, lastname, username, password, phoneNumber):
    if not username or not password:
        return 1
    if checkExistingUser(username):
        return 2
    creerProfile(name, lastname, username, password, phoneNumber)
    return 0

# Fonction pour supprimer un utilisateur
def removeUser(username):
    user_file = user_file_path(username)
    if not os.path.exists(user_file):
        return 1
    try:
        files = os.listdir(user_folder_path())
        for file in files :
            fichier = os.path.join(user_folder_path(),file)
            if username not in fichier:
                with open(fichier,'r') as fichierProfile:
                    user_data = json.load(fichierProfile)
                if username in user_data["amis"]:
                    user_data["amis"].remove(username)
                if username in user_data["demandeAmi"]:
                    user_data["demandeAmi"].remove(username)
                with open(fichier,'w') as fichierProfile:
                    json.dump(user_data,fichierProfile)
        try:
            os.remove(user_file)
        except OSError as e :
            print("Failed with ",e.strerror)
        return 0
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return 2

def requestFriend(username, ami_username):
    if not checkExistingUser(ami_username) or not checkExistingUser(username):
        return 1
    try:
        with open(user_file_path(ami_username),'r') as fichierProfile:
            user_data = json.load(fichierProfile)
        user_data["demandeAmi"].append(username+":0")
        with open(user_file_path(ami_username),'w') as fichierProfile:
            json.dump(user_data,fichierProfile)
        
        with open(user_file_path(username),'r') as fichierProfile:
            user_data = json.load(fichierProfile)
        user_data["demandeAmi"].append(ami_username + ":0")
        with open(user_file_path(username),'w') as fichierProfile:
            json.dump(user_data,fichierProfile)
        return 0
    except IOError as e :
        return 2
        
def confirmRequestFriend(username,ami_username):
    if not checkExistingUser(ami_username) and not checkExistingUser(username):
        return 1
    try:
        with open(user_file_path(username),'r') as fichierProfile:
            user_data = json.load(fichierProfile)
        index_ami=0
        indice=0

        for item in user_data["demandeAmi"]:
            if ami_username in item:
                index_ami=indice
            indice+=1

        situation_username = user_data["demandeAmi"][index_ami]
        situation_username = situation_username.split(':')

        if situation_username[1] == str(1) :
            situation_username[1] = "2"

        elif situation_username[1] == str(0) :
            situation_username[1] = "1"

        user_data["demandeAmi"][index_ami]=':'.join(situation_username)

        with open(user_file_path(username),'w') as fichierProfile:
            json.dump(user_data,fichierProfile)

        with open(user_file_path(ami_username),'r') as fichierProfile:
            user_data = json.load(fichierProfile)
        index_ami=0
        indice=0

        for item in user_data["demandeAmi"]:
            if username in item:
                index_ami=indice
            indice+=1

        situation_ami = user_data["demandeAmi"][index_ami]
        situation_ami = situation_ami.split(':')

        if situation_ami[1] == str(1) :
            situation_ami[1] = "2"

        elif situation_ami[1] == str(0) :
            situation_ami[1] = "1"

        user_data["demandeAmi"][index_ami]= ':'.join(situation_ami)
        with open(user_file_path(ami_username),'w') as fichierProfile:
            json.dump(user_data,fichierProfile)

        if situation_ami[1] == str(2) and situation_username[1] == str(2):
            return ajouterAmi(username,ami_username)
        
        return 0
    except IOError as e :
        return 2


# Fonction pour ajouter un ami à la liste d'amis de l'utilisateur
def ajouterAmi(username, ami_username):
    if not checkExistingUser(ami_username):
        print("Utilisateur non trouvé")
        return 1
    try:
        if os.path.exists(user_file_path(username)):
            with open(user_file_path(username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            index_ami=0
            indice=0
            for item in user_data["demandeAmi"]:
                if ami_username in item:
                    index_ami=indice
                indice+=1
            situation = user_data["demandeAmi"][index_ami]
            situation = situation.split(':')
            if situation[1] == str(2) :
                if ami_username in situation[0]:
                    user_data["amis"].append(str(ami_username))
                    user_data["demandeAmi"].remove(ami_username+":2")
                with open(user_file_path(username), 'w+') as fichierProfile:
                    json.dump(user_data, fichierProfile)
            
            with open(user_file_path(ami_username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            index_ami=0
            indice=0
            for item in user_data["demandeAmi"]:
                if ami_username in item:
                    index_ami=indice
                indice+=1
            situation = user_data["demandeAmi"][index_ami]
            situation = situation.split(':')
            if situation[1] == str(2) :
                if username in situation[0]:
                    user_data["amis"].append(str(username))
                    user_data["demandeAmi"].remove(username+":2")
                with open(user_file_path(ami_username), 'w+') as fichierProfile:
                    json.dump(user_data, fichierProfile)
            return 0
        else:
            print("Le chemin du fichier utilisateur n'existe pas")
            return 3  # Ou une autre valeur indiquant cette situation spécifique
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return 2

#enlever une demande en ami une personne
def enleverDemandeAmi(username, ami_username):
    if not checkExistingUser(ami_username):
        return 1
    try:
        if os.path.exists(user_file_path(username)) and os.path.exists(user_file_path(ami_username)):
            with open(user_file_path(username),'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            demande_status= ""
            for demande in user_data["demandeAmi"] :
                if demande.startswith(ami_username):
                    demande_status = demande
                    break
            user_data["demandeAmi"].remove(demande_status)
            with open(user_file_path(username),'w') as fichierProfile:
                json.dump(user_data,fichierProfile)
            
            with open(user_file_path(ami_username),'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            demande_status= ""
            for demande in user_data["demandeAmi"] :
                if demande.startswith(username):
                    demande_status = demande
                    break
            user_data["demandeAmi"].remove(demande_status)
            with open(user_file_path(ami_username),'w') as fichierProfile:
                json.dump(user_data,fichierProfile)
            
            return 0
    except IOError as e :
        return 2
    
# Fonction pour retirer un ami de la liste d'amis de l'utilisateur
def enleverAmi(username, ami_username):
    if not checkExistingUser(ami_username):
        return 1
    try:
        if os.path.exists(user_file_path(username)) and os.path.exists(user_file_path(ami_username)):
            with open(user_file_path(username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            user_data["amis"].remove(ami_username)

            with open(user_file_path(username), 'w') as fichierProfile:
                json.dump(user_data, fichierProfile)


            with open(user_file_path(ami_username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
            user_data["amis"].remove(username)

            with open(user_file_path(ami_username), 'w') as fichierProfile:
                json.dump(user_data, fichierProfile)
            return 0
        else:
            return 4
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return 3

# Fonction pour obtenir la liste d'amis de l'utilisateur
def getAmis(username):
    try:
        if os.path.exists(user_file_path(username)):
            with open(user_file_path(username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
                return user_data.get("amis", [])
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return []
    

def getUserInfo(username):
    try:
        if os.path.exists(user_file_path(username)):
            with open(user_file_path(username), 'r') as fichierProfile:
                user_data = json.load(fichierProfile)
                return user_data  # Renvoie les informations de l'utilisateur
        else:
            return None 
    except IOError as e:
        print(f"Erreur de fichier : {e}")
        return None  
