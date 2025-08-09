import datetime
import os
import subprocess
import shutil
import json
import random
from chat_utils import display_chat # Import display_chat from chat_utils.py
from chat_management_menu import chat_management_menu # Import the new chat management menu

random.seed() # Initialize random number generator

def get_command_output(command_list, check=False):
    try:
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if check and process.returncode != 0:
            return f"Erreur (code {process.returncode}): {stderr.strip()}"
        elif stderr:
            return f"{stdout.strip()}\nErreur (stderr): {stderr.strip()}"
        else:
            return stdout.strip()
    except FileNotFoundError:
        return "Non trouve"
    except Exception as e:
        return f"Erreur inattendue: {e}"

def run_command_stream_output(command_list):
    try:
        process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end='') # Print in real-time
        process.wait() # Wait for the process to finish
        return process.returncode
    except FileNotFoundError:
        print("Erreur: Commande non trouvee.")
        return 1
    except Exception as e:
        print(f"Erreur inattendue lors de l'execution de la commande: {e}")
        return 1

def display_python_env_details():
    print("\n--- Details de l'environnement Python ---")

    # Python Version
    python_version = get_command_output(["python3", "--version"])
    print(f"  - Python : {python_version}")

    # Python Tools
    print("\n--- Outils Python ---")
    pip_version = get_command_output(["python3", "-m", "pip", "--version"])
    print(f"  - Pip    : {pip_version.splitlines()[0] if pip_version != 'Non trouve' else pip_version}")

    pipx_version = get_command_output(["pipx", "--version"])
    print(f"  - Pipx   : {pipx_version}")

    ruff_version = get_command_output(["ruff", "--version"])
    print(f"  - Ruff   : {ruff_version}")

    poetry_version = get_command_output(["poetry", "--version"])
    print(f"  - Poetry : {poetry_version}")

    # Git Details
    print("\n--- Details Git ---")
    git_version = get_command_output(["git", "--version"])
    print(f"  - Git Client : {git_version}")

    if os.path.isdir(".git"):
        print("  - Statut du depot Git : ")
        branch = get_command_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        print(f"    - Branche courante : {branch}")
        last_commit = get_command_output(["git", "log", "-1", "--oneline"])
        print(f"    - Dernier commit   : {last_commit}")
    else:
        print("  - Pas dans un depot Git.")

def list_virtual_environments():
    """Lists virtual environments in the current directory."""
    envs = []
    for item in os.listdir('.'):
        if os.path.isdir(item):
            # Check for common venv activation scripts
            if os.path.exists(os.path.join(item, 'bin', 'activate')):
                envs.append(item)
    return envs

def create_virtual_environment():
    print("\n--- Creation d'un environnement virtuel ---")
    env_name = input("Nom du nouvel environnement virtuel (laisser vide pour '.venv'): ").strip()
    if not env_name:
        env_name = ".venv"

    full_path = os.path.abspath(env_name)
    print(f"L'environnement virtuel sera cree a : {full_path}")

    if os.path.exists(env_name):
        print(f"Le repertoire '{env_name}' existe deja. Veuillez choisir un autre nom ou le supprimer d'abord.")
        return

    print(f"Creation de l'environnement virtuel '{env_name}'...")
    # Check if python3 is available
    if get_command_output(["which", "python3"]) == "Non trouve":
        print("Erreur: python3 n'est pas trouve. Assurez-vous qu'il est installe et dans votre PATH.")
        return

    return_code = run_command_stream_output(["python3", "-m", "venv", env_name])
    
    if return_code == 0:
        print(f"Environnement virtuel '{env_name}' cree avec succes.")
    else:
        print(f"Echec de la creation de l'environnement virtuel '{env_name}'.")

def activate_virtual_environment():
    print("\n--- Activation d'un environnement virtuel ---")
    envs = list_virtual_environments()
    if not envs:
        print("Aucun environnement virtuel trouve dans le repertoire courant.")
        return

    print("Environnements virtuels disponibles:")
    for i, env in enumerate(envs):
        print(f"{i+1}) {env}")

    choice = input("Choisissez le numero de l'environnement a activer (0 pour annuler): ").strip()
    if choice == '0':
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(envs):
            selected_env = envs[index]
            print(f"\nPour activer '{selected_env}', copiez et collez la commande suivante dans votre terminal:")
            print(f"source {selected_env}/bin/activate")
            print("\nNote: Ce script ne peut pas activer l'environnement pour le shell parent.")
        else:
            print("Choix invalide.")
    except ValueError:
        print("Entree invalide. Veuillez entrer un numero.")

def delete_virtual_environment():
    print("\n--- Suppression d'un environnement virtuel ---")
    envs = list_virtual_environments()
    if not envs:
        print("Aucun environnement virtuel trouve dans le repertoire courant.")
        return

    print("Environnements virtuels disponibles:")
    for i, env in enumerate(envs):
        print(f"{i+1}) {env}")

    choice = input("Choisissez le numero de l'environnement a supprimer (0 pour annuler): ").strip()
    if choice == '0':
        return

    try:
        index = int(choice) - 1
        if 0 <= index < len(envs):
            selected_env = envs[index]
            confirm = input(f"Etes-vous sur de vouloir supprimer '{selected_env}' et tout son contenu? (oui/non): ").strip().lower()
            if confirm == 'oui':
                try:
                    shutil.rmtree(selected_env)
                    print(f"Environnement virtuel '{selected_env}' supprime avec succes.")
                except OSError as e:
                    print(f"Erreur lors de la suppression de '{selected_env}': {e}")
            else:
                print("Suppression annulee.")
        else:
            print("Choix invalide.")
    except ValueError:
        print("Entree invalide. Veuillez entrer un numero.")

def manage_virtual_environments():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n--- Gestion des environnements virtuels ---")
        print("1) Creer un environnement virtuel")
        print("2) Activer un environnement virtuel")
        print("3) Supprimer un environnement virtuel")
        print("0) Retour au menu principal")
        print("\n")

        choice = input("👉 Choisis une option: ").strip()

        if choice == '1':
            create_virtual_environment()
        elif choice == '2':
            activate_virtual_environment()
        elif choice == '3':
            delete_virtual_environment()
        elif choice == '0':
            break
        else:
            print("❌ Option invalide.")
        
        input("Appuyez sur Entree pour continuer...")

def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear') # Clear console
        print("\n╔═════════════════════════════════════════════════════════════╗")
        print("║   'Gestion de l'environnement Python sous Debian'           ║")
        print("╚═════════════════════════════════════════════════════════════╝")
        
        display_chat() # This function is now imported from chat_utils.py

        print("\n--- Options du menu Python ---")
        print("1) Gerer les environnements virtuels (creer, activer, supprimer)")
        print("2) Installer/Desinstaller des paquets Python")
        print("3) Executer des linters et formateurs de code (Ruff, Black)")
        print("4) Lancer les tests du projet (Pytest)")
        print("5) Afficher les details de l'environnement Python")
        print("0) Quitter")
        print("\n")

        choice = input("👉 Choisis une option: ").strip()

        if choice == '1':
            manage_virtual_environments()
        elif choice == '2':
            print("Fonctionnalite: Installer/Desinstaller des paquets Python (a implementer)")
        elif choice == '3':
            print("Fonctionnalite: Executer des linters et formateurs de code (a implementer)")
        elif choice == '4':
            print("Fonctionnalite: Lancer les tests du projet (a implementer)")
        elif choice == '5':
            display_python_env_details()
        elif choice == '0':
            print("\n👋 A bientot !\n")
            break
        else:
            print("❌ Option invalide.")
        
        input("Appuyez sur Entree pour continuer...")

if __name__ == "__main__":
    main_menu()