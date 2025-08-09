# launch_gemini.py
import subprocess
import os

def launch():
    script_path = os.path.join(os.path.dirname(__file__), "gemini_main.py")
    print("🚀 Lancement de Gemini...")
    subprocess.run(["python", script_path], check=True)

if __name__ == "__main__":
    launch()
