1. Identification
   * ID de l'Exigence : GIT-REQ-002
   * Nom du Script : init-repository.sh
   * Version : Gérée par les tags Git (ex: v0.1.0)
   * Objectif (Raison d'être) : Assister l'utilisateur dans l'initialisation complète d'un nouveau dépôt Git local, en
     le liant à un dépôt distant et en créant un premier commit propre.

  2. Description Fonctionnelle (Le "Quoi")
   * Déclencheur : Manuellement par le développeur, dans le dossier racine d'un projet qui n'est pas encore un dépôt Git.
   * Processus :
       1. Vérification Initiale : Le script vérifie d'abord si un dossier .git existe déjà. Si c'est le cas, il informe
          l'utilisateur que le dépôt est déjà initialisé et se termine.
       2. Initialisation : Exécute git init pour créer le dépôt local.
       3. Configuration Utilisateur : Vérifie si user.name et user.email sont configurés localement. Si non, il demande à
          l'utilisateur de les saisir (en utilisant la fonction check_git_config de _common.sh).
       4. Demande du Distant : Demande à l'utilisateur de fournir l'URL SSH du dépôt distant (ex:
          git@github.com:user/repo.git).
       5. Ajout du Distant : Exécute git remote add origin <URL_fournie>.
       6. Création du README : Crée un fichier README.md avec le nom du dossier du projet comme titre, pour s'assurer que
          le premier commit ne soit pas vide.
       7. Indexation : Ajoute tous les fichiers à l'index avec git add ..
       8. Message de Commit : Demande à l'utilisateur un message pour le commit initial, en proposant "feat: Initial
          commit" comme valeur par défaut.
       9. Commit Initial : Exécute git commit avec le message fourni.
       10. Push Initial (Optionnel) : Demande à l'utilisateur s'il souhaite pousser la branche main vers origin. Si oui,
           exécute git push -u origin main.
   * Résultat Attendu : Le dossier courant est un dépôt Git fonctionnel, avec un remote nommé origin configuré, un fichier
     README.md, et un premier commit créé. La branche main est potentiellement déjà synchronisée avec le dépôt distant.



  3. Exigences Non-Fonctionnelles (Les "Contraintes")
   * Performance : L'exécution doit être rapide, limitée principalement par le temps de réponse de l'utilisateur aux
     questions.
   * Sécurité : Aucune information sensible n'est stockée ou affichée.
   * Configuration : Le script est entièrement interactif et ne nécessite aucun fichier de configuration.
   * Gestion des Erreurs : Chaque commande git critique (init, remote add, commit, push) doit être vérifiée. En cas
     d'échec, le script doit afficher un message d'erreur clair et s'arrêter.

  4. Spécifications Techniques (Le "Comment")
   * Langage et Dépendances : Bash, git. Le script doit "sourcer" _common.sh pour les fonctions utilitaires.
   * Environnement d'Exécution : Tout environnement de type Unix (Linux, macOS, WSL).
   * Entrées / Sorties :
       * Arguments en ligne de commande : Aucun.
       * Sortie standard (stdout) : Messages de guidage pour l'assistant interactif et retours d'information sur les
         commandes exécutées.

  5. Cas d'Utilisation
   * Exemple d'Appel :

   1     # Se placer dans le nouveau projet
   2     cd ~/projets/mon-nouveau-site
   3     # Lancer l'assistant
   4     /chemin/vers/les/scripts/init-repository.sh

  Processus (mis à jour) :
   1. Vérification Initiale : ... (inchangé)
   2. Initialisation : Exécute git init.
   3. Configuration Utilisateur : ... (inchangé)
   4. Demande du Distant : Demande à l'utilisateur de fournir l'URL SSH du dépôt distant.
   5. Vérification du Distant (Nouvelle Étape) :
       * Le script exécute git ls-remote <URL_fournie> en silence.
       * Si la commande réussit (code de sortie 0), cela signifie que le dépôt existe.
       * Le script affiche alors un message d'avertissement et demande à l'utilisateur s'il souhaite continuer.
       * Si l'utilisateur ne confirme pas explicitement, le script s'arrête avec un message expliquant qu'il devrait
         peut-être utiliser git clone.
   6. Ajout du Distant : Exécute git remote add origin <URL_fournie>.
   7. Création du README : ... (anciennement 6)
   8. Indexation : ... (anciennement 7)
   9. Message de Commit : ... (anciennement 8)
   10. Commit Initial : ... (anciennement 9)
   11. Push Initial (Optionnel) : ... (anciennement 10)