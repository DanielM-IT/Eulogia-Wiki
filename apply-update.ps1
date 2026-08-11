$ErrorActionPreference = "Stop"

Write-Host "Generating item-based enchantment pages..."
& .\.venv\Scripts\python.exe .\scripts\generate_enchant_docs.py

Write-Host "Validating MkDocs build..."
& .\.venv\Scripts\python.exe -m mkdocs build --strict

Write-Host "Checking Git whitespace..."
git diff --check

Write-Host ""
Write-Host "PASS: update generated and MkDocs strict build succeeded."
Write-Host "Next commands:"
Write-Host '  git add .'
Write-Host '  git commit -m "Reorganize enchantments by compatible item"'
Write-Host '  git push'
