import os, re, pathlib
from collections import defaultdict

REPO_ROOT = pathlib.Path(".").resolve()
DATA_SPACES = ["tems", "tamis"]
SECTIONS = ["ontologies", "shapes", "indexes", "policies"]
# Treat as ontology serializations (for compact display):
ONTO_EXTS = {".ttl", ".jsonld", ".rdf", ".owl", ".xml", ".rdfxml", ".n3", ".nt"}
# Everything else shows as a plain file row.

def list_files(root):
  files = []
  for p in sorted(root.rglob("*")):
    if p.is_file():
      files.append(p.relative_to(REPO_ROOT))
  return files

def make_rel_link(path):
  return f"./{path.as_posix()}"

def md_escape(s):
  return s.replace("|", "\\|")

def build_ontology_table(section_root):
  """
  Group by top-level ontology name and version directory if present.
  Example tree:
    ontologies/core/V0.1.0/core.ttl
    ontologies/core/V0.1.0/core.jsonld
  Table columns: Ontology | Version | Files
  """
  rows = []
  # Find all files under ontologies/
  for file in list_files(section_root):
    ext = file.suffix.lower()
    if ext not in ONTO_EXTS:
      continue
    parts = file.parts
    # Expect: <dataspace>/ontologies/<name>/Vx.y.z/<file>
    # Be lenient if version folder is missing.
    try:
      name_idx = parts.index("ontologies") + 1
    except ValueError:
      continue
    name = parts[name_idx] if len(parts) > name_idx else "unknown"
    version = None
    if len(parts) > name_idx + 1 and parts[name_idx+1].lower().startswith("v"):
      version = parts[name_idx+1]
    # Collect all siblings with same name+version
    rows.append( (name, version or "—", file) )

  # Merge files per (name,version)
  grouped = defaultdict(list)
  for name, version, file in rows:
    grouped[(name, version)].append(file)

  if not grouped:
    return "_(none found)_"

  # Build table
  out = ["| Ontology | Version | Files |",
          "|---|---:|---|"]
  for (name, version), files in sorted(grouped.items()):
    links = []
    # group by serialization extension for nicer display
    by_ext = defaultdict(list)
    for f in files:
      by_ext[f.suffix.lower()].append(f)
    for ext, flist in sorted(by_ext.items()):
      for f in sorted(flist):
        label = f.name
        links.append(f"[{md_escape(label)}]({make_rel_link(f)})")
    out.append(f"| {md_escape(name)} | {md_escape(version)} | " + ", ".join(links) + " |")
  return "\n".join(out)

def build_simple_file_table(section_root):
  """
  Flat table: File | Path
  """
  files = [p for p in list_files(section_root) if p.is_file()]
  # Filter out README.md we're maintaining
  files = [p for p in files if p.name.lower() != "readme.md"]
  if not files:
    return "_(none found)_"
  out = ["| File | Path |",
          "|---|---|"]
  for f in files:
    out.append(f"| {md_escape(f.name)} | [{md_escape(f.as_posix())}]({make_rel_link(f)}) |")
  return "\n".join(out)

def replace_block(text, marker_key, content):
  pattern = re.compile(
    rf"(<!-- BEGIN:GENERATED {re.escape(marker_key)} -->)(.*?)(<!-- END:GENERATED {re.escape(marker_key)} -->)",
    re.DOTALL
  )
  return pattern.sub(rf"\\1\n{content}\n\\3", text)

changed = False
for space in DATA_SPACES:
  landing = REPO_ROOT / space / "README.md"
  if not landing.exists():
    continue
  with open(landing, "r", encoding="utf-8") as fh:
    original = fh.read()
  updated = original

  for section in SECTIONS:
    section_root = REPO_ROOT / space / section
    marker = f"{space}/{section}"
    if not section_root.exists():
      # keep placeholder
      continue
    if section == "ontologies":
      table = build_ontology_table(section_root)
    else:
      table = build_simple_file_table(section_root)
    updated = replace_block(updated, marker, table)

  if updated != original:
    with open(landing, "w", encoding="utf-8") as fh:
      fh.write(updated)
    changed = True

# Optional: also write a tiny index at the dataspace root linking to subfolders
for space in DATA_SPACES:
  space_readme = REPO_ROOT / space / "README.md"
  # ensure top intro exists (non-destructive)
  if not space_readme.exists():
    space_readme.write_text(f"# {space.upper()} assets\\n\\n", encoding="utf-8")

# Exit code 0 always; an action down the line will commit if files changed.