1. Identification
   * ID de l'Exigence : GIT-REQ-004
   * Nom du Script : sync-remote.sh
   * Version : Gérée par les tags Git (ex: v0.1.0)
   * Objectif (Raison d'être) : Fournir un moyen sûr de synchroniser la branche de travail locale avec son équivalent sur le dépôt distant, en privilégiant la sécurité et la clarté sur l'état du dépôt.

  2. Description Fonctionnelle (Le "Quoi")
   * Déclencheur : Manuellement par le développeur, avant de commencer à travailler ou lorsqu'il souhaite récupérer les dernières mises à jour.
   * Processus :
       1. Vérification du Contexte : Le script s'assure qu'il est bien exécuté à l'intérieur d'un dépôt Git.
       2. Récupération des Données : Il exécute `git fetch` pour télécharger les dernières informations du remote sans modifier la copie de travail locale.
       3. Analyse de l'État : Il compare la branche locale (HEAD) avec la branche distante suivie.
       4. Scénarios de Synchronisation :
           * **À jour :** Si les deux branches sont identiques, il informe l'utilisateur que tout est synchronisé et se termine.
           * **En retard :** Si la branche distante a de nouveaux commits, il affiche ces commits et demande à l'utilisateur s'il souhaite les intégrer via `git pull --ff-only`. Cette commande ne fonctionne que si la branche locale n'a pas de nouveaux commits de son côté (avance rapide), ce qui évite les merges automatiques non désirés.
           * **En avance :** Si la branche locale a des commits qui ne sont pas sur la branche distante, il en informe l'utilisateur et lui suggère d'utiliser `commit-push.sh`.
           * **Divergence :** Si les deux branches ont des commits que l'autre n'a pas, il informe l'utilisateur qu'un merge ou un rebase manuel est nécessaire pour résoudre le conflit.
   * Résultat Attendu : La branche locale est mise à jour avec les changements du distant si et seulement si cela peut être fait de manière "fast-forward" (sans conflit de merge).

  3. Exigences Non-Fonctionnelles (Les "Contraintes")
   * Performance : Rapide, limitée par la vitesse de la connexion réseau pour `git fetch`.
   * Sécurité : En utilisant `git pull --ff-only`, le script évite de créer des commits de merge inattendus, laissant à l'utilisateur le contrôle total en cas de branches divergentes.
   * Configuration : Aucune. Le script est entièrement interactif.
   * Gestion des Erreurs : Échoue proprement si `git fetch` ne fonctionne pas ou si le `pull` ne peut pas être effectué en avance rapide.

  4. Spécifications Techniques (Le "Comment")
   * Langage et Dépendances : Bash, git. Doit "sourcer" `_common.sh`.
   * Environnement d'Exécution : Tout environnement de type Unix (Linux, macOS, WSL).
   * Entrées / Sorties :
       * Arguments en ligne de commande : Aucun.
       * Sortie standard (stdout) : Informations claires sur l'état de synchronisation et guidage interactif.

  5. Cas d'Utilisation
   * Exemple d'Appel :

   1     # Se placer dans le projet
   2     cd ~/projets/mon-projet
   3     # Lancer la synchronisation
   4     /chemin/vers/les/scripts/sync-remote.sh