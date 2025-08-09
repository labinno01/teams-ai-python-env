# env.ps1

function Detect-PythonEnvs {
    $windowsPaths = @(Get-Command python -All -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
    $wslPaths = @()

    try {
        $wslOutput = wsl -e bash -c "command -v python3 || command -v python"
        if ($wslOutput) {
            $wslPaths += "wsl:$wslOutput"
        }
    } catch {
        Write-Host "⚠️ Impossible de détecter Python dans WSL." -ForegroundColor Yellow
    }

    return $windowsPaths + $wslPaths
}

function Test-PythonPath {
    param([string]$path)

    if ($path.StartsWith("wsl:")) {
        $wslPath = $path.Substring(4)
        try {
            wsl -e bash -c "command -v $wslPath" | Out-Null
            return $true
        } catch {
            return $false
        }
    } else {
        return Test-Path $path
    }
}

function Validate-PythonEnv {
    param([string]$path)

    if (-not (Test-PythonPath $path)) {
        return $false
    }

    $versionString = Get-PythonVersion -pythonPath $path
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

function Is-VirtualEnv {
    param([string]$path)
    return $path -like "*venv*" -or $path -like "*virtualenv*"
}

function Get-PythonEnvType {
    param([string]$path)

    if ($path.StartsWith("wsl:")) {
        return "WSL"
    }
    if ($path -like "*conda*") {
        return "conda"
    }
    if (Is-VirtualEnv $path) {
        return "venv"
    }
    return "global"
}

# --- Fonctions de détection génériques ---

function Test-CommandExists {
    param($Command)
    return [bool](Get-Command $Command -ErrorAction SilentlyContinue)
}

function Test-WSLCommandExists {
    param($Command)
    $output = wsl.exe -e bash -c "command -v $Command" 2>$null
    return ($LASTEXITCODE -eq 0 -and $output)
}
