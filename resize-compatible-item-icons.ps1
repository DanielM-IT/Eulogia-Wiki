$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RepoRoot

$Css = Join-Path $RepoRoot "docs\stylesheets\extra.css"

if (-not (Test-Path $Css)) {
    throw "Could not find docs\stylesheets\extra.css. Extract this update into the Eulogia-Wiki repository root."
}

Write-Host "Resizing Compatible Items sprites..."

$text = [System.IO.File]::ReadAllText($Css)

$old = @'
.item-icon {
    width: 28px;
    height: 28px;
    margin: 1px 4px 1px 0;
    vertical-align: middle;
    image-rendering: pixelated;
}
'@

$new = @'
.item-icon {
    width: 18px;
    height: 18px;
    margin: 0 3px 0 0;
    vertical-align: -3px;
    image-rendering: pixelated;
}
'@

if ($text.Contains($old)) {
    $text = $text.Replace($old, $new)
}
elseif ($text.Contains("width: 18px;") -and $text.Contains("height: 18px;")) {
    Write-Host "Compatible Items sprites are already set to 18x18."
}
else {
    throw "Expected .item-icon CSS block was not found. Refusing to guess."
}

[System.IO.File]::WriteAllText(
    $Css,
    $text,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Validating MkDocs build..."
& .\.venv\Scripts\python.exe -m mkdocs build --strict
if ($LASTEXITCODE -ne 0) { throw "MkDocs strict build failed." }

Write-Host "Checking Git whitespace..."
git diff --check
if ($LASTEXITCODE -ne 0) { throw "git diff --check failed." }

Write-Host ""
Write-Host "PASS: Compatible Items icons resized to 18x18 px."
Write-Host ""
Write-Host "Publish with:"
Write-Host '  git add .'
Write-Host '  git commit -m "Resize compatible item icons"'
Write-Host '  git push'
