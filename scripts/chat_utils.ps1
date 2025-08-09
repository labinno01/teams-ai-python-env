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

function Display-Chat {
    param(
        [string]$PSScriptRoot
    )
    (Get-Random -SetSeed (Get-Random)) | Out-Null # Ensure random is re-seeded for each display
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
}