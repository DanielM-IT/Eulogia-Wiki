from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate_enchant_docs.py"

text = GENERATOR.read_text(encoding="utf-8")

# The earlier broken PowerShell patch wrote these characters literally into Python.
# Repair them if they are present.
text = text.replace("`r`n", "\n")

# Spear uses the explicitly requested PNG filename.
old_spear = '"spear": ("Spear", "spear.webp", "🗡️"),'
new_spear = '"spear": ("Spear", "spear.png", "🗡️"),'
if old_spear in text:
    text = text.replace(old_spear, new_spear)
elif new_spear not in text:
    raise SystemExit("ERROR: Could not locate the Spear TARGETS entry.")

# Add output-only compatibility exclusions.
hidden = 'HIDDEN_COMPATIBILITY_TARGETS = {"brush", "flint_and_steel"}'
if hidden not in text:
    marker = "REQUIRED_FIELDS = {"
    if marker not in text:
        raise SystemExit("ERROR: Could not locate REQUIRED_FIELDS.")
    text = text.replace(marker, hidden + "\n\n" + marker, 1)

# Make the compatibility renderer skip Brush and Flint and Steel.
loop = '    for target in [part.strip() for part in raw_targets.split(",") if part.strip()]:'
skip = (
    loop
    + "\n"
    + "        if target in HIDDEN_COMPATIBILITY_TARGETS:\n"
    + "            continue"
)
if "if target in HIDDEN_COMPATIBILITY_TARGETS:" not in text:
    if loop not in text:
        raise SystemExit("ERROR: Could not locate render_targets loop.")
    # Only patch the render_targets occurrence. It is the first occurrence after def render_targets.
    start = text.find("def render_targets(")
    if start == -1:
        raise SystemExit("ERROR: Could not locate render_targets function.")
    pos = text.find(loop, start)
    if pos == -1:
        raise SystemExit("ERROR: Could not locate target loop inside render_targets.")
    text = text[:pos] + skip + text[pos + len(loop):]

# Preserve the already-correct Complete List asset path.
old_call = 'render_targets(row["Targets"], "../assets"),'
new_call = 'render_targets(row["Targets"], "../../assets"),'
if old_call in text:
    text = text.replace(old_call, new_call, 1)

GENERATOR.write_text(text, encoding="utf-8", newline="\n")

# Compile before proceeding so syntax errors stop here, before docs generation.
compile(text, str(GENERATOR), "exec")

print("PASS: generator syntax is valid")
print("PASS: spear target uses spear.png")
print("PASS: Brush and Flint and Steel are hidden from Compatible Items output")
print("PASS: Complete List compatibility asset path is ../../assets")
