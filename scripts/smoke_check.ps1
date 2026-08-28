[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).ProviderPath
$smokeTests = @(
    "tests/test_strategy_selector.py",
    "tests/test_ranking.py",
    "tests/test_proxy_ranking.py",
    "tests/test_metrics_and_failures.py",
    "tests/test_cut_patch.py",
    "tests/test_scripts_importable.py"
)
$runs = @()
foreach ($i in 1..3) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & python -m pytest -q -p no:cacheprovider @smokeTests
    if ($LASTEXITCODE -ne 0) { throw "smoke run $i failed" }
    $sw.Stop()
    $runs += [pscustomobject]@{ run = $i; seconds = [math]::Round($sw.Elapsed.TotalSeconds, 2) }
}
foreach ($r in $runs) {
    if ($r.seconds -gt 60) { throw "smoke run $($r.run) took $($r.seconds)s > 60s" }
}
$result = [pscustomobject]@{
    schema_version = 1
    command = "python -m pytest -q -p no:cacheprovider tests/test_strategy_selector.py tests/test_ranking.py tests/test_proxy_ranking.py tests/test_metrics_and_failures.py tests/test_cut_patch.py tests/test_scripts_importable.py"
    max_seconds = 60
    runs = $runs
    passed = $true
}
$outDir = Join-Path $repoRoot "docs\phase0"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$outPath = Join-Path $outDir "smoke_timings.json"
$result | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $outPath -Encoding utf8
Write-Output "smoke passed in $($runs.seconds -join ', ')s"
