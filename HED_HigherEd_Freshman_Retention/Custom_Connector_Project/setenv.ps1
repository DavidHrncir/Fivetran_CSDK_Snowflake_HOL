<#
.SYNOPSIS
    Loads environment variables from a specified .env file into the current PowerShell session.

.DESCRIPTION
    - Skips lines starting with '#' (comments).
    - Skips empty lines.
    - Handles values enclosed in single or double quotes.

.EXAMPLE
    . .\setenv.ps1 .env.development
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$EnvFile
)

function Show-Usage {
    Write-Host "Usage: . .\setenv.ps1 <path_to_env_file>"
    Write-Host ""
    Write-Host "Loads environment variables from the specified .env file into the current PowerShell session."
    Write-Host "  - Skips lines starting with '#' (comments)."
    Write-Host "  - Skips empty lines."
    Write-Host "  - Handles values enclosed in single or double quotes."
    Write-Host "Example: . .\setenv.ps1 .env.development"
}

if (-not (Test-Path $EnvFile)) {
    Write-Host "Error: Environment file '$EnvFile' not found or is not a regular file."
    Show-Usage
    return
}

Write-Host "--- Loading environment variables from '$EnvFile' ---"

Get-Content $EnvFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -eq "" -or $line -match '^\s*#') {
        return
    }
    if ($line -match '=') {
        $parts = $line -split '=', 2
        $key = $parts[0].Trim()
        $value = $parts[1].Trim()

        # Remove surrounding quotes if present
        if ($value -match '^(["''])((?:.|\n)*)\1$') {
            $value = $matches[2]
        }

        # Unset existing variable if present
        if (Test-Path "env:$key") {
            Remove-Item "env:$key"
            Write-Host "  Unset existing: $key"
        }

        # Set and export the variable
        $env:$key = $value
        Write-Host "  Exported: $key"
    }
    else {
        Write-Host "  Skipping malformed line (no '=' found): $line"
    }
}

Write-Host "--- Environment variable loading complete ---"
Write-Host ""
Write-Host "To verify variables, you can use '`$env:VARIABLE_NAME' or 'Get-ChildItem env: | findstr VARIABLE_NAME'."
Write-Host "Example: `$env:MY_APP_NAME"