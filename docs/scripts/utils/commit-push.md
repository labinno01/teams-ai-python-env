1. Identification
   * ID de l'Exigence : GIT-REQ-003
   * Nom du Script : commit-push.sh
   * Version : Gérée par les tags Git (ex: v0.1.0)
   * Objectif (Raison d'être) : Simplifier et accélérer le processus quotidien de sauvegarde du travail en combinant les
     étapes d'indexation, de commit et de push en une seule commande.

  2. Description Fonctionnelle (Le "Quoi")
   * Déclencheur : Manuellement par le développeur lorsqu'il souhaite enregistrer et synchroniser ses modifications
     locales avec le dépôt distant.
   * Processus :
       1. Vérification du Contexte : Le script s'assure qu'il est bien exécuté à l'intérieur d'un dépôt Git.
       2. Vérification des Modifications : Il vérifie s'il y a des modifications à commiter (git status). S'il n'y en a
          aucune, il informe l'utilisateur et se termine proprement.
       3. Configuration Utilisateur : Il appelle la fonction check_git_config de _common.sh pour s'assurer que l'identité
          de l'utilisateur est configurée.
       4. Indexation : Il ajoute toutes les modifications actuelles (fichiers modifiés, nouveaux et supprimés) à l'index
          avec git add ..
       5. Message de Commit :
           * Si un argument est passé au script, il est utilisé comme message de commit.
           * Sinon, le script demande interactivement à l'utilisateur d'entrer un message de commit. Cette saisie est
             obligatoire.
       6. Commit : Il exécute git commit avec le message fourni.
       7. Push : Il exécute git push. Le script est conçu pour fonctionner sur une branche qui suit déjà une branche
          distante.
   * Résultat Attendu : Toutes les modifications du répertoire de travail sont commitées localement avec le message
     fourni, et ce nouveau commit est poussé vers la branche distante correspondante.

  3. Exigences Non-Fonctionnelles (Les "Contraintes")
   * Performance : L'exécution est rapide, la durée dépendant principalement du volume de données à pousser (git push).
   * Sécurité : Pas de contraintes de sécurité particulières.
   * Configuration : Aucune. Le script est autonome. Le message de commit peut être fourni soit de manière interactive,
     soit via un argument en ligne de commande.
   * Gestion des Erreurs :
       * Doit se terminer proprement s'il n'y a rien à commiter.
       * Doit échouer avec un message clair si la commande git commit ou git push échoue (par exemple, en cas de
         conflits ou si la branche locale ne suit aucune branche distante).

  4. Spécifications Techniques (Le "Comment")
   * Langage et Dépendances : Bash, git. Doit "sourcer" _common.sh.
   * Environnement d'Exécution : Tout environnement de type Unix (Linux, macOS, WSL).
   * Entrées / Sorties :
       * Arguments en ligne de commande : Optionnel. Une chaîne de caractères qui sera utilisée comme message de commit.
         (ex: ./commit-push.sh "feat: Ajouter une nouvelle fonctionnalité")
       * Sortie standard (stdout) : Retour d'information sur les étapes (indexation, commit, push) et leurs résultats.

  5. Cas d'Utilisation
   * Exemple d'Appel Interactif :

   1     ./scripts/commit-push.sh
   2     # Le script demandera le message de commit
   * Exemple d'Appel Non-Interactif :
   1     ./scripts/commit-push.sh "fix: Corriger un bug d'affichage sur le bouton principal"