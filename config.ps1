# config.ps1

function global:Get-EnvConfigPath {
    $configDir = "$HOME\.config\ps"
    if (-not (Test-Path $configDir)) {
        New-Item -ItemType Directory -Path $configDir | Out-Null
    }
    return "$configDir\python_env.json"
}

function Ensure-EnvStore {
    $configPath = Get-EnvConfigPath
    if (-not (Test-Path $configPath)) {
        New-Item -ItemType File -Path $configPath -Force | Out-Null
        Set-Content -Path $configPath -Value "{}"
    }
}

function global:Load-PythonEnvConfig {
    Ensure-EnvStore
    $configPath = Get-EnvConfigPath
    
    $content = Get-Content $configPath -Raw
    
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

function Save-PythonEnvConfig {
    param(
        [string]$selectedEnv
    )
    $configPath = Get-EnvConfigPath
    $config = Load-PythonEnvConfig
    $config.selected_env = $selectedEnv
    $config | ConvertTo-Json | Set-Content -Path $configPath
    Write-Host "✅ Environnement Python enregistré : $selectedEnv" -ForegroundColor Green
}

function Show-PythonEnvConfig {
    $config = Load-PythonEnvConfig
    if ($config.selected_env) {
        Write-Host "📦 Environnement sélectionné : $($config.selected_env)"
    } else {
        Write-Host "⚠️ Aucun environnement Python sélectionné"
    }
}

function Edit-PythonEnvConfig {
    notepad (Get-EnvConfigPath)
}

function Clear-PythonEnvConfig {
    $configPath = Get-EnvConfigPath
    Set-Content -Path $configPath -Value "{}"
    Write-Host "🧹 Configuration Python réinitialisée"
}

function Select-PythonEnv {
    $envs = Detect-PythonEnvs
    if ($envs.Count -eq 0) {
        Write-Host "❌ Aucun environnement Python détecté" -ForegroundColor Red
        return
    }

    Write-Host "`n📜 Environnements Python détectés :`n"
    for ($i = 0; $i -lt $envs.Count; $i++) {
        Write-Host "$($i+1). $($envs[$i])"
    }

    $choice = Read-Host "`n👉 Choisis le numéro de l’environnement"
    if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $envs.Count) {
        $selected = $envs[[int]$choice - 1]
        Save-PythonEnvConfig $selected
    } else {
        Write-Host "❌ Choix invalide" -ForegroundColor Yellow
    }
}

function Set-WSLProjectDirectory {
    Write-Host "`n🔍 Recherche des projets dans WSL (~/projets)..." -ForegroundColor Cyan
    try {
        $projects = wsl -e bash -c "ls -d ~/projets/*/ 2>/dev/null"
        if ($null -eq $projects) { $projects = @() }
    } catch {
        Write-Host "❌ Impossible de lister les répertoires dans ~/projets sur WSL." -ForegroundColor Red
        Pause
        return
    }

    if ($projects.Count -eq 0) {
        Write-Host "⚠️ Aucun projet trouvé dans ~/projets sur WSL." -ForegroundColor Yellow
        Pause
        return
    }

    Write-Host "`n📂 Projets disponibles :"
    for ($i = 0; $i -lt $projects.Count; $i++) {
        Write-Host "  $($i+1). $($projects[$i])"
    }

    $choice = Read-Host "`n👉 Choisis le numéro du projet par défaut"
    if ($choice -match '^\d+$' -and [int]$choice -ge 1 -and [int]$choice -le $projects.Count) {
        $selectedProject = $projects[[int]$choice - 1]
        $configPath = Get-EnvConfigPath
        $config = Load-PythonEnvConfig
        $config.wsl_project_dir = $selectedProject
        $config | ConvertTo-Json | Set-Content -Path $configPath
        Write-Host "✅ Projet par défaut enregistré : $selectedProject" -ForegroundColor Green
    } else {
        Write-Host "❌ Choix invalide." -ForegroundColor Red
    }
    MainMenu # Refresh the main menu
}

function Manage-PythonEnvConfig {
    $config = Load-PythonEnvConfig
    if ($config.selected_env -and (Validate-PythonEnv $config.selected_env)) {
        Write-Host "✅ Environnement actuel :" -ForegroundColor Green
        Show-PythonEnvDetails
    } else {
        Write-Host "⚠️ Aucun environnement valide configuré." -ForegroundColor Yellow
        Select-PythonEnv
    }

    Write-Host "`nQue veux-tu faire ?"
    Write-Host "1) Choisir un autre environnement"
    Write-Host "2) Définir le répertoire de projet WSL"
    Write-Host "3) Modifier le fichier de configuration"
    Write-Host "4) Réinitialiser la configuration"
    Write-Host "0) Retour"

    $choice = Read-Host "👉"
    switch ($choice) {
        '1' { Select-PythonEnv }
        '2' { Set-WSLProjectDirectory }
        '3' { Edit-PythonEnvConfig }
        '4' { Clear-PythonEnvConfig }
        '0' {}
        default { Write-Host "❌ Option invalide." -ForegroundColor Red }
    }
}

function Reset-PythonEnv {
    Clear-PythonEnvConfig
    Select-PythonEnv
}
