import re, glob, sys, pathlib, subprocess, html
import build
from build import ROOT, esc, to_pdf
NAVY, TEAL, AMBER, GREY = build.NAVY, build.TEAL, build.AMBER, build.GREY
SRC = pathlib.Path("/tmp/claude-0/p145"); OUT = ROOT / "out"
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
            cur = dict(n=int(m.group(1)), STEM="", S=[], O=[], ANS="", EXP=[], STMT=[], OPT=[], FACTS=[], UPDATE=[], TIPS=[], QR=[], PQ=[], TRANS=[], KEYNOTE=[]); qs.append(cur); key = None; continue
        if cur is None: continue
        mm = re.match(r"(STEM|S|O|ANS|EXP|STMT|OPT|FACTS|UPDATE|TIPS|QR|PQ|TRANS|KEYNOTE):\s?(.*)", ln)
        if mm:
            key, val = mm.group(1), mm.group(2)
            if key == "STEM": cur[key] = val
            elif key == "ANS": cur["ANS"] = val.strip()
            elif key in ("S", "O", "STMT", "OPT"): cur[key].append(val)
            elif val.strip(): cur[key].append(val)
        elif ln.strip() and key in ("EXP", "FACTS", "UPDATE", "TIPS", "QR", "PQ", "TRANS", "KEYNOTE", "STMT", "OPT"):
            cur[key].append(ln.strip())
        elif ln.strip() and key == "STEM":
            cur[key] += " " + ln.strip()
    return qs

def bullets(lines):
    items = [re.sub(r"^-\s*", "", l) for l in lines if l.strip()]
    return "<ul>" + "".join(f"<li>{inl(i)}</li>" for i in items) + "</ul>"

def linkify(t):
    t = inl(t)
    return re.sub(r"(https?://[^\s<)]+)", lambda m: f'<a class="url" href="{m.group(1)}">{m.group(1)}</a>', t)

def qhtml(q):
    n, a = q["n"], q["ANS"]
    opts = ""
    for o in q["O"]:
        ok = a != "X" and o.strip().startswith(a + ")")
        opts += f'<div class="opt{" ok" if ok else ""}">{inl(o)}{"  ✔" if ok else ""}</div>'
    atext = "ഉത്തരം നൽകിയിട്ടില്ല (X)" if a == "X" else f"ശരിയുത്തരം: {a}"
    h = [f'<div class="q" id="q{n}"><div class="qhead"><span class="n">ചോദ്യം {n}</span><span class="a">{atext}</span></div>']
    h.append('<div class="qbox"><div class="stem">' + inl(q["STEM"]) + '</div>' + "".join(f'<div class="s">{inl(x)}</div>' for x in q["S"]) + f'<div class="opts">{opts}</div></div>')
    h.append('<h3 class="sec">വോയ്സ് ഓവർ: ശരിയുത്തരവും വിശദീകരണവും</h3>' + "".join(f"<p>{inl(p)}</p>" for p in q["EXP"]))
    if q["STMT"]:
        rows = ""
        for l in q["STMT"]:
            m = re.match(r"(.+?)\s(ശരി|തെറ്റ്)\s*(?:—|-|:)?\s*(.*)", l)
            if m: rows += f'<tr><td class="{"s" if m.group(2)=="ശരി" else "t"}">{m.group(1)}<br>{m.group(2)}</td><td>{inl(m.group(3))}</td></tr>'
            else: rows += f'<tr><td colspan="2">{inl(l)}</td></tr>'
        h.append('<h3 class="sec">ഓരോ പ്രസ്താവനയും പ്രത്യേകം</h3><table class="stm">' + rows + '</table>')
    if q["OPT"]: h.append('<h3 class="sec">ഓപ്ഷനുകളുടെ വിശകലനം</h3>' + "".join(f"<p>{inl(l)}</p>" for l in q["OPT"]))
    if q["FACTS"]: h.append('<h3 class="sec am">അനുബന്ധ വസ്തുതകൾ</h3>' + bullets(q["FACTS"]))
    up = " ".join(q["UPDATE"]).strip()
    if up and "പുതുക്കൽ ആവശ്യമില്ല" not in up[:40]:
        h.append('<div class="upd"><b>ഏറ്റവും പുതിയ വിവരങ്ങൾ (Current Affairs Update):</b><br>' + "<br>".join(linkify(l) for l in q["UPDATE"]) + '</div>')
    if q["TIPS"]: h.append('<h3 class="sec am">പരീക്ഷാ നുറുങ്ങുകൾ</h3>' + bullets(q["TIPS"]))
    if q["KEYNOTE"]: h.append('<div class="note"><b>ഉത്തരസൂചിക / ചോദ്യം സംബന്ധിച്ച കുറിപ്പ്:</b> ' + inl(" ".join(q["KEYNOTE"])) + '</div>')
    if q["TRANS"]: h.append('<div class="trans">🎙 ' + inl(" ".join(q["TRANS"])) + '</div>')
    h.append('</div>')
    return "".join(h)

EXTRA = """
.trans { margin-top:4mm; border-left:1.2mm solid #F2A900; background:#fff8e1; padding:2mm 4mm; font-weight:600; font-size:10.4pt; }

.cover { padding:22mm 20mm !important; } .cover h1 { font-size:21pt !important; margin:8mm 0 4mm !important; } .cover .sub { font-size:12.5pt !important; } .cover table { margin-top:7mm !important; font-size:10pt !important; } .cover td { padding:1.2mm 3mm 1.2mm 0 !important; } .cover .bar { margin-top:8mm !important; } .cover .disc { bottom:10mm !important; font-size:8.6pt !important; }
.upd { margin-top:3mm; border:.4mm solid #7fb4d6; background:#eef7fd; padding:2mm 4mm; border-radius:1.5mm; font-size:10.2pt; }
.url { word-break:break-all; font-family:'NSL'; font-size:8.6pt; color:#0b5394; }
table.qrt { border-collapse:collapse; width:100%; font-size:9.2pt; } table.qrt td, table.qrt th { border:.25mm solid #c7d0d9; padding:1.2mm 2mm; vertical-align:top; }
table.qrt th { background:#0B2A4A; color:#fff; } table.qrt td:first-child, table.qrt td:nth-child(2) { text-align:center; font-family:'NSL'; font-weight:700; }
"""

def export_txt(byn):
    L = ["PSC Tips & Tricks — 145/2025-M voice-over script (editable text)", ""]
    for n in sorted(byn):
        q = byn[n]
        L += [f"ചോദ്യം {n}: {q['STEM']}"] + q["S"] + q["O"] + [f"ശരിയുത്തരം: {q['ANS']}", ""] + q["EXP"] + [""]
        for k, t in (("STMT", "ഓരോ പ്രസ്താവനയും"), ("OPT", "ഓപ്ഷനുകൾ"), ("FACTS", "അനുബന്ധ വസ്തുതകൾ"), ("UPDATE", "പുതിയ വിവരം"), ("TIPS", "നുറുങ്ങുകൾ"), ("KEYNOTE", "കീ കുറിപ്പ്")):
            if q[k]: L += [t + ":"] + q[k] + [""]
        L += q["TRANS"] + ["", "-----", ""]
    (OUT/"voiceover_145_2025_M.txt").write_text("\n".join(L), encoding="utf-8")

def main():
    qs = []
    for f in sorted(glob.glob(str(SRC/"out"/"pages_*.txt"))): qs += parse(f)
    byn = {q["n"]: q for q in qs}
    export_txt(byn)
    print("questions", len(byn), "missing", [n for n in range(1, 101) if n not in byn])
    cover = """<section class="cover"><div class="brand">PSC Tips &amp; Tricks · psctipsandtricks.online</div>
<h1>Kerala PSC ചോദ്യപേപ്പർ –<br>ഉത്തരങ്ങളും വിശദീകരണങ്ങളും</h1><div class="sub">YouTube ടീച്ചിങ് സ്ലൈഡ് PDF · അനുബന്ധ വസ്തുതകൾ · Current Affairs അപ്ഡേറ്റുകൾ</div><div class="bar"></div>
<table><tr><td>തസ്തിക</td><td>Attender Gr II, Salesman Gr II / Saleswoman Gr II, Attender, Storekeeper etc.</td></tr><tr><td>കാറ്റഗറി നമ്പർ</td><td>037/2024, 199/2024, 328/2024, 377/2024</td></tr><tr><td>ചോദ്യപേപ്പർ കോഡ്</td><td>145/2025-M (മലയാളം മാധ്യമം)</td></tr><tr><td>പരീക്ഷാ തീയതി</td><td>08-Nov-2025</td></tr><tr><td>ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ്</td><td>A</td></tr><tr><td>ഉത്തരസൂചിക</td><td>Kerala PSC Final Answer Key</td></tr><tr><td>ആകെ ചോദ്യങ്ങൾ</td><td>100</td></tr><tr><td>തയ്യാറാക്കിയ തീയതി</td><td>23-Oct-2026</td></tr></table>
<div class="disc">ഉത്തരങ്ങൾ Kerala PSC-യുടെ ഫൈനൽ ആൻസർ കീ (ബുക്ക്‌ലെറ്റ് A) പ്രകാരമാണ്. പിന്നീടുള്ള സംഭവങ്ങൾ കാരണം ഉത്തരം കാലഹരണപ്പെട്ടെങ്കിൽ അത് "ഏറ്റവും പുതിയ വിവരങ്ങൾ" ഭാഗത്ത് പ്രത്യേകം കാണിച്ചിട്ടുണ്ട്; കീയിലെ ഉത്തരം നിശ്ശബ്ദമായി മാറ്റിയിട്ടില്ല. "ഏറ്റവും പുതിയ വിവരങ്ങൾ" ഭാഗം പരീക്ഷയിലെ ഉത്തരത്തിൽ നിന്ന് വേറിട്ടതാണ്; അവ വെബിൽ തിരഞ്ഞ് കണ്ടെത്തിയ വിവരങ്ങളാണ്, ഉറവിട ലിങ്ക് സഹിതം. ഉറപ്പാക്കാൻ കഴിയാത്തവ [VERIFY] / "സ്ഥിരീകരിക്കാനായില്ല" എന്ന് അടയാളപ്പെടുത്തിയിട്ടുണ്ട്. ഇത് PSC Tips &amp; Tricks തയ്യാറാക്കിയ പഠനസഹായിയാണ്; Kerala PSC-യുമായി ഔദ്യോഗിക ബന്ധമില്ല.</div></section>"""
    intro = """<h1 class="pg">വീഡിയോ ആമുഖം (ഓപ്പണിങ് സ്ക്രിപ്റ്റ്)</h1>
<p>നമസ്കാരം! PSC Tips &amp; Tricks ചാനലിലേക്ക് സ്വാഗതം.</p>
<p>ഇന്ന് നമ്മൾ 2025 നവംബർ 8-ന് നടന്ന Attender Gr II, Salesman Gr II / Saleswoman Gr II, Storekeeper തുടങ്ങിയ തസ്തികകളിലേക്കുള്ള പരീക്ഷയുടെ ചോദ്യപേപ്പർ ഓരോ ചോദ്യമായി ഉത്തരസൂചിക സഹിതം പഠിക്കാൻ പോകുകയാണ്. ചോദ്യപേപ്പർ കോഡ് 145/2025-M, ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ് A ആണ്.</p>
<p>ഓരോ ചോദ്യവും ആദ്യം വായിക്കും. തുടർന്ന് ശരിയുത്തരം ഏതെന്നും എന്തുകൊണ്ട് ആ ഉത്തരം ശരിയാകുന്നു, മറ്റ് ഓപ്ഷനുകൾ എന്തുകൊണ്ട് തെറ്റാകുന്നു എന്നും നോക്കാം. ആ വിഷയത്തിൽ ഇനി ചോദിച്ചേക്കാവുന്ന കാര്യങ്ങളും ഏറ്റവും പുതിയ അപ്ഡേറ്റുകളും കൂടി ഓർത്തുവെക്കാം.</p>
<p>ഉത്തരങ്ങൾ PSC പ്രസിദ്ധീകരിച്ച ഫൈനൽ ആൻസർ കീ പ്രകാരമാണ്. കീയിൽ സംശയമുള്ള ചോദ്യങ്ങളുണ്ടെങ്കിൽ അവ പ്രത്യേകം പറയും. ആദ്യം സ്വയം ഉത്തരം കണ്ടെത്താൻ ശ്രമിക്കുക. വീഡിയോ ഇഷ്ടമായെങ്കിൽ ലൈക്ക് ചെയ്യുക, ഷെയർ ചെയ്യുക, PSC Tips &amp; Tricks ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യുക. നമുക്ക് തുടങ്ങാം!</p>"""
    outro = """<h1 class="pg">വീഡിയോ ഉപസംഹാരം (ക്ലോസിങ് സ്ക്രിപ്റ്റ്)</h1>
<p>അങ്ങനെ ഈ പരീക്ഷയുടെ 100 ചോദ്യങ്ങളും ഉത്തരസൂചിക സഹിതം നമ്മൾ പഠിച്ചു കഴിഞ്ഞു.</p>
<p>ഓർക്കുക: PSC പരീക്ഷകളിൽ ഒരേ വിഷയം വ്യത്യസ്ത രൂപത്തിൽ ആവർത്തിച്ച് ചോദിക്കാറുണ്ട്. അതുകൊണ്ട് ഉത്തരം മാത്രം മനഃപാഠമാക്കാതെ അനുബന്ധ വസ്തുതകളും പഠിക്കുക. അവസാനം കണ്ട Quick Revision പട്ടികയും 10 പരിശീലന ചോദ്യങ്ങളും ഒന്നുകൂടി ചെയ്തു നോക്കണം.</p>
<p>ഉത്തരസൂചികയിൽ ഉത്തരം നൽകിയിട്ടില്ലാത്തതോ സംശയമുള്ളതോ ആയ ചോദ്യങ്ങളെക്കുറിച്ചുള്ള നിങ്ങളുടെ അഭിപ്രായം കമന്റിൽ അറിയിക്കുക. കൂടുതൽ പഠനസാമഗ്രികൾക്ക് psctipsandtricks.online സന്ദർശിക്കുക.</p>
<p>വീഡിയോ ഇഷ്ടമായെങ്കിൽ ലൈക്ക് ചെയ്യുക, കൂട്ടുകാർക്ക് ഷെയർ ചെയ്യുക, PSC Tips &amp; Tricks ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യാൻ മറക്കരുത്. പരീക്ഷയ്ക്ക് എല്ലാവിധ ആശംസകളും! നന്ദി, നമസ്കാരം.</p>"""
    xs = [n for n in sorted(byn) if byn[n]["ANS"] == "X"]
    kn = [n for n in sorted(byn) if byn[n]["KEYNOTE"]]
    grid = "".join(f'<a href="#q{n}">{n}<br><b>{KEY[n]}</b></a>' for n in range(1, 101))
    keypage = f'<h1 class="pg" style="break-before:auto">ഉത്തരസൂചിക ഒറ്റനോട്ടത്തിൽ (ബുക്ക്‌ലെറ്റ് A)</h1><p class="small">ചോദ്യ നമ്പറിൽ ക്ലിക്ക് ചെയ്താൽ ആ ചോദ്യത്തിലെത്താം. X = ഉത്തരസൂചികയിൽ ഉത്തരം നൽകിയിട്ടില്ല.</p><div class="keygrid">{grid}</div>'
    disc = '<h1 class="pg">ഉത്തരസൂചിക പരിശോധന — ശ്രദ്ധിക്കേണ്ട ചോദ്യങ്ങൾ</h1><p>എല്ലാ ഉത്തരങ്ങളും ഫൈനൽ ആൻസർ കീ പ്രകാരമാണ്; ഒരു ഉത്തരവും നിശ്ശബ്ദമായി മാറ്റിയിട്ടില്ല. സംശയമുള്ളവ താഴെ.</p>'
    disc += '<h3 class="sec rd">ഉത്തരസൂചികയിൽ ഉത്തരം നൽകിയിട്ടില്ലാത്തവ (X)</h3><p>' + (", ".join(f'<a href="#q{n}">ചോദ്യം {n}</a>' for n in xs) or "ഇല്ല") + '</p>'
    disc += '<h3 class="sec rd">മറ്റ് കുറിപ്പുകൾ</h3>' + ("".join(f'<p><a href="#q{n}"><b>ചോദ്യം {n}:</b></a> ' + inl(" ".join(byn[n]["KEYNOTE"])) + '</p>' for n in kn) or "<p>ഇല്ല</p>")
    # revision table
    rows = ""
    for n in range(1, 101):
        q = byn.get(n)
        if not q: continue
        qr = " ".join(re.sub(r"^-\s*", "", l) for l in q["QR"])
        up = " ".join(q["UPDATE"])
        m = re.search(r"ഏറ്റവും പുതിയ വിവരം[^:]*:\s*(.+?)(?:ഉറവിടം|$)", up)
        upd = inl(m.group(1).strip()[:160]) if m else "—"
        rows += f'<tr><td>{n}</td><td>{q["ANS"]}</td><td>{inl(qr)}</td><td>{upd}</td></tr>'
    qrt = '<h1 class="pg">Quick Revision പട്ടിക</h1><table class="qrt"><tr><th>ചോ.</th><th>ഉത്തരം</th><th>പ്രധാന വസ്തുത</th><th>ഏറ്റവും പുതിയ അപ്ഡേറ്റ്</th></tr>' + rows + '</table>'
    # practice questions
    pqs = []
    for n in sorted(byn):
        for l in byn[n]["PQ"]:
            pqs.append((n, re.sub(r"^-\s*", "", l)))
            break
    step = max(1, len(pqs) // 10)
    pick = pqs[::step][:10]
    pq = '<h1 class="pg">10 പരിശീലന ചോദ്യങ്ങൾ (ഉത്തരം സഹിതം)</h1><p class="small">ഈ പേപ്പറിലെ വിഷയങ്ങളെ അടിസ്ഥാനമാക്കി പരിശീലനത്തിനായി തയ്യാറാക്കിയവ; മുൻവർഷ ചോദ്യങ്ങളല്ല.</p><ol>' + "".join(f'<li>{inl(t)} <span class="small">(ചോദ്യം {n} അടിസ്ഥാനം)</span></li>' for n, t in pick) + '</ol>'
    # sources
    urls = []
    for n in sorted(byn):
        for l in byn[n]["UPDATE"]:
            for u in re.findall(r"https?://[^\s<)\]]+", l):
                u = u.rstrip(".,;")
                if u not in [x[1] for x in urls]: urls.append((n, u))
    src = '<h1 class="pg">ഉറവിടങ്ങൾ (Current Affairs Updates)</h1><p class="small">ഈ ലിങ്കുകൾ വെബ് തിരച്ചിലിൽ കണ്ടെത്തിയവയാണ്; ഉപയോഗിക്കുന്നതിനു മുമ്പ് ഉറവിടത്തിൽ ഒന്നുകൂടി പരിശോധിക്കുക.</p><ol>' + "".join(f'<li><span class="small">Q{n}</span> <a class="url" href="{u}">{u}</a></li>' for n, u in urls) + '</ol>'
    body = cover + keypage + disc + intro + "".join(qhtml(byn[n]) for n in sorted(byn)) + outro + qrt + pq + src
    doc = f"<!doctype html><html lang='ml'><head><meta charset='utf-8'><title>Kerala PSC Previous Questions – Attender Gr II 145/2025-M</title><style>{CSS}{EXTRA}</style></head><body>{body}</body></html>"
    (ROOT/"psc_145.html").write_text(doc, encoding="utf-8")
    to_pdf(str(ROOT/"psc_145.html"), str(OUT/"psc_145_145_2025_M.pdf"))
    print(len(urls), "source urls;", subprocess.check_output(["pdfinfo", str(OUT/"psc_145_145_2025_M.pdf")]).decode().split("Pages:")[1].split("\n")[0].strip(), "pages")
if __name__ == "__main__": main()
