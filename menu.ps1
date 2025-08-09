# menu.ps1

function Wrap-Text {
    param(
        [string]$Text,
        [int]$Width
    )
    $lines = @()
    $words = $Text.Split(' ')
    $currentLine = ""
    foreach ($word in $words) {
        if (($currentLine.Length + $word.Length + 1) -gt $Width) {
            $lines += $currentLine.Trim()
            $currentLine = $word
        } else {
            $currentLine += " " + $word
        }
    }
    $lines += $currentLine.Trim()
    return $lines
}

function MainMenu {
    (Get-Random -SetSeed (Get-Random)) | Out-Null # Ensure random is re-seeded for each menu display
    do {
        $projectName = Split-Path -Leaf $PSScriptRoot
        $config = Load-PythonEnvConfig
        $displayProjectName = if (-not [string]::IsNullOrEmpty($config.wsl_project_dir)) { $config.wsl_project_dir } else { $projectName }
        # --- Titre ---
        Write-Host "`n╔═════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
        Write-Host "║       Gestion des parametres de lancement de wsl            ║" -ForegroundColor Cyan
        Write-Host "╚═════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

        # --- Affichage du chat ---
        $currentDate = Get-Date
        $time = "Il est $((Get-Date).ToString('HH:mm'))"
        $hour = (Get-Date).Hour # Get hour for time-based message

        # Determine time-based message
        if (($hour -ge 22) -or ($hour -lt 6)) {
            $cat_msg_time = "Le chat dort... Bonne nuit !"
        } elseif ($hour -lt 9) {
            $cat_msg_time = "Pret pour la journee ?"
        } elseif ($hour -lt 12) {
            $cat_msg_time = "Belle matinee !"
        } elseif ($hour -lt 14) {
            $cat_msg_time = "Bon appetit !"
        } elseif ($hour -lt 18) {
            $cat_msg_time = "Bon apres-midi !"
        } else {
            $cat_msg_time = "Bonsoir !"
        }

        # ANSI color codes for PowerShell
        $COLOR_RESET = "`e[0m"
        $COLOR_RED = "`e[91m"
        $COLOR_GREEN = "`e[92m"
        $COLOR_YELLOW = "`e[93m"
        $COLOR_BLUE = "`e[94m"
        $COLOR_MAGENTA = "`e[95m"
        $COLOR_CYAN = "`e[96m"
        $colors = @($COLOR_RED, $COLOR_GREEN, $COLOR_YELLOW, $COLOR_BLUE, $COLOR_MAGENTA, $COLOR_CYAN)

        if ($currentDate.Month -eq 8 -and $currentDate.Day -eq 8) {
            # Special Cat Day logic
            $chatJsonPath = Join-Path -Path $PSScriptRoot -ChildPath "scripts\chat.json"
            $anecdote = "Une anecdote sur les chats (fichier chat.json manquant ou invalide)."
            if (Test-Path $chatJsonPath) {
                try {
                    $anecdotes = (Get-Content $chatJsonPath | ConvertFrom-Json)
                    if ($anecdotes.Count -gt 0) {
                        $anecdote = $anecdotes | Get-Random
                    }
                } catch {
                    # Handle JSON parsing error
                }
            }

            $random_color = $colors | Get-Random
            $cat_msg_line1 = "Aujourd'hui c'est le 8 aout, c'est ma fete !"
            $cat_face = "( ^.^ )"

            $wrappedAnecdote = Wrap-Text -Text $anecdote -Width 68 # Adjust width as needed
            $anecdoteLine1 = $wrappedAnecdote[0]
            $anecdoteLine2 = if ($wrappedAnecdote.Count -gt 1) { $wrappedAnecdote[1] } else { "" }

            $cat = @"
${random_color}
     /\_/\    ${cat_msg_line1}
    ${cat_face}   ${anecdoteLine1}
     > ^ <    ${anecdoteLine2}
              (${time}) ${cat_msg_time}
${COLOR_RESET}
"@
        } else {
            # Existing time-based chat logic
            $cat_face = "( -.- )" # Default cat face for regular days
            if (($hour -ge 22) -or ($hour -lt 6)) {
                $cat_face = "( -.- ) zZz"
            }
            $cat = @"
     /\_/\    ${cat_msg_time}
    ${cat_face}   (${time})
     > ^ <
"@
        }
        Write-Host $cat
        
        # --- Fin du chat ---

        # --- Options du menu ---
        Write-Host "`n1) Afficher les détails de l’environnement Python"
        Write-Host "2) Lister les modules pip installés"
        Write-Host "3) Exécuter un script Python"
        Write-Host "4) Gérer la configuration de l'environnement Python"
        
        Write-Host "5) Lancer WSL dans le répertoire du projet ($displayProjectName)"
        Write-Host "6) Lancer le menu de gestion des environnements Python"
        Write-Host "7) Afficher les alias disponibles"
        Write-Host "8) Afficher les raccourcis Tmux/Byobu"
        Write-Host "9) Définir le répertoire de projet WSL"
        Write-Host "0) Quitter"
        Write-Host ""

        $choice = Read-Host "👉 Choisis une option"

        switch ($choice) {
            '1' {
                Show-PythonEnvDetails
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '2' {
                Show-PipModules
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '3' {
                $scriptName = Read-Host "📄 Nom du script (défaut: hello.py)"
                if ([string]::IsNullOrWhiteSpace($scriptName)) {
                    $scriptName = "hello.py"
                }
                $args = Read-Host "📦 Arguments (séparés par des espaces)"
                $argArray = $args.Split(' ', [System.StringSplitOptions]::RemoveEmptyEntries)
                Run-PythonScript -scriptName $scriptName -scriptArgs $argArray
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '4' {
                Manage-PythonEnvConfig
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            
            '5' {
                # Sub-menu for screen configuration
                Write-Host "`n🖥️  Quelle configuration d'écran pour WSL ?" -ForegroundColor Cyan
                Write-Host "  1) Défaut (lancer WSL sans tmux)"
                Write-Host "  2) Tmux (lancer WSL avec l'alias 'tmuxg')"
                Write-Host "  3) Byobu (lancer WSL avec l'alias 'byobug')"
                $screenChoice = Read-Host "👉 Choisis une option (défaut: 1)"

                $screenMode = "default"
                switch ($screenChoice) {
                    '2' { $screenMode = "tmux" }
                    '3' { $screenMode = "byobu" }
                }

                $distribution = Read-Host "🐧 Nom de la distribution WSL (laisser vide pour défaut)"
                $name = Read-Host "👤 Nom d'utilisateur (laisser vide pour défaut)"
                Launch-WSL -distribution $distribution -name $name -screenMode $screenMode
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '6' {
                Launch-PythonMenu
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '7' {
                Show-Aliases
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '8' {
                Show-TmuxByobuShortcuts
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '9' {
                Set-WSLProjectDirectory
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
            '0' {
                Write-Host "`n👋 À bientôt Frédéric ! Pour relancer le menu, tapez 'run'." -ForegroundColor Green
            }
            default {
                Write-Host "❌ Option invalide." -ForegroundColor Red
                Write-Host -NoNewline 'Press Enter to continue...'; $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            }
        }
    } while ($choice -ne '0')
}