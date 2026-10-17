#!/usr/bin/env python3
"""Build tool: chapter text files -> A5 HTML -> PDF (headless Chromium).
Usage: build.py ch01 [ch02 ...]   (builds proof PDF 'out/<name>.pdf')
"""
import re, sys, html, os, subprocess, json, pathlib

ROOT = pathlib.Path(__file__).parent
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

NAVY, TEAL, AMBER, GREY = "#0B2A4A", "#0E8F8F", "#F2A900", "#F1F3F5"

CSS = f"""
@font-face {{ font-family:'NSM'; font-weight:400; src:url('fonts/noto-sans-malayalam-malayalam-400-normal.woff2'); unicode-range: U+0D00-0D7F,U+200C-200D,U+25CC; }}
@font-face {{ font-family:'NSM'; font-weight:600; src:url('fonts/noto-sans-malayalam-malayalam-600-normal.woff2'); unicode-range: U+0D00-0D7F,U+200C-200D,U+25CC; }}
@font-face {{ font-family:'NSM'; font-weight:700; src:url('fonts/noto-sans-malayalam-malayalam-700-normal.woff2'); unicode-range: U+0D00-0D7F,U+200C-200D,U+25CC; }}
@font-face {{ font-family:'NSL'; font-weight:400; src:url('fonts/noto-sans-malayalam-latin-400-normal.woff2'); }}
@font-face {{ font-family:'NSL'; font-weight:600; src:url('fonts/noto-sans-malayalam-latin-600-normal.woff2'); }}
@font-face {{ font-family:'NSL'; font-weight:700; src:url('fonts/noto-sans-malayalam-latin-700-normal.woff2'); }}
@page {{ size:148mm 210mm; margin:12mm 10mm 14mm 10mm;
  @bottom-center {{ content: counter(page); font-family:'NSL','NSM',sans-serif; font-size:8.5pt; color:#55606b; }}
}}
html {{ font-family:'NSM','NSL','DejaVu Sans',sans-serif; font-size:9.6pt; line-height:1.55; color:#1d2733; }}
body {{ margin:0; }}
h1,h2,h3 {{ font-weight:700; color:{NAVY}; line-height:1.4; margin:0; }}
.chapter-head {{ background:{NAVY}; color:#fff; padding:6mm 6mm 5mm; margin:0 0 5mm; border-bottom:2.2mm solid {AMBER}; page-break-before:always; page-break-after:avoid; }}
.chapter-head .part {{ font-size:8.5pt; color:{AMBER}; letter-spacing:.5pt; font-weight:600; }}
.chapter-head .num {{ font-size:9pt; color:#cfe3ee; }}
.chapter-head h1 {{ color:#fff; font-size:19pt; margin-top:1.5mm; }}
.chapter-head .en {{ font-size:10.5pt; color:#cfe3ee; font-family:'NSL',sans-serif; margin-top:1mm; }}
h2 {{ font-size:12pt; margin:3.5mm 0 1.5mm; padding-bottom:1mm; border-bottom:.4mm solid {TEAL}; page-break-after:avoid; }}
h3.sec {{ font-size:11.5pt; color:#fff; background:{TEAL}; padding:1.2mm 3mm; margin:6mm 0 3mm; border-radius:1mm; page-break-after:avoid; }}
h3.sec.navy {{ background:{NAVY}; }}
p {{ margin:0 0 1.6mm; text-align:left; }}
ul {{ margin:0 0 2.5mm 0; padding-left:5mm; }}
li {{ margin-bottom:1mm; }}
.box {{ border-left:1.6mm solid {TEAL}; background:#e7f5f5; padding:2.5mm 3.5mm; margin:3mm 0; page-break-inside:avoid; }}
.box .lab {{ font-weight:700; color:{TEAL}; font-size:9pt; display:block; }}
.box.tip {{ border-color:{AMBER}; background:#fff6dc; }} .box.tip .lab {{ color:#a06f00; }}
.box.formula {{ border-color:#7a8793; background:{GREY}; font-family:'NSL','NSM',monospace; }} .box.formula .lab {{ color:#4a5560; }}
.box.warn {{ border:.5mm solid #c0392b; border-left:1.6mm solid #c0392b; background:#fdecea; }} .box.warn .lab {{ color:#c0392b; }}
.trap-title {{ background:#c0392b; color:#fff; font-weight:700; padding:1.4mm 3mm; margin:6mm 0 3mm; page-break-after:avoid; border-radius:1mm; }}
table {{ border-collapse:collapse; width:100%; margin:2.5mm 0 4mm; font-size:8.8pt; line-height:1.4; }}
th {{ background:{NAVY}; color:#fff; padding:1.3mm 2mm; text-align:left; font-weight:600; }}
td {{ border:.25mm solid #b9c3cc; padding:1.2mm 2mm; vertical-align:top; }}
tr:nth-child(even) td {{ background:#f6f8fa; }}
tr {{ page-break-inside:avoid; }}
.mcq {{ margin:0 0 2.6mm; page-break-inside:avoid; }}
.mcq .q {{ font-weight:600; margin-bottom:1mm; }}
.mcq .opts {{ display:grid; grid-template-columns:1fr 1fr; column-gap:4mm; }}
.mcq .opt {{ margin:0 0 .1mm 4mm; }}
.mcq .ans {{ margin:1.5mm 0 0 0; background:{GREY}; padding:1.8mm 3mm; border-left:1.2mm solid {NAVY}; font-size:9pt; line-height:1.5; }}
.mcq .ans b.k {{ color:{TEAL}; }}
.rev li {{ margin-bottom:1.2mm; }}
.small {{ font-size:8.5pt; color:#55606b; }}
.keep {{ page-break-inside:avoid; }}
a {{ color:{TEAL}; text-decoration:none; }}
"""

def esc(s): return html.escape(s, quote=False)

def inline(s):
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"__(.+?)__", r"<i>\1</i>", s)
    return s

def table_html(lines, header=True):
    rows = []
    for ln in lines:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    out = ["<table>"]
    for i, r in enumerate(rows):
        tag = "th" if (header and i == 0) else "td"
        out.append("<tr>" + "".join(f"<{tag}>{inline(c)}</{tag}>" for c in r) + "</tr>")
    out.append("</table>")
    return "\n".join(out)

def render_block_text(lines):
    """paragraphs, bullets, ## headings, ::def/::tip/::formula/::warn boxes, | tables"""
    out, para, bullets, tbl = [], [], [], []
    def flush():
        nonlocal para, bullets, tbl
        if para: out.append("<p>" + inline(" ".join(para)) + "</p>"); para = []
        if bullets: out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in bullets) + "</ul>"); bullets = []
        if tbl: out.append(table_html(tbl)); tbl = []
    for ln in lines:
        s = ln.rstrip()
        if not s.strip(): flush(); continue
        if s.startswith("## "): flush(); out.append(f"<h2>{inline(s[3:])}</h2>"); continue
        m = re.match(r"::(def|tip|formula|warn)\s+(.*)", s)
        if m:
            flush(); kind, body = m.groups()
            labs = {"def": "നിർവചനം", "tip": "പരീക്ഷാ ടിപ്പ്", "formula": "സൂത്രവാക്യം", "warn": "ശ്രദ്ധിക്കുക"}
            if kind == "def" and "|" in body:
                t, b = [x.strip() for x in body.split("|", 1)]
                out.append(f'<div class="box"><span class="lab">നിർവചനം</span><b>{inline(t)}:</b> {inline(b)}</div>')
            else:
                out.append(f'<div class="box {kind}"><span class="lab">{labs[kind]}</span>{inline(body)}</div>')
            continue
        if s.startswith("|"):
            if para or bullets: flush()
            tbl.append(s); continue
        if s.startswith("- "):
            if para: flush()
            bullets.append(s[2:]); continue
        if tbl: flush()
        para.append(s.strip())
    flush()
    return "\n".join(out)

def parse_sections(text):
    secs, cur, buf = {}, None, []
    head = {}
    for ln in text.splitlines():
        if ln.startswith("@chapter"):
            parts = [p.strip() for p in ln[len("@chapter"):].split("|")]
            head = dict(num=parts[0], part=parts[1], ml=parts[2], en=parts[3]); continue
        if ln.startswith("@"):
            if cur: secs[cur] = buf
            cur, buf = ln[1:].strip(), []; continue
        if cur is not None: buf.append(ln)
    if cur: secs[cur] = buf
    return head, secs

def parse_mcqs(lines):
    qs, cur = [], None
    for ln in lines:
        s = ln.strip()
        if s.startswith("Q:"):
            cur = dict(q=s[2:].strip(), opts=[], ans="", exp=""); qs.append(cur)
        elif re.match(r"^[ABCD]:", s): cur["opts"].append((s[0], s[2:].strip()))
        elif s.startswith("ANS:"): cur["ans"] = s[4:].strip()
        elif s.startswith("EXP:"): cur["exp"] = s[4:].strip()
        elif cur and s and cur["exp"]: cur["exp"] += " " + s
    return qs

def build_chapter(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    head, secs = parse_sections(text)
    cid = f"ch{int(head['num']):02d}"
    h = [f'<div class="chapter-head" id="{cid}"><div class="part">{esc(head["part"])}</div><div class="num">അധ്യായം {esc(head["num"])}</div><h1>{esc(head["ml"])}</h1><div class="en">{esc(head["en"])}</div></div>']
    def sec(title, key, cls=""):
        if key in secs:
            h.append(f'<h3 class="sec {cls}">{title}</h3>')
            h.append(render_block_text(secs[key]))
    sec("A. ആമുഖം", "intro")
    sec("B. പ്രധാന പഠനക്കുറിപ്പുകൾ", "notes", "navy")
    sec("C. പ്രധാന വസ്തുതകൾ (Important Facts)", "facts")
    if "terms" in secs:
        h.append('<h3 class="sec">D. മലയാളം–ഇംഗ്ലീഷ് പദാവലി</h3>')
        rows = ["| English | മലയാളം |"] + ["| " + " | ".join(x.strip() for x in l.split("|")) + " |" for l in secs["terms"] if l.strip()]
        h.append(table_html(rows))
    if "trap" in secs:
        h.append('<div class="trap-title">E. ശ്രദ്ധിക്കുക — പരീക്ഷയിൽ തെറ്റാൻ സാധ്യതയുള്ള വസ്തുതകൾ</div>')
        for l in secs["trap"]:
            if l.strip().startswith("- "):
                t = l.strip()[2:]
                if "||" in t:
                    a, b = t.split("||", 1)
                    h.append(f'<div class="box warn"><span class="lab">{inline(a.strip())}</span>{inline(b.strip())}</div>')
                else:
                    h.append(f'<div class="box warn">{inline(t)}</div>')
    sec("F. ഓർമിക്കാൻ എളുപ്പവഴികൾ (Memory Tricks)", "tricks")
    if "current" in secs: sec("കറന്റ് അഫയേഴ്സ് ബന്ധം (Current Affairs)", "current")
    if "mcq" in secs:
        qs = parse_mcqs(secs["mcq"])
        h.append(f'<h3 class="sec navy">G. പരിശീലന ചോദ്യങ്ങൾ (Practice MCQs) — {len(qs)} ചോദ്യങ്ങൾ</h3>')
        h.append('<p class="small">ഈ ചോദ്യങ്ങൾ ഈ പുസ്തകത്തിനായി തയ്യാറാക്കിയ മൗലിക പരിശീലന ചോദ്യങ്ങളാണ്; മുൻവർഷ PSC ചോദ്യങ്ങളല്ല.</p>')
        for i, q in enumerate(qs, 1):
            opts = "".join(f'<div class="opt">{l}) {inline(t)}</div>' for l, t in q["opts"])
            h.append(f'<div class="mcq"><div class="q">{i}. {inline(q["q"])}</div><div class="opts">{opts}</div><div class="ans"><b class="k">ഉത്തരം: {q["ans"]}</b> — {inline(q["exp"])}</div></div>')
    sec("H. ഒറ്റനോട്ടത്തിൽ റിവിഷൻ (Quick Revision)", "revision")
    return cid, "\n".join(h), head

def full_html(body):
    return f"<!doctype html><html lang='ml'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"

def to_pdf(html_path, pdf_path):
    cmd = [CHROME, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
           f"--print-to-pdf={pdf_path}", "--virtual-time-budget=10000", f"file://{html_path}"]
    subprocess.run(cmd, check=True, capture_output=True, timeout=300)

def main():
    names = sys.argv[1:]
    (ROOT / "out").mkdir(exist_ok=True)
    body, qcount = [], 0
    for n in names:
        cid, b, head = build_chapter(ROOT / "chapters" / f"{n}.txt")
        body.append(b)
        qcount += b.count('class="mcq"')
    out = "_".join(names)
    hp = ROOT / "out" / f"{out}.html"
    hp.write_text(full_html("\n".join(body)), encoding="utf-8")
    # fonts referenced relatively -> copy html next to fonts dir
    (ROOT / f"{out}.html").write_text(hp.read_text(encoding="utf-8"), encoding="utf-8")
    to_pdf(str(ROOT / f"{out}.html"), str(ROOT / "out" / f"{out}.pdf"))
    print("built", out, "MCQs:", qcount)

if __name__ == "__main__":
    main()
