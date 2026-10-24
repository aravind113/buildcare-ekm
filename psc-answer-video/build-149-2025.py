import re, glob, pathlib, subprocess
import psc_145 as m
from build import ROOT, to_pdf
from psc_145 import inl, linkify, parse, qhtml, CSS, EXTRA, OUT

SRC = pathlib.Path("/tmp/claude-0/p149")
KEY = {int(a): b for a, b in (l.split() for l in (SRC/"keyA.txt").read_text().splitlines())}
TAG = "149_2025_M"
POST = "Lift Operator / Mixing Yard Supervisor / Salesman / Cobbler തുടങ്ങിയ തസ്തികകൾ"
CATS = "040/2024, 083/2024, 329/2024, 386/2024, 448/2024, 526/2024, 581/2024"
DATE = "15-Nov-2025"
TODAY = "24-Oct-2026"
EXTRA2 = EXTRA + """
.vo { font-size:12.5pt; line-height:1.85; } .vo h2 { font-size:14pt; color:#0B2A4A; border-bottom:.5mm solid #F2A900; margin:7mm 0 2mm; break-after:avoid; }
.vo .pause { color:#999; font-size:9pt; } .vo p { margin:2mm 0; }
table.qrt td { overflow-wrap:anywhere; } table.cat td:nth-child(1) { width:11mm; text-align:center; font-weight:700; } table.cat td:nth-child(5) { width:34%; } table.cat td:nth-child(3) { width:30%; } table.cat td:nth-child(4) { width:16mm; }
"""

def load():
    qs = []
    for f in sorted(glob.glob(str(SRC/"out"/"pages_*.txt"))): qs += parse(f)
    for q in qs:
        out = []
        for l in q["UPDATE"]:
            out += [x.strip() for x in re.split(r"\s+/\s+(?=(?:പരീക്ഷയിലെ ഉത്തരം|ഏറ്റവും പുതിയ വിവരം|ഉറവിടം))", l) if x.strip()]
        q["UPDATE"] = out
    return {q["n"]: q for q in qs}

def has_update(q):
    up = " ".join(q["UPDATE"])
    return bool(up.strip()) and "പുതുക്കൽ ആവശ്യമില്ല" not in up[:40] and "സ്ഥിരീകരിക്കാനായില്ല" not in up[:30]

def latest(q):
    up = " ".join(q["UPDATE"])
    mm = re.search(r"ഏറ്റവും പുതിയ വിവരം[^:]*:\s*(.+?)(?:\s*ഉറവിടം|$)", up)
    return mm.group(1).strip() if mm else ""

def cover(title, sub):
    return f"""<section class="cover"><div class="brand">PSC Tips &amp; Tricks · psctipsandtricks.online</div>
<h1>{title}</h1><div class="sub">{sub}</div><div class="bar"></div>
<table><tr><td>തസ്തിക</td><td>{POST}</td></tr><tr><td>കാറ്റഗറി നമ്പർ</td><td>{CATS}</td></tr><tr><td>ചോദ്യപേപ്പർ കോഡ്</td><td>149/2025-M (മലയാളം മാധ്യമം)</td></tr><tr><td>പരീക്ഷാ തീയതി</td><td>{DATE}</td></tr><tr><td>ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ്</td><td>A</td></tr><tr><td>ഉത്തരസൂചിക</td><td>Kerala PSC Final Answer Key</td></tr><tr><td>ആകെ ചോദ്യങ്ങൾ</td><td>100</td></tr><tr><td>തയ്യാറാക്കിയ തീയതി</td><td>{TODAY}</td></tr></table>
<div class="disc">ഉത്തരങ്ങൾ Kerala PSC-യുടെ ഫൈനൽ ആൻസർ കീ (ബുക്ക്‌ലെറ്റ് A) പ്രകാരമാണ്; ഒരു ഉത്തരവും നിശ്ശബ്ദമായി മാറ്റിയിട്ടില്ല. "ഏറ്റവും പുതിയ വിവരങ്ങൾ" പരീക്ഷയിലെ ഉത്തരത്തിൽ നിന്ന് വേറിട്ടതാണ്; വെബ് തിരച്ചിലിൽ കണ്ടെത്തിയവ, ഉറവിടം സഹിതം. ഉറപ്പാക്കാനാകാത്തവ [VERIFY] / "സ്ഥിരീകരിക്കാനായില്ല" എന്ന് അടയാളപ്പെടുത്തി. ഇത് PSC Tips &amp; Tricks തയ്യാറാക്കിയ പഠനസഹായിയാണ്; Kerala PSC-യുമായി ഔദ്യോഗിക ബന്ധമില്ല.</div></section>"""

def wrap(title, body, extra=""):
    return f"<!doctype html><html lang='ml'><head><meta charset='utf-8'><title>{title}</title><style>{CSS}{EXTRA2}{extra}</style></head><body>{body}</body></html>"

def sources(byn):
    urls = []
    for n in sorted(byn):
        for l in byn[n]["UPDATE"]:
            for u in re.findall(r"https?://[^\s<)\]]+", l):
                u = u.rstrip(".,;")
                if u not in [x[1] for x in urls]: urls.append((n, u))
    return urls

def ca_summary_rows(byn):
    rows = ""
    for n in sorted(byn):
        q = byn[n]
        if not has_update(q): continue
        exam = next((re.sub(r"^പരീക്ഷയിലെ ഉത്തരം:\s*", "", l) for l in q["UPDATE"] if l.startswith("പരീക്ഷയിലെ ഉത്തരം")), "")
        dm = re.search(r"ഏറ്റവും പുതിയ വിവരം\s*\(([^)]*)\)", " ".join(q["UPDATE"]))
        us = [u.rstrip(".,;") for l in q["UPDATE"] for u in re.findall(r"https?://[^\s<)\]]+", l)]
        links = "<br>".join(f'<a class="url" href="{u}">{u}</a>' for u in us)
        rows += f'<tr><td>{n}</td><td>{inl(exam)}</td><td>{inl(latest(q))}</td><td>{inl(dm[1]) if dm else "—"}</td><td>{links}</td></tr>'
    return rows

# ---------- Deliverable 1: study PDF ----------
def study(byn):
    for q in byn.values(): q["TRANS"] = []
    xs = [n for n in sorted(byn) if byn[n]["ANS"] == "X"]
    kn = [n for n in sorted(byn) if byn[n]["KEYNOTE"]]
    grid = "".join(f'<a href="#q{n}">{n}<br><b>{KEY[n]}</b></a>' for n in range(1, 101))
    keypage = f'<h1 class="pg" style="break-before:auto">ഉത്തരസൂചിക ഒറ്റനോട്ടത്തിൽ (ബുക്ക്‌ലെറ്റ് A)</h1><p class="small">ചോദ്യ നമ്പറിൽ ക്ലിക്ക് ചെയ്താൽ ആ ചോദ്യത്തിലെത്താം. X = ഉത്തരസൂചികയിൽ ഉത്തരം നൽകിയിട്ടില്ല (ചോദ്യം ഒഴിവാക്കി).</p><div class="keygrid">{grid}</div>'
    disc = '<h1 class="pg">ഉത്തരസൂചിക പരിശോധന — ശ്രദ്ധിക്കേണ്ട ചോദ്യങ്ങൾ</h1><p>എല്ലാ ഉത്തരങ്ങളും ഫൈനൽ ആൻസർ കീ പ്രകാരമാണ്. സംശയമുള്ളവ താഴെ; കീയിൽ മാറ്റം വരുത്തിയിട്ടില്ല.</p>'
    disc += '<h3 class="sec rd">ഉത്തരസൂചികയിൽ ഉത്തരം നൽകിയിട്ടില്ലാത്തവ (X)</h3><p>' + (", ".join(f'<a href="#q{n}">ചോദ്യം {n}</a>' for n in xs) or "ഇല്ല") + '</p>'
    disc += '<h3 class="sec rd">മറ്റ് കുറിപ്പുകൾ</h3>' + ("".join(f'<p><a href="#q{n}"><b>ചോദ്യം {n}:</b></a> ' + inl(" ".join(byn[n]["KEYNOTE"])) + '</p>' for n in kn) or "<p>ഇല്ല</p>")
    rows = ""
    for n in sorted(byn):
        q = byn[n]
        qr = " ".join(re.sub(r"^-\s*", "", l) for l in q["QR"])
        rows += f'<tr><td>{n}</td><td>{q["ANS"]}</td><td>{inl(qr)}</td><td>{inl(latest(q)[:160]) if has_update(q) else "—"}</td></tr>'
    qrt = '<h1 class="pg">Quick Revision പട്ടിക</h1><table class="qrt"><tr><th>ചോ.</th><th>ഉത്തരം</th><th>പ്രധാന വസ്തുത</th><th>ഏറ്റവും പുതിയ അപ്ഡേറ്റ്</th></tr>' + rows + '</table>'
    cas = ca_summary_rows(byn)
    cat = '<h1 class="pg">Current Affairs അപ്ഡേറ്റുകളുടെ സംഗ്രഹം</h1><p class="small">പരീക്ഷയിലെ ഉത്തരവും ഇന്നത്തെ വിവരവും വേറിട്ട് കാണിക്കുന്നു. ലിങ്കുകൾ വെബ് തിരച്ചിലിൽ കണ്ടെത്തിയവയാണ്; ഉപയോഗിക്കും മുമ്പ് തുറന്ന് പരിശോധിക്കുക.</p>' + ('<table class="qrt cat"><tr><th>ചോ.</th><th>പരീക്ഷയിലെ ഉത്തരം</th><th>ഏറ്റവും പുതിയ വിവരം</th><th>തീയതി</th><th>ഉറവിടം</th></tr>' + cas + '</table>' if cas else '<p>ഈ പേപ്പറിൽ കീയെ മാറ്റുന്നതോ പുതിയ വിവരം ചേർക്കുന്നതോ ആയ അപ്ഡേറ്റുകൾ കണ്ടെത്തിയില്ല.</p>')
    pqs = []
    for n in sorted(byn):
        for l in byn[n]["PQ"]:
            pqs.append((n, re.sub(r"^-\s*", "", l))); break
    pick = pqs[::max(1, len(pqs)//10)][:10]
    pq = '<h1 class="pg">10 പരിശീലന ചോദ്യങ്ങൾ (ഉത്തരം സഹിതം)</h1><p class="small">ഈ പേപ്പറിലെ വിഷയങ്ങളെ അടിസ്ഥാനമാക്കി തയ്യാറാക്കിയ പരിശീലന ചോദ്യങ്ങൾ; മുൻവർഷ ചോദ്യങ്ങളല്ല.</p><ol>' + "".join(f'<li>{inl(t)} <span class="small">(ചോദ്യം {n} അടിസ്ഥാനം)</span></li>' for n, t in pick) + '</ol>'
    urls = sources(byn)
    src = '<h1 class="pg">ഉറവിടങ്ങൾ</h1><ol>' + "".join(f'<li><span class="small">Q{n}</span> <a class="url" href="{u}">{u}</a></li>' for n, u in urls) + '</ol>'
    body = cover("Kerala PSC ചോദ്യപേപ്പർ –<br>ഉത്തരങ്ങളും വിശദീകരണങ്ങളും", "പഠന സഹായി · അനുബന്ധ വസ്തുതകൾ · Current Affairs അപ്ഡേറ്റുകൾ") + keypage + disc + "".join(qhtml(byn[n]) for n in sorted(byn)) + cat + qrt + pq + src
    (ROOT/"psc_149_study.html").write_text(wrap("Kerala PSC 149/2025-M – പഠന സഹായി", body), encoding="utf-8")
    to_pdf(str(ROOT/"psc_149_study.html"), str(OUT/f"study_{TAG}.pdf"))

# ---------- Deliverable 2: voice-over script ----------
LET = {"A": "എ", "B": "ബി", "C": "സി", "D": "ഡി"}

def spoken_update(q):
    if not has_update(q): return ""
    t = latest(q)
    dm = re.search(r"ഏറ്റവും പുതിയ വിവരം\s*\(([^)]*)\)", " ".join(q["UPDATE"]))
    lead = f"ഇനി ഏറ്റവും പുതിയ വിവരം കൂടി അറിയാം. {dm[1]} വരെയുള്ള റിപ്പോർട്ട് പ്രകാരം, " if dm else "ഇനി ഏറ്റവും പുതിയ വിവരം കൂടി അറിയാം. "
    return lead + t

def vo_block(q):
    n, a = q["n"], q["ANS"]
    h = [f'<h2 id="q{n}">ചോദ്യം {n}</h2>']
    stem = inl(q["STEM"])
    h.append(f"<p>ചോദ്യം നമ്പർ {n}. {stem}</p>")
    for s in q["S"]: h.append(f"<p>{inl(s)}</p>")
    opts = []
    for o in q["O"]:
        mm = re.match(r"([A-D])\)\s*(.*)", o.strip())
        if mm: opts.append(f"ഓപ്ഷൻ {LET[mm[1]]}: {mm[2]}")
    h.append("<p>" + "; ".join(inl(o) for o in opts) + ".</p>")
    h.append('<p class="pause">[ഇവിടെ ഒരു ചെറിയ ഇടവേള]</p>')
    if a == "X":
        h.append("<p><b>ഈ ചോദ്യം ഉത്തരസൂചികയിൽ ഒഴിവാക്കിയിരിക്കുകയാണ്, അതായത് ഔദ്യോഗിക ഉത്തരം നൽകിയിട്ടില്ല.</b></p>")
    else:
        ot = next((re.match(r"[A-D]\)\s*(.*)", o.strip())[1] for o in q["O"] if o.strip().startswith(a + ")")), "")
        h.append(f"<p><b>ശരിയുത്തരം ഓപ്ഷൻ {LET[a]}: {inl(ot)}.</b></p>")
    h += [f"<p>{inl(p)}</p>" for p in q["EXP"]]
    facts = [re.sub(r"^-\s*", "", l) for l in q["FACTS"] if l.strip()]
    if facts:
        h.append("<p>ഇനി ഈ ചോദ്യവുമായി ബന്ധപ്പെട്ട ചില പ്രധാന കാര്യങ്ങൾ കൂടി ഓർത്തുവെക്കാം.</p>" + "".join(f"<p>{inl(f)}</p>" for f in facts))
    su = spoken_update(q)
    if su: h.append(f"<p>{inl(su)}</p>")
    tips = [re.sub(r"^-\s*", "", l) for l in q["TIPS"] if l.strip()]
    if tips: h.append("<p>പരീക്ഷയ്ക്ക് ഓർക്കാൻ: " + " ".join(inl(t) for t in tips) + "</p>")
    if q["TRANS"]: h.append("<p><b>" + inl(" ".join(q["TRANS"])) + "</b></p>")
    return "".join(h)

def vo_text(q):
    n, a = q["n"], q["ANS"]
    L = [f"ചോദ്യം നമ്പർ {n}. {q['STEM']}"] + q["S"]
    L.append("; ".join(f"ഓപ്ഷൻ {LET[mm[1]]}: {mm[2]}" for mm in (re.match(r"([A-D])\)\s*(.*)", o.strip()) for o in q["O"]) if mm) + ".")
    L.append("[ഇടവേള]")
    if a == "X": L.append("ഈ ചോദ്യം ഉത്തരസൂചികയിൽ ഒഴിവാക്കിയിരിക്കുകയാണ്, അതായത് ഔദ്യോഗിക ഉത്തരം നൽകിയിട്ടില്ല.")
    else:
        ot = next((re.match(r"[A-D]\)\s*(.*)", o.strip())[1] for o in q["O"] if o.strip().startswith(a + ")")), "")
        L.append(f"ശരിയുത്തരം ഓപ്ഷൻ {LET[a]}: {ot}.")
    L += q["EXP"]
    facts = [re.sub(r"^-\s*", "", l) for l in q["FACTS"] if l.strip()]
    if facts: L += ["ഇനി ഈ ചോദ്യവുമായി ബന്ധപ്പെട്ട ചില പ്രധാന കാര്യങ്ങൾ കൂടി ഓർത്തുവെക്കാം."] + facts
    su = spoken_update(q)
    if su: L.append(su)
    tips = [re.sub(r"^-\s*", "", l) for l in q["TIPS"] if l.strip()]
    if tips: L.append("പരീക്ഷയ്ക്ക് ഓർക്കാൻ: " + " ".join(tips))
    L += q["TRANS"]
    return "\n".join(L)

INTRO = ["നമസ്കാരം! PSC Tips & Tricks ചാനലിലേക്ക് സ്വാഗതം.",
 "ഇന്ന് നമ്മൾ 2025 നവംബർ 15-ന് നടന്ന Lift Operator, Mixing Yard Supervisor, Salesman, Cobbler തുടങ്ങിയ തസ്തികകളിലേക്കുള്ള പരീക്ഷയുടെ ചോദ്യപേപ്പർ ഓരോ ചോദ്യമായി ഉത്തരസൂചിക സഹിതം പഠിക്കാൻ പോകുകയാണ്. ചോദ്യപേപ്പർ കോഡ് 149/2025-M, ബുക്ക്‌ലെറ്റ് ആൽഫ കോഡ് A ആണ്.",
 "ഓരോ ചോദ്യവും ഓപ്ഷനുകൾ സഹിതം വായിക്കും. അതിനുശേഷം ശരിയുത്തരം ഏതെന്നും എന്തുകൊണ്ട് ആ ഉത്തരം ശരിയാകുന്നു എന്നും, ആ വിഷയത്തിൽ ഇനി ചോദിച്ചേക്കാവുന്ന കാര്യങ്ങളും, ഏറ്റവും പുതിയ അപ്ഡേറ്റുകളും നമുക്ക് നോക്കാം.",
 "ഉത്തരങ്ങൾ PSC പ്രസിദ്ധീകരിച്ച ഫൈനൽ ആൻസർ കീ പ്രകാരമാണ്. ആദ്യം സ്വയം ഉത്തരം കണ്ടെത്താൻ ശ്രമിക്കുക. വീഡിയോ ഇഷ്ടമായെങ്കിൽ ലൈക്ക് ചെയ്യുക, ഷെയർ ചെയ്യുക, ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യുക. നമുക്ക് തുടങ്ങാം!"]
OUTRO = ["അങ്ങനെ ഈ പരീക്ഷയുടെ 100 ചോദ്യങ്ങളും നമ്മൾ പഠിച്ചു കഴിഞ്ഞു.",
 "ഓർക്കുക: PSC പരീക്ഷകളിൽ ഒരേ വിഷയം വ്യത്യസ്ത രൂപത്തിൽ ആവർത്തിച്ച് ചോദിക്കാറുണ്ട്. അതുകൊണ്ട് ഉത്തരം മാത്രം മനഃപാഠമാക്കാതെ അനുബന്ധ വസ്തുതകളും പഠിക്കുക.",
 "കൂടുതൽ പഠനസാമഗ്രികൾക്ക് psctipsandtricks.online സന്ദർശിക്കുക. വീഡിയോ ഇഷ്ടമായെങ്കിൽ ലൈക്ക് ചെയ്യുക, കൂട്ടുകാർക്ക് ഷെയർ ചെയ്യുക, PSC Tips & Tricks ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യാൻ മറക്കരുത്. പരീക്ഷയ്ക്ക് എല്ലാവിധ ആശംസകളും! നന്ദി, നമസ്കാരം."]

def voiceover(byn):
    body = cover("Kerala PSC ചോദ്യപേപ്പർ –<br>YouTube വോയ്സ് ഓവർ സ്ക്രിപ്റ്റ്", "വായിച്ച് റെക്കോർഡ് ചെയ്യാവുന്ന പൂർണ്ണ സ്ക്രിപ്റ്റ് · 100 ചോദ്യങ്ങൾ")
    body += '<div class="vo"><h1 class="pg" style="break-before:auto">ആമുഖം</h1>' + "".join(f"<p>{inl(p)}</p>" for p in INTRO)
    body += "".join(vo_block(byn[n]) for n in sorted(byn))
    body += '<h1 class="pg">ഉപസംഹാരം</h1>' + "".join(f"<p>{inl(p)}</p>" for p in OUTRO) + "</div>"
    css = ".q{break-before:auto}"
    (ROOT/"psc_149_vo.html").write_text(wrap("Kerala PSC 149/2025-M – വോയ്സ് ഓവർ സ്ക്രിപ്റ്റ്", body, css), encoding="utf-8")
    to_pdf(str(ROOT/"psc_149_vo.html"), str(OUT/f"voiceover_{TAG}.pdf"))
    txt = ["PSC Tips & Tricks — 149/2025-M voice-over script (editable text)", "", "=== ആമുഖം ===", ""] + INTRO + [""]
    for n in sorted(byn): txt += [f"=== ചോദ്യം {n} ===", vo_text(byn[n]), ""]
    txt += ["=== ഉപസംഹാരം ===", ""] + OUTRO
    (OUT/f"voiceover_{TAG}.txt").write_text("\n".join(txt), encoding="utf-8")

# ---------- Deliverable 3: current-affairs & facts revision list ----------
def revision(byn):
    cas = ca_summary_rows(byn)
    ca = ('<table class="qrt cat"><tr><th>ചോ.</th><th>പരീക്ഷയിലെ ഉത്തരം</th><th>ഏറ്റവും പുതിയ വിവരം</th><th>തീയതി</th><th>ഉറവിടം</th></tr>' + cas + '</table>') if cas else "<p>കീയെ മാറ്റുന്നതോ പുതിയ വിവരം ചേർക്കുന്നതോ ആയ അപ്ഡേറ്റുകൾ ഈ പേപ്പറിൽ കണ്ടെത്തിയില്ല.</p>"
    unv = [n for n in sorted(byn) if any("സ്ഥിരീകരിക്കാനായില്ല" in l[:40] for l in byn[n]["UPDATE"])]
    unv_t = (", ".join(f'Q{n}' for n in unv) or "ഇല്ല")
    facts = ""
    for n in sorted(byn):
        q = byn[n]
        fl = [re.sub(r"^-\s*", "", l) for l in q["FACTS"] if l.strip()][:3]
        qr = " ".join(re.sub(r"^-\s*", "", l) for l in q["QR"])
        facts += f'<tr><td>{n}</td><td><b>{inl(qr)}</b><ul>' + "".join(f"<li>{inl(f)}</li>" for f in fl) + '</ul></td></tr>'
    body = f'<h1 class="pg" style="break-before:auto">Current Affairs അപ്ഡേറ്റുകൾ — Revision List</h1><p class="small">149/2025-M ({DATE}) · തയ്യാറാക്കിയത് {TODAY}. പരീക്ഷയിലെ ഉത്തരവും ഇന്നത്തെ വിവരവും വേറിട്ട് നൽകുന്നു.</p>{ca}'
    body += f'<h3 class="sec rd">അപ്ഡേറ്റ് സ്ഥിരീകരിക്കാനാകാത്ത ചോദ്യങ്ങൾ</h3><p>{unv_t}</p>'
    body += '<h1 class="pg">അനുബന്ധ വസ്തുതകൾ — Quick Facts (ചോദ്യം തോറും)</h1><table class="qrt cat">' + facts + '</table>'
    (ROOT/"psc_149_rev.html").write_text(wrap("Kerala PSC 149/2025-M – Revision List", body), encoding="utf-8")
    to_pdf(str(ROOT/"psc_149_rev.html"), str(OUT/f"revision_{TAG}.pdf"))

def main():
    byn = load()
    print("questions", len(byn), "missing", [n for n in range(1, 101) if n not in byn])
    voiceover(byn)
    study(byn)
    revision(byn)
    for f in ("study", "voiceover", "revision"):
        p = OUT/f"{f}_{TAG}.pdf"
        print(f, subprocess.check_output(["pdfinfo", str(p)]).decode().split("Pages:")[1].split("\n")[0].strip(), "pages")
    print(len(sources(byn)), "source urls")

if __name__ == "__main__": main()
