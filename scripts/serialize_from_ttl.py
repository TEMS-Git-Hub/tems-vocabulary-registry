#!/usr/bin/env python3
"""
Convert every *.ttl ontology into JSON-LD (*.jsonld) and RDF/XML (*.rdf.xml),
side-by-side with the source .ttl.

Scans:
  tems/**/ontologies/**/*.ttl
  tamis/**/ontologies/**/*.ttl
"""
import sys, pathlib
from rdflib import Graph

TTL_GLOBS = [
    "tems/**/ontologies/**/*.ttl",
    "tamis/**/ontologies/**/*.ttl",
]

# A compact context for nicer JSON-LD (adjust as you add prefixes)
JSONLD_CONTEXT = {
  "@context": {
    "tems":   "https://w3id.org/tems/core#",
    "schema": "http://schema.org/",
    "dct":    "http://purl.org/dc/terms/",
    "owl":    "http://www.w3.org/2002/07/owl#",
    "rdfs":   "http://www.w3.org/2000/01/rdf-schema#",
    "xsd":    "http://www.w3.org/2001/XMLSchema#"
  }
}

def serialize_one(ttl: pathlib.Path) -> None:
    g = Graph()
    g.parse(ttl.as_posix(), format="turtle")

    jsonld_path = ttl.with_suffix(".jsonld")
    rdfxml_path = ttl.with_suffix(".rdf.xml")

    # JSON-LD (compacted with our context)
    jsonld_str = g.serialize(
        format="json-ld",
        context=JSONLD_CONTEXT,
        auto_compact=True,
        indent=2,
    )
    if isinstance(jsonld_str, bytes):
        jsonld_str = jsonld_str.decode("utf-8")
    jsonld_path.write_text(jsonld_str, encoding="utf-8")

    # RDF/XML (pretty abbreviated)
    g.serialize(destination=rdfxml_path.as_posix(), format="xml")

    print(f"✓ {ttl} → {jsonld_path.name}, {rdfxml_path.name}")

def main() -> int:
    root = pathlib.Path(".").resolve()
    files = []
    for pattern in TTL_GLOBS:
        files.extend(root.glob(pattern))
    files = sorted(p for p in files if p.is_file())

    if not files:
        print("No ontology .ttl files found.")
        return 0

    for ttl in files:
        try:
            serialize_one(ttl)
        except Exception as e:
            print(f"ERROR converting {ttl}: {e}", file=sys.stderr)
            return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
