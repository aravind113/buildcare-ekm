import re, glob, pathlib, subprocess
import build
from build import ROOT, esc, to_pdf
NAVY, TEAL, AMBER, GREY = build.NAVY, build.TEAL, build.AMBER, build.GREY
SRC = pathlib.Path("/tmp/claude-0/psc3"); OUT = ROOT / "out"
KEY = {int(a): b for a, b in (l.split() for l in (SRC/"keyA.txt").read_text().splitlines())}
FONTS = build.CSS.split("@page")[0]
CSS = FONTS + f"""
@page {{ size:A4; margin:16mm 16mm 18mm 16mm; @bottom-center {{ content: counter(page); font-family:'NSL'; font-size:9pt; color:#55606b; }} }}
@page :first {{ margin:0; @bottom-center {{ content:none; }} }}
html {{ font-family:'NSM','NSL',sans-serif; font-size:11.5pt; line-height:1.7; color:#1d2733; }} body {{ margin:0; }}
.cover {{ height:297mm; width:210mm; background:{NAVY}; color:#fff; padding:40mm 20mm; box-sizing:border-box; break-after:page; position:relative; }}
.cover .brand {{ color:{AMBER}; font-size:14pt; font-weight:700; }} .cover h1 {{ color:#fff; font-size:30pt; line-height:1.35; margin:14mm 0 6mm; }}
.cover .sub {{ font-size:15pt; color:#cfe3ee; }} .cover .bar {{ width:40mm; height:2mm; background:{AMBER}; margin-top:12mm; }}
.cover table {{ margin-top:16mm; border-collapse:collapse; font-size:11.5pt; }} .cover td {{ padding:2mm 4mm 2mm 0; vertical-align:top; color:#fff; }} .cover td:first-child {{ color:{AMBER}; width:44mm; }}
.cover .disc {{ position:absolute; bottom:20mm; left:20mm; right:20mm; font-size:9.5pt; color:#cfe3ee; line-height:1.5; }}
h1.pg {{ font-size:18pt; color:{NAVY}; border-bottom:.7mm solid {AMBER}; padding-bottom:2mm; margin:0 0 5mm; break-before:page; }}
.q {{ margin:0 0 6mm; padding:0 0 4mm; border-bottom:.25mm solid #d5dce3; }}
.q .h {{ display:flex; justify-content:space-between; align-items:baseline; }} .q .n {{ color:{NAVY}; font-weight:700; font-size:12.5pt; }}
.q .stem {{ font-weight:600; margin:1mm 0; }} .q .s {{ margin:.6mm 0 .6mm 6mm; }}
.opt {{ padding:.5mm 2.5mm; margin:.4mm 0 .4mm 3mm; border-radius:1mm; }} .opt.ok {{ background:#e3f4ea; color:#0d5a2c; font-weight:700; }}
.ans {{ margin-top:2mm; background:{AMBER}; color:#1b1b1b; display:inline-block; padding:1mm 4mm; border-radius:1.5mm; font-weight:700; }}
.en {{ margin-top:2.2mm; padding:1.6mm 3mm; background:{GREY}; border-radius:1.2mm; font-family:'NSL','NSM',sans-serif; font-size:9.2pt; line-height:1.45; color:#4a5560; }}
.note {{ margin-top:2mm; border:.3mm solid #e0b4b0; background:#fdf1f0; padding:1.6mm 3mm; border-radius:1.2mm; font-size:10pt; }}
.keygrid {{ display:grid; grid-template-columns:repeat(10,1fr); gap:1.5mm; font-family:'NSL'; font-size:10pt; }}
.keygrid a {{ text-decoration:none; color:#1d2733; background:{GREY}; border-radius:1mm; padding:1.2mm 0; text-align:center; }} .keygrid b {{ color:{TEAL}; }}
p {{ margin:1.5mm 0; }} .core {{ break-inside:avoid; }}
"""
def parse(path):
    qs=[]; cur=None; key=None
    for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m=re.match(r"@q\s+(\d+)",ln)
        if m: cur=dict(n=int(m.group(1)),STEM="",S=[],O=[],ANS="",EN="",ES=[],EO=[],NOTE=[]); qs.append(cur); key=None; continue
        if cur is None: continue
        mm=re.match(r"(STEM|S|O|ANS|EN|ES|EO|NOTE):\s?(.*)",ln)
        if mm:
            key,val=mm.groups()
            if key in("STEM","EN"): cur[key]=val
            elif key=="ANS": cur[key]=val.strip()
            else: cur[key].append(val)
        elif ln.strip() and key in("STEM","EN"): cur[key]+=" "+ln.strip()
        elif ln.strip() and key=="NOTE": cur["NOTE"].append(ln.strip())
    return qs
def qhtml(q):
    n,a=q["n"],q["ANS"]; ok_text=""
    only_en = not q["O"]
    if only_en: q = dict(q, O=q["EO"], S=q["ES"])
    opts=""
    for o in q["O"]:
        ok=o.strip().startswith(a+")"); 
        if ok: ok_text=o.strip()
        opts+=f'<div class="opt{" ok" if ok else ""}">{esc(o)}{"  ✔" if ok else ""}</div>'
    h=[f'<div class="q" id="q{n}"><div class="core"><div class="h"><span class="n">ചോദ്യം {n}</span></div><div class="stem">{esc(q["STEM"] or q["EN"])}</div>']
    h+= [f'<div class="s">{esc(s)}</div>' for s in q["S"]]
    h.append(f'<div class="opts">{opts}</div><div class="ans">ഉത്തരം: {esc(ok_text) if ok_text else esc(a)}</div></div>')
    if q["STEM"] and q["EN"]:
        e=f'<b>Original (English):</b> {esc(q["EN"])}'+"".join(f"<br>{esc(s)}" for s in q["ES"])+"".join(f"<br>{esc(o)}" for o in q["EO"])
        h.append(f'<div class="en">{e}</div>')
    if q["NOTE"]: h.append('<div class="note"><b>കുറിപ്പ്:</b> '+esc(" ".join(q["NOTE"]))+'</div>')
    h.append('</div>'); return "".join(h)
def main():
    qs=[]
    for f in sorted(glob.glob(str(SRC/"out"/"pages_*.txt"))): qs+=parse(f)
    byn={q["n"]:q for q in qs}; print("questions",len(byn),"missing",[n for n in range(1,101) if n not in byn])
    cover='''<section class="cover"><div class="brand">PSC Tips &amp; Tricks · psctipsandtricks.online</div><h1>Kerala PSC ചോദ്യപേപ്പർ<br>ചോദ്യങ്ങളും ഉത്തരങ്ങളും</h1><div class="sub">ചോദ്യോത്തര രൂപത്തിൽ പഠനത്തിനായി</div><div class="bar"></div>
<table><tr><td>തസ്തിക</td><td>Assistant (Universities in Kerala)</td></tr><tr><td>കാറ്റഗറി നമ്പർ</td><td>454/2025</td></tr><tr><td>ചോദ്യപേപ്പർ കോഡ്</td><td>91/26-M (മലയാളം മാധ്യമം)</td></tr><tr><td>പരീക്ഷാ തീയതി</td><td>14-Oct-2026</td></tr><tr><td>ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ്</td><td>A</td></tr><tr><td>ഉത്തരസൂചിക</td><td>Kerala PSC Provisional Answer Key</td></tr><tr><td>ആകെ ചോദ്യങ്ങൾ</td><td>100</td></tr></table>
<div class="disc">ഇതിലെ ഉത്തരങ്ങൾ Kerala PSC പ്രസിദ്ധീകരിച്ച <b>പ്രൊവിഷണൽ</b> ആൻസർ കീ (ബുക്ക്‌ലെറ്റ് A) പ്രകാരമാണ്. ഫൈനൽ കീ വരുമ്പോൾ ഉത്തരങ്ങളിൽ മാറ്റം വന്നേക്കാം. ഇത് PSC Tips &amp; Tricks തയ്യാറാക്കിയ പഠനസഹായിയാണ്; Kerala PSC-യുമായി ഔദ്യോഗിക ബന്ധമില്ല.</div></section>'''
    grid="".join(f'<a href="#q{n}">{n}<br><b>{KEY[n]}</b></a>' for n in range(1,101))
    keypage=f'<h1 class="pg" style="break-before:auto">ഉത്തരസൂചിക ഒറ്റനോട്ടത്തിൽ (ബുക്ക്‌ലെറ്റ് A)</h1><p style="font-size:9.5pt;color:#55606b">ചോദ്യ നമ്പറിൽ ക്ലിക്ക് ചെയ്താൽ ആ ചോദ്യത്തിലെത്താം. ഇത് പ്രൊവിഷണൽ കീ ആണ്.</p><div class="keygrid">{grid}</div>'
    notes=[n for n in sorted(byn) if byn[n]["NOTE"]]
    nt='<h1 class="pg">വ്യക്തമല്ലാത്തതും പ്രത്യേകം ശ്രദ്ധിക്കേണ്ടതുമായ കാര്യങ്ങൾ</h1><p>താഴെ പറയുന്ന ചോദ്യങ്ങളിൽ ചോദ്യപേപ്പറിലെ അച്ചടിയോ ഇംഗ്ലീഷ്/മലയാളം പതിപ്പുകൾ തമ്മിലുള്ള വ്യത്യാസമോ കാരണം ശ്രദ്ധ വേണം. ഊഹിച്ച് ഉത്തരം മാറ്റിയിട്ടില്ല; ഉത്തരങ്ങൾ പ്രൊവിഷണൽ കീ പ്രകാരമാണ്.</p>'+("".join(f'<p><a href="#q{n}"><b>ചോദ്യം {n}:</b></a> {esc(" ".join(byn[n]["NOTE"]))}</p>' for n in notes) or "<p>പ്രത്യേക കുറിപ്പുകൾ ഇല്ല.</p>")
    body=cover+keypage+'<h1 class="pg">ചോദ്യങ്ങളും ഉത്തരങ്ങളും</h1>'+"".join(qhtml(byn[n]) for n in sorted(byn))+nt
    doc=f"<!doctype html><html lang='ml'><head><meta charset='utf-8'><title>Kerala PSC 91/26-M Assistant (Universities) — ചോദ്യോത്തരങ്ങൾ</title><style>{CSS}</style></head><body>{body}</body></html>"
    (ROOT/"psc_qa.html").write_text(doc,encoding="utf-8"); to_pdf(str(ROOT/"psc_qa.html"),str(OUT/"psc_qa_91_26_M.pdf"))
    print(subprocess.check_output(["pdfinfo",str(OUT/"psc_qa_91_26_M.pdf")]).decode().split("Pages:")[1].split("\n")[0].strip(),"pages")
if __name__=="__main__": main()
