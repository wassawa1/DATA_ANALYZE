<#
Runs the analysis scripts in this project.

Usage:
  # run all
  .\run_all.ps1

  # run specific parts
  .\run_all.ps1 -RunMovieGroup

  # run all and open outputs folder when done
  .\run_all.ps1 -OpenOutputs

This script expects the data file at `data\raw\データ_edit.xlsx`.
#>

param(
    [switch]$RunMovieGroup,
    [switch]$RunLevelByScore,
    [switch]$RunLowHigh,
    [switch]$OpenOutputs
)

Set-StrictMode -Version Latest

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root

function Abort($msg) {
    Write-Error $msg
    Pop-Location
    exit 1
}

# Ensure data file exists (robust to Unicode normalization/encoding differences)
$dataDir = Join-Path $root "data\raw"
$expectedName = 'データ_edit.xlsx'
$dataPath = Join-Path $dataDir $expectedName

# Find any .xlsx files in dataDir (ensure array to safely use .Count)
$xlsxFiles = @(Get-ChildItem -LiteralPath $dataDir -Filter '*.xlsx' -ErrorAction SilentlyContinue)

if ($xlsxFiles.Count -eq 0) {
    Abort "Data file not found: $dataPath`nPlease place your データ_edit.xlsx in data\raw\ and re-run."
}

# Try to find file matching expected name (exact or normalized NFC)
$found = $null
$expectedNorm = $expectedName.Normalize([System.Text.NormalizationForm]::FormC)
foreach ($f in $xlsxFiles) {
    $n = $f.Name
    if ($n -eq $expectedName) { $found = $f; break }
    if ($n.Normalize([System.Text.NormalizationForm]::FormC) -eq $expectedNorm) { $found = $f; break }
}

if (-not $found) {
    # fallback: use first .xlsx and warn
    $found = $xlsxFiles[0]
    Write-Host "Warning: expected file not found; using first .xlsx: $($found.Name)" -ForegroundColor Yellow
}

# If the found file path is not the expected path, copy it to expected filename so scripts that
# look for the canonical name will work regardless of filename normalization.
if ($found.FullName -ne $dataPath) {
    Write-Host "Preparing data file: copying $($found.Name) -> $expectedName"
    try {
        Copy-Item -LiteralPath $found.FullName -Destination $dataPath -Force
    } catch {
        Abort "Failed to copy data file: $($_.Exception.Message)"
    }
}

# Ensure outputs directory
$outDir = Join-Path $root "outputs"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

if (-not ($RunMovieGroup -or $RunLevelByScore -or $RunLowHigh)) {
    $RunMovieGroup = $true
    $RunLevelByScore = $true
    $RunLowHigh = $true
}

function Run-PythonScript($script) {
    Write-Host "---- Running: $script ----" -ForegroundColor Cyan
    & python $script
    if ($LASTEXITCODE -ne 0) {
        Abort "$script exited with code $LASTEXITCODE"
    }
}

try {
    if ($RunMovieGroup) {
        Run-PythonScript ".\plot_movie_group_accuracy.py"
    }

    if ($RunLevelByScore) {
        Run-PythonScript ".\plot_level_by_score.py"
    }

    if ($RunLowHigh) {
        Run-PythonScript ".\plot_low_high_individuals.py"
    }

    Write-Host "All scripts finished successfully." -ForegroundColor Green

    if ($OpenOutputs) {
        Write-Host "Opening outputs folder: $outDir"
        Start-Process explorer.exe $outDir
    }

} finally {
    Pop-Location
}
