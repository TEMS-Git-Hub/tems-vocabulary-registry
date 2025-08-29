#!/usr/bin/env python3
import re, pathlib
from collections import defaultdict

REPO_ROOT = pathlib.Path(".").resolve()
DATA_SPACES = ["tems", "tamis"]
SECTIONS = ["ontologies", "shapes", "indexes", "policies"]

ONTO_EXTS = {".ttl", ".jsonld", ".rdf", ".owl", ".xml", ".n3", ".nt"}

def rglob_files(root: pathlib.Path):
    # Yield files under root (absolute Paths)
    for p in sorted(root.rglob("*")):
        if p.is_file():
            yield p

def md_escape(s: str) -> str:
    return s.replace("|", "\\|")

def rel_link_from_space(space_root: pathlib.Path, abs_path: pathlib.Path) -> str:
    """
    Build a README link relative to the dataspace root.
    Example:
      space_root = /.../repo/tems
      abs_path   = /.../repo/tems/indexes/media.jsonld
      -> ./indexes/media.jsonld
    """
    rel = abs_path.relative_to(space_root).as_posix()
    return f"./{rel}"

def build_ontology_table(space_root: pathlib.Path, space: str) -> str:
    ont_root = space_root / "ontologies"
    if not ont_root.exists():
        return "_(none found)_"

    groups = defaultdict(list)  # (name, version) -> [abs_file]
    for f_abs in rglob_files(ont_root):
        if f_abs.suffix.lower() not in ONTO_EXTS:
            continue
        parts = f_abs.relative_to(space_root).parts  # ('ontologies','core','V0.1.0','core.ttl')
        if len(parts) < 2:
            continue
        name = parts[1] if len(parts) > 1 else "unknown"
        version = parts[2] if len(parts) > 2 and parts[2].lower().startswith("v") else "—"
        groups[(name, version)].append(f_abs)

    if not groups:
        return "_(none found)_"

    out = [
        "| Ontology | Version | Files |",
        "|---|---:|---|",
    ]
    for (name, version), files in sorted(groups.items()):
        files = sorted(files)
        links = [f"[{md_escape(f_abs.name)}]({rel_link_from_space(space_root, f_abs)})"
                 for f_abs in files]
        out.append(f"| {md_escape(name)} | {md_escape(version)} | {', '.join(links)} |")
    return "\n".join(out)

def build_simple_file_table(space_root: pathlib.Path, section: str) -> str:
    sec_root = space_root / section
    if not sec_root.exists():
        return "_(none found)_"
    files = [f_abs for f_abs in rglob_files(sec_root) if f_abs.name.lower() != "readme.md"]
    if not files:
        return "_(none found)_"
    files = sorted(files)
    out = [
        "| File | Path |",
        "|---|---|",
    ]
    for f_abs in files:
        rel_href = rel_link_from_space(space_root, f_abs)
        out.append(f"| {md_escape(f_abs.name)} | [{md_escape(rel_href[2:])}]({rel_href}) |")
    return "\n".join(out)

def replace_block(text: str, marker_key: str, content: str) -> str:
    pat = re.compile(
        rf"(<!-- BEGIN:GENERATED {re.escape(marker_key)} -->)(.*?)(<!-- END:GENERATED {re.escape(marker_key)} -->)",
        re.DOTALL,
    )
    def _repl(m):
        return m.group(1) + "\n" + content + "\n" + m.group(3)
    return pat.sub(_repl, text)

def ensure_landing(space: str, landing_path: pathlib.Path):
    if landing_path.exists():
        return
    landing_path.write_text(
        f"# {space.upper()} assets\n\n"
        f"## Ontologies\n<!-- BEGIN:GENERATED {space}/ontologies -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/ontologies -->\n\n"
        f"## Shapes\n<!-- BEGIN:GENERATED {space}/shapes -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/shapes -->\n\n"
        f"## Indexes\n<!-- BEGIN:GENERATED {space}/indexes -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/indexes -->\n\n"
        f"## Policies\n<!-- BEGIN:GENERATED {space}/policies -->\n_(CI will populate)_\n<!-- END:GENERATED {space}/policies -->\n",
        encoding="utf-8",
    )

def main():
    for space in DATA_SPACES:
        space_root = REPO_ROOT / space
        landing = space_root / "README.md"
        ensure_landing(space, landing)

        original = landing.read_text(encoding="utf-8")
        updated = original

        updated = replace_block(
            updated, f"{space}/ontologies", build_ontology_table(space_root, space)
        )
        for section in ("shapes", "indexes", "policies"):
            updated = replace_block(
                updated, f"{space}/{section}", build_simple_file_table(space_root, section)
            )

        if updated != original:
            landing.write_text(updated, encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
