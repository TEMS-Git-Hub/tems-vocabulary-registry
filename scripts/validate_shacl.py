#!/usr/bin/env python
import os, sys
from pyshacl import validate
from rdflib import Graph

def find_files(root, pattern):
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(pattern):
                yield os.path.join(dirpath, fn)

def main():
    # naive pass: for each shapes TTL file, validate each ontology TTL
    ont_ttls = list(find_files(".", ".ttl"))
    ont_ttls = [f for f in ont_ttls if "/ontologies/" in f]
    shape_ttls = list(find_files("tems/shapes", ".ttl")) + list(find_files("tamis/shapes", ".ttl"))
    had_error = False

    if not shape_ttls:
        print("No shapes found, skipping SHACL validation.")
        return 0

    for shapes_path in shape_ttls:
        shapes = Graph()
        shapes.parse(shapes_path, format="turtle")
        for ttl in ont_ttls:
            data = Graph()
            data.parse(ttl, format="turtle")
            conforms, results_graph, results_text = validate(
                data_graph=data, shacl_graph=shapes, inference="rdfs", abort_on_first=False, serialize_report_graph=True
            )
            print(f"\n=== SHACL check ===\nShapes: {shapes_path}\nData  : {ttl}\nConforms: {conforms}\n")
            if not conforms:
                print(results_text)
                had_error = True
    return 1 if had_error else 0

if __name__ == "__main__":
    sys.exit(main())
