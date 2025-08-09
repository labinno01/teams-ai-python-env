# gemini_main.py
import os
import getpass
import google.generativeai as genai

KEY_FILE = os.path.join(os.path.expanduser("~"), ".gemini_api_key")

def get_api_key():
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key

    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()

    print("🔐 Clé API Gemini non trouvée.")
    api_key = getpass.getpass("👉 Entrez votre clé API Gemini : ").strip()

    with open(KEY_FILE, "w") as f:
        f.write(api_key)

    print(f"✅ Clé API enregistrée dans {KEY_FILE}")
    return api_key

def main():
    api_key = get_api_key()
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content("Explique-moi la mécanique quantique en 3 phrases.")
    print("\n🧠 Réponse Gemini :\n")
    print(response.text)

if __name__ == "__main__":
    main()
