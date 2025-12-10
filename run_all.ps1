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
    [switch]$RunMemoryType,
    [switch]$RunOrderGroupsAccuracy,
    [switch]$RunOrderGroupsHalves,
    [switch]$RunOrderGroupsLevels,
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

## Resolve data file path strictly from ./data (no choices elsewhere).
$expectedName = 'データ_edit.xlsx'
$dataDir = Join-Path $root 'data'

# If the exact expected file exists under ./data, use it.
$expectedPath = Join-Path $dataDir $expectedName
if (Test-Path $expectedPath) {
    $env:DATA_FILE = (Resolve-Path -LiteralPath $expectedPath).Path
    Write-Host "Using expected data file: $env:DATA_FILE"
} else {
    # If the expected file isn't present, but there's exactly one .xlsx in ./data, use that one.
    $xlsxFiles = @(Get-ChildItem -LiteralPath $dataDir -Filter '*.xlsx' -ErrorAction SilentlyContinue)
    if ($xlsxFiles.Count -eq 1) {
        $env:DATA_FILE = $xlsxFiles[0].FullName
        Write-Host "Expected file not found; using the single .xlsx found in ./data: $env:DATA_FILE"
    } else {
        # zero or multiple files -> abort to avoid choices
        if ($xlsxFiles.Count -eq 0) {
            Abort "Data file not found: $expectedPath`nPlease place the exact file '$expectedName' under the 'data' directory and re-run."
        } else {
            $names = $xlsxFiles | ForEach-Object { $_.Name } | Sort-Object
            $list = $names -join ", "
            Abort "Multiple .xlsx files found in ./data: $list`nPlease ensure the expected file '$expectedName' is present (or leave exactly one .xlsx in ./data)."
        }
    }
}

# Ensure outputs directory
$outDir = Join-Path $root "outputs"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir | Out-Null
}

if (-not ($RunMovieGroup -or $RunLevelByScore -or $RunLowHigh -or $RunMemoryType -or $RunOrderGroupsAccuracy -or $RunOrderGroupsHalves -or $RunOrderGroupsLevels)) {
    # If no specific switches provided, enable the common set including the new order-group plots
    $RunMovieGroup = $true
    $RunLevelByScore = $true
    $RunLowHigh = $true
    $RunMemoryType = $true
    $RunOrderGroupsAccuracy = $true
    $RunOrderGroupsHalves = $true
    $RunOrderGroupsLevels = $true
}

function Run-PythonScript($script) {
    Write-Host "---- Running: $script ----" -ForegroundColor Cyan
    & python $script
    if ($LASTEXITCODE -ne 0) {
        Abort "$script exited with code $LASTEXITCODE"
    }
}

try {
    # すべての plot_*.py を自動実行
    $plotScripts = Get-ChildItem -Path $root -Filter 'plot_*.py' | Sort-Object Name
    foreach ($script in $plotScripts) {
        Run-PythonScript $script.Name
    }

    Write-Host "All plot_*.py scripts finished successfully." -ForegroundColor Green

    if ($OpenOutputs) {
        Write-Host "Opening outputs folder: $outDir"
        Start-Process explorer.exe $outDir
    }

    Pop-Location
    return

    if ($RunMovieGroup) {
        Run-PythonScript ".\plot_movie_group_accuracy.py"
    }

    if ($RunLevelByScore) {
        Run-PythonScript ".\plot_level_by_score.py"
    }

    if ($RunLowHigh) {
        Run-PythonScript ".\plot_low_high_individuals.py"
    }

    if ($RunMemoryType) {
        Run-PythonScript ".\plot_memory_type_accuracy.py"
    }

    if ($RunOrderGroupsAccuracy) {
        Run-PythonScript ".\plot_order_groups_accuracy.py"
    }

    if ($RunOrderGroupsHalves) {
        Run-PythonScript ".\plot_order_groups_halves.py"
    }

    if ($RunOrderGroupsLevels) {
        Run-PythonScript ".\plot_order_groups_levels.py"
    }

    Write-Host "All scripts finished successfully." -ForegroundColor Green

    if ($OpenOutputs) {
        Write-Host "Opening outputs folder: $outDir"
        Start-Process explorer.exe $outDir
    }

} finally {
    Pop-Location
}
