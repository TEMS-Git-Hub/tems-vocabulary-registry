#!/usr/bin/env python3
import os, html, pathlib
from markdown import markdown

SITE_ROOT = pathlib.Path("public").resolve()
REPO_ROOT = pathlib.Path(".").resolve()
README_MD = REPO_ROOT / "README.md"

def listing(path: pathlib.Path) -> str:
    items = sorted(os.listdir(path))
    lis = []
    for name in items:
        if name.startswith('.'):
            continue
        href = html.escape(name)
        text = html.escape(name)
        lis.append(f'<li><a href="{href}">{text}</a></li>')
    return "<ul>" + "".join(lis) + "</ul>"

def make_root_index_from_readme():
    md = README_MD.read_text(encoding="utf-8")
    body = markdown(md, extensions=["fenced_code", "tables", "toc"])
    html_page = f"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vocabulary Registry</title>
<style>
  body {{ margin: 0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; line-height: 1.55; }}
  .wrap {{ max-width: 920px; margin: 2rem auto; padding: 0 1rem; }}
  .markdown-body h1, .markdown-body h2, .markdown-body h3 {{ line-height: 1.25; }}
  pre {{ overflow:auto; padding: 1rem; background:#f6f8fa; border-radius: 6px; }}
  code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
  table {{ border-collapse: collapse; }}
  th, td {{ border:1px solid #ddd; padding:.4rem .6rem; }}
  th {{ background:#f7f7f7; text-align:left; }}
</style>
<body>
  <main class="wrap markdown-body">
    {body}
  </main>
</body>
</html>"""
    (SITE_ROOT / "index.html").write_text(html_page, encoding="utf-8")

def make_subdir_indexes():
    # Create index.html in subdirectories only (skip the site root)
    for dirpath, dirnames, filenames in os.walk(SITE_ROOT):
        p = pathlib.Path(dirpath)
        if p.samefile(SITE_ROOT):
            continue
        rel = "/" + p.relative_to(SITE_ROOT).as_posix()
        (p / "index.html").write_text(
            f"<h2>{html.escape(rel)}</h2>\n{listing(p)}\n", encoding="utf-8"
        )

def main():
    make_root_index_from_readme()
    make_subdir_indexes()

if __name__ == "__main__":
    main()
