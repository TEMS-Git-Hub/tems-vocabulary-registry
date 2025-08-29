#!/usr/bin/env python3
import os, re, pathlib
from collections import defaultdict

REPO_ROOT = pathlib.Path(".").resolve()
DATA_SPACES = ["tems", "tamis"]
SECTIONS = ["ontologies", "shapes", "indexes", "policies"]

ONTO_EXTS = {".ttl", ".jsonld", ".rdf", ".owl", ".xml", ".n3", ".nt"}

def list_files(root: pathlib.Path):
    for p in sorted(root.rglob("*")):
        if p.is_file():
            yield p

def md_escape(s: str) -> str:
    return s.replace("|", "\\|")

def rel_link(p: pathlib.Path) -> str:
    return f"./{p.as_posix()}"

def build_ontology_table(space_root: pathlib.Path, space: str) -> str:
    ont_root = space_root / "ontologies"
    if not ont_root.exists():
        return "_(none found)_"
    groups = defaultdict(list)
    for f in list_files(ont_root):
        if f.suffix.lower() not in ONTO_EXTS:
            continue
        parts = f.relative_to(space_root).parts  # ('ontologies','core','V0.1.0','core.ttl')
        if len(parts) < 2:
            continue
        name = parts[1] if len(parts) > 1 else "unknown"
        version = parts[2] if len(parts) > 2 and parts[2].lower().startswith("v") else "—"
        groups[(name, version)].append(f)

    if not groups:
        return "_(none found)_"

    out = [
        "| Ontology | Version | Files |",
        "|---|---:|---|",
    ]
    for (name, version), files in sorted(groups.items()):
        links = []
        for f in sorted(files):
            links.append(f"[{md_escape(f.name)}]({rel_link(f)})")
        out.append(f"| {md_escape(name)} | {md_escape(version)} | {', '.join(links)} |")
    return "\n".join(out)

def build_simple_file_table(space_root: pathlib.Path, section: str) -> str:
    sec_root = space_root / section
    if not sec_root.exists():
        return "_(none found)_"
    files = [p for p in list_files(sec_root) if p.name.lower() != "readme.md"]
    if not files:
        return "_(none found)_"
    out = [
        "| File | Path |",
        "|---|---|",
    ]
    for f in files:
        out.append(f"| {md_escape(f.name)} | [{md_escape(f.as_posix())}]({rel_link(f)}) |")
    return "\n".join(out)

def replace_block(text: str, marker_key: str, content: str) -> str:
    pat = re.compile(
        rf"(<!-- BEGIN:GENERATED {re.escape(marker_key)} -->)(.*?)(<!-- END:GENERATED {re.escape(marker_key)} -->)",
        re.DOTALL,
    )
    # Use a function to avoid backreference issues (\1, \3 showing up)
    def _repl(m):
        return m.group(1) + "\n" + content + "\n" + m.group(3)
    return pat.sub(_repl, text)

def main():
    changed = False
    for space in DATA_SPACES:
        landing = REPO_ROOT / space / "README.md"
        if not landing.exists():
            # create minimal landing with markers if missing
            landing.write_text(
                f"# {space.upper()} assets\n\n"
                f"## Ontologies\n<!-- BEGIN:GENERATED {space}/ontologies -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/ontologies -->\n\n"
                f"## Shapes\n<!-- BEGIN:GENERATED {space}/shapes -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/shapes -->\n\n"
                f"## Indexes\n<!-- BEGIN:GENERATED {space}/indexes -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/indexes -->\n\n"
                f"## Policies\n<!-- BEGIN:GENERATED {space}/policies -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/policies -->\n",
                encoding="utf-8",
            )

        text = landing.read_text(encoding="utf-8")
        updated = text

        space_root = REPO_ROOT / space

        # Ontologies
        updated = replace_block(
            updated,
            f"{space}/ontologies",
            build_ontology_table(space_root, space),
        )
        # Simple sections
        for section in ("shapes", "indexes", "policies"):
            updated = replace_block(
                updated,
                f"{space}/{section}",
                build_simple_file_table(space_root, section),
            )

        if updated != text:
            landing.write_text(updated, encoding="utf-8")
            changed = True

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
