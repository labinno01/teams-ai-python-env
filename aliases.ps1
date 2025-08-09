# aliases.ps1
. "$PSScriptRoot\config.ps1"

if (-not (Get-Command Load-PythonEnvConfig -ErrorAction SilentlyContinue)) {
    function Get-EnvConfigPath {
        $configDir = "$HOME\.config\ps"
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir | Out-Null
        }
        return "$configDir\python_env.json"
    }

    function Load-PythonEnvConfig {
        $configPath = Get-EnvConfigPath
        
        $content = Get-Content $configPath -Raw -ErrorAction SilentlyContinue
        
        $config = $null
        if (-not [string]::IsNullOrWhiteSpace($content)) {
            $config = $content | ConvertFrom-Json -ErrorAction SilentlyContinue
        }

        if ($null -eq $config) {
            $config = [PSCustomObject]@{ }
        }

        if (-not $config.PSObject.Properties['selected_env']) {
            Add-Member -InputObject $config -MemberType NoteProperty -Name 'selected_env' -Value $null
        }
        if (-not $config.PSObject.Properties['wsl_project_dir']) {
            Add-Member -InputObject $config -MemberType NoteProperty -Name 'wsl_project_dir' -Value $null
        }

        return $config
    }
}

function Define-Aliases {
    Set-Alias pipall Show-PipModules
    Set-Alias runenv Run-PythonScript
    Set-Alias editenv Edit-PythonEnvConfig
    Set-Alias tmuxg Launch-TmuxWSL
    Set-Alias byobug Launch-TmuxWSL # Ajout de l'alias byobug
    Set-Alias launchwsl Launch-WSL
    Set-Alias showaliases Show-Aliases
    Set-Alias pymenu Launch-PythonMenu
}

function Show-Aliases {
    Write-Host "`n📜 Alias disponibles :"
    Write-Host "  pipall        → Affiche les modules pip/pipx installés"
    Write-Host "  runenv        → Exécute un script Python dans l'environnement actif"
    Write-Host "  editenv       → Ouvre le fichier de configuration JSON de l'environnement"
    Write-Host "  tmuxg/byobug  → Lance une session tmux/byobu avec Gemini"
    Write-Host "  launchwsl     → Lance WSL (avec options : défaut, tmux, byobu)"
    Write-Host "  pymenu        → Lance le menu de gestion d'environnement Python dans WSL"
    Write-Host "  showaliases   → Affiche cette liste"
}

function Convert-WindowsPathToWslPath {
    param (
        [string]$windowsPath
    )
    $wslPath = $windowsPath.Replace("C:", "/mnt/c").Replace("\", "/")
    return $wslPath
}

function Launch-WSL {
    param(
        [string]$distribution,
        [string]$name,
        [string]$screenMode = "default" # New parameter
    )
    Write-Host "🚀 Lancement de WSL dans le répertoire du projet..." -ForegroundColor Cyan

    $config = Load-PythonEnvConfig # Load the configuration
    # Determine the target directory in WSL
    $targetDir = if (-not [string]::IsNullOrEmpty($config.wsl_project_dir)) {
        $config.wsl_project_dir
    } else {
        # Use the global variable which is the calculated WSL path of the script root
        $global:WslScriptRoot
    }

    # Prepare arguments for wsl.exe
    $argList = New-Object System.Collections.Generic.List[string]

    if (-not [string]::IsNullOrEmpty($distribution)) {
        $argList.Add("--distribution")
        $argList.Add($distribution)
    }
    if (-not [string]::IsNullOrEmpty($name)) {
        $argList.Add("--user")
        $argList.Add($name)
    }

    # Set the starting directory for WSL
    $argList.Add("--cd")
    $argList.Add($targetDir)

    # Determine the command to execute inside WSL and add it to the arguments
    switch ($screenMode) {
        'tmux' {
            # bash -ic ensures .bashrc is sourced so the 'tmuxg' alias is available
            $argList.Add("-e")
            $argList.Add("bash -ic tmuxg")
        }
        'byobu' {
            # Launch byobu directly
            $argList.Add("-e")
            $argList.Add("byobu")
        }
        default {
            # For the default case, we don't add any command (-e),
            # so WSL will start its default interactive shell.
        }
    }

    # Launch WSL in a new window
    Start-Process -FilePath "wsl.exe" -ArgumentList $argList
}

function Launch-PythonMenu {
    Write-Host "🚀 Lancement du menu Python dans WSL..." -ForegroundColor Cyan
    $pythonScriptPath = "$global:WslScriptRoot/scripts/python_menu.py"
    wsl.exe -e python3 "$pythonScriptPath"
}

function Launch-TmuxWSL {
    $session = "gemini_session"

    # Vérifier si la session tmux existe déjà
    wsl.exe -e bash -c "tmux has-session -t $session 2>/dev/null"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "🔄 Session tmux '$session' existante. Attachement via Byobu..." -ForegroundColor Cyan
        wsl.exe -e bash -c "byobu attach-session -t '$session'"
        return
    }

    Write-Host "🚀 Lancement d'une nouvelle session tmux '$session' pour Byobu..." -ForegroundColor Cyan

    # Créer une nouvelle session tmux détachée
    wsl.exe -e bash -c "tmux new-session -d -s '$session' -n gemini"

    # Diviser la fenêtre verticalement
    wsl.exe -e bash -c "tmux split-window -h -t '$session':0"

    # Lancer Gemini dans le panneau de gauche
    wsl.exe -e bash -c "tmux send-keys -t '$session':0.0 'gemini' C-m"

    # Le panneau de droite reste un terminal par défaut

    # Attacher à la session via Byobu
    wsl.exe -e bash -c "byobu attach-session -t '$session'"
}

function Create-PSMenuShortcut {
    $shortcutPath = "$HOME\Desktop\Launch-PS-Menu.lnk"
    $target = "powershell.exe"
    $scriptPath = "$PSScriptRoot\ps.ps1"
    $arguments = "-ExecutionPolicy Bypass -File `"$scriptPath`""
    $wshShell = New-Object -ComObject WScript.Shell
    $shortcut = $wshShell.CreateShortcut($shortcutPath)
    $shortcut.TargetPath = $target
    $shortcut.Arguments = $arguments
    $shortcut.WindowStyle = 1
    $shortcut.Description = "Lance le menu PowerShell principal"
    $shortcut.IconLocation = "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe"
    $shortcut.Save()

    Write-Host "✅ Raccourci créé sur le bureau : Launch-PS-Menu.lnk" -ForegroundColor Green
}

function Show-TmuxByobuShortcuts {
    Get-Content "$PSScriptRoot\tmux_byobu_shortcuts.txt" | ForEach-Object {
        Write-Host $_ 
    }
}
