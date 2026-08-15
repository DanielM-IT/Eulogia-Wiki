$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$Generator = Join-Path $RepoRoot "scripts\generate_enchant_docs.py"
$Patcher = Join-Path $RepoRoot "scripts\patch_compatibility_generator.py"
$Spear = Join-Path $RepoRoot "docs\assets\items\spear.png"

if (-not (Test-Path $Generator)) {
    throw "Missing scripts\generate_enchant_docs.py"
}
if (-not (Test-Path $Patcher)) {
    throw "Missing scripts\patch_compatibility_generator.py"
}
if (-not (Test-Path $Spear)) {
    throw "Missing docs\assets\items\spear.png"
}

# If the previous failed patch left literal PowerShell newline tokens in the Python
# source, restore only this generator from the current committed HEAD first.
$current = [System.IO.File]::ReadAllText($Generator)
if ($current.Contains('`r`n')) {
    Write-Host "Detected malformed previous patch. Restoring generator from current Git HEAD..."
    Copy-Item $Generator "$Generator.broken-backup" -Force
    git restore --source=HEAD -- scripts/generate_enchant_docs.py
    if ($LASTEXITCODE -ne 0) {
        throw "git restore failed. A backup remains at scripts\generate_enchant_docs.py.broken-backup"
    }
    Write-Host "PASS: clean committed generator restored."
}

Write-Host "Applying safe compatibility patch..."
& .\.venv\Scripts\python.exe .\scripts\patch_compatibility_generator.py
if ($LASTEXITCODE -ne 0) { throw "Compatibility generator patch failed." }

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
Write-Host "PASS: repair completed successfully."
Write-Host "  - spear.png is used for Spear"
Write-Host "  - Brush is hidden from Compatible Items"
Write-Host "  - Flint and Steel is hidden from Compatible Items"
Write-Host ""
Write-Host "Publish with:"
Write-Host '  git add .'
Write-Host '  git commit -m "Fix compatibility item output"'
Write-Host '  git push'
