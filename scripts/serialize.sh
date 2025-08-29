#!/usr/bin/env bash
set -euo pipefail

# Requires Apache Jena 'riot' in PATH
# Converts every .ttl ontology to JSON-LD (.jsonld) and RDF/XML (.rdf.xml) next to it.

shopt -s globstar nullglob

convert_file () {
  local ttl="$1"
  local base="${ttl%.ttl}"
  echo "Serializing $ttl"
  riot --output=jsonld "$ttl" > "${base}.jsonld"
  riot --output=rdfxml-abbrev "$ttl" > "${base}.rdf.xml"
}

for ttl in tems/**/ontologies/**/*.ttl tamis/**/ontologies/**/*.ttl; do
  convert_file "$ttl"
done

echo "Done."
