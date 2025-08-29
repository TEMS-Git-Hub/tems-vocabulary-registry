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
    C[ContributorsPRs]:::actor
    M[Maintainers]:::actor
    U1[Data Space Apps<br/>UIs, Search, Forms]:::client
    U2[Connectors / Gateways<br/>/public APIs]:::client
    U3[Validation Services<br/>ingestion/data-plane]:::client
  end

  subgraph Core["Vocabulary Registry (Monorepo)"]
    R[Monorepo: /tems & /tamis<br/>ontologies · shapes · indexes · policies]:::repo
  end

  subgraph CI["CI / CD"]
    V[RDF/SHACL Validation]:::ci
    B[Build & Serialize<br/>ttl · json-ld · rdf-xml]:::ci
    T[Tag & Version - semver]:::ci
    P[Publish Static Artifacts]:::ci
  end

  subgraph Dist["Distribution"]
    H[Static Hosting - gh-pages/S3/Pages]:::dist
    CDN[CDN]:::dist
    W[Persistent IDs Resolver<br/>w3id.org]:::dist
  end

  C -->|Pull Requests - new/updated vocabs| R
  M -->|Review/Merge| R
  R --> V --> B --> T --> P --> H --> CDN
  W -->|HTTP 302| CDN

  U1 -->|Fetch contexts/vocabs<br/>to auto-generate UI facets| CDN
  U2 -->|Fetch shapes to constrain APIs| CDN
  U3 -->|Fetch shapes/policies<br/>to validate payloads| CDN

  classDef actor fill:#f7f7ff,stroke:#556,stroke-width:1px
  classDef repo fill:#eef,stroke:#447,stroke-width:1px
  classDef ci fill:#efe,stroke:#484,stroke-width:1px
  classDef dist fill:#fee,stroke:#844,stroke-width:1px
  classDef client fill:#fff,stroke:#777,stroke-dasharray:3 3
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
