import os
import user

def comm_file_path(username1, username2):
    return os.path.join(os.path.expanduser("~"), "Documents","PyWhats", "msg",f"{username1}"+"_"+f"{username2}"+".txt") # type: ignore

def comm_folder_path():
    return os.path.join(os.path.expanduser("~"), "Documents", "PyWhats", "msg")

def comm_save(username1, username2, msg):
    if os.path.exists(comm_folder_path()):
        if os.path.exists(comm_file_path(username1,username2)) or os.path.exists(comm_file_path(username2,username1)):
            if os.path.exists(comm_file_path(username1,username2)):
                with open(comm_file_path(username1,username2),'r') as fichierComm:
                    communication = fichierComm.readlines()
                communication.append(msg)
                with open(comm_file_path(username1,username2),'w+') as fichierComm :
                    fichierComm.writelines(communication)
            else :
                with open(comm_file_path(username1,username2),'r') as fichierComm:
                    communication = fichierComm.readlines()
                communication.append(msg)
                with open(comm_file_path(username1,username2),'w+') as fichierComm :
                    fichierComm.writelines(communication)
        else :
            with open(comm_file_path(username1,username2),'w+') as fichierComm :
                fichierComm.writelines(msg)
    else:
        try :
            os.makedirs(comm_folder_path())
            comm_save(username1, username2, msg)
        except FileExistsError :
            print("Dossier existant")