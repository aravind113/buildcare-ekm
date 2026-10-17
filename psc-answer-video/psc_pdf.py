import re, glob, sys, pathlib, subprocess, html
import build
from build import ROOT, esc, to_pdf
NAVY, TEAL, AMBER, GREY = build.NAVY, build.TEAL, build.AMBER, build.GREY
SRC = pathlib.Path("/tmp/claude-0/psc"); OUT = ROOT / "out"
KEY = {int(a): b for a, b in (l.split() for l in (SRC/"keyA.txt").read_text().splitlines())}

FONTS = build.CSS.split("@page")[0]  # font-face block
CSS = FONTS + f"""
@page {{ size:A4; margin:14mm 14mm 16mm 14mm; @bottom-center {{ content: counter(page); font-family:'NSL'; font-size:9pt; color:#55606b; }} }}
@page :first {{ margin:0; @bottom-center {{ content:none; }} }}
html {{ font-family:'NSM','NSL',sans-serif; font-size:11pt; line-height:1.65; color:#1d2733; }}
body {{ margin:0; }}
.cover {{ height:297mm; width:210mm; background:{NAVY}; color:#fff; padding:40mm 20mm; box-sizing:border-box; break-after:page; }}
.cover .brand {{ color:{AMBER}; font-size:14pt; font-weight:700; }}
.cover h1 {{ color:#fff; font-size:30pt; line-height:1.35; margin:14mm 0 6mm; }}
.cover .sub {{ font-size:15pt; color:#cfe3ee; }}
.cover table {{ margin-top:16mm; border-collapse:collapse; font-size:11.5pt; }}
.cover td {{ padding:2mm 4mm 2mm 0; vertical-align:top; color:#fff; }} .cover td:first-child {{ color:{AMBER}; width:42mm; }}
.cover .bar {{ width:40mm; height:2mm; background:{AMBER}; margin-top:12mm; }}
.cover .disc {{ position:absolute; bottom:22mm; left:20mm; right:20mm; font-size:9pt; color:#cfe3ee; line-height:1.5; }}
h1.pg {{ font-size:18pt; color:{NAVY}; border-bottom:.7mm solid {AMBER}; padding-bottom:2mm; margin:0 0 5mm; break-before:page; }}
.keygrid {{ display:grid; grid-template-columns:repeat(10,1fr); gap:1.5mm; font-family:'NSL'; font-size:10pt; }}
.keygrid a {{ text-decoration:none; color:#1d2733; background:{GREY}; border-radius:1mm; padding:1.2mm 0; text-align:center; }}
.keygrid b {{ color:{TEAL}; }}
.q {{ break-before:page; }}
.qhead {{ background:{NAVY}; color:#fff; padding:3.5mm 5mm; border-bottom:1.6mm solid {AMBER}; display:flex; justify-content:space-between; align-items:center; }}
.qhead .n {{ font-size:15pt; font-weight:700; }} .qhead .a {{ background:{AMBER}; color:#1b1b1b; font-weight:700; padding:1mm 4mm; border-radius:2mm; font-size:11pt; }}
.qbox {{ border:.3mm solid #c7d0d9; background:#fafbfc; padding:3.5mm 5mm; margin:4mm 0; border-radius:1.5mm; }}
.qbox .stem {{ font-weight:600; }} .qbox .s {{ margin:.8mm 0 .8mm 5mm; }}
.opts {{ margin-top:2mm; }} .opt {{ padding:.6mm 2mm; border-radius:1mm; }}
.opt.ok {{ background:#e3f4ea; color:#0d5a2c; font-weight:700; }}
h3.sec {{ background:{TEAL}; color:#fff; font-size:11.5pt; padding:1.3mm 4mm; margin:5mm 0 2mm; border-radius:1mm; break-after:avoid; }}
h3.sec.am {{ background:{AMBER}; color:#1b1b1b; }} h3.sec.rd {{ background:#b3261e; }}
p {{ margin:1.2mm 0; }} ul {{ margin:1mm 0 1mm 6mm; padding:0; }} li {{ margin:.6mm 0; }}
table.stm {{ border-collapse:collapse; width:100%; font-size:10.4pt; }} table.stm td {{ border:.25mm solid #c7d0d9; padding:1.6mm 2.4mm; vertical-align:top; }}
td.t {{ background:#fde8e6; color:#8a1b13; font-weight:700; width:16mm; text-align:center; }} td.s {{ background:#e3f4ea; color:#0d5a2c; font-weight:700; width:16mm; text-align:center; }}
.note {{ border:.3mm solid #e0b4b0; background:#fdf1f0; padding:2.5mm 4mm; border-radius:1.5mm; margin:3mm 0; font-size:10.2pt; }}
.small {{ font-size:9.2pt; color:#55606b; }}
"""

def inl(s):
    s = esc(s)
    s = re.sub(r"\[VERIFY[^\]]*\]", lambda m: f'<span style="background:#fff3cd;padding:0 1mm">{m.group(0)}</span>', s)
    return s

def parse(path):
    qs = []; cur = None; key = None
    for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m = re.match(r"@q\s+(\d+)", ln)
        if m:
            cur = dict(n=int(m.group(1)), STEM="", S=[], O=[], ANS="", EXP=[], STMT=[], OPT=[], FACTS=[], PSC=[], KEYNOTE=[]); qs.append(cur); key = None; continue
        if cur is None: continue
        mm = re.match(r"(STEM|S|O|ANS|EXP|STMT|OPT|FACTS|PSC|KEYNOTE):\s?(.*)", ln)
        if mm:
            key, val = mm.group(1), mm.group(2)
            if key == "STEM": cur["STEM"] = val
            elif key == "ANS": cur["ANS"] = val.strip()
            elif key in ("S", "O", "STMT", "OPT"): cur[key].append(val)
            elif val.strip(): cur[key].append(val)
        elif ln.strip() and key in ("EXP", "FACTS", "PSC", "KEYNOTE", "STMT", "OPT"):
            cur[key].append(ln.strip())
        elif ln.strip() and key == "STEM":
            cur["STEM"] += " " + ln.strip()
    return qs

def bullets(lines):
    items = [re.sub(r"^-\s*", "", l) for l in lines if l.strip()]
    return "<ul>" + "".join(f"<li>{inl(i)}</li>" for i in items) + "</ul>"

def qhtml(q):
    n, a = q["n"], q["ANS"]
    opts = ""
    for o in q["O"]:
        ok = a != "X" and o.strip().startswith(a + ")")
        opts += f'<div class="opt{" ok" if ok else ""}">{inl(o)}{"  ✔" if ok else ""}</div>'
    atext = "ഉത്തരം നൽകിയിട്ടില്ല (X)" if a == "X" else f"ശരിയുത്തരം: {a}"
    h = [f'<div class="q" id="q{n}"><div class="qhead"><span class="n">ചോദ്യം {n}</span><span class="a">{atext}</span></div>']
    h.append('<div class="qbox"><div class="stem">' + inl(q["STEM"]) + '</div>' + "".join(f'<div class="s">{inl(s)}</div>' for s in q["S"]) + f'<div class="opts">{opts}</div></div>')
    h.append('<h3 class="sec">വിശദീകരണം</h3>' + "".join(f"<p>{inl(p)}</p>" for p in q["EXP"]))
    if q["STMT"]:
        rows = ""
        for l in q["STMT"]:
            m = re.match(r"(.+?)\s(ശരി|തെറ്റ്)\s*(?:—|-|:)?\s*(.*)", l)
            if m: rows += f'<tr><td class="{"s" if m.group(2)=="ശരി" else "t"}">{m.group(1)}<br>{m.group(2)}</td><td>{inl(m.group(3))}</td></tr>'
            else: rows += f'<tr><td colspan="2">{inl(l)}</td></tr>'
        h.append('<h3 class="sec">ഓരോ പ്രസ്താവനയും പ്രത്യേകം</h3><table class="stm">' + rows + '</table>')
    if q["OPT"]:
        h.append('<h3 class="sec">ഓപ്ഷനുകളുടെ വിശകലനം</h3>' + "".join(f"<p>{inl(l)}</p>" for l in q["OPT"]))
    if q["FACTS"]: h.append('<h3 class="sec am">അനുബന്ധ വസ്തുതകൾ</h3>' + bullets(q["FACTS"]))
    if q["PSC"]: h.append('<h3 class="sec am">പരീക്ഷയ്ക്കുള്ള പോയിന്റുകൾ</h3>' + bullets(q["PSC"]))
    if q["KEYNOTE"]: h.append('<div class="note"><b>ഉത്തരസൂചിക സംബന്ധിച്ച കുറിപ്പ്:</b> ' + inl(" ".join(q["KEYNOTE"])) + '</div>')
    h.append('</div>')
    return "".join(h)

def main():
    qs = []
    for f in sorted(glob.glob(str(SRC/"out"/"pages_*.txt"))): qs += parse(f)
    byn = {}
    for q in qs: byn[q["n"]] = q
    missing = [n for n in range(1, 101) if n not in byn]
    print("questions", len(byn), "missing", missing)
    cover = f"""<section class="cover"><div class="brand">PSC Tips &amp; Tricks · psctipsandtricks.online</div>
<h1>Kerala PSC ചോദ്യപേപ്പർ<br>ഉത്തരങ്ങളും വിശദീകരണങ്ങളും</h1><div class="sub">ചോദ്യം തോറുമുള്ള വിശദമായ വിശകലനം · അനുബന്ധ വസ്തുതകൾ · പരീക്ഷാ പോയിന്റുകൾ</div><div class="bar"></div>
<table><tr><td>തസ്തിക</td><td>Women Civil Excise Officer (Trainee) — Excise Department</td></tr><tr><td>കാറ്റഗറി നമ്പർ</td><td>502/2023</td></tr><tr><td>ചോദ്യപേപ്പർ കോഡ്</td><td>11/2026 M (മലയാളം മാധ്യമം)</td></tr><tr><td>പരീക്ഷാ തീയതി</td><td>07-Feb-2026</td></tr><tr><td>ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ്</td><td>A</td></tr><tr><td>ആകെ ചോദ്യങ്ങൾ</td><td>100</td></tr></table>
<div class="disc">ഉത്തരങ്ങൾ Kerala PSC പ്രസിദ്ധീകരിച്ച ഫൈനൽ ആൻസർ കീ (ബുക്ക്‌ലെറ്റ് A) പ്രകാരമാണ്. വിശദീകരണങ്ങളും അനുബന്ധ വസ്തുതകളും PSC Tips &amp; Tricks തയ്യാറാക്കിയ പഠനസഹായിയാണ്; Kerala PSC-യുമായി ഔദ്യോഗിക ബന്ധമില്ല. ഉറപ്പാക്കാൻ കഴിയാത്ത വസ്തുതകൾ [VERIFY] എന്ന് അടയാളപ്പെടുത്തിയിട്ടുണ്ട്. "പരീക്ഷയ്ക്കുള്ള പോയിന്റുകൾ" ഈ പുസ്തകത്തിനായി തയ്യാറാക്കിയ പരിശീലന ചോദ്യങ്ങളാണ്, മുൻവർഷ ചോദ്യങ്ങളല്ല.</div></section>"""
    grid = "".join(f'<a href="#q{n}">{n}<br><b>{KEY[n]}</b></a>' for n in range(1, 101))
    keypage = f'<h1 class="pg" style="break-before:auto">ഉത്തരസൂചിക ഒറ്റനോട്ടത്തിൽ (ബുക്ക്‌ലെറ്റ് A)</h1><p class="small">ചോദ്യ നമ്പറിൽ ക്ലിക്ക് ചെയ്താൽ ആ ചോദ്യത്തിന്റെ വിശദീകരണത്തിലെത്താം. X = ഉത്തരസൂചികയിൽ ഉത്തരം നൽകിയിട്ടില്ല.</p><div class="keygrid">{grid}</div>'
    body = cover + keypage + "".join(qhtml(byn[n]) for n in sorted(byn))
    doc = f"<!doctype html><html lang='ml'><head><meta charset='utf-8'><title>Kerala PSC 11/2026 M — ഉത്തരങ്ങളും വിശദീകരണങ്ങളും</title><style>{CSS}</style></head><body>{body}</body></html>"
    (ROOT/"psc_qp.html").write_text(doc, encoding="utf-8")
    to_pdf(str(ROOT/"psc_qp.html"), str(OUT/"psc_qp_11_26_M.pdf"))
    print(subprocess.check_output(["pdfinfo", str(OUT/"psc_qp_11_26_M.pdf")]).decode().split("Pages:")[1].split("\n")[0].strip(), "pages")
if __name__ == "__main__": main()
