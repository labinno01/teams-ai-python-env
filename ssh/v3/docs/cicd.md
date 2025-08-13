# Intégration Continue (CI) avec GitHub Actions

Ce document décrit la mise en place d'un workflow d'Intégration Continue (CI) simple pour votre projet, utilisant GitHub Actions. L'objectif est d'automatiser la vérification de la qualité du code à chaque modification.

---

## 1. Qu'est-ce que l'Intégration Continue ?

L'Intégration Continue (CI) est une pratique de développement logiciel où les développeurs intègrent fréquemment leur code dans un dépôt partagé. Chaque intégration est ensuite vérifiée par une construction automatisée (build) et des tests automatisés.

**Bénéfices :**
*   Détection rapide des erreurs.
*   Amélioration de la qualité du code.
*   Réduction des risques lors des fusions de code.
*   Confiance accrue dans la base de code.

---

## 2. Workflow de Linting avec `ruff`

Nous avons mis en place un premier workflow simple qui utilise l'outil `ruff` pour vérifier la qualité de votre code Python.

### Fichier de Configuration

Le workflow est défini dans le fichier `.github/workflows/lint.yml` :

```yaml
name: Lint Code

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install ruff
    - name: Run ruff
      run: |
        ruff check .
```

### Explication du Workflow

*   **`name: Lint Code`** : Le nom du workflow, visible dans l'interface GitHub.
*   **`on:`** : Définit les événements qui déclenchent le workflow :
    *   `push` sur la branche `main`.
    *   `pull_request` ciblant la branche `main`.
*   **`jobs:`** : Contient les différentes tâches à exécuter. Ici, un seul job nommé `lint`.
    *   **`runs-on: ubuntu-latest`** : Le job s'exécutera sur une machine virtuelle Ubuntu hébergée par GitHub.
    *   **`steps:`** : La séquence d'actions à réaliser :
        1.  **`uses: actions/checkout@v3`** : Télécharge le code de votre dépôt sur la machine virtuelle.
        2.  **`name: Set up Python`** et **`uses: actions/setup-python@v4`** : Configure un environnement Python (dernière version 3.x) nécessaire pour `ruff`.
        3.  **`name: Install dependencies`** : Installe `pip` et `ruff`.
        4.  **`name: Run ruff`** : Exécute la commande `ruff check .` pour analyser votre code.

---

## 3. Comment Utiliser ce Workflow ?

1.  **Commitez et Poussez le Fichier :** Le workflow sera actif dès que le fichier `.github/workflows/lint.yml` sera poussé sur votre dépôt GitHub.
    ```bash
    git add .github/workflows/lint.yml
    git commit -m "feat: Add GitHub Actions workflow for linting with ruff"
    git push
    ```
2.  **Déclenchement Automatique :** Chaque fois que vous pousserez du code sur `main` ou ouvrirez/mettrez à jour une Pull Request vers `main`, le workflow se lancera automatiquement.

---

## 4. Visualiser les Résultats et Corriger les Erreurs

*   **Interface GitHub :** Rendez-vous sur la page de votre Pull Request ou sur l'onglet "Actions" de votre dépôt GitHub.
*   **Statut :** Vous verrez le statut du workflow (en cours, succès, échec).
*   **Logs Détaillés :** En cas d'échec, cliquez sur le lien "Details" à côté du job `lint`. Vous accéderez aux logs complets, affichant les messages d'erreur de `ruff` (lignes concernées, type d'erreur, etc.).
*   **Correction :** Corrigez les erreurs localement, commitez et poussez à nouveau. Le workflow se relancera pour valider vos corrections.

---

## 5. Le Workflow CI/CD comme Filet de Sécurité

Il est crucial de comprendre que ce workflow est un **filet de sécurité**. Vous devez toujours exécuter `ruff check .` (et vos tests) **localement** avant de pousser votre code. Le CI est là pour : 
*   Garantir que les standards sont respectés par tous les contributeurs.
*   Attraper les erreurs qui auraient pu être manquées localement.
*   Assurer la qualité constante de la branche principale.
