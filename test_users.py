import user
import os
import json
import bcrypt
import base64

# Vous devrez peut-être ajuster ce chemin selon votre environnement de test
user_dir = os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "Users")

def test_checkExistingUser():
    # Test d'un utilisateur qui n'existe pas
    assert not user.checkExistingUser("nonexistinguser")

    # Créer un utilisateur de test et vérifier son existence
    user.addUser("Test", "User", "testuser", "password123", "123456789")
    assert user.checkExistingUser("testuser")

    # Nettoyage
    user.removeUser("testuser")

def test_creerProfile():
    username = "testuser7"
    username2 = "testuser9"
    user.creerProfile("Test", "User", username, "password123", "123456789")
    user.creerProfile("Test2", "Useraer", username2, "batlescouilles", "123456789")
    # Vérifier si le fichier de l'utilisateur a été créé
    expected_file_path = os.path.join(user_dir, f"{username}.json")
    assert os.path.exists(expected_file_path)


def test_user_file_path():
    username = "testuser3"
    result = user.addUser("Test", "User", username, "password123", "123456789")
    assert result == 0  # Succès

    # Vérifier l'existence de l'utilisateur
    assert user.checkExistingUser(username)

    # Test de suppression de l'utilisateur
    assert user.removeUser(username) == 0
    assert not user.checkExistingUser(username)

def test_modifierPassword():
    user.modifierPassword("testuser7","password123","password")
    with open(os.path.join(user_dir,"testuser7.json"),'r') as fichierProfile :
        user_data = json.load(fichierProfile)
    new_pass = base64.b64decode(user_data["password"]).decode()

    assert bcrypt.checkpw("password".encode(),new_pass.encode())
    

def test_modifierPhoneNumber():
    username = "testuser7"
    with open(os.path.join(user_dir,"testuser7.json"),'r') as fichierProfile :
        user_data = json.load(fichierProfile)
    old_phone = user_data["phoneNumber"]
    assert user.modifierPhoneNumber(username,"098765432") == 0
    with open(os.path.join(user_dir,"testuser7.json"),'r') as fichierProfile :
        user_data = json.load(fichierProfile)
    new_phone = user_data["phoneNumber"]
    assert new_phone != old_phone

def test_addUser():
    username = "testuser4"
    assert user.addUser("george","ford",username,"password123","0612315612")==0
    assert os.path.exists(os.path.join(user_dir,"testuser4.json"))

def test_removeUser():
    username = "testuser5"
    assert user.addUser("george","ford",username,"password123","0612315612")==0
    assert os.path.exists(os.path.join(user_dir,"testuser5.json"))

    assert user.removeUser(username) == 0
    assert os.path.exists(os.path.join(user_dir,"testuser5.json")) == False

def test_requestFriend():
    ami1 = "testuser4"
    ami2 = "testuser7"
    ami3 = "testuser9"

    assert user.requestFriend(ami1,ami2) == 0

    print("Test enlevement demande")
    assert user.requestFriend(ami1,ami3) == 0
    print(user.getUserInfo(ami3))
    assert user.enleverDemandeAmi(ami1,ami3) == 0
    print(user.getUserInfo(ami3))

def test_confirmRequestFriend():
    ami1 = "testuser4"
    ami2 = "testuser7"

    assert user.confirmRequestFriend(ami1,ami2) == 0
    assert user.confirmRequestFriend(ami2,ami1) == 0
    with open(os.path.join(user_dir,"testuser4.json"),'r') as fichierProfile:
        user_data = json.load(fichierProfile)
    amis1 = user_data["amis"]
    assert "testuser7" in amis1
    with open(os.path.join(user_dir,"testuser7.json"),'r') as fichierProfile:
        user_data = json.load(fichierProfile)
    amis2 = user_data["amis"]
    assert "testuser4" in amis2

def test_enleverAmi():
    ami1="testuser4"
    ami2="testuser7"

    assert user.enleverAmi(ami1,ami2) == 0

    with open(os.path.join(user_dir,"testuser4.json"),'r') as fichierProfile:
        user_data = json.load(fichierProfile)
    amis1 = user_data["amis"]
    assert "testuser7" not in amis1
    with open(os.path.join(user_dir,"testuser7.json"),'r') as fichierProfile:
        user_data = json.load(fichierProfile)
    amis2 = user_data["amis"]
    assert "testuser4" not in amis2

def test_getUserInfo():
    # Testez ici la fonction getUserInfo
    username = "testuser4"
    with open(os.path.join(user_dir,"testuser4.json"),'r') as fichierProfile:
        user_data = json.load(fichierProfile)
    results = user.getUserInfo(username)
    print(results)
    print(user_data)


if __name__ == "__main__":
    # Exécutez ici tous les tests
    test_checkExistingUser()
    test_creerProfile()
    test_user_file_path()
    test_modifierPassword()
    test_modifierPhoneNumber()
    test_addUser()
    test_removeUser()
    test_requestFriend()
    test_confirmRequestFriend()
    test_enleverAmi()
    test_getUserInfo()
