import tkinter as tk
from tkinter import filedialog, messagebox
from client import Client

class ChatApp:
    def __init__(self):
        self.client=Client("127.0.0.1",12345,"invited")
        self.app = tk.Tk()
        self.app.withdraw()  # Cache la fenêtre principale initialement
        self.show_login_window()

    def show_login_window(self):
        self.login_window = tk.Toplevel()
        self.login_window.title("Connexion")
        self.center_window(self.login_window, 300, 150)

        # Widgets pour la connexion
        tk.Label(self.login_window, text="Login").pack()
        self.login_entry = tk.Entry(self.login_window)
        self.login_entry.pack()

        tk.Label(self.login_window, text="Mot de passe").pack()
        self.password_entry = tk.Entry(self.login_window, show="*")
        self.password_entry.pack()

        tk.Button(self.login_window, text="Connexion", command=self.login).pack()
        tk.Button(self.login_window, text="Mot de passe oublié", command=self.reset_password).pack()
        tk.Button(self.login_window, text="Création compte", command=self.show_subscribe_window).pack()

    def show_error_connect(self):
        self.error_connect=tk.Toplevel()
        self.error_connect.title("Erreur")
        self.center_window(self.error_connect,200, 200)
        tk.Label(self.error_connect, text="Erreur identifiant/mdp incconus")

        tk.Button(self.error_connect,text="OK", command=self.show_error_connect.destroy())

    def show_subscribe_window(self):
        self.subscribe_window = tk.Toplevel()
        self.subscribe_window.title("Création de Compte")
        self.center_window(self.subscribe_window, 300, 250)

        # Widgets pour la création de compte
        tk.Label(self.subscribe_window, text="Pseudo").pack()
        self.username_entry = tk.Entry(self.subscribe_window)
        self.username_entry.pack()

        tk.Label(self.subscribe_window, text="Mot de passe").pack()
        self.password_entry_sub = tk.Entry(self.subscribe_window, show="*")
        self.password_entry_sub.pack()

        tk.Label(self.subscribe_window, text="Nom").pack()
        self.name_entry = tk.Entry(self.subscribe_window)
        self.name_entry.pack()

        tk.Label(self.subscribe_window, text="Prénom").pack()
        self.firstname_entry = tk.Entry(self.subscribe_window)
        self.firstname_entry.pack()

        tk.Label(self.subscribe_window, text="Numéro de téléphone").pack()
        self.phone_entry = tk.Entry(self.subscribe_window)
        self.phone_entry.pack()

        # Vérifier si les champs nécessaires sont remplis pour activer le bouton
        self.username_entry.bind("<KeyRelease>", self.check_subscribe_fields)
        self.password_entry_sub.bind("<KeyRelease>", self.check_subscribe_fields)

        self.subscribe_button = tk.Button(self.subscribe_window, text="S'inscrire", state=tk.DISABLED, command=self.on_subscribe_button_click)
        self.subscribe_button.pack()

    def on_subscribe_button_click(self):
        username = self.username_entry.get()
        password = self.password_entry_sub.get()
        name = self.name_entry.get()
        firstname = self.firstname_entry.get()
        phone = self.phone_entry.get()
        

        # Envoyer les données d'inscription au serveur via le client
        # Cette fonction doit être définie dans client.py
        # self.client.send_signup_data(username, password, name, firstname, phone)

    def check_subscribe_fields(self, event=None):
        if self.username_entry.get() and self.password_entry_sub.get():
            self.subscribe_button['state'] = tk.NORMAL
        else:
            self.subscribe_button['state'] = tk.DISABLED
    
    def center_window(self, window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = int((screen_width - width) / 2)
        y = int((screen_height - height) / 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

    def login(self):
        username = self.login_entry.get()
        password = self.password_entry.get()
        print(f"Tentative de connexion {username}")
        if self.client.connect(username,password):
        # Si la connexion est réussie :
            self.login_window.destroy()
            self.app.title(f"WhatsApp-Like Chat Application - {username}")
            self.username = username
            self.initialize_widgets()
            self.app.deiconify()  # Affiche la fenêtre principale
        else:
            self.client.connect_to_server()
            self.show_error_connect()


    def reset_password(self):
        messagebox.showinfo("Réinitialiser le mot de passe", "Procédure de réinitialisation du mot de passe.")

    def initialize_widgets(self):
        # Diviser la fenêtre principale en deux parties
        self.frame_contacts = tk.Frame(self.app, width=200)
        self.frame_chat = tk.Frame(self.app)

        # Configurer le layout
        self.frame_contacts.pack(side=tk.LEFT, fill=tk.Y)
        self.frame_chat.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.client_info_frame = tk.Frame(self.frame_contacts)
        self.client_info_label = tk.Label(self.client_info_frame, text=self.client.name)

        # Layout pour les informations du client
        self.client_info_label.pack()
        self.client_info_frame.pack(fill=tk.X)
        # Liste des contacts (exemple simple)
        self.contacts_list = tk.Listbox(self.frame_contacts)
        self.contacts_list.pack(fill=tk.BOTH, expand=True)

        # Zone de Chat (sera développée plus tard)
        self.chat_log = tk.Text(self.frame_chat, state=tk.DISABLED)
        self.chat_log.pack(fill=tk.BOTH, expand=True)

        self.message_entry_frame = tk.Frame(self.frame_chat)
        self.message_entry = tk.Entry(self.message_entry_frame)
        self.send_button = tk.Button(self.message_entry_frame, text="Envoyer", command=self.send_message)

        # Layout pour le champ de saisie et le bouton
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.send_button.pack(side=tk.RIGHT)
        self.message_entry_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.send_file_button = tk.Button(self.message_entry_frame, text="Envoyer fichier", command=self.send_file)
        self.send_file_button.pack(side=tk.LEFT)

    def send_file(self):
        filename = filedialog.askopenfilename(title="Sélectionnez un fichier")
        if filename:
            print(f"Fichier à envoyer: {filename}")
            # TODO: Ajouter la logique pour envoyer le fichier
    
    def send_message(self):
        message = self.message_entry.get()
        # TODO: Ajouter la logique pour envoyer le message
        print(f"Message à envoyer: {message}")  # Affiche le message dans la console pour le test
        self.message_entry.delete(0, tk.END)

    def run(self):
        self.app.mainloop()
        self.app.quit()

if __name__ == "__main__":
    chat_app = ChatApp()
    chat_app.run()
