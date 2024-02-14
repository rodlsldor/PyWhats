from ast import mod
import base64
from email import message, message_from_binary_file
import unittest
import socket
import threading
import time
import json
import os
from urllib import request, response

import bcrypt

from user import user_file_path

class TestServer(unittest.TestCase):
    server_address = '127.0.0.1'
    server_port = 12345  # Assurez-vous que le serveur est lancé sur ce port

    @classmethod
    def setUpClass(cls):
        # Lancer le serveur dans un thread séparé si nécessaire
        pass

    def setUp(self):
        # Cette méthode est appelée avant chaque test
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_address, self.server_port))
        self.client_socket.send('TestUser'.encode('utf-8'))  # Envoyer un nom d'utilisateur de test au serveur
        time.sleep(1)  # Attendre que le serveur traite la connexion

    def test_a_client_communication(self):
        # Test de l'envoi et de la réception de messages
        print("Test commu")
        test_message = "TestUser: Hello Server!"
        self.client_socket.send(test_message.encode())
        time.sleep(1)
        received_message = self.client_socket.recv(1024).decode()
        test_message ="TestUser:  Hello Server!"
        self.assertEqual(test_message, received_message)
        # OK

    def test_b_command_add_usr(self):
        # Test des commandes de gestion d'utilisateur
        print("\najout utilisateur")
        add_user_command = "/add user camilo jahsh TestUser TestPassword 0612315612"
        self.client_socket.send(add_user_command.encode())
        time.sleep(1)  # Attendre la réponse du serveur
        # Vérifier l'existence du fichier utilisateur
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents", "PyWhats" ,"Users","TestUser.json")
        self.assertTrue(os.path.exists(user_file_path))
        # OK

    def test_c_command_request_friend(self):
        # OK
        print("\nRequête d'ami")
        add_friend_command= "/request friend TestUser testuser4"
        request_friend = "/request friend TestUser testuser7"
        self.client_socket.send(add_friend_command.encode())
        time.sleep(1)
        self.client_socket.send(request_friend.encode())
        time.sleep(1)
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents","PyWhats","Users", "TestUser.json")
        with (open(user_file_path,"r")) as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertIn("testuser4:0",user_data["demandeAmi"])
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents","PyWhats","Users", "testuser4.json")
        with (open(user_file_path,"r")) as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertIn("TestUser:0",user_data["demandeAmi"])


    def test_da_command_confirm_request(self):
        # OK
        print("\nConfirmation requête :")
        confirm_request = "/confirm friend TestUser testuser4"
        confirm_request2 = "/confirm friend testuser4 TestUser"
        self.client_socket.send(confirm_request.encode())
        time.sleep(1)
        self.client_socket.send(confirm_request2.encode())
        time.sleep(1)
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents","PyWhats","Users", "TestUser.json")
        with (open(user_file_path,"r")) as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertIn("testuser4",user_data["amis"])
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents","PyWhats","Users", "testuser4.json")
        with (open(user_file_path,"r")) as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertIn("TestUser", user_data["amis"])

    def test_db_remove_request_fr(self):
        # OK
        print("\nEnlever la demande d'ami")
        request_ = "/remove request friend TestUser testuser7"
        self.client_socket.send(request_.encode())
        time.sleep(1)
        user_file_path = os.path.join(os.path.expanduser("~"), "Documents","PyWhats","Users", "TestUser.json")
        with (open(user_file_path,"r")) as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertNotIn("testuser7:0",user_data["demandeAmi"])

    def test_f_command_modify_pass(self):
        print("\nModification mdp")
        user_file_path= os.path.join(os.path.expanduser("~"), "Documents", "PyWhats","Users" ,"TestUser.json")
        with open(user_file_path,"r") as fichierProfile :
            user_data=json.load(fichierProfile)
        modify_command= "/modify password TestUser TestPassword oui"
        self.client_socket.send(modify_command.encode())
        time.sleep(1)
        with open(user_file_path,"r") as fichierProfile :
            user_data=json.load(fichierProfile)
        self.assertTrue(bcrypt.checkpw("oui".encode(),base64.b64decode(user_data["password"])))
        
    def test_g_command_modify_phone(self):
        #OK
        print("\nModification numero ")
        modify_command="/modify phoneNumber TestUser 0712121212"
        self.client_socket.send(modify_command.encode())
        time.sleep(1)
        user_file_path= os.path.join(os.path.expanduser("~"), "Documents","PyWhats", "Users" ,"TestUser.json")
        with open(user_file_path,"r") as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertTrue("0712121212" == user_data["phoneNumber"])

    def test_h_command_help(self):
        # OK
        print("\nAide")
        message = "/help"
        self.client_socket.send(message.encode('utf-8'))
        time.sleep(1)
        response = self.client_socket.recv(1024).decode('utf-8')
        self.assertIn("Bienvenue", response)
    
    def test_dc_command_remove_friend(self):
        # OK
        print("\nEnlevement ami")
        message = "/remove friend TestUser testuser4"
        self.client_socket.send(message.encode())
        time.sleep(1)
        user_file_path= os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "Users", "TestUser.json")
        with open(user_file_path,"r") as fichierProfile:
            user_data=json.load(fichierProfile)
        self.assertNotIn("testuser4",user_data["amis"])

    def test_i_command_authentification(self):
        print("\nTest de connexion")
        message = "/connect testuser4 password123"
        self.client_socket.send(message.encode())
        time.sleep(1)
        response = self.client_socket.recv(1024).decode()
        if "True" in response :
            self.client_socket.close()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_address, self.server_port))
            self.client_socket.send('testuser4'.encode('utf-8'))
            time.sleep(1)
            self.client_socket.send("testuser4: coucou fdp".encode('utf-8'))
            time.sleep(1)
            response = self.client_socket.recv(1024).decode()
            self.assertIn("fdp",response)


    def test_j_command_remove_usr(self):
        print("\nEnlever utilisateur")
        message = "/remove user TestUser"
        self.client_socket.send(message.encode())
        time.sleep(1)
        user_file_path= os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "Users", "TestUser.json")
        self.assertFalse(os.path.exists(user_file_path))

    def test_z_error_handling(self):
        print("\nTest erreur")
        # Test de la gestion des erreurs pour une commande invalide
        invalid_command = "/invalid_command"
        self.client_socket.send(invalid_command.encode())
        time.sleep(1)
        response = self.client_socket.recv(1024).decode()
        self.assertIn("Erreur", response)  # Supposer que le serveur répond avec "Erreur" pour une commande invalide

    def tearDown(self):
        # Fermeture de la connexion client
        self.client_socket.close()

    @classmethod
    def tearDownClass(cls):
        # Nettoyage global après tous les tests
        pass

if __name__ == '__main__':
    unittest.main()
