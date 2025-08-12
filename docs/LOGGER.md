# Git Workflow Tool - Logger Module

## Table des matières
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Concepts clés](#concepts-clés)
4. [Utilisation](#utilisation)
   - [Initialisation](#initialisation)
   - [Affichage de messages](#affichage-de-messages)
   - [Interactions utilisateur](#interactions-utilisateur)
   - [Mode non-interactif](#mode-non-interactif)
5. [Exemples complets](#exemples-complets)
6. [Personnalisation](#personnalisation)
7. [Variables d'environnement](#variables-denvironnement)
8. [Bonnes pratiques](#bonnes-pratiques)

---

## Introduction
Le module `logger.py` fournit une interface unifiée pour :
- **Gérer les sorties utilisateur** (messages, erreurs, succès, avertissements)
- **Interagir avec l'utilisateur** (confirmations, saisies)
- **Supporter les modes interactif/non-interactif**
- **Gérer le debugging** via une variable d'environnement

Il est conçu pour être :
✅ **Testable** (mockable facilement)
✅ **Extensible** (nouveaux types de loggers)
✅ **Consistant** (messages formatés de manière uniforme)
✅ **Flexible** (comportements non-interactifs)

---

## Installation
Le module est inclus dans le package principal. Aucune installation supplémentaire n'est nécessaire.

---

## Concepts clés

### 1. L'interface `Logger`
Définit le contrat que doivent respecter tous les loggers :
```python
class Logger(Protocol):
    def info(self, message: str, newline: bool = True) -> None: ...
    def success(self, message: str, newline: bool = True) -> None: ...
    # ... (autres méthodes)
```
### 2. Implémentations disponibles

| Classe | Description |
|---|---|
| `ConsoleLogger` | Affiche des messages colorisés en console (mode interactif par défaut) |
| `SilentLogger` | Ignore la plupart des messages (pour les scripts non-interactifs) |

### 3. Niveaux de messages

| Méthode | Icône | Couleur | Utilisation typique |
|---|---|---|---|
| `info()` | ℹ | Bleu | Messages informatifs |
| `success()` | ✓ | Vert | Opérations réussies |
| `warning()` | ⚠ | Jaune | Avertissements |
| `error()` | ✗ | Rouge | Erreurs (affichées sur stderr) |
| `debug()` | 🐛 | Violet | Messages de debug (si `DEBUG=1`) |

---

## Utilisation

### Initialisation
```python
from logger import get_logger

# Mode interactif (par défaut)
logger = get_logger()

# Mode non-interactif (silencieux)
logger = get_logger(non_interactive=True)

# Forcer les couleurs (même si stdout n'est pas un TTY)
logger = get_logger(force_color=True)
```

### Affichage de messages
```python
logger.info("Début du traitement...")
logger.success("Opération terminée avec succès !")
logger.warning("Cette action est irréversible")
logger.error("Échec de la connexion au dépôt")
logger.debug("Détails techniques: {...}")  # Affiché seulement si DEBUG=1
```

### Interactions utilisateur

#### Confirmations
```python
# Confirmation avec valeur par défaut "oui"
if logger.confirm("Voulez-vous continuer?", default=True):
    print("L'utilisateur a confirmé")

# Confirmation avec abort (quitte le programme si non)
logger.confirm("Êtes-vous sûr?", abort=True)  # Quitte si réponse = non
```

#### Saisies utilisateur
```python
# Saisie simple
nom = logger.prompt("Quel est votre nom?")

# Saisie avec valeur par défaut
version = logger.prompt("Numéro de version", default="1.0.0")

# Saisie de mot de passe (masqué)
mdp = logger.prompt("Mot de passe", password=True)
```

### Mode non-interactif
En mode non-interactif (`SilentLogger`) :
- Tous les messages sauf les erreurs sont ignorés
- Les confirmations retournent toujours `True` (sauf si `default=False`)
- Les prompts retournent la valeur par défaut ou une chaîne vide

```python
logger = get_logger(non_interactive=True)
logger.info("Ce message ne sera pas affiché")
result = logger.confirm("Cette question ne sera pas posée")  # retourne True
```

---

## Exemples complets

### 1. Script interactif
```python
from logger import get_logger

def main():
    logger = get_logger()

    logger.info("Bienvenue dans l'assistant Git!")

    if not logger.confirm("Voulez-vous commencer?"):
        logger.warning("Opération annulée")
        return

    message = logger.prompt("Message de commit")
    logger.info(f"Commit en cours avec le message: {message}")

    # Simulation d'une opération
    logger.success("Opération terminée!")

if __name__ == "__main__":
    main()
```

### 2. Script non-interactif
```python
from logger import get_logger

def main():
    logger = get_logger(non_interactive=True)

    # En mode non-interactif, toutes les interactions ont des valeurs par défaut
    if logger.confirm("Voulez-vous continuer?", default=True):
        version = logger.prompt("Numéro de version", default="1.0.0")
        logger.info(f"Traitement de la version {version}...")  # Ne sera pas affiché
        logger.success("Terminé!")  # Ne sera pas affiché

    logger.error("Cette erreur sera affichée même en mode silencieux")

if __name__ == "__main__":
    main()
```

### 3. Utilisation avancée avec gestion d'erreurs
```python
from logger import get_logger

def safe_operation(logger):
    try:
        logger.info("Début de l'opération...")
        # Simulation d'une erreur
        raise ValueError("Quelque chose s'est mal passé!")
    except Exception as e:
        logger.error(f"Échec: {str(e)}")
        if logger.confirm("Voulez-vous réessayer?", default=False):
            safe_operation(logger)
        else:
            logger.warning("Opération abandonnée")

def main():
    logger = get_logger()
    safe_operation(logger)

if __name__ == "__main__":
    main()
```

---

## Personnalisation

### 1. Créer un logger personnalisé
```python
from logger import Logger

class FileLogger:
    """Logger qui écrit dans un fichier."""

    def __init__(self, log_file="app.log"):
        self.log_file = log_file

    def info(self, message: str, newline: bool = True):
        with open(self.log_file, "a") as f:
            f.write(f"[INFO] {message}\n")

    # Implémenter les autres méthodes de l'interface Logger...
    ...

# Utilisation
logger = FileLogger("mon_fichier.log")
logger.info("Test")
```

### 2. Surcharger les couleurs/icônes
```python
from logger import ConsoleLogger

class MyCustomLogger(ConsoleLogger):
    def _format_message(self, icon, message, color):
        # Personnalisation des icônes/couleurs
        if "erreur" in message.lower():
            icon = "💥"
            color = "\033[31m"  # Rouge
        return super()._format_message(icon, message, color)

logger = MyCustomLogger()
logger.error("Une erreur critique est survenue")  # Affiche 💥 au lieu de ✗
```

---

## Variables d'environnement

| Variable | Description | Valeurs possibles |
|---|---|---|
| `DEBUG` | Active les messages de debug | `1`, `true`, `yes` |
| `FORCE_COLOR` | Force l'affichage des couleurs (même si stdout n'est pas un TTY) | `1`, `true`, `yes` |
| `NO_COLOR` | Désactive complètement les couleurs | Toute valeur |

**Exemple :**
```bash
# Activer le mode debug
DEBUG=1 python mon_script.py

# Forcer les couleurs
FORCE_COLOR=1 python mon_script.py | grep "erreur"
```

---

## Bonnes pratiques

- **Utiliser `get_logger()`** plutôt que d'instancier directement les classes.
- **Gérer les modes interactif/non-interactif** dès le début du script.
- **Utiliser les valeurs par défaut** pour les prompts en mode non-interactif.
- **Réserver `logger.error()`** pour les erreurs critiques.
- **Utiliser `newline=False`** pour les messages sur la même ligne.
- **Documenter les interactions utilisateur** dans les docstrings.

---

## Résolution des problèmes

- **Problème : Les couleurs ne s'affichent pas**
  - **Causes :** Sortie non-TTY, variable `NO_COLOR`, terminal incompatible.
  - **Solutions :** Forcer avec `FORCE_COLOR=1`, vérifier la configuration.

- **Problème : Le script plante en mode non-interactif**
  - **Cause :** `prompt()` ou `confirm()` sans valeur par défaut.
  - **Solution :** Toujours fournir une valeur par défaut.

- **Problème : Les messages de debug n'apparaissent pas**
  - **Cause :** Variable `DEBUG` non définie.
  - **Solution :** Lancer avec `DEBUG=1`.

---

## Changelog
- **v1.0.0 (2023-11-15):** Première version stable.
- **v1.1.0 (2023-11-20):** Ajout du support des mots de passe masqués.
