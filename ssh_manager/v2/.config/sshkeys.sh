#!/bin/bash

# BUG: Un bug a été signalé sur l'option --log : aucun contenu n'est écrit dans le fichier log.

# ┌────────────────────────────────────────────┐
# │ SSH Key Manager v2.3                       │
# │ Gestion multi-clés SSH avec empreintes     │
# │ et configuration automatique de ~.ssh/config │
# └────────────────────────────────────────────┘

SSHKEYS_VERSION="2.3"
SSH_DIR="$HOME/.ssh"
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
  _log_rotate; _log_cleanup
  local msg; msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  mkdir -p "$(dirname "$LOG_FILE")"
  echo -e "$msg" >> "$LOG_FILE"
}

_info()    { echo -e "${BLUE}ℹ️  $*${NC}"; _log "INFO: $*"; }
_success() { echo -e "${GREEN}✅ $*${NC}"; _log "SUCCESS: $*"; }
_warn()    { echo -e "${YELLOW}⚠️  $*${NC}"; _log "WARNING: $*"; }
_error()   { echo -e "${RED}❌ $*${NC}"; _log "ERROR: $*"; }

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

_sshkeys_init() {
  if [[ -z "$SSH_AUTH_SOCK" ]]; then
    _error "Agent SSH non détecté (variable SSH_AUTH_SOCK vide)."
    _info "Veuillez démarrer l'agent avec : eval \$(ssh-agent -s)"
    return 1
  fi

  for key in "$@"; do
    local path="$SSH_DIR/$key"
    if [[ -f "$path" ]]; then
      if ssh-add "$path"; then
        _success "Clé '$key' chargée dans l'agent."
      else
        _error "Impossible de charger la clé '$key'."
      fi
    else
      _warn "Fichier de clé introuvable : $key"
    fi
  done
}

_sshkeys_reload() {
  if [[ -z "$SSH_AUTH_SOCK" ]]; then
    _error "Agent SSH non détecté."
    return 1
  fi
  _info "Vidage de toutes les clés de l'agent..."
  ssh-add -D
  _sshkeys_init "$@"
}

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

_sshkeys_debug() {
  _info "🔍 Debug SSH Agent"
  echo "Agent PID: $SSH_AGENT_PID"
  echo "Auth Sock: $SSH_AUTH_SOCK"
  ssh-add -l
  echo "Contenu de ~.ssh :"
  ls -l "$SSH_DIR"
}

_sshkeys_create() {
  local force_overwrite=false email_arg="" host_arg="" keys=()
  while (( "$#" )); do
    case "$1" in
      --force|-f) force_overwrite=true; shift ;;
      --email) email_arg="$2"; shift 2 ;;
      --host) host_arg="$2"; shift 2 ;;
      -*) _error "Option inconnue pour 'create': $1"; return 1 ;;
      *) keys+=("$1"); shift ;;
    esac
  done

  if [[ ${#keys[@]} -eq 0 ]]; then _error "'create' requiert un nom de clé."; return 1; fi

  for key in "${keys[@]}"; do
    local path="$SSH_DIR/$key"
    if [[ -f "$path" ]]; then
      if [[ "$force_overwrite" = true ]]; then
        _info "Option --force : écrasement de la clé '$key'."
      elif [[ -t 0 ]]; then
        local confirm; read -r -p "⚠️  Clé '$key' existante. La remplacer ? (Archivage de l'ancienne) [y/N]: " confirm
        if [[ ! "$confirm" =~ ^[Yy]$ ]]; then _info "Création annulée."; continue; fi
      else
        _error "Clé '$key' existante. Utilisez --force en mode non-interactif."; continue
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
    if [[ -z "$host" ]]; then host="${email%%@*}"; fi

    echo "DEBUG: Creating key $key at $path"
    if ssh-keygen -t ed25519 -f "$path" -C "$email" -N ""; then
      echo "DEBUG: ssh-keygen exit code: $?"
      _success "Clé '$key' créée."
      _info "Empreinte de la clé : $(ssh-keygen -l -f "$path.pub")"
      if ssh-add "$path"; then _success "Clé chargée dans l'agent."; else _warn "Impossible de charger la clé '$key' dans l'agent."; fi
      _ssh_config_update "add" "$key" "$host" "$path"
      if [[ -t 0 ]]; then echo -e "\n${YELLOW}Clé publique pour ${host}:${NC}"; cat "$path.pub"; echo; fi
    else
      echo "DEBUG: ssh-keygen exit code: $?"
      _error "La création de la clé '$key' a échoué."
    fi
  done
}

_sshkeys_delete() {
  for key in "$@"; do
    local path="$SSH_DIR/$key"
    if [[ ! -f "$path" ]]; then _warn "Clé introuvable: $key"; continue; fi
    if rm -f "$path" "$path.pub"; then
      _success "Fichiers de la clé '$key' supprimés."
      if ssh-add -d "$path"; then _success "Clé déchargée de l'agent."; else _warn "Impossible de décharger la clé '$key' de l'agent."; fi
      _ssh_config_update "delete" "$key"
    else
      _error "Impossible de supprimer les fichiers de la clé '$key'."
    
    fi
  done
}

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
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
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
    *)        _error "Commande inconnue : '$1'"; echo -e "Utilisez '${BLUE}sshkeys help${NC}' pour l’aide."
  esac
fi
