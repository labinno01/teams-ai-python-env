# menu.ps1

. "$PSScriptRoot\scripts\chat_utils.ps1"



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
        Display-Chat -PSScriptRoot $PSScriptRoot

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
