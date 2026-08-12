$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$Generator = Join-Path $RepoRoot "scripts\generate_enchant_docs.py"

if (-not (Test-Path $Generator)) {
    throw "Could not find scripts\generate_enchant_docs.py. Extract this update into the Eulogia-Wiki repository root."
}

Write-Host "Fixing Compatible Items image path..."
$text = [System.IO.File]::ReadAllText($Generator)

$old = 'render_targets(row["Targets"], "../assets"),'
$new = 'render_targets(row["Targets"], "../../assets"),'

if (-not $text.Contains($old)) {
    if ($text.Contains($new)) {
        Write-Host "Compatible Items path is already fixed."
    }
    else {
        throw "Expected Compatible Items path was not found in generate_enchant_docs.py. Refusing to guess."
    }
}
else {
    $text = $text.Replace($old, $new)
    [System.IO.File]::WriteAllText(
        $Generator,
        $text,
        [System.Text.UTF8Encoding]::new($false)
    )
    Write-Host "PASS: Compatible Items path updated to ../../assets."
}

Write-Host "Removing abandoned enchantment-name icon assets..."
$EnchantIconDir = Join-Path $RepoRoot "docs\assets\enchantments"
if (Test-Path $EnchantIconDir) {
    Remove-Item $EnchantIconDir -Recurse -Force
    Write-Host "PASS: Removed docs\assets\enchantments."
}
else {
    Write-Host "No enchantment-name icon directory present."
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
Write-Host "PASS: item icon path fixed, enchantment-name icons removed, docs regenerated, strict build succeeded."
Write-Host ""
Write-Host "Publish with:"
Write-Host '  git add .'
Write-Host '  git commit -m "Fix compatible item icons"'
Write-Host '  git push'
