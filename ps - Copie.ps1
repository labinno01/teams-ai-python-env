# ps.ps1 – Script principal
. "$PSScriptRoot\env.ps1"
. "$PSScriptRoot\config.ps1"
. "$PSScriptRoot\run.ps1"
. "$PSScriptRoot\aliases.ps1" # Ajout des alias
. "$PSScriptRoot\menu.ps1"



# Définir les alias après avoir sourcé les fonctions
Define-Aliases

# Afficher le menu principal
MainMenu
