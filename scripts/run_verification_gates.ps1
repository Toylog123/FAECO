[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).ProviderPath
$phase0Dir = Join-Path $repoRoot "docs\phase0"
New-Item -ItemType Directory -Force -Path $phase0Dir | Out-Null

function Invoke-Step {
    param([string]$Name, [scriptblock]$Body)
    $logPath = Join-Path $phase0Dir "gate_${Name}.log"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $oldEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $output = & $Body 2>&1
        $ErrorActionPreference = $oldEap
        if ($LASTEXITCODE -ne 0) { throw "step '$Name' exited with $LASTEXITCODE; see $logPath" }
        $output | Out-File -LiteralPath $logPath -Encoding utf8
        $sw.Stop()
        return [pscustomobject]@{ name = $Name; ok = $true; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); detail = "ok; log=$logPath" }
    } catch {
        $ErrorActionPreference = $oldEap
        $sw.Stop()
        return [pscustomobject]@{ name = $Name; ok = $false; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2); detail = $_.Exception.Message }
    }
}

$steps = @()
$steps += Invoke-Step "git_diff_check" { git diff --check }
$steps += Invoke-Step "toolchain_snapshot" { & (Join-Path $repoRoot "scripts\check_toolchain.ps1") -OutputPath (Join-Path $phase0Dir "toolchain_snapshot.json") | Out-Null }
$steps += Invoke-Step "full_pytest" { python -m pytest -q -p no:cacheprovider }
$steps += Invoke-Step "smoke_3x" { & (Join-Path $repoRoot "scripts\smoke_check.ps1") | Out-Null }
$steps += Invoke-Step "real_sec_smoke" { python -m pytest -q -p no:cacheprovider tests/test_sol_review_residuals.py::test_real_wsl_sec_models_async_clear_polarity_and_connection }
$steps += Invoke-Step "yosys_map_encoding" { python -m pytest -q -p no:cacheprovider tests/test_yosys_map_script_encoding.py }

$allOk = ($steps | Where-Object { -not $_.ok }).Count -eq 0
$summary = [pscustomobject]@{
    schema_version = 1
    checked_at_utc = (Get-Date).ToUniversalTime().ToString("o")
    head_sha = (git rev-parse HEAD)
    worktree = $repoRoot
    all_gates_passed = $allOk
    steps = $steps
}
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $phase0Dir "verification-summary.json") -Encoding utf8
if (-not $allOk) { throw "verification gates failed; see docs/phase0/verification-summary.json" }
Write-Output "verification gates passed"
