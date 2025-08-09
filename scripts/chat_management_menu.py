import os
import json

def load_json_file(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def manage_anecdotes():
    chat_json_path = os.path.join(os.path.dirname(__file__), 'chat.json')
    anecdotes = load_json_file(chat_json_path)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n--- Gestion des anecdotes de chat ---")
        print("1) Lister les anecdotes")
        print("2) Ajouter une anecdote")
        print("3) Modifier une anecdote")
        print("4) Supprimer une anecdote")
        print("0) Retour au menu de gestion du chat")
        print("\n")

        choice = input("👉 Choisis une option: ").strip()

        if choice == '1':
            print("\n--- Liste des anecdotes ---")
            if not anecdotes:
                print("Aucune anecdote trouvee.")
            for i, anec in enumerate(anecdotes):
                print(f"{i+1}) {anec}")
        elif choice == '2':
            new_anecdote = input("Nouvelle anecdote (doit commencer par 'Savez vous que...'): ").strip()
            if new_anecdote.startswith("Savez vous que"):
                anecdotes.append(new_anecdote)
                save_json_file(chat_json_path, anecdotes)
                print("Anecdote ajoutee avec succes.")
            else:
                print("L'anecdote doit commencer par 'Savez vous que...'.")
        elif choice == '3':
            print("\n--- Modifier une anecdote ---")
            if not anecdotes:
                print("Aucune anecdote a modifier.")
                input("Appuyez sur Entree pour continuer...")
                continue
            for i, anec in enumerate(anecdotes):
                print(f"{i+1}) {anec}")
            try:
                idx = int(input("Numero de l'anecdote a modifier: ")) - 1
                if 0 <= idx < len(anecdotes):
                    updated_anecdote = input(f"Nouvelle valeur pour '{anecdotes[idx]}': ").strip()
                    if updated_anecdote.startswith("Savez vous que"):
                        anecdotes[idx] = updated_anecdote
                        save_json_file(chat_json_path, anecdotes)
                        print("Anecdote modifiee avec succes.")
                    else:
                        print("L'anecdote doit commencer par 'Savez vous que...'.")
                else:
                    print("Numero invalide.")
            except ValueError:
                print("Entree invalide. Veuillez entrer un numero.")
        elif choice == '4':
            print("\n--- Supprimer une anecdote ---")
            if not anecdotes:
                print("Aucune anecdote a supprimer.")
                input("Appuyez sur Entree pour continuer...")
                continue
            for i, anec in enumerate(anecdotes):
                print(f"{i+1}) {anec}")
            try:
                idx = int(input("Numero de l'anecdote a supprimer: ")) - 1
                if 0 <= idx < len(anecdotes):
                    confirm = input(f"Etes-vous sur de vouloir supprimer '{anecdotes[idx]}'? (oui/non): ").strip().lower()
                    if confirm == 'oui':
                        anecdotes.pop(idx)
                        save_json_file(chat_json_path, anecdotes)
                        print("Anecdote supprimee avec succes.")
                    else:
                        print("Suppression annulee.")
                else:
                    print("Numero invalide.")
            except ValueError:
                print("Entree invalide. Veuillez entrer un numero.")
        elif choice == '0':
            break
        else:
            print("❌ Option invalide.")
        input("Appuyez sur Entree pour continuer...")

def manage_special_dates():
    special_chats_json_path = os.path.join(os.path.dirname(__file__), 'special_chats.json')
    special_dates = load_json_file(special_chats_json_path)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n--- Gestion des dates speciales ---")
        print("1) Lister les dates speciales")
        print("2) Ajouter une date speciale")
        print("3) Modifier une date speciale")
        print("4) Supprimer une date speciale")
        print("0) Retour au menu de gestion du chat")
        print("\n")

        choice = input("👉 Choisis une option: ").strip()

        if choice == '1':
            print("\n--- Liste des dates speciales ---")
            if not special_dates:
                print("Aucune date speciale configuree.")
            for i, date_config in enumerate(special_dates):
                print(f"{i+1}) {date_config.get('month')}/{date_config.get('day')}: {date_config.get('message_line1')}")
        elif choice == '2':
            print("\n--- Ajouter une date speciale ---")
            try:
                month = int(input("Mois (1-12): "))
                day = int(input("Jour (1-31): "))
                msg1 = input("Message ligne 1: ").strip()
                cat_face = input("Visage du chat (ex: ( ^.^ )): ").strip()
                msg2 = input("Message ligne 2 (optionnel): ").strip()
                anecdote_src = input("Source d'anecdote (ex: chat.json, optionnel): ").strip()

                new_date = {"month": month, "day": day, "message_line1": msg1, "cat_face": cat_face}
                if msg2:
                    new_date["message_line2"] = msg2
                if anecdote_src:
                    new_date["anecdote_source"] = anecdote_src

                special_dates.append(new_date)
                save_json_file(special_chats_json_path, special_dates)
                print("Date speciale ajoutee avec succes.")
            except ValueError:
                print("Entree invalide. Veuillez entrer des nombres pour le mois et le jour.")
        elif choice == '3':
            print("\n--- Modifier une date speciale ---")
            if not special_dates:
                print("Aucune date speciale a modifier.")
                input("Appuyez sur Entree pour continuer...")
                continue
            for i, date_config in enumerate(special_dates):
                print(f"{i+1}) {date_config.get('month')}/{date_config.get('day')}: {date_config.get('message_line1')}")
            try:
                idx = int(input("Numero de la date speciale a modifier: ")) - 1
                if 0 <= idx < len(special_dates):
                    date_config = special_dates[idx]
                    print(f"Modification de la date: {date_config.get('month')}/{date_config.get('day')}")
                    date_config['message_line1'] = input(f"Message ligne 1 (actuel: {date_config.get('message_line1')}): ").strip() or date_config['message_line1']
                    date_config['cat_face'] = input(f"Visage du chat (actuel: {date_config.get('cat_face')}): ").strip() or date_config['cat_face']
                    date_config['message_line2'] = input(f"Message ligne 2 (actuel: {date_config.get('message_line2', '')} - optionnel): ").strip()
                    date_config['anecdote_source'] = input(f"Source d'anecdote (actuel: {date_config.get('anecdote_source', '')} - optionnel): ").strip()

                    save_json_file(special_chats_json_path, special_dates)
                    print("Date speciale modifiee avec succes.")
                else:
                    print("Numero invalide.")
            except ValueError:
                print("Entree invalide. Veuillez entrer un numero.")
        elif choice == '4':
            print("\n--- Supprimer une date speciale ---")
            if not special_dates:
                print("Aucune date speciale a supprimer.")
                input("Appuyez sur Entree pour continuer...")
                continue
            for i, date_config in enumerate(special_dates):
                print(f"{i+1}) {date_config.get('month')}/{date_config.get('day')}: {date_config.get('message_line1')}")
            try:
                idx = int(input("Numero de la date speciale a supprimer: ")) - 1
                if 0 <= idx < len(special_dates):
                    confirm = input(f"Etes-vous sur de vouloir supprimer la date {special_dates[idx].get('month')}/{special_dates[idx].get('day')}? (oui/non): ").strip().lower()
                    if confirm == 'oui':
                        special_dates.pop(idx)
                        save_json_file(special_chats_json_path, special_dates)
                        print("Date speciale supprimee avec succes.")
                    else:
                        print("Suppression annulee.")
                else:
                    print("Numero invalide.")
            except ValueError:
                print("Entree invalide. Veuillez entrer un numero.")
        elif choice == '0':
            break
        else:
            print("❌ Option invalide.")
        input("Appuyez sur Entree pour continuer...")

def chat_management_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n╔═════════════════════════════════════════════════════════════╗")
        print("║   Gestion du Chat et des Dates Speciales                    ║")
        print("╚═════════════════════════════════════════════════════════════╝")
        print("\n--- Menu de gestion du chat ---")
        print("1) Gerer les anecdotes (chat.json)")
        print("2) Gerer les dates speciales (special_chats.json)")
        print("0) Retour au menu principal")
        print("\n")

        choice = input("👉 Choisis une option: ").strip()

        if choice == '1':
            manage_anecdotes()
        elif choice == '2':
            manage_special_dates()
        elif choice == '0':
            break
        else:
            print("❌ Option invalide.")
        
        input("Appuyez sur Entree pour continuer...")

if __name__ == "__main__":
    chat_management_menu()
