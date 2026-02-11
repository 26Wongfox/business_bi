#!/usr/bin/env python3
from pathlib import Path
import csv
import html
import markdown
from playwright.sync_api import sync_playwright

ROOT = Path('product/template_shop')
HTML_DIR = ROOT / 'html_pages'
IMG_DIR = ROOT / 'jpg_pages'
HTML_DIR.mkdir(parents=True, exist_ok=True)
IMG_DIR.mkdir(parents=True, exist_ok=True)

CSS = """
:root { --bg:#f6f8fb; --card:#ffffff; --text:#1f2937; --muted:#6b7280; --line:#d1d5db; }
body { margin:0; background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',Arial,sans-serif; }
.wrap { max-width:980px; margin:24px auto; padding:0 16px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:24px; box-shadow:0 2px 8px rgba(0,0,0,.04); }
h1,h2,h3 { line-height:1.3; margin:1em 0 .5em; }
p,li { line-height:1.7; }
code,pre { background:#f3f4f6; border-radius:6px; }
pre { padding:12px; overflow:auto; }
table { width:100%; border-collapse:collapse; margin:12px 0; font-size:14px; }
th,td { border:1px solid var(--line); padding:8px 10px; text-align:left; vertical-align:top; }
th { background:#f9fafb; }
.small { color:var(--muted); font-size:12px; margin-top:8px; }
"""


def page_shell(title: str, body_html: str) -> str:
    return f"""<!doctype html>
<html lang=\"zh-CN\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><div class=\"wrap\"><div class=\"card\">{body_html}<p class=\"small\">Generated from local template file.</p></div></div></body></html>"""


def md_to_html(src: Path, dst: Path):
    text = src.read_text(encoding='utf-8')
    body = markdown.markdown(text, extensions=['fenced_code', 'tables', 'toc'])
    dst.write_text(page_shell(src.name, body), encoding='utf-8')


def csv_to_html(src: Path, dst: Path):
    with src.open('r', encoding='utf-8') as f:
        rows = list(csv.reader(f))
    if not rows:
        body = '<p>Empty CSV</p>'
    else:
        head = rows[0]
        body_rows = rows[1:]
        thead = '<tr>' + ''.join(f'<th>{html.escape(c)}</th>' for c in head) + '</tr>'
        tbody = ''
        for r in body_rows:
            cells = ''.join(f'<td>{html.escape(c)}</td>' for c in r)
            tbody += f'<tr>{cells}</tr>'
        body = f'<h1>{html.escape(src.name)}</h1><table><thead>{thead}</thead><tbody>{tbody}</tbody></table>'
    dst.write_text(page_shell(src.name, body), encoding='utf-8')


def render_jpg_from_html(html_files):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1300, 'height': 1800})
        for f in html_files:
            page.goto(f'file://{f.resolve()}')
            page.wait_for_timeout(350)
            out = IMG_DIR / (f.stem + '.jpg')
            page.screenshot(path=str(out), type='jpeg', quality=90, full_page=True)
        browser.close()


def main():
    sources = []
    sources.extend(sorted(ROOT.glob('*.md')))
    sources.extend(sorted((ROOT / 'day2_templates').glob('*.md')))
    sources.extend(sorted((ROOT / 'day2_templates').glob('*.csv')))

    html_files = []
    for src in sources:
        dst = HTML_DIR / (src.stem + '.html')
        if src.suffix.lower() == '.md':
            md_to_html(src, dst)
        elif src.suffix.lower() == '.csv':
            csv_to_html(src, dst)
        html_files.append(dst)

    render_jpg_from_html(html_files)

    print('HTML outputs:')
    for f in html_files:
        print(f)
    print('JPG outputs:')
    for f in sorted(IMG_DIR.glob('*.jpg')):
        print(f)


if __name__ == '__main__':
    main()
