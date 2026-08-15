$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$Generator = Join-Path $RepoRoot "scripts\generate_enchant_docs.py"
if (-not (Test-Path $Generator)) {
    throw "Could not find scripts\generate_enchant_docs.py. Extract this update into the Eulogia-Wiki repository root."
}

$text = [System.IO.File]::ReadAllText($Generator)

# Keep the published list page asset path correct.
$text = $text.Replace('../assets/items/', '../../assets/items/')

# Use spear.png, not spear.webp.
$text = $text.Replace('"spear": ("Spear", "spear.webp", "🗡️"),', '"spear": ("Spear", "spear.png", "🗡️"),')

# Add hidden compatibility targets once.
if (-not $text.Contains('HIDDEN_COMPATIBILITY_TARGETS = {"brush", "flint_and_steel"}')) {
    $needle = 'REQUIRED_FIELDS = {'
    if (-not $text.Contains($needle)) {
        throw "Could not locate REQUIRED_FIELDS block."
    }
    $text = $text.Replace(
        $needle,
        'HIDDEN_COMPATIBILITY_TARGETS = {"brush", "flint_and_steel"}' + "`r`n`r`n" + $needle
    )
}

# Make render_targets skip Brush and Flint and Steel.
if (-not $text.Contains('if target in HIDDEN_COMPATIBILITY_TARGETS:')) {
    $oldLoop = '    for target in [part.strip() for part in raw_targets.split(",") if part.strip()]:'
    $newLoop = '    for target in [part.strip() for part in raw_targets.split(",") if part.strip()]:`r`n        if target in HIDDEN_COMPATIBILITY_TARGETS:`r`n            continue'
    if (-not $text.Contains($oldLoop)) {
        throw "Could not locate render_targets loop."
    }
    $text = $text.Replace($oldLoop, $newLoop)
}

[System.IO.File]::WriteAllText(
    $Generator,
    $text,
    [System.Text.UTF8Encoding]::new($false)
)

$SpearPath = Join-Path $RepoRoot "docs\assets\items\spear.png"
if (-not (Test-Path $SpearPath)) {
    throw "Expected docs\assets\items\spear.png after extracting the update."
}

Write-Host "Regenerating enchantment documentation..."
& .\.venv\Scripts\python.exe .\scripts\generate_enchant_docs.py
if ($LASTEXITCODE -ne 0) { throw "Enchantment documentation generation failed." }

Write-Host "Validating MkDocs build..."
& .\.venv\Scripts\python.exe -m mkdocs build --strict
if ($LASTEXITCODE -ne 0) { throw "MkDocs strict build failed." }

Write-Host "Checking Git whitespace..."
git diff --check
if ($LASTEXITCODE -ne 0) { throw "git diff --check failed." }

Write-Host ""
Write-Host "PASS: spear.png configured; Brush and Flint and Steel hidden from compatibility output."
Write-Host "Publish with:"
Write-Host '  git add .'
Write-Host '  git commit -m "Fix spear compatibility sprite"'
Write-Host '  git push'
