# =============================================================================
# Chinese paper compile script (LuaLaTeX)
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File compile.ps1
#   powershell ... -File compile.ps1 -Name <paper-name>
# Output: paper/zh/build/<paper-name>.pdf
# Fonts: OSFONTDIR points to paper/zh/fonts/ (project-local fonts)
# =============================================================================
param([string]$Name = "template")

$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot                                   # paper/zh/scripts
$paperRoot = (Resolve-Path (Join-Path $scriptDir "..")).Path # paper/zh (absolute path; avoids ".." breaking lualatex -output-directory)
$manuscript = Join-Path $paperRoot "manuscript"
$build = Join-Path $paperRoot "build"
$fontsDir = Join-Path $paperRoot "fonts"

New-Item -ItemType Directory -Force -Path $build | Out-Null
$src = Join-Path $manuscript "$Name.tex"
if (-not (Test-Path $src)) {
    Write-Error "Manuscript not found: $src"
    exit 1
}

# Project-local font search path (LuaLaTeX + luaotfload reads OSFONTDIR)
$env:OSFONTDIR = $fontsDir

# Run from the build directory and reference the manuscript with an ASCII
# relative path. This avoids passing non-ASCII absolute paths to LuaTeX,
# which Windows PowerShell 5.1 mangles when building native-command args.
Push-Location $build
try {
    # Two passes to resolve cross-references
    lualatex -interaction=nonstopmode "../manuscript/$Name.tex"
    lualatex -interaction=nonstopmode "../manuscript/$Name.tex"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Compile failed, see $build\$Name.log"
        exit $LASTEXITCODE
    }
} finally {
    Pop-Location
}

# 最新版 PDF 放到 paper/zh/ 根目录（方便查找最新稿）
$latestPdf = Join-Path $paperRoot "${Name}.pdf"
Copy-Item -Force (Join-Path $build "${Name}.pdf") $latestPdf
Write-Host "Compiled (latest): ${latestPdf}"
