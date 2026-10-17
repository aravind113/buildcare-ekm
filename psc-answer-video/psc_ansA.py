import re, glob, pathlib, subprocess
import build
from build import ROOT, esc, to_pdf
NAVY, TEAL, AMBER, GREY = build.NAVY, build.TEAL, build.AMBER, build.GREY
SRC = pathlib.Path("/tmp/claude-0/vfaA"); SRCD = pathlib.Path("/tmp/claude-0/vfa"); OUT = ROOT / "out"
KEY = {}
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

EXTRA = """
.conf { display:inline-block; font-family:'NSL'; font-size:8.5pt; font-weight:700; padding:.3mm 2.2mm; border-radius:1mm; margin-left:3mm; }
.c-high { background:#e3f4ea; color:#0d5a2c; } .c-medium { background:#fff3cd; color:#7a5a00; } .c-low { background:#fde8e6; color:#8a1b13; }
.g-high { background:#e3f4ea !important; } .g-medium { background:#fff3cd !important; } .g-low { background:#fde8e6 !important; }
.exp { margin-top:2mm; }
.warn { border:.4mm solid #e0b4b0; background:#fdf1f0; padding:3mm 4mm; border-radius:1.5mm; margin:4mm 0; font-size:10.5pt; }
"""
def parse(path):
    qs=[]; cur=None; key=None
    for ln in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        m=re.match(r"@q\s+(\d+)",ln)
        if m: cur=dict(n=int(m.group(1)),STEM="",S=[],O=[],ANS="",CONF="",EXP=[],NOTE=[]); qs.append(cur); key=None; continue
        if cur is None: continue
        mm=re.match(r"(STEM|S|O|ANS|CONF|EXP|NOTE):\s?(.*)",ln)
        if mm:
            key,val=mm.groups()
            if key=="STEM": cur[key]=val
            elif key in("ANS","CONF"): cur[key]=val.strip().lower() if key=="CONF" else val.strip()
            elif key in("S","O"): cur[key].append(val)
            elif val.strip(): cur[key].append(val)
        elif ln.strip() and key=="STEM": cur["STEM"]+=" "+ln.strip()
        elif ln.strip() and key in("EXP","NOTE"): cur[key].append(ln.strip())
    return qs
def conf(q):
    c=q["CONF"] if q["CONF"] in("high","medium","low") else "low"
    return c
def qhtml(q):
    n,a=q["n"],q["ANS"]; ok_text=""
    opts=""
    for o in q["O"]:
        ok=o.strip().startswith(a+")")
        if ok: ok_text=o.strip()
        opts+=f'<div class="opt{" ok" if ok else ""}">{esc(o)}{"  ✔" if ok else ""}</div>'
    c=conf(q); lab={"high":"ഉറപ്പ്: ഉയർന്നത്","medium":"ഉറപ്പ്: ഇടത്തരം","low":"ഉറപ്പ്: കുറവ് — പരിശോധിക്കുക"}[c]
    ans=("ഉത്തരം: "+esc(ok_text)) if ok_text else "ഉത്തരം: നിർണയിക്കാനായില്ല (?)"
    h=[f'<div class="q" id="q{n}"><div class="core"><div class="h"><span class="n">ചോദ്യം {n}</span></div><div class="stem">{esc(q["STEM"])}</div>']
    h+=[f'<div class="s">{esc(s)}</div>' for s in q["S"]]
    h.append(f'<div class="opts">{opts}</div><div class="ans">{ans}</div><span class="conf c-{c}">{lab}</span></div>')
    if q["EXP"]: h.append('<div class="exp">'+"".join(f"<p>{esc(x)}</p>" for x in q["EXP"])+'</div>')
    if q["NOTE"]: h.append('<div class="note"><b>കുറിപ്പ്:</b> '+esc(" ".join(q["NOTE"]))+'</div>')
    h.append('</div>'); return "".join(h)
def main():
    qs=[]
    for f in sorted(glob.glob(str(SRC/"out"/"img_*.txt"))): qs+=parse(f)
    byn={q["n"]:q for q in qs}; miss=[n for n in range(1,101) if n not in byn]; print("questions",len(byn),"missing",miss)
    cover='''<section class="cover"><div class="brand">PSC Tips &amp; Tricks · psctipsandtricks.online</div><h1>Village Field Assistant<br>Stage 02 — ഉത്തരങ്ങൾ</h1><div class="sub">ചോദ്യവും ഓപ്ഷനുകളും ഉത്തരവും ചെറു വിശദീകരണവും</div><div class="bar"></div>
<table><tr><td>തസ്തിക</td><td>Village Field Assistant (VFA) — Stage 02</td></tr><tr><td>ചോദ്യപേപ്പർ കോഡ്</td><td>092/2026-M (മലയാളം മാധ്യമം)</td></tr><tr><td>ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ്</td><td>A</td></tr><tr><td>പരീക്ഷാ തീയതി</td><td>17-10-2026</td></tr><tr><td>ഉത്തരങ്ങളുടെ അടിസ്ഥാനം</td><td><b>ഔദ്യോഗിക ഉത്തരസൂചിക അല്ല</b></td></tr><tr><td>ആകെ ചോദ്യങ്ങൾ</td><td>100</td></tr></table>
<div class="disc"><b>ശ്രദ്ധിക്കുക:</b> ഈ ഉത്തരങ്ങൾ Kerala PSC-യുടെ ഔദ്യോഗിക ആൻസർ കീ അല്ല. ചോദ്യപേപ്പറിന്റെ ഫോട്ടോകളിൽ നിന്ന് വായിച്ചെടുത്ത ചോദ്യങ്ങൾക്ക് ലഭ്യമായ അറിവിന്റെ അടിസ്ഥാനത്തിൽ തയ്യാറാക്കിയവയാണ്. ഓരോ ഉത്തരത്തിനും ഉറപ്പിന്റെ നില നൽകിയിട്ടുണ്ട്; PSC ആൻസർ കീ പ്രസിദ്ധീകരിക്കുമ്പോൾ ഒത്തുനോക്കുക. ഫോട്ടോകളിലെ കൈകൊണ്ടുള്ള അടയാളങ്ങൾ ഉത്തരങ്ങളായി എടുത്തിട്ടില്ല.</div></section>'''
    grid="".join(f'<a class="g-{conf(byn[n]) if n in byn else "low"}" href="#q{n}">{n}<br><b>{byn[n]["ANS"] if n in byn else "?"}</b></a>' for n in range(1,101))
    keypage=f'<h1 class="pg" style="break-before:auto">ഉത്തരങ്ങൾ ഒറ്റനോട്ടത്തിൽ (ബുക്ക്‌ലെറ്റ് A)</h1><div class="warn">ഇത് <b>അനൗദ്യോഗിക</b> ഉത്തരപട്ടികയാണ്. നിറം ഉറപ്പിന്റെ നില കാണിക്കുന്നു: പച്ച = ഉയർന്നത്, മഞ്ഞ = ഇടത്തരം, ചുവപ്പ് = കുറവ്/നിർണയിക്കാനായില്ല. ചോദ്യ നമ്പറിൽ ക്ലിക്ക് ചെയ്താൽ ചോദ്യത്തിലെത്താം.</div><div class="keygrid">{grid}</div>'
    import difflib
    def nz(t): return re.sub(r'[^\w]+','',t)
    dq=[]
    for f in sorted(glob.glob(str(SRCD/"out"/"img_*.txt"))): dq+=parse(f)
    def anstext(q):
        for o in q["O"]:
            if o.strip().startswith(q["ANS"]+")"): return nz(o.strip()[2:])
        return ""
    xc={}
    for n,q in byn.items():
        best=(0,None)
        for d in dq:
            r=difflib.SequenceMatcher(None,nz(q["STEM"]),nz(d["STEM"])).ratio()
            if r>best[0]: best=(r,d)
        r,d=best
        if d is not None and r>=0.7:
            a1,a2=anstext(q),anstext(d)
            same=difflib.SequenceMatcher(None,a1,a2).ratio()>=0.65
            xc[n]=(d["n"],same)
    agree=[n for n in xc if xc[n][1]]; differ=[n for n in sorted(xc) if not xc[n][1]]; nomatch=[n for n in sorted(byn) if n not in xc]
    print("crosscheck agree",len(agree),"differ",differ,"nomatch",nomatch)
    cx='<h1 class="pg">ബുക്ക്‌ലെറ്റ് D യുമായി ഒത്തുനോക്കൽ</h1><p>ഇതേ ചോദ്യപേപ്പറിന്റെ ബുക്ക്‌ലെറ്റ് D-യിലെ ചോദ്യങ്ങളുമായി (ഓപ്ഷനുകളുടെ ക്രമം മാറിയിരിക്കും) ഓരോ ഉത്തരവും ഒത്തുനോക്കി. ഒരേ ചോദ്യത്തിന് രണ്ട് ബുക്ക്‌ലെറ്റുകളിലും ഒരേ ഉത്തരം ലഭിച്ചാൽ അത് ഒരു അധിക പരിശോധനയാണ്; ഔദ്യോഗിക കീ അല്ല.</p>'
    cx+=f'<p><b>ഒത്തുനോക്കി ഒരേ ഉത്തരം ലഭിച്ചവ:</b> {len(agree)} ചോദ്യങ്ങൾ.</p>'
    cx+='<p><b>ഉത്തരം വ്യത്യാസപ്പെട്ടവ (പ്രത്യേകം പരിശോധിക്കുക):</b> '+(", ".join(f'<a href="#q{n}">ചോദ്യം {n}</a> (D-യിൽ {xc[n][0]})' for n in differ) or "ഇല്ല")+'</p>'
    cx+='<p><b>D-യിൽ ചോദ്യം കണ്ടെത്താനാകാത്തവ:</b> '+(", ".join(f'<a href="#q{n}">{n}</a>' for n in nomatch) or "ഇല്ല")+'</p>'
    low=[n for n in sorted(byn) if conf(byn[n])=="low" or byn[n]["ANS"]=="?"]
    nt='<h1 class="pg">ഉറപ്പ് കുറഞ്ഞതും പ്രത്യേകം ശ്രദ്ധിക്കേണ്ടതുമായ ചോദ്യങ്ങൾ</h1><p>ഈ ചോദ്യങ്ങളുടെ ഉത്തരം ഔദ്യോഗിക ആൻസർ കീ വരുമ്പോൾ പ്രത്യേകം ഒത്തുനോക്കുക.</p>'+"".join(f'<p><a href="#q{n}"><b>ചോദ്യം {n} ({byn[n]["ANS"]}):</b></a> {esc(" ".join(byn[n]["NOTE"])) or "ഉറപ്പ് കുറവ്"}</p>' for n in low)
    body=cover+keypage+cx+nt+'<h1 class="pg">ചോദ്യങ്ങളും ഉത്തരങ്ങളും</h1>'+"".join(qhtml(byn[n]) for n in sorted(byn))
    doc=f"<!doctype html><html lang='ml'><head><meta charset='utf-8'><title>VFA Stage 02 092/2026-M Booklet A — ഉത്തരങ്ങൾ (അനൗദ്യോഗികം)</title><style>{CSS}{EXTRA}</style></head><body>{body}</body></html>"
    (ROOT/"psc_ansA.html").write_text(doc,encoding="utf-8"); to_pdf(str(ROOT/"psc_ansA.html"),str(OUT/"psc_ans_092_2026_A.pdf"))
    print(subprocess.check_output(["pdfinfo",str(OUT/"psc_ans_092_2026_A.pdf")]).decode().split("Pages:")[1].split("\n")[0].strip(),"pages")
if __name__=="__main__": main()
