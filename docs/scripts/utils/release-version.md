1. Identification
   * ID de l'Exigence : GIT-REQ-005
   * Nom du Script : release-version.sh
   * Version : Gérée par les tags Git (ex: v0.1.0)
   * Objectif (Raison d'être) : Automatiser et sécuriser le processus de création d'une release, en garantissant la synchronisation entre le fichier `version.json` et les tags Git.

  2. Description Fonctionnelle (Le "Quoi")
   * Déclencheur : Manuellement par le développeur depuis la branche principale (`main`) lorsque le code est stable et prêt à être versionné.
   * Processus :
       1. **Vérification du Contexte :**
          * Le script s'assure qu'il est bien exécuté à l'intérieur d'un dépôt Git.
          * Il vérifie que le répertoire de travail est "propre" (pas de modifications non commitées).
       2. **Choix de la Version :**
          * Il lit la version actuelle depuis `version.json`.
          * Il demande à l'utilisateur de choisir le type de la nouvelle version : `PATCH`, `MINEUR`, ou `MAJEUR`.
          * Il calcule le nouveau numéro de version (ex: `0.1.0` -> `0.1.1`).
       3. **Génération des Notes de Version :**
          * **Pour un `PATCH` :** Le script génère automatiquement la liste des commits depuis le dernier tag.
          * **Pour un `MINEUR` :** Il demande à l'utilisateur de décrire la nouvelle fonctionnalité.
          * **Pour un `MAJEUR` :** Il demande à l'utilisateur de justifier le changement non rétrocompatible.
       4. **Confirmation :**
          * Le script affiche un résumé complet : nouvelle version, message du tag.
          * Il demande une confirmation finale avant d'exécuter les changements.
       5. **Exécution de la Release :**
          * Il met à jour le numéro de version dans le fichier `version.json`.
          * Il crée un commit avec le message `chore(release): Bump version to X.Y.Z`.
          * Il crée un tag Git annoté (`git tag -a`) avec le message généré.
          * Il pousse le nouveau commit et le nouveau tag vers le dépôt distant (`origin`).
   * Résultat Attendu : Le projet a une nouvelle version officielle, visible dans `version.json` et dans les tags Git, et synchronisée avec le dépôt distant.

  3. Exigences Non-Fonctionnelles (Les "Contraintes")
   * Sécurité : Le script ne permet pas de créer une release si le code n'est pas dans un état stable (commitée).
   * Configuration : Entièrement interactif.

  4. Spécifications Techniques (Le "Comment")
   * Langage et Dépendances : Bash, git. Doit "sourcer" `_common.sh`.
   * Environnement d'Exécution : Tout environnement de type Unix (Linux, macOS, WSL).

  5. Cas d'Utilisation
   * Exemple d'Appel :

   1     # Se placer sur la branche main et s'assurer qu'elle est à jour
   2     git checkout main
   3     git pull
   4     # Lancer l'assistant de release
   5     ./scripts/release-version.sh