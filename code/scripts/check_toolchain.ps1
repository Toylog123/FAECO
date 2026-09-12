[CmdletBinding()]
param(
    [string]$OutputPath
)

$ErrorActionPreference = "Stop"

function Get-ExecutableStatus {
    param(
        [string]$Id,
        [string[]]$Candidates,
        [string]$EnvVar
    )

    if ($EnvVar) {
        $explicit = [Environment]::GetEnvironmentVariable($EnvVar)
        if ($explicit) {
            $resolvedExplicit = Resolve-CommandSpec -CommandSpec $explicit
            if ($null -ne $resolvedExplicit) {
                return [pscustomobject]@{
                    id = $Id
                    available = $true
                    command = $explicit
                    path = $resolvedExplicit.Path
                    version = Get-ExecutableVersion -Id $Id -CommandSpec $explicit
                }
            }
        }
    }

    foreach ($candidate in $Candidates) {
        $command = Get-Command $candidate -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            return [pscustomobject]@{
                id = $Id
                available = $true
                command = $candidate
                path = $command.Source
                version = Get-ExecutableVersion -Id $Id -CommandSpec $candidate
            }
        }
    }

    return [pscustomobject]@{
        id = $Id
        available = $false
        command = $null
        path = $null
        version = $null
    }
}

function Get-ExecutableVersion {
    param(
        [string]$Id,
        [string]$CommandSpec
    )

    if ($Id -eq "python") {
        $resolvedPython = Resolve-CommandSpec -CommandSpec $CommandSpec
        if ($null -eq $resolvedPython) {
            return $null
        }
        $version = & $resolvedPython.Path @($resolvedPython.Arguments + @("-c", "import sys; print(sys.version.split()[0])")) 2>$null
        if ($LASTEXITCODE -eq 0 -and $version) {
            return ($version | Select-Object -First 1).Trim()
        }
        return $null
    }

    $arguments = switch ($Id) {
        "yosys" { @("-V") }
        "abc" { @("-h") }
        "opensta" { @("-version") }
        default { @("--version") }
    }

    $resolvedCommand = Resolve-CommandSpec -CommandSpec $CommandSpec
    if ($null -eq $resolvedCommand) {
        return $null
    }

    $previousErrorActionPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = & $resolvedCommand.Path @($resolvedCommand.Arguments + $arguments) 2>&1
        return Select-VersionLine -Id $Id -Output $output
    } catch {
        return $null
    } finally {
        $ErrorActionPreference = $previousErrorActionPreference
    }
    return $null
}

function Select-VersionLine {
    param(
        [string]$Id,
        [object[]]$Output
    )

    if ($Id -eq "opensta") {
        foreach ($line in $Output) {
            if ($null -eq $line) {
                continue
            }
            $text = $line.ToString().Trim()
            if (-not $text) {
                continue
            }
            if ($text -match "(?:OpenSTA\s+)?([0-9]+(?:\.[0-9]+)+)") {
                return $matches[1]
            }
        }
        return $null
    }

    foreach ($line in $Output) {
        if ($null -eq $line) {
            continue
        }
        $text = $line.ToString().Trim()
        if (-not $text) {
            continue
        }
        if ($text -match "wsl: Failed to translate") {
            continue
        }
        return $text
    }
    return $null
}

function Resolve-CommandSpec {
    param(
        [string]$CommandSpec
    )

    if (-not $CommandSpec) {
        return $null
    }

    $tokens = @([System.Management.Automation.PSParser]::Tokenize($CommandSpec, [ref]$null) |
        Where-Object { $_.Type -in @("Command", "CommandArgument", "CommandParameter", "String") } |
        ForEach-Object { $_.Content })
    if (-not $tokens) {
        return $null
    }

    $executable = $tokens[0]
    if (Test-Path -LiteralPath $executable -PathType Leaf) {
        $resolvedPath = (Resolve-Path -LiteralPath $executable).ProviderPath
    } else {
        $command = Get-Command $executable -ErrorAction SilentlyContinue
        if ($null -eq $command) {
            return $null
        }
        $resolvedPath = $command.Source
    }

    return [pscustomobject]@{
        Path = $resolvedPath
        Arguments = @($tokens | Select-Object -Skip 1)
    }
}

function Get-PythonPackageStatus {
    param(
        [string]$Id,
        [string]$PackageName,
        [string]$DistributionName,
        [string]$PythonPath
    )

    if (-not $DistributionName) {
        $DistributionName = $PackageName
    }

    $available = $false
    if ($null -ne $PythonPath) {
        & $PythonPath -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('$PackageName') else 1)" 2>$null
        $available = $LASTEXITCODE -eq 0
    }

    return [pscustomobject]@{
        id = $Id
        available = $available
        command = if ($available) { "python -m $PackageName" } else { $null }
        path = $null
        version = if ($available) { Get-PythonPackageVersion -PackageName $DistributionName -PythonPath $PythonPath } else { $null }
    }
}

function Get-PythonPackageVersion {
    param(
        [string]$PackageName,
        [string]$PythonPath
    )

    if ($null -eq $PythonPath) {
        return $null
    }

    $version = & $PythonPath -c "import importlib.metadata; print(importlib.metadata.version('$PackageName'))" 2>$null
    if ($LASTEXITCODE -eq 0 -and $version) {
        return ($version | Select-Object -First 1).Trim()
    }
    return $null
}

$python = Get-ExecutableStatus -Id "python" -Candidates @("python")
$tools = @(
    $python
    (Get-ExecutableStatus -Id "yosys" -Candidates @("yosys") -EnvVar "FAECO_YOSYS")
    (Get-ExecutableStatus -Id "abc" -Candidates @("yosys-abc", "abc") -EnvVar "FAECO_ABC")
    (Get-ExecutableStatus -Id "opensta" -Candidates @("opensta", "sta") -EnvVar "FAECO_OPENSTA")
    (Get-PythonPackageStatus -Id "z3" -PackageName "z3" -DistributionName "z3-solver" -PythonPath $python.path)
    (Get-PythonPackageStatus -Id "networkx" -PackageName "networkx" -PythonPath $python.path)
)

$snapshot = [pscustomobject]@{
    schema_version = 1
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    tools = $tools
}

$json = $snapshot | ConvertTo-Json -Depth 3
if ($OutputPath) {
    Set-Content -LiteralPath $OutputPath -Value $json -Encoding utf8
}

Write-Output $json
