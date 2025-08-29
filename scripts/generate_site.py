#!/usr/bin/env python3
import os, re, html, pathlib
from markdown import markdown

REPO_ROOT = pathlib.Path(".").resolve()
SITE_ROOT = pathlib.Path("public").resolve()

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vocabulary Registry</title>
<link rel="preconnect" href="https://cdn.jsdelivr.net">
<style>
  body { margin:0; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; line-height:1.55; }
  .wrap { max-width: 980px; margin: 2rem auto; padding: 0 1rem; }
  pre { overflow:auto; padding:1rem; background:#f6f8fa; border-radius:6px; }
  code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
  table { border-collapse: collapse; }
  th, td { border:1px solid #ddd; padding:.4rem .6rem; }
  th { background:#f7f7f7; text-align:left; }
</style>
<body>
  <main class="wrap markdown-body">
    {{BODY}}
  </main>
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>
  (function(){
    // Convert ```mermaid code fences to <div class="mermaid">...</div>
    document.querySelectorAll('pre code.language-mermaid').forEach(function(code){
      var pre = code.parentElement;
      var d = document.createElement('div');
      d.className = 'mermaid';
      d.textContent = code.textContent;
      pre.replaceWith(d);
    });
    mermaid.initialize({ startOnLoad: true, securityLevel: 'loose' });
  })();
  </script>
</body>
</html>
"""

def md_to_html(md_text: str) -> str:
    body = markdown(md_text, extensions=["fenced_code", "tables", "toc"])
    # Rewrite README links to folder roots in the built site
    body = re.sub(r'href="\.?/tems/README\.md"', 'href="tems/"', body)
    body = re.sub(r'href="\.?/tamis/README\.md"', 'href="tamis/"', body)
    return HTML_TEMPLATE.replace("{{BODY}}", body)

def write_html_from_readme(src_md: pathlib.Path, dst_html: pathlib.Path):
    md = src_md.read_text(encoding="utf-8")
    dst_html.parent.mkdir(parents=True, exist_ok=True)
    dst_html.write_text(md_to_html(md), encoding="utf-8")

def listing(path: pathlib.Path) -> str:
    items = sorted(os.listdir(path))
    lis = []
    for name in items:
        if name.startswith('.'): continue
        lis.append(f'<li><a href="{html.escape(name)}">{html.escape(name)}</a></li>')
    return "<ul>" + "".join(lis) + "</ul>"

def write_dir_listing(dir_path: pathlib.Path):
    rel = "/" + dir_path.relative_to(SITE_ROOT).as_posix()
    (dir_path / "index.html").write_text(
        f"<h2>{html.escape(rel)}</h2>\n{listing(dir_path)}\n", encoding="utf-8"
    )

def main():
    # Root README -> /index.html (Mermaid-enabled)
    write_html_from_readme(REPO_ROOT / "README.md", SITE_ROOT / "index.html")

    # TEMS/TAMIS READMEs -> /tems/index.html and /tamis/index.html
    for ds in ("tems", "tamis"):
        src = REPO_ROOT / ds / "README.md"
        if src.exists():
            write_html_from_readme(src, SITE_ROOT / ds / "index.html")

    # Simple directory listings for deeper folders
    skip = {
        SITE_ROOT.as_posix(),
        (SITE_ROOT / 'tems').as_posix(),
        (SITE_ROOT / 'tamis').as_posix(),
    }
    for dirpath, dirnames, filenames in os.walk(SITE_ROOT):
        p = pathlib.Path(dirpath)
        if p.as_posix() in skip:
            continue
        if (p / "index.html").exists():
            continue
        write_dir_listing(p)

if __name__ == "__main__":
    main()
