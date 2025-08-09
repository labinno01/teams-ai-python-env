# run.ps1

# Définir la racine du projet au démarrage pour résoudre les chemins de manière fiable
if (-not $global:ScriptRoot) {
    $global:ScriptRoot = $PSScriptRoot
}
if (-not $global:WslScriptRoot) {
    if ($global:ScriptRoot) {
        $global:WslScriptRoot = (wsl -e bash -c "cd `$(wslpath '$global:ScriptRoot')`; pwd").Trim()
    }
}

function Get-ActivePythonEnv {
    $config = Load-PythonEnvConfig
    if ($config.selected_env -and (Validate-PythonEnv $config.selected_env)) {
        return $config.selected_env
    } else {
        Write-Host "🔁 Environnement invalide ou absent, relance la détection..." -ForegroundColor Yellow
        Reset-PythonEnv
        $newConfig = Load-PythonEnvConfig
        return $newConfig.selected_env
    }
}


function Is-PythonVersionCompatible {
    param (
        [string]$pythonPath
    )

    $versionString = Get-PythonVersion -pythonPath $pythonPath

    if ($versionString -match "Python (\d+)\.(\d+)") {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -gt 3) {
            return $true
        }
        if ($major -eq 3 -and $minor -ge 10) {
            return $true
        }
    }

    return $false
}

function Get-PythonVersion {
    param (
        [string]$pythonPath
    )

    if ($pythonPath.StartsWith("wsl:")) {
        $cmd = "wsl " + $pythonPath.Substring(4) + " --version"
        try {
            $versionOutput = Invoke-Expression $cmd 2>&1
            return $versionOutput.Trim()
        } catch {
            return "❌ Erreur lors de la récupération de la version (WSL)"
        }
    } else {
        try {
            # Use the call operator & for local commands. It's safer.
            $versionOutput = & $pythonPath --version 2>&1
            # The output might be an array of strings, so join them.
            return ($versionOutput | Out-String).Trim()
        } catch {
            $ErrorMessage = $_.Exception.Message
            return "❌ Erreur lors de la récupération de la version: $ErrorMessage"
        }
    }
}

function Get-ToolVersion {
    param(
        [string]$pythonPath,
        [string]$toolName
    )

    $command = ""
    if ($pythonPath.StartsWith("wsl:")) {
        $wslPython = $pythonPath.Substring(4)
        $command = "wsl $wslPython -m $toolName --version"
    } else {
        $command = "& `"$pythonPath`" -m $toolName --version"
    }

    try {
        $versionOutput = Invoke-Expression $command 2>&1
        if ($LASTEXITCODE -eq 0) {
            return ($versionOutput | Out-String).Trim()
        } else {
            return "❌ Non trouvé"
        }
    } catch {
        return "❌ Non trouvé"
    }
}

function Show-PythonEnvDetails {
    $envPath = Get-ActivePythonEnv
    if (-not $envPath) {
        Write-Host "❌ Aucun environnement Python valide" -ForegroundColor Red
        return
    }

    Write-Host "`n🔍 Détails de l’environnement Python :" -ForegroundColor Cyan
    Write-Host "  - Chemin : $envPath"
    Write-Host "  - Version: $(Get-PythonVersion -pythonPath $envPath)"
    Write-Host "  - Type   : $(Get-PythonEnvType -path $envPath)"

    Write-Host "`n🔧 Outils Python :" -ForegroundColor Cyan
    Write-Host "  - Pip    : $(Get-ToolVersion -pythonPath $envPath -toolName 'pip')"
    Write-Host "  - Pipx   : $(Get-ToolVersion -pythonPath $envPath -toolName 'pipx')"
    Write-Host "  - Ruff   : $(Get-ToolVersion -pythonPath $envPath -toolName 'ruff')"
    Write-Host "  - Poetry : $(Get-ToolVersion -pythonPath $envPath -toolName 'poetry')"

    Write-Host "`n🛠️ Outils système :" -ForegroundColor Cyan
    # --- Git ---
    if (Test-CommandExists -Command "git") {
        $gitVersion = (git --version).Trim()
        Write-Host "  - Git      : ✅ Trouvé ($gitVersion)" -ForegroundColor Green
    } else {
        Write-Host "  - Git      : ❌ Non trouvé" -ForegroundColor Red
    }
    # --- Tmux (WSL) ---
    if (Test-WSLCommandExists -Command "tmux") {
        $tmuxVersion = (wsl.exe -e bash -c "tmux -V").Trim()
        Write-Host "  - Tmux (WSL): ✅ Trouvé ($tmuxVersion)" -ForegroundColor Green
    } else {
        Write-Host "  - Tmux (WSL): ❌ Non trouvé" -ForegroundColor Red
    }
    # --- Node.js ---
    if (Test-CommandExists -Command "node") {
        $nodeVersion = (node --version).Trim()
        Write-Host "  - Node.js  : ✅ Trouvé ($nodeVersion)" -ForegroundColor Green
    } else {
        Write-Host "  - Node.js  : ❌ Non trouvé" -ForegroundColor Red
    }
    # --- npm ---
    if (Test-CommandExists -Command "npm") {
        $npmVersion = (npm --version).Trim()
        Write-Host "  - npm      : ✅ Trouvé (v$npmVersion)" -ForegroundColor Green
    } else {
        Write-Host "  - npm      : ❌ Non trouvé" -ForegroundColor Red
    }
}

function Show-PipModules {
    $envPath = Get-ActivePythonEnv
    if (-not $envPath) {
        Write-Host "❌ Aucun environnement Python valide" -ForegroundColor Red
        return
    }

    # --- Modules Pip ---
    Write-Host "`n📦 Modules installés via pip :" -ForegroundColor Cyan
    $pip_output = if ($envPath.StartsWith("wsl:")) {
        $pythonInWsl = $envPath.Substring(4)
        wsl $pythonInWsl -m pip list | Out-String
    } else {
        Invoke-Expression "& `"$envPath`" -m pip list" | Out-String
    }

    $pip_lines = $pip_output.Trim().Split([System.Environment]::NewLine)
    $pip_count = if ($pip_lines.Length -gt 2) { $pip_lines.Length - 2 } else { 0 }
    Write-Host "   -> $pip_count modules trouvés."

    if ($pip_count -gt 0) {
        $choice_pip = Read-Host "    afficher la liste complète ? (o/N)"
        if ($choice_pip -eq 'o') {
            Write-Host ""
            $pip_output | Out-Host
        }
    }

    # --- Modules Pipx ---
    Write-Host "`n📦 Modules installés via pipx :" -ForegroundColor Cyan
    if (Test-CommandExists -Command "pipx") {
        $pipx_output = pipx list | Out-String
        $pipx_lines = $pipx_output.Trim().Split([System.Environment]::NewLine)
        $pipx_count = ($pipx_lines | Where-Object { $_ -like '*package*' }).Count
        Write-Host "   -> $pipx_count modules trouvés (Windows)."

        if ($pipx_count -gt 0) {
            $choice_pipx = Read-Host "    afficher la liste complète ? (o/N)"
            if ($choice_pipx -eq 'o') {
                Write-Host ""
                $pipx_output | Out-Host
            }
        }
    } elseif (Test-WSLCommandExists -Command "pipx") {
        $pipx_output = wsl pipx list | Out-String
        $pipx_lines = $pipx_output.Trim().Split([System.Environment]::NewLine)
        $pipx_count = ($pipx_lines | Where-Object { $_ -like '*package*' }).Count
        Write-Host "   -> $pipx_count modules trouvés (WSL)."

        if ($pipx_count -gt 0) {
            $choice_pipx = Read-Host "    afficher la liste complète ? (o/N)"
            if ($choice_pipx -eq 'o') {
                Write-Host ""
                $pipx_output | Out-Host
            }
        }
    } else {
        Write-Host "   -> pipx n'est pas installé ou accessible." -ForegroundColor Yellow
    }
}

function Run-PythonScript {
    param (
        [string]$scriptName,
        [string[]]$scriptArgs = @()
    )

    # 🔧 Chargement ou détection de l'environnement Python
    $envPath = Get-ActivePythonEnv
    if (-not $envPath) {
        Write-Host "❌ Aucun environnement Python valide" -ForegroundColor Red
        return
    }

    # 📁 Construction du chemin vers le script
    $winScriptPath = Join-Path -Path $global:ScriptRoot -ChildPath "scripts\$scriptName"
    if (-not (Test-Path $winScriptPath)) {
        Write-Host "❌ Script introuvable : $winScriptPath" -ForegroundColor Red
        return
    }

    # 🧾 Affichage des arguments
    if ($scriptArgs.Count -gt 0) {
        Write-Host "📦 Arguments ($($scriptArgs.Count)) :"
        $scriptArgs | ForEach-Object { Write-Host " - $_" }
    } else {
        Write-Host "📦 Aucun argument fourni."
    }

    # ✨ Affichage des informations sur l'environnement
    $pythonVersion = Get-PythonVersion -pythonPath $envPath
    Write-Host "`n🐍 Utilisation de l'environnement : $envPath" -ForegroundColor DarkGray
    Write-Host "   (Version: $pythonVersion)" -ForegroundColor DarkGray

    # 🚀 Exécution du script avec l'environnement Python
    Write-Host "`n🚀 Exécution : $scriptName" -ForegroundColor Cyan
    if ($envPath.StartsWith("wsl:")) {
        $wslScriptPath = "$global:WslScriptRoot/scripts/$scriptName"
        & wsl ($envPath.Substring(4)) $wslScriptPath $scriptArgs
    } else {
        & $envPath $winScriptPath $scriptArgs
    }
}


function Test-CommandExists {
    param([string]$Command)
    return (Get-Command $Command -ErrorAction SilentlyContinue) -ne $null
}

function Test-WSLCommandExists {
    param([string]$Command)
    $result = wsl.exe -e bash -c "command -v $Command"
    return $LASTEXITCODE -eq 0
}