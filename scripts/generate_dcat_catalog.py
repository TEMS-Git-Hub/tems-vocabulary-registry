#!/usr/bin/env python3
"""
Generate a DCAT JSON-LD catalog for the repo.

- Scans: tems/{ontologies,shapes,indexes,policies} and tamis/{...}
- Ontologies are grouped by: {dataspace}/{ontologies}/{name}/{version}/
  Each file in that folder becomes a dcat:Distribution with mediaType + format.
- Shapes / Indexes / Policies: one dcat:Dataset per file (simpler, usually single-serialization).

Outputs:
  docs/catalog.jsonld    (committed to repo)
  (your workflow should also copy it to public/catalog.jsonld for GitHub Pages)

You can override the public base URL by setting env PAGES_BASE_URL (e.g. custom domain).
A raw download base is derived from RAW_BASE_URL if provided (else built from GitHub env).
"""

import os, sys, json, pathlib, datetime
from collections import defaultdict

REPO = os.environ.get("GITHUB_REPOSITORY")  # "owner/repo"
REF_NAME = os.environ.get("GITHUB_REF_NAME", "main")
OWNER = os.environ.get("GITHUB_REPOSITORY_OWNER", (REPO.split("/")[0] if REPO else ""))

# Public site base (for human-friendly URLs)
PAGES_BASE_URL = os.environ.get("PAGES_BASE_URL")  # e.g. https://org.github.io/repo
if not PAGES_BASE_URL and REPO:
    owner, repo = REPO.split("/")
    PAGES_BASE_URL = f"https://{owner}.github.io/{repo}"
PAGES_BASE_URL = PAGES_BASE_URL.rstrip("/")

# Raw download base (for programmatic file fetch)
RAW_BASE_URL = os.environ.get("RAW_BASE_URL")
if not RAW_BASE_URL and REPO:
    RAW_BASE_URL = f"https://raw.githubusercontent.com/{REPO}/{REF_NAME}"
RAW_BASE_URL = RAW_BASE_URL.rstrip("/")

ROOT = pathlib.Path(".").resolve()
OUT = ROOT / "docs" / "catalog.jsonld"
OUT.parent.mkdir(parents=True, exist_ok=True)

DATA_SPACES = ["tems", "tamis"]
SECTIONS = ["ontologies", "shapes", "indexes", "policies", "open-api"]

# MIME guess for RDF-ish files and OpenAPI
MT_BY_EXT = {
    ".ttl": "text/turtle",
    ".jsonld": "application/ld+json",
    ".rdf": "application/rdf+xml",
    ".owl": "application/rdf+xml",
    ".xml": "application/rdf+xml",
    ".n3": "text/n3",
    ".nt": "application/n-triples",
    ".yaml": "application/x-yaml",
    ".yml": "application/x-yaml",
    ".json": "application/json",
}

def rel_to_url(rel_path: pathlib.Path) -> str:
    # Human-friendly site link (works on GitHub Pages)
    return f"{PAGES_BASE_URL}/{rel_path.as_posix().lstrip('./')}"

def rel_to_raw(rel_path: pathlib.Path) -> str:
    # Direct download link
    return f"{RAW_BASE_URL}/{rel_path.as_posix().lstrip('./')}"

def list_files(root: pathlib.Path):
    for p in sorted(root.rglob("*")):
        if p.is_file():
            yield p

def build_ontology_datasets(space_root: pathlib.Path, space_name: str):
    """
    Group by {space}/ontologies/{name}/{version}/ and create one dcat:Dataset per group.
    Each file in the version folder becomes a dcat:Distribution.
    """
    datasets = []
    ont_root = space_root / "ontologies"
    if not ont_root.exists():
        return datasets

    groups = defaultdict(list)
    for f in list_files(ont_root):
        parts = f.relative_to(space_root).parts  # e.g. ('ontologies','core','0.1.0','core.ttl')
        if len(parts) < 4:  # must have at least ontologies/name/version/file
            continue
        name = parts[1]
        version = parts[2]  # version without V prefix
        groups[(name, version)].append(f)

    for (name, version), files in sorted(groups.items()):
        # Dataset ID = folder URL
        if version == "—":
            ds_rel = space_root / "ontologies" / name
            title = f"{space_name.upper()} ontology: {name}"
        else:
            ds_rel = space_root / "ontologies" / name / version
            title = f"{space_name.upper()} ontology: {name} ({version})"

        distributions = []
        for f in sorted(files):
            ext = f.suffix.lower()
            mt = MT_BY_EXT.get(ext)
            distributions.append({
                "@id": rel_to_url(f.relative_to(ROOT)),
                "@type": "dcat:Distribution",
                "dct:title": f.name,
                "dcat:accessURL": {"@id": rel_to_url(f.relative_to(ROOT))},
                "dcat:downloadURL": {"@id": rel_to_raw(f.relative_to(ROOT))},
                **({"dcat:mediaType": mt, "dct:format": mt} if mt else {}),
            })

        dataset = {
            "@id": rel_to_url(ds_rel.relative_to(ROOT)) + "/",
            "@type": "dcat:Dataset",
            "dct:title": title,
            "dct:identifier": f"{space_name}:{name}:{version}",
            "dcat:keyword": [space_name, "ontologies", name],
            **({"dct:hasVersion": version} if version not in (None, "—") else {}),
            "dcat:distribution": distributions,
        }
        datasets.append(dataset)
    return datasets

def build_single_file_datasets(space_root: pathlib.Path, space_name: str, section: str):
    """
    For shapes / indexes / policies: group by {name}/{version}/ and create one dataset per group.
    """
    datasets = []
    sec_root = space_root / section
    if not sec_root.exists():
        return datasets

    groups = defaultdict(list)
    for f in list_files(sec_root):
        parts = f.relative_to(space_root).parts  # e.g. ('shapes','media-objects','0.1.0','media-objects.jsonld')
        if len(parts) < 4:  # must have at least section/name/version/file
            continue
        name = parts[1]
        version = parts[2]
        groups[(name, version)].append(f)

    for (name, version), files in sorted(groups.items()):
        # Dataset ID = folder URL (use first file's directory)
        folder_rel = files[0].parent.relative_to(ROOT)
        dataset_id = rel_to_url(folder_rel)
        
        title = f"{space_name.upper()} {section[:-1]}: {name} ({version})"
        distributions = []
        for f in sorted(files):
            rel = f.relative_to(ROOT)
            ext = f.suffix.lower()
            mt = MT_BY_EXT.get(ext, "application/octet-stream")
            distributions.append({
                "@id": rel_to_url(rel),
                "@type": "dcat:Distribution",
                "dct:title": f.name,
                "dcat:accessURL": {"@id": rel_to_url(rel)},
                "dcat:downloadURL": {"@id": rel_to_raw(rel)},
                "dcat:mediaType": mt,
                "dct:format": mt,
            })
        
        datasets.append({
            "@id": dataset_id,
            "@type": "dcat:Dataset",
            "dct:title": title,
            "dct:identifier": f"{space_name}:{section}:{name}:{version}",
            "dct:hasVersion": version,
            "dcat:keyword": [space_name, section, name],
            "dcat:distribution": distributions,
        })
    return datasets

def main():
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    catalog_datasets = []

    for space in DATA_SPACES:
        space_root = ROOT / space
        if not space_root.exists():
            continue
        # ontologies grouped
        catalog_datasets.extend(build_ontology_datasets(space_root, space))
        # other sections per-file
        for section in ("shapes", "indexes", "policies", "open-api"):
            catalog_datasets.extend(build_single_file_datasets(space_root, space, section))

    catalog = {
        "@context": {
            "@vocab": "http://www.w3.org/ns/dcat#",
            "dcat": "http://www.w3.org/ns/dcat#",
            "dct": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
            "foaf": "http://xmlns.com/foaf/0.1/",
            "schema": "http://schema.org/",
            "id": "@id",
            "type": "@type"
        },
        "id": f"{PAGES_BASE_URL}/catalog.jsonld",
        "type": "dcat:Catalog",
        "dct:title": "TEMS / TAMIS Vocabulary Registry",
        "dct:description": "DCAT catalog of ontologies, shapes, indexes, and policies published from this repository.",
        "dct:issued": now,
        "dct:modified": now,
        "dct:publisher": {
            "type": "foaf:Agent",
            "foaf:name": "TEMS project"
        },
        "dcat:dataset": catalog_datasets
    }

    OUT.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")

if __name__ == "__main__":
    sys.exit(main())
