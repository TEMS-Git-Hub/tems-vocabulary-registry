#!/usr/bin/env python3
import os, html

ROOT = "public"

def listing(path):
    items = sorted(os.listdir(path))
    lis = []
    for name in items:
        # Skip hidden items if any
        if name.startswith('.'):
            continue
        href = html.escape(name)
        text = html.escape(name)
        lis.append(f'<li><a href="{href}">{text}</a></li>')
    return "<ul>" + "".join(lis) + "</ul>"

# Make an index.html for ROOT and every subdir
for dirpath, dirnames, filenames in os.walk(ROOT):
    rel = "/" if dirpath == ROOT else dirpath.replace(ROOT, "", 1) or "/"
    with open(os.path.join(dirpath, "index.html"), "w", encoding="utf-8") as f:
        f.write(f"<h2>{html.escape(rel)}</h2>\n{listing(dirpath)}\n")