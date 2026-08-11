from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "enchantments.csv"
DOCS_DIR = ROOT / "docs" / "enchantments"
ITEMS_DIR = ROOT / "docs" / "assets" / "items"

EXPECTED_TOTAL = 160
CATEGORY_CONFIG = [
    ("Armor", "Armour", "armour.md", 40),
    ("Weapon", "Weapons", "weapons.md", 41),
    ("Bow", "Bows and Crossbows", "bows.md", 22),
    ("Tool", "Tools", "tools.md", 29),
    ("Trident", "Tridents", "tridents.md", 6),
    ("Fishing", "Fishing", "fishing.md", 7),
    ("Shield", "Shields", "shields.md", 4),
    ("Elytra", "Elytra", "elytra.md", 4),
    ("Universal", "Universal", "universal.md", 7),
]

TARGETS = {
    "pickaxe": ("Pickaxe", "pickaxe.webp", "⛏️"),
    "axe": ("Axe", "axe.webp", "🪓"),
    "hoe": ("Hoe", "hoe.webp", "🌾"),
    "shovel": ("Shovel", "shovel.webp", "🪏"),
    "sword": ("Sword", "sword.webp", "⚔️"),
    "spear": ("Spear", "spear.webp", "🗡️"),
    "helmet": ("Helmet", "helmet.webp", "🪖"),
    "chestplate": ("Chestplate", "chestplate.webp", "🥋"),
    "leggings": ("Leggings", "leggings.webp", "👖"),
    "boots": ("Boots", "boots.webp", "🥾"),
    "trident": ("Trident", "trident.webp", "🔱"),
    "bow": ("Bow", "bow.webp", "🏹"),
    "crossbow": ("Crossbow", "crossbow.webp", "🎯"),
    "shears": ("Shears", "shears.webp", "✂️"),
    "brush": ("Brush", "brush.webp", "🖌️"),
    "shield": ("Shield", "shield.webp", "🛡️"),
    "fishing_rod": ("Fishing Rod", "fishing_rod.webp", "🎣"),
    "flint_and_steel": ("Flint and Steel", "flint_and_steel.webp", "🔥"),
    "elytra": ("Elytra", "elytra.webp", "🪽"),
    "mace": ("Mace", "mace.webp", "🔨"),
}

REQUIRED_FIELDS = {
    "Category",
    "ID",
    "Name",
    "Summary",
    "Incompatible With",
    "Max Level",
    "Targets",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def clean(value: str | None) -> str:
    return " ".join((value or "").replace("\r", " ").replace("\n", " ").split())


def escape_table(value: str) -> str:
    return clean(value).replace("|", "\\|")


def load_rows() -> list[dict[str, str]]:
    if not DATA_FILE.exists():
        fail(f"Missing data file: {DATA_FILE}")

    with DATA_FILE.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            fail("CSV has no header row")
        missing = REQUIRED_FIELDS - set(reader.fieldnames)
        if missing:
            fail(f"CSV is missing required columns: {', '.join(sorted(missing))}")
        rows = [{k: clean(v) for k, v in row.items()} for row in reader]

    return rows


def validate(rows: list[dict[str, str]]) -> None:
    errors: list[str] = []

    if len(rows) != EXPECTED_TOTAL:
        errors.append(f"expected {EXPECTED_TOTAL} rows, found {len(rows)}")

    ids = [row["ID"] for row in rows]
    names = [row["Name"] for row in rows]
    if len(ids) != len(set(ids)):
        errors.append("duplicate enchantment IDs found")
    if len(names) != len(set(names)):
        errors.append("duplicate enchantment display names found")

    expected_categories = {source for source, *_ in CATEGORY_CONFIG}
    actual_categories = {row["Category"] for row in rows}
    if actual_categories != expected_categories:
        errors.append(
            "category set mismatch: "
            f"expected {sorted(expected_categories)}, found {sorted(actual_categories)}"
        )

    counts = Counter(row["Category"] for row in rows)
    for source, _label, _file, expected_count in CATEGORY_CONFIG:
        if counts[source] != expected_count:
            errors.append(
                f"{source}: expected {expected_count} enchants, found {counts[source]}"
            )

    for row_number, row in enumerate(rows, start=2):
        for field in REQUIRED_FIELDS:
            if not row[field]:
                errors.append(f"row {row_number}: blank required field {field}")

        raw_targets = [part.strip() for part in row["Targets"].split(",") if part.strip()]
        unknown = [target for target in raw_targets if target not in TARGETS]
        if unknown:
            errors.append(
                f"row {row_number} ({row['ID']}): unknown targets {', '.join(unknown)}"
            )

    if errors:
        print("Validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)

    print(f"PASS: {len(rows)} enchantments loaded")
    print("PASS: enchantment IDs are unique")
    print("PASS: enchantment display names are unique")
    for source, label, _file, expected_count in CATEGORY_CONFIG:
        print(f"PASS: {label}: {expected_count}")
    print("PASS: all compatible-item targets are recognised")


def render_targets(raw_targets: str) -> str:
    rendered: list[str] = []
    for target in [part.strip() for part in raw_targets.split(",") if part.strip()]:
        label, filename, fallback = TARGETS[target]
        image_path = ITEMS_DIR / filename
        if image_path.exists():
            rendered.append(
                f'<img src="../assets/items/{filename}" '
                f'alt="{label}" title="{label}" class="item-icon">'
            )
        else:
            rendered.append(f'<span title="{label}">{fallback}</span>')
    return " ".join(rendered) or "—"


def table_for(rows: list[dict[str, str]]) -> str:
    lines = [
        "| Name | Summary | Max Level | Compatible Items | Incompatible With |",
        "|---|---|:---:|---|---|",
    ]

    for row in sorted(rows, key=lambda item: item["Name"].casefold()):
        lines.append(
            "| "
            + " | ".join(
                [
                    f"**{escape_table(row['Name'])}**",
                    escape_table(row["Summary"]),
                    escape_table(row["Max Level"]),
                    render_targets(row["Targets"]),
                    escape_table(row["Incompatible With"] or "—"),
                ]
            )
            + " |"
        )

    return "\n".join(lines)


def category_page(label: str, rows: list[dict[str, str]]) -> str:
    return f"""# {label} Enchantments

**{len(rows)} custom enchantments**

The table below lists every Eulogia enchantment in this category, including its effect, maximum level, compatible equipment, and conflicts.

{table_for(rows)}

---

*Generated from `data/enchantments.csv`. Do not edit this table by hand.*
"""


def complete_page(rows: list[dict[str, str]]) -> str:
    sections = [
        "# Complete Enchantment List",
        "",
        f"This catalogue contains **{len(rows)} validated Eulogia custom enchantments**.",
        "",
        "Compatible equipment is shown with item icons. Hover an icon to see its item name.",
        "",
    ]

    grouped = {category: [] for category, *_ in CATEGORY_CONFIG}
    for row in rows:
        grouped[row["Category"]].append(row)

    for source, label, _file, _expected in CATEGORY_CONFIG:
        sections.extend(
            [
                f"## {label}",
                "",
                table_for(grouped[source]),
                "",
            ]
        )

    sections.extend(
        [
            "---",
            "",
            "*Generated from `data/enchantments.csv`. Do not edit this catalogue by hand.*",
            "",
        ]
    )
    return "\n".join(sections)


def write_docs(rows: list[dict[str, str]]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    grouped = {category: [] for category, *_ in CATEGORY_CONFIG}
    for row in rows:
        grouped[row["Category"]].append(row)

    (DOCS_DIR / "list.md").write_text(
        complete_page(rows), encoding="utf-8", newline="\n"
    )
    print(f"WROTE: {DOCS_DIR / 'list.md'}")

    for source, label, filename, _expected in CATEGORY_CONFIG:
        destination = DOCS_DIR / filename
        destination.write_text(
            category_page(label, grouped[source]), encoding="utf-8", newline="\n"
        )
        print(f"WROTE: {destination}")


def main() -> None:
    rows = load_rows()
    validate(rows)
    write_docs(rows)
    print("SUCCESS: enchantment documentation generated")


if __name__ == "__main__":
    main()
