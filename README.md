# Vocabulary Registry — First Iteration

This repository hosts the **Vocabulary Registry** for **TEMS** and **TAMIS**.

It provides:

- Sharing of **ontologies and vocabularies** (multi-serialization: TTL, JSON-LD, RDF/XML).
- Sharing of **TEMS-supported policies** and their shapes (e.g., ODRL + SHACL).
- Sharing of **shapes** to constrain APIs and generate UIs/facets.
- Automatic **validation, serialization, versioning, and publishing** via CI/CD.
- **Permanent URIs** (e.g., via w3id.org) for stability.

> GitHub renders Mermaid diagrams in **Discussions**, **Issues**, **PRs**, and **README.md**.

---

## Architecture (Context)

```mermaid
flowchart LR
  subgraph Users["Actors & Clients"]
    C[Contributors (PRs)]
    M[Maintainers]
    U1[Data Space Apps<br/>(UIs, Search, Forms)]
    U2[Connectors / Gateways<br/>(/public APIs)]
    U3[Validation Services<br/>(ingestion/data-plane)]
  end

  subgraph Core["Vocabulary Registry (Monorepo)"]
    R[Monorepo: /tems & /tamis<br/>ontologies · shapes · indexes · policies]
  end

  subgraph CI["CI / CD"]
    V[RDF/SHACL Validation]
    B[Build & Serialize]
    T[Semver Auto-Version]
    P[Publish Static Artifacts]
  end

  subgraph Dist["Distribution"]
    H[Static Hosting]
    CDN[CDN]
    W[Persistent IDs (w3id.org)]
  end

  C --> R
  M --> R
  R --> V --> B --> T --> P --> H --> CDN
  W --> CDN
  U1 --> CDN
  U2 --> CDN
  U3 --> CDN
```

---

## CI/CD Flow

```mermaid
sequenceDiagram
  actor Dev as Contributor
  participant Repo as Registry Repo
  participant CI as CI Runner
  participant Host as Hosting/CDN
  participant W3 as w3id.org

  Dev->>Repo: PR with ontology update
  Repo-->>CI: Trigger CI (PR)
  CI->>CI: Validate RDF/SHACL
  CI-->>Dev: Status (pass/fail)
  Dev->>Repo: Merge to main
  Repo-->>CI: Trigger CI (main)
  CI->>CI: Build serializations
  CI->>CI: Create release (semver)
  CI->>Host: Publish artifacts
  W3-->>Host: Redirect stable IDs
```

---

## Folder Structure

```text
/tems
  /ontologies
    /core/Vx.x.x/*.ttl|.jsonld|.xml
  /indexes
    media-objects.jsonld
    3d-objects.jsonld
  /shapes
    media-objects.jsonld
    3d-objects.jsonld
  /policies
    eu.jsonld
    media.jsonld
/tamis
  /ontologies …
  /indexes …
  /shapes …
  /policies …
```

---

## Usage

- Put ontology sources in Turtle under `*/ontologies/*/Vx.y.z/*.ttl`.
- CI will:
  1) validate TTL syntax (Apache Jena **riot**),
  2) run **pySHACL** against shapes,
  3) serialize **.ttl** → **.jsonld** and **.rdf.xml** next to the source,
  4) (optional) create a semver release,
  5) publish `public/` to GitHub Pages.

---

## Local Dev

```bash
# Validate TTL
docker run --rm -v "$PWD":/work stain/jena riot --validate /work/tems/ontologies/core/V0.1.0/core.ttl

# Serialize (requires Apache Jena locally)
./scripts/serialize.sh
```
