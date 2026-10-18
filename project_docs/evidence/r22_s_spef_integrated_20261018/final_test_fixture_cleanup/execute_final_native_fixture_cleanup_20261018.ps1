$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Get-Location).Path)
$sourceBase = [IO.Path]::GetFullPath((Join-Path $taskRoot 'data/cases/minimal/iscas85_c17_case01/results'))
$outputBase = [IO.Path]::GetFullPath((Join-Path $taskRoot 'project_docs/evidence/r22_s_spef_integrated_20261018/final_test_fixture_cleanup'))
$movePlan = Get-Content -LiteralPath (Join-Path $outputBase 'MOVE_PLAN.json') -Raw -Encoding UTF8 | ConvertFrom-Json
foreach ($entry in $movePlan) {
    $resolvedSource = [IO.Path]::GetFullPath($entry.source)
    $resolvedDestination = [IO.Path]::GetFullPath($entry.destination)
    if (-not $resolvedSource.StartsWith($sourceBase + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Source outside intended test output folder" }
    if (-not $resolvedDestination.StartsWith($outputBase + '\', [StringComparison]::OrdinalIgnoreCase)) { throw "Destination outside intended evidence folder" }
    if (Test-Path -LiteralPath $resolvedDestination) { throw 'Destination already exists' }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $resolvedDestination) | Out-Null
    Move-Item -LiteralPath $resolvedSource -Destination $resolvedDestination
}
Copy-Item -LiteralPath $PSCommandPath -Destination (Join-Path $outputBase 'execute_final_native_fixture_cleanup_20261018.ps1')
Write-Output "Moved $(@($movePlan).Count) verified test output items into evidence"
