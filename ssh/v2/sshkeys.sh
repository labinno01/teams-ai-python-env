#!/bin/bash



# ┌────────────────────────────────────────────┐
# │ SSH Key Manager v2.3                       │
# │ Gestion multi-clés SSH avec empreintes     │
# │ et configuration automatique de ~.ssh/config │
# └────────────────────────────────────────────┘

# ─── Global Variables ─────────────────────────
SSHKEYS_VERSION="2.5.1"
SSH_DIR="${SSH_DIR:-$HOME/.ssh}"
SSHKEYS_CONFIG_FILE="$HOME/.config/sshkeys.conf"
_LOGGING_ENABLED=false # Global flag for logging

# Load configuration from file if it exists
if [[ -f "$SSHKEYS_CONFIG_FILE" ]]; then
  source "$SSHKEYS_CONFIG_FILE"
fi
# --- Configuration des Logs ---
LOG_FILE="${SSHKEYS_LOG_FILE:-$(dirname "${BASH_SOURCE[0]}")/load_ssh_keys.log}"
LOG_MAX_SIZE=$((1024 * 1024)) # 1 Mo
LOG_ARCHIVE_DAYS=7

# ─── Couleurs ─────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ─── Logging & Helpers ────────────────────────

# ─── Logging & Helpers ────────────────────────

_log_rotate() {
  if [[ ! -f "$LOG_FILE" ]] || [[ ! -s "$LOG_FILE" ]]; then return; fi
  local current_size; current_size=$(wc -c <"$LOG_FILE")
  if (( current_size > LOG_MAX_SIZE )); then
    local timestamp; timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
    local archive_path="${LOG_FILE}.${timestamp}.gz"
    gzip -c "$LOG_FILE" > "$archive_path" && true > "$LOG_FILE"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] INFO: Log rotated to ${archive_path}" >> "$LOG_FILE"
  fi
}

_log_cleanup() {
  find "$(dirname "$LOG_FILE")" -name "$(basename "$LOG_FILE").*.gz" -mtime "+$LOG_ARCHIVE_DAYS" -delete &>/dev/null
}

_log() {
  if [[ "$_LOGGING_ENABLED" = true ]]; then # Only log to file if enabled
    _log_rotate; _log_cleanup
    local msg; msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
    mkdir -p "$(dirname "$LOG_FILE")"
    echo -e "$msg" >> "$LOG_FILE"
  fi
}

_info()    { echo -e "${BLUE}ℹ️  $*${NC}"; _log "INFO: $*"; }
_success() { echo -e "${GREEN}✅ $*${NC}"; _log "SUCCESS: $*"; }
_warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; _log "WARNING: $*"; }
_error()   { echo -e "${RED}❌ $*${NC}"; _log "ERROR: $*"; }

_die() {
  _error "$*"
  exit 1
}

# ─── SSH Config Management ────────────────────

# ─── SSH Config Management ────────────────────

_ssh_config_update() {
  local action="$1"
  local key_name="$2"
  local host_alias="$3"
  local key_path="$4"
  local config_file="$SSH_DIR/config"
  local start_marker="# BEGIN SSHKEYS BLOCK FOR KEY: ${key_name}"
  local end_marker="# END SSHKEYS BLOCK FOR KEY: ${key_name}"

  touch "$config_file"

  # Remove existing block to ensure idempotency
  if grep -q -F "$start_marker" "$config_file"; then
    local temp_file; temp_file=$(mktemp)
    awk -v start="$start_marker" -v end="$end_marker" ' 
      $0 == start {p=1} !p; $0 == end {p=0}
    ' "$config_file" > "$temp_file" && mv "$temp_file" "$config_file"
  fi

  if [[ "$action" == "add" ]]; then
    echo -e "\n$start_marker
Host ${host_alias}
  HostName ${host_alias} # Defaulting HostName to Host alias
  User git
  IdentityFile ${key_path}
  IdentitiesOnly yes
$end_marker" >> "$config_file"
    _info "Fichier ~.ssh/config mis à jour pour l'hôte '${host_alias}'"
  fi
}

# ─── Core Commands ─────────────────────────────

# ─── Core Commands ─────────────────────────────

# --- init ---
_sshkeys_init() {
  if [[ -z "$SSH_AUTH_SOCK" ]]; then
    _info "Agent SSH non détecté. Tentative de démarrage..."
    local agent_output
    agent_output=$(ssh-agent -s 2>/dev/null)
    if [[ -n "$agent_output" ]]; then
      eval "$agent_output"
      _success "Agent SSH démarré."
      _info "Pour que l'agent persiste dans votre session, veuillez exécuter la commande suivante dans votre terminal :"
      _info "eval \n$(ssh-agent -s)"
    else
      _die "Impossible de démarrer l'agent SSH. Veuillez le démarrer manuellement avec : eval $(ssh-agent -s)"
    fi
  fi

  for key in "$@"; do
    local path="$SSH_DIR/$key"
    if [[ -f "$path" ]]; then
      # Check if key is encrypted
      if ssh-keygen -y -P "" -f "$path" &>/dev/null;
      then
        # Key is not encrypted, or passphrase is empty. Attempt to add.
        if ssh-add "$path"; then
          _success "Clé '$key' chargée dans l'agent."
        else
          _error "Impossible de charger la clé '$key'. Veuillez vérifier l'agent SSH."
        fi
      else
        # Key is encrypted. Inform user to add manually.
        _warn "La clé '$key' est chiffrée. Veuillez la charger manuellement dans l'agent SSH avec : ssh-add $path"
      fi
    else
      _warn "Fichier de clé introuvable : $key"
    fi
  done
}

# --- reload ---
_sshkeys_reload() {
  if [[ -z "$SSH_AUTH_SOCK" ]]; then
    _die "Agent SSH non détecté."
  fi
  _info "Vidage de toutes les clés de l'agent..."
  ssh-add -D
  _sshkeys_init "$@"
}

# --- status ---
_sshkeys_status() {
  if ! ssh-add -l &>/dev/null; then
    _info "Agent SSH en cours d'exécution mais aucune clé n'est chargée."
    return
  fi
  _info "Clés actuellement chargées dans l'agent :"
  ssh-add -l | while read -r line; do
    local type; type=$(echo "$line" | awk '{print $1}')
    local fp; fp=$(echo "$line" | awk '{print $2}')
    local comment; comment=$(echo "$line" | awk '{print $3}')
    echo -e "${GREEN}🔐 $comment${NC} → ${BLUE}$fp${NC} [$type]"
  done
}

# --- debug ---
_sshkeys_debug() {
  _info "🔍 Debug SSH Agent"
  echo "Agent PID: $SSH_AGENT_PID"
  echo "Auth Sock: $SSH_AUTH_SOCK"
  ssh-add -l
  echo "Contenu de ~.ssh :"
  ls -l "$SSH_DIR"
}

# --- create ---
_sshkeys_create() {
  local force_overwrite=false email_arg="" host_arg="" keys=()
  local passphrase_arg="" # New variable for passphrase
  while (( "$#" )); do
    case "$1" in
      --force|-f) force_overwrite=true; shift ;;
      --email) email_arg="$2"; shift 2 ;;
      --host) host_arg="$2"; shift 2 ;;
      --passphrase|-P) passphrase_arg="true"; shift ;; # Handle new passphrase option
      -*) _die "Option inconnue pour 'create': $1" ;;
      *) keys+=("$1"); shift ;;
    esac
  done

  if [[ ${#keys[@]} -eq 0 ]]; then _die "'create' requiert un nom de clé."; fi

  for key in "${keys[@]}"; do
    # Input Validation: Valid characters
    if ! [[ "$key" =~ ^[a-zA-Z0-9_-]+$ ]]; then
      _die "Nom de clé invalide : '$key'. Le nom doit contenir uniquement des caractères alphanumériques, des tirets (-) ou des underscores (_)."
    fi

    # Input Validation: Reserved names
    local lower_key; lower_key=$(echo "$key" | tr '[:upper:]' '[:lower:]')
    if [[ "$lower_key" == "config" ]] || [[ "$lower_key" == "known_hosts" ]]; then
      _die "Nom de clé réservé : '$key'. Les noms 'config' et 'known_hosts' ne sont pas autorisés."
    fi

    local path="$SSH_DIR/$key"
    if [[ -f "$path" ]]; then
      if [[ "$force_overwrite" = true ]]; then
        _info "Option --force : écrasement de la clé '$key'."
      elif [[ -t 0 ]]; then
        local confirm; read -r -p "⚠️  Clé '$key' existante. La remplacer ? (Archivage de l'ancienne) [y/N]: " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then _info "Création annulée."; continue; fi
      else
        _die "Clé '$key' existante. Utilisez --force en mode non-interactif."
      fi
      local ts; ts=$(date '+%Y%m%d-%H%M%S'); mv "$path" "${path}.${ts}.bak"; mv "$path.pub" "${path}.pub.${ts}.bak"
      _success "Ancienne clé '$key' archivée."
    fi

    local email; email="$email_arg"
    if [[ -z "$email" ]] && [[ -t 0 ]]; then
      local default_email="${key}@teams.ai"; read -r -p "Email pour le commentaire [${default_email}]: " email
      email="${email:-$default_email}"
    elif [[ -z "$email" ]]; then
      email="${key}@teams.ai"
    fi

    local host; host="$host_arg"
    # Better default host alias logic
    if [[ -z "$host" ]]; then
      if [[ -n "$email" ]]; then
        host="${email%%@*}" # Use part before @ from email if email is provided
      else
        host="$key" # Fallback to key name if no email
      fi
    fi

    local passphrase="" # Initialize passphrase to empty
    if [[ "$passphrase_arg" == "true" ]]; then
      if [[ -t 0 ]]; then # Check if running in interactive terminal
        read -r -s -p "Entrez la phrase secrète pour la clé '$key' (laissez vide pour aucune) : " passphrase_input
        
        passphrase="$passphrase_input" # Set passphrase variable
      else
        _die "L'option --passphrase requiert un terminal interactif."
      fi
    fi

    

    echo "DEBUG: Creating key $key at $path"

    local askpass_script; askpass_script=$(mktemp)
    chmod +x "$askpass_script"
    echo -e "#!/bin/bash\necho \"$passphrase\"" > "$askpass_script"

    SSH_ASKPASS="$askpass_script" DISPLAY=:0.0 ssh-keygen -t ed25519 -f "$path" -C "$email" # Let ssh-keygen use SSH_ASKPASS
    local ssh_keygen_exit_code=$?

    rm -f "$askpass_script" # Clean up temp script
    unset SSH_ASKPASS # Unset environment variable

    if [[ "$ssh_keygen_exit_code" -eq 0 ]]; then
      echo "DEBUG: ssh-keygen exit code: $ssh_keygen_exit_code"
      _success "Clé '$key' créée."
      _info "Empreinte de la clé : $(ssh-keygen -l -f "$path.pub")"

      if [[ "$passphrase_arg" == "true" ]]; then
        _info "La clé '$key' a été créée avec une phrase secrète. Vous devrez la saisir manuellement pour la charger dans l'agent SSH."
        _warn "Impossible de charger la clé '$key' automatiquement dans l'agent. Veuillez l'ajouter manuellement avec : ssh-add $path"
      elif ssh-add "$path"; then # Only attempt to add if no passphrase was specified during creation
        _success "Clé chargée dans l'agent."
      else
        _error "Impossible de charger la clé '$key' dans l'agent. Veuillez vérifier l'agent SSH."
      fi
      _ssh_config_update "add" "$key" "$host" "$path"
      if [[ -t 0 ]]; then echo -e "\n${YELLOW}Clé publique pour ${host}:${NC}"; cat "$path.pub"; echo; fi
    else
      echo "DEBUG: ssh-keygen exit code: $ssh_keygen_exit_code"
      _die "La création de la clé '$key' a échoué."
    fi
  done
}


# --- delete ---
_sshkeys_delete() {
  for key in "$@"; do
    local path="$SSH_DIR/$key"
    if [[ ! -f "$path" ]]; then _warn "Clé introuvable: $key"; continue; fi

    # Attempt to remove all instances of the key from the agent
    local key_removed_from_agent=false
    # Get all loaded keys and filter for the one being deleted
    local loaded_keys; loaded_keys=$(ssh-add -l 2>/dev/null | grep "$key")
    if [[ -n "$loaded_keys" ]]; then
      # Iterate through each line (each loaded key)
      echo "$loaded_keys" | while read -r line; do
        # Extract the fingerprint and comment (which often contains the path or name)
        local fingerprint=$(echo "$line" | awk '{print $2}')
        local comment=$(echo "$line" | awk '{print $3}')

        # If the comment matches the key name, try to remove it by path
        if [[ "$comment" == *"$key"* ]]; then
          if ssh-add -d "$path" &>/dev/null; then
            key_removed_from_agent=true
          fi
        fi
      done
    fi

    if [[ "$key_removed_from_agent" = true ]]; then
      _success "Clé déchargée de l'agent."
    else
      true # No operation, just to have a command in else branch
    fi

    # Then delete files
    if rm -f "$path" "$path.pub"; then
      _success "Fichiers de la clé '$key' supprimés."
      _ssh_config_update "delete" "$key"
    else
      _die "Impossible de supprimer les fichiers de la clé '$key'."
    fi
  done
}

# --- list ---
_sshkeys_list() {
  _info "📂 Clés privées trouvées dans ~.ssh :"
  for f in "$SSH_DIR"/*;
  do
    if [[ -f "$f" ]] && ! [[ "$f" == *.pub ]]; then
      local filename; filename=$(basename "$f")
      if [[ "$filename" != "known_hosts" ]] && [[ "$filename" != "config" ]]; then
        echo "$filename"
        if [[ -f "$f.pub" ]]; then
          _info "  Empreinte : $(ssh-keygen -l -f "$f.pub")"
        else
          _warn "  Fichier public manquant pour $filename"
        fi
      fi
    fi
  done
}

# --- help ---
_sshkeys_help() {
  cat <<EOF
${BLUE}SSH Key Manager v$SSHKEYS_VERSION${NC}
Gestionnaire de clés SSH qui automatise la création, le chargement et la configuration.

${YELLOW}Usage :${NC} sshkeys <commande> [arguments]

${YELLOW}Commandes principales :${NC}
  ${GREEN}create <nom_clés> [--host <hote>] [--email <email>] [--force]${NC}
    Crée une clé, la charge et met à jour ~.ssh/config.
    --host:   Nom d'hôte pour le fichier config (défaut: déduit de l'email).
    --email:  Email pour le commentaire de la clé (défaut: interactif).
    --force:  Écrase une clé existante sans demander.

  ${GREEN}delete <nom_clés>${NC}
    Supprime une clé, la décharge et nettoie ~.ssh/config.

  ${GREEN}init <nom_clés>${NC}
    Charge des clés spécifiées dans l'agent SSH.

  ${GREEN}reload <nom_clés>${NC}
    Décharge toutes les clés, puis charge celles spécifiées.

${YELLOW}Autres commandes :${NC}
  ${GREEN}status${NC}           → Affiche les clés actuellement chargées dans l'agent.
  ${GREEN}list${NC}             → Liste les fichiers de clés privées trouvées dans ~.ssh.
  ${GREEN}debug${NC}            → Affiche des informations de débogage sur l'agent.
  ${GREEN}version${NC}          → Affiche la version du script.
  ${GREEN}help, -h, --help${NC} → Affiche cette aide.

${YELLOW}Prérequis :${NC}
  L'agent SSH doit être démarré dans votre session.
  Exécutez ${BLUE}eval \$(ssh-agent -s)${NC} si ce n'est pas déjà fait.
EOF
}

# ─── Main Entrypoint ───────────────────────────
# ─── Main Entrypoint ───────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  # Argument parsing for global options
  cmd_args=() # Use a different name to avoid confusion with global args
  while (( "$#" )); do
    case "$1" in
      --log) _LOGGING_ENABLED=true; shift ;;
      *) cmd_args+=("$1"); shift ;;
    esac
  done
  set -- "${cmd_args[@]}" # Restore positional parameters without global options

  case "$1" in
    init)     shift; _sshkeys_init "$@" ;;
    reload)   shift; _sshkeys_reload "$@" ;;
    status)   _sshkeys_status ;;
    debug)    _sshkeys_debug ;;
    create)   shift; _sshkeys_create "$@" ;;
    delete)   shift; _sshkeys_delete "$@" ;;
    list)     _sshkeys_list ;;
    help|-h|--help) _sshkeys_help ;;
    version)  echo "SSH Key Manager v$SSHKEYS_VERSION" ;;
    *)        _die "Commande inconnue : '$1'"; echo -e "Utilisez '${BLUE}sshkeys help${NC}' pour l’aide."
  esac
fi
