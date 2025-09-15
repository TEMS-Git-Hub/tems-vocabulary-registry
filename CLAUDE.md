# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **Vocabulary Registry** for TEMS and TAMIS dataspaces that manages ontologies, shapes, indexes, and policies. The repository provides:

- TTL-first approach with automated serialization to JSON-LD and RDF/XML
- Automated RDF validation and SHACL constraint checking
- CI/CD publishing to GitHub Pages
- Persistent URI resolution via w3id.org
- DCAT catalog generation

## Architecture

The repository is structured as a monorepo with two dataspaces:
- `tems/` - TEMS dataspace assets
- `tamis/` - TAMIS dataspace assets  

Each dataspace contains:
- `ontologies/` - Core ontologies in TTL format, organized by name and version (e.g., `core/0.1.0/core.ttl`)
- `shapes/` - SHACL constraint files in TTL format, organized by name and version (e.g., `media-objects/0.1.0/media-objects.ttl`)
- `indexes/` - Facet/search descriptors in TTL format, organized by name and version (e.g., `media-objects/0.1.0/media-objects.ttl`)
- `policies/` - ODRL policies in TTL format, organized by name and version (e.g., `media/0.1.0/media.ttl`)
- `open-api/` - API specifications in TTL format, organized by name and version (e.g., `media-objects/0.1.0/media-objects.ttl`)

The `public/` directory contains the built static site deployed to GitHub Pages.

## Key Commands

### Validation
```bash
# Validate TTL syntax using Apache Jena (via Docker)
docker run --rm -v "$PWD":/work stain/jena riot --validate /work/tems/ontologies/core/0.1.0/core.ttl

# Run SHACL validation against all ontologies
python scripts/validate_shacl.py
```

### Serialization  
```bash
# Convert TTL files to JSON-LD and RDF/XML formats
./scripts/serialize.sh
# OR using Python script:
python scripts/serialize_from_ttl.py
```

### Site Generation
```bash
# Generate dataspace README indexes (auto-populated tables)
python scripts/generate_dataspace_indexes.py

# Generate static HTML site 
python scripts/generate_site.py

# Generate DCAT catalog
python scripts/generate_dcat_catalog.py
```

### Full CI/CD Simulation
```bash
# Run the complete CI pipeline locally
python scripts/validate_shacl.py &&
python scripts/serialize_from_ttl.py &&
python scripts/generate_dataspace_indexes.py &&
rm -rf public && mkdir -p public &&
cp -R tems tamis public/ &&
python scripts/generate_site.py &&
python scripts/generate_dcat_catalog.py
```

## Dependencies

Python dependencies (install via pip):
- `pyshacl` - SHACL validation
- `rdflib` - RDF parsing/serialization  
- `rdflib-jsonld` - JSON-LD support
- `markdown` - Markdown to HTML conversion

Apache Jena (via Docker):
- `stain/jena` - RDF validation and serialization

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) automatically:

1. **Validates** all TTL files with Apache Jena riot
2. **Validates** ontologies against SHACL shapes  
3. **Serializes** TTL files to JSON-LD and RDF/XML
4. **Updates** dataspace README files with asset tables
5. **Builds** static site in `public/` directory
6. **Generates** DCAT catalog at `docs/catalog.jsonld`
7. **Deploys** to GitHub Pages (main branch only)
8. **Creates** semantic version releases

## File Patterns

All source files are in TTL format:
- Ontologies: `{dataspace}/ontologies/{name}/{x.y.z}/{name}.ttl`
- Shapes: `{dataspace}/shapes/{name}/{x.y.z}/{name}.ttl`
- Indexes: `{dataspace}/indexes/{name}/{x.y.z}/{name}.ttl`
- Policies: `{dataspace}/policies/{name}/{x.y.z}/{name}.ttl`
- OpenAPI specs: `{dataspace}/open-api/{name}/{x.y.z}/{name}.ttl`
- Generated serializations: `{name}.jsonld`, `{name}.rdf.xml` (automatically generated alongside TTL)
- Auto-generated tables in: `tems/README.md`, `tamis/README.md`
- Static site output: `public/` directory

## Important Notes

- **TTL-first approach**: All source files must be in Turtle (TTL) format
- The `tems/README.md` and `tamis/README.md` files contain auto-generated tables - do not edit the table sections manually
- All files should be placed in version-specific directories: `{section}/{name}/{version}/{name}.ttl`
- CI automatically generates and commits JSON-LD and RDF/XML serializations alongside TTL sources
- CI automatically commits updated README tables
- SHACL validation runs against TTL files in shapes directories
- All changes trigger validation; only main branch deployments create releases