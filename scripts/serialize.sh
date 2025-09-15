#!/usr/bin/env bash
set -euo pipefail
shopt -s globstar nullglob

# Wrapper to call riot either from PATH or via Docker
riot_cmd () {
  if command -v riot >/dev/null 2>&1; then
    riot "$@"
  else
    docker run --rm -v "$PWD":/rdf -w /rdf stain/jena riot "$@"
  fi
}

convert_file () {
  local ttl="$1"
  local base="${ttl%.ttl}"
  echo "Serializing $ttl"
  riot_cmd --output=jsonld "$ttl" > "${base}.jsonld"
  riot_cmd --output=rdfxml-abbrev "$ttl" > "${base}.rdf.xml"
}

files=( tems/**/*.ttl tamis/**/*.ttl )
if ((${#files[@]})); then
  for ttl in "${files[@]}"; do
    convert_file "$ttl"
  done
else
  echo "No .ttl files found; nothing to serialize."
fi

echo "Done."
