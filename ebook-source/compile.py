import re, sys, pathlib, subprocess, html
import build, cover
from build import ROOT, esc, inline, parse_sections, parse_mcqs, build_chapter, full_html, to_pdf, NAVY, TEAL, AMBER

PARTS = {
 "I": ("ഭാഗം I", "ഇന്ത്യൻ സമ്പദ്‌വ്യവസ്ഥയുടെ അടിസ്ഥാനങ്ങൾ", "Chapters 1–5"),
 "II": ("ഭാഗം II", "ബാങ്കിങ്, ധനകാര്യം, നികുതി", "Chapters 6–10"),
 "III": ("ഭാഗം III", "ഇന്ത്യയിലെ സാമ്പത്തിക വികസനം", "Chapters 11–15"),
 "IV": ("ഭാഗം IV", "കേരള സമ്പദ്‌വ്യവസ്ഥ", "Chapters 16–20 · additional material"),
 "V": ("ഭാഗം V", "മോഡൽ ടെസ്റ്റുകൾ", "Model Tests · original practice questions"),
}
EXTRA_CSS = """
.pp{break-before:page;break-after:page;height:186mm;display:flex;flex-direction:column;justify-content:center;background:%s;color:#fff;padding:0 12mm;margin:0 -0mm}
.pp .n{color:%s;font-size:13pt;font-weight:700}.pp h1{color:#fff;font-size:26pt;margin:4mm 0}.pp .e{color:#cfe3ee;font-family:'NSL';font-size:11pt}
.pp .bar{width:30mm;height:1.6mm;background:%s;margin-top:6mm}
.front{break-before:page}.front h1{font-size:17pt;border-bottom:.6mm solid %s;padding-bottom:2mm;margin-bottom:4mm}
.toc a{display:flex;color:#1d2733;text-decoration:none;padding:.9mm 0;border-bottom:.2mm dotted #9aa5b1;font-size:9.4pt;line-height:1.35}
.toc a .t{flex:1}.toc a .p{width:9mm;text-align:right;font-family:'NSL';font-weight:600}
.toc .part{background:%s;color:#fff;padding:1.2mm 3mm;margin:3mm 0 1mm;font-weight:700;font-size:9.6pt}
.toc .part a{color:#fff;border:0;padding:0}
.test-head{break-before:page}
.gl td{font-size:8.6pt}
""" % (NAVY, AMBER, AMBER, TEAL, TEAL)

def part_page(key, anchor):
    a, b, c = PARTS[key]
    return f'<div class="pp" id="{anchor}"><div class="n">{a}</div><h1>{b}</h1><div class="e">{c}</div><div class="bar"></div></div>'

def build_test(path):
    t = pathlib.Path(path).read_text(encoding="utf-8")
    m = re.match(r"@test\s+(\d+)\s*\|\s*(.+)", t.splitlines()[0])
    n, title = int(m.group(1)), m.group(2).strip()
    qs = parse_mcqs(t.splitlines()[1:])
    tid = f"t{n:02d}"
    h = [f'<div class="chapter-head" id="{tid}"><div class="part">ഭാഗം V — മോഡൽ ടെസ്റ്റുകൾ</div><div class="num">Test {n}</div><h1>{esc(title)}</h1><div class="en">{len(qs)} original MCQs · answer and explanation under each question</div></div>']
    h.append('<p class="small">ഈ ചോദ്യങ്ങൾ ഈ പുസ്തകത്തിനായി തയ്യാറാക്കിയ മൗലിക പരിശീലന ചോദ്യങ്ങളാണ്; മുൻവർഷ PSC ചോദ്യങ്ങളല്ല. സമയം: 50 മിനിറ്റ് (സ്വയം പരിശീലനത്തിനുള്ള നിർദേശം).</p>')
    for i, q in enumerate(qs, 1):
        opts = "".join(f'<div class="opt">{l}) {inline(x)}</div>' for l, x in q["opts"])
        h.append(f'<div class="mcq"><div class="q">{i}. {inline(q["q"])}</div><div class="opts">{opts}</div><div class="ans"><b class="k">ഉത്തരം: {q["ans"]}</b> — {inline(q["exp"])}</div></div>')
    return tid, title, "\n".join(h), len(qs)

def glossary(chs):
    seen, rows = {}, []
    for c in chs:
        _, secs = parse_sections((ROOT/"chapters"/f"{c}.txt").read_text(encoding="utf-8"))
        for l in secs.get("terms", []):
            if "|" in l:
                e, m = [x.strip() for x in l.split("|", 1)]
                if e and e.lower() not in seen: seen[e.lower()] = (e, m)
    for k in sorted(seen): rows.append(seen[k])
    body = "".join(f"<tr><td>{inline(e)}</td><td>{inline(m)}</td></tr>" for e, m in rows)
    return f'<div class="front" id="gloss"><h1>പദാവലി — Glossary (A–Z)</h1><table class="gl"><thead><tr><th>English</th><th>മലയാളം</th></tr></thead><tbody>{body}</tbody></table></div>', len(rows)

ABBR = [("CPI","Consumer Price Index"),("GDP","Gross Domestic Product"),("GSDP","Gross State Domestic Product"),("GVA","Gross Value Added"),("NDP","Net Domestic Product"),("NNP","Net National Product"),("RBI","Reserve Bank of India"),("CRR","Cash Reserve Ratio"),("SLR","Statutory Liquidity Ratio"),("MPC","Monetary Policy Committee"),("NPA","Non-Performing Asset"),("GST","Goods and Services Tax"),("FRBM","Fiscal Responsibility and Budget Management"),("MGNREGA","Mahatma Gandhi National Rural Employment Guarantee Act"),("MPI","Multidimensional Poverty Index"),("HDI","Human Development Index"),("SDG","Sustainable Development Goals"),("FDI","Foreign Direct Investment"),("BoP","Balance of Payments"),("KIIFB","Kerala Infrastructure Investment Fund Board"),("KSFE","Kerala State Financial Enterprise"),("MTFP","Medium Term Fiscal Policy")]
FORM = [("GDP (market prices)","GDP at factor cost + indirect taxes − subsidies"),("NNP at factor cost","GNP at factor cost − depreciation"),("Real GDP","Nominal GDP ÷ Price index × 100"),("Inflation rate","(CPI₂ − CPI₁) ÷ CPI₁ × 100"),("Fiscal deficit","Total expenditure − (Revenue receipts + Non-debt capital receipts)"),("Revenue deficit","Revenue expenditure − Revenue receipts"),("Primary deficit","Fiscal deficit − Interest payments"),("Effective revenue deficit","Revenue deficit − Grants for creation of capital assets"),("Money multiplier","1 ÷ Reserve ratio"),("Price elasticity of demand","% change in quantity ÷ % change in price"),("Poverty ratio","Number below poverty line ÷ Total population × 100"),("Per-capita income","National income ÷ Population"),("Current account balance","Exports − Imports (goods and services) + Net income + Net transfers")]
def backmatter():
    ab = "".join(f"<tr><td><b>{a}</b></td><td>{b}</td></tr>" for a, b in ABBR)
    fm = "".join(f"<tr><td>{a}</td><td>{inline(b)}</td></tr>" for a, b in FORM)
    return (f'<div class="front" id="abbr"><h1>ചുരുക്കെഴുത്തുകളും ഫോർമുലകളും</h1><h2>Abbreviations</h2><table><thead><tr><th>Short form</th><th>Full form</th></tr></thead><tbody>{ab}</tbody></table>'
            f'<h2>Key formulas</h2><table><thead><tr><th>Measure</th><th>Formula</th></tr></thead><tbody>{fm}</tbody></table></div>')

SOURCES = """<div class="front" id="src"><h1>ഉറവിടങ്ങളും പരിമിതികളും</h1>
<p>ഈ പുസ്തകത്തിലെ കണക്കുകൾ താഴെ പറയുന്ന ഔദ്യോഗിക രേഖകളെ അടിസ്ഥാനമാക്കിയുള്ളതാണ്. ഓരോ കണക്കിനും വർഷം നൽകിയിട്ടുണ്ട്.</p>
<ul><li>Union Budget 2026-27 — Budget at a Glance</li>
<li>Reserve Bank of India — Annual Report 2025-26 (year ended March 31, 2026)</li>
<li>Kerala State Planning Board — Economic Review 2025, Volumes I and II (January 2026)</li>
<li>Government of Kerala — Medium Term Fiscal Policy 2026-27 to 2028-29 (January 29, 2026)</li>
<li>Government of Kerala — Revised Citizen's Guide to Budget 2026-27 (June 19, 2026)</li>
<li>Kerala PSC — Degree Level Preliminary examination syllabus</li></ul>
<div class="box warn"><span class="lab">പരിമിതികൾ</span>[VERIFY] എന്ന് അടയാളപ്പെടുത്തിയ വസ്തുതകൾ ഉറവിടരേഖകളിൽ ഉറപ്പാക്കാൻ കഴിയാത്തവയാണ്; പരീക്ഷയ്ക്ക് മുമ്പ് ഔദ്യോഗിക സ്രോതസ്സിൽ പരിശോധിക്കുക. ബജറ്റ് കണക്കുകൾ (BE), പുതുക്കിയ (RE), താൽക്കാലിക (provisional) കണക്കുകൾ എന്നിവ വേർതിരിച്ചാണ് കൊടുത്തിരിക്കുന്നത്. പുതിയ ചോദ്യങ്ങളെല്ലാം മൗലിക പരിശീലന ചോദ്യങ്ങളാണ്; മുൻവർഷ ചോദ്യങ്ങളല്ല.</div></div>"""

def copyright_page():
    return """<div class="front"><h1>പ്രസാധക വിവരങ്ങൾ</h1>
<p><b>ഇന്ത്യൻ സമ്പദ്‌വ്യവസ്ഥയും കേരള സമ്പദ്‌വ്യവസ്ഥയും</b><br>സമ്പൂർണ്ണ പഠനക്കുറിപ്പുകൾ, ചോദ്യങ്ങൾ, ഉത്തരങ്ങൾ, വിശദീകരണങ്ങൾ</p>
<p>പ്രസാധകർ: PSC Tips &amp; Tricks · psctipsandtricks.online</p>
<p>© PSC Tips &amp; Tricks. എല്ലാ അവകാശങ്ങളും നിക്ഷിപ്തം. പ്രസാധകരുടെ അനുമതിയില്ലാതെ പകർത്തുകയോ വിതരണം ചെയ്യുകയോ ചെയ്യരുത്.</p>
<div class="box warn"><span class="lab">നിരാകരണം</span>ഇത് ഒരു സ്വതന്ത്ര പഠനസഹായിയാണ്; Kerala PSC യുമായോ സർക്കാരുമായോ ഇതിന് ഔദ്യോഗിക ബന്ധമില്ല. ഉള്ളടക്കം ലഭ്യമായ ഔദ്യോഗിക രേഖകളെ ആസ്പദമാക്കി തയ്യാറാക്കിയതാണ്; പരീക്ഷയ്ക്ക് മുമ്പ് ഏറ്റവും പുതിയ വിജ്ഞാപനവും സിലബസും പരിശോധിക്കുക. [VERIFY] അടയാളമുള്ള ഭാഗങ്ങൾ പ്രത്യേകം ഉറപ്പാക്കുക.</div></div>"""

def how_to():
    return """<div class="front"><h1>ഈ പുസ്തകം എങ്ങനെ ഉപയോഗിക്കാം</h1>
<p>പുസ്തകം അഞ്ച് ഭാഗങ്ങളായി തിരിച്ചിരിക്കുന്നു: ഭാഗം I–III ഇന്ത്യൻ സമ്പദ്‌വ്യവസ്ഥ, ഭാഗം IV കേരള സമ്പദ്‌വ്യവസ്ഥ, ഭാഗം V മോഡൽ ടെസ്റ്റുകൾ.</p>
<ul><li>ഓരോ അധ്യായത്തിലും ആമുഖം, പഠനക്കുറിപ്പുകൾ, പ്രധാന വസ്തുതകൾ, പദാവലി, തെറ്റാൻ സാധ്യതയുള്ള വസ്തുതകൾ, ഓർമിക്കാൻ എളുപ്പവഴികൾ, പരിശീലന MCQ-കൾ, റിവിഷൻ എന്നിവയുണ്ട്.</li>
<li>ഓരോ MCQ-ക്കും താഴെ ഉത്തരവും വിശദീകരണവുമുണ്ട്. ആദ്യം ഉത്തരം മറച്ചുവച്ച് സ്വയം ശ്രമിക്കുക.</li>
<li>ഉള്ളടക്കപ്പട്ടികയിലെ ഓരോ വരിയിലും ക്ലിക്ക് ചെയ്താൽ അതത് പേജിലെത്താം.</li>
<li>ഓരോ കണക്കിനുമൊപ്പം വർഷം കൊടുത്തിട്ടുണ്ട്. ബജറ്റ് കണക്കുകൾ ഓരോ വർഷവും മാറുന്നതിനാൽ പരീക്ഷയ്ക്ക് മുമ്പ് ഏറ്റവും പുതിയവ പരിശോധിക്കുക.</li>
<li>കേരളവുമായി ബന്ധപ്പെട്ട അധ്യായങ്ങൾ (16–20) "അധിക ഉള്ളടക്കം" ആണ്; ഡിഗ്രി ലെവൽ പ്രിലിമിനറി സിലബസിൽ നേരിട്ട് പറയാത്തതും എന്നാൽ സെക്രട്ടേറിയറ്റ് ലെവൽ പരീക്ഷകളിൽ ഉപയോഗപ്രദവുമായ ഭാഗങ്ങളാണ്.</li></ul></div>"""

def pnums(pdf, anchors):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.check_output(["pdfinfo", pdf]).decode()).group(1))
    pages = []
    for i in range(1, n + 1):
        pages.append(subprocess.check_output(["pdftotext", "-f", str(i), "-l", str(i), "-layout", pdf, "-"]).decode())
    res = {}
    for key, needle, start in anchors:
        for i in range(start, n):
            if needle in pages[i]:
                res[key] = i + 1; break
    return res, n

def main():
    chs = [f"ch{i:02d}" for i in range(1, 21)]
    tests = sorted((ROOT/"tests").glob("t*.txt"))
    body, toc, nq = [], [], 0
    pstart = {"I": 1, "II": 6, "III": 11, "IV": 16}
    body_main, anchors = [], []
    cur = None
    for c in chs:
        num = int(c[2:]); key = "I" if num<=5 else "II" if num<=10 else "III" if num<=15 else "IV"
        if key != cur:
            body_main.append(part_page(key, f"part{key}")); cur = key
            toc.append(("part", f"{PARTS[key][0]} — {PARTS[key][1]}", f"part{key}"))
        cid, b, head = build_chapter(ROOT/"chapters"/f"{c}.txt")
        nq += b.count('class="mcq"')
        body_main.append(b)
        toc.append(("ch", f"അധ്യായം {num}: {head['ml']}", cid))
    if tests:
        body_main.append(part_page("V", "partV")); toc.append(("part", f"{PARTS['V'][0]} — {PARTS['V'][1]}", "partV"))
        for t in tests:
            tid, title, b, k = build_test(t); nq += k
            body_main.append(b); toc.append(("ch", f"{title} ({k} MCQs)", tid))
    g, gn = glossary(chs)
    for key, label in (("gloss", "പദാവലി — Glossary"), ("abbr", "ചുരുക്കെഴുത്തുകളും ഫോർമുലകളും"), ("src", "ഉറവിടങ്ങളും പരിമിതികളും")):
        toc.append(("ch", label, key))
    tail = g + backmatter() + SOURCES
    TOCPAGES = 3
    def render(pn):
        rows = []
        for kind, label, a in toc:
            p = pn.get(a, "")
            if kind == "part": rows.append(f'<div class="part"><a href="#{a}"><span class="t">{esc(label)}</span><span class="p">{p}</span></a></div>')
            else: rows.append(f'<a href="#{a}"><span class="t">{esc(label)}</span><span class="p">{p}</span></a>')
        tocp = '<div class="front toc" id="toc"><h1>ഉള്ളടക്കപ്പട്ടിക</h1>' + "".join(rows) + '</div>'
        pad = '<div style="break-after:page"></div>' * 0
        front = copyright_page() + how_to() + tocp
        return cover.cover_html() + front + '<div style="break-after:page"></div>' * 0 + "\n".join(body_main) + tail
    out = ROOT/"out"/"book"
    pn = {}
    for rnd in range(3):
        doc = full_html(render(pn)).replace("</style>", cover.COVER_CSS + EXTRA_CSS + "</style>", 1)
        doc = doc.replace("<head>", "<head><title>ഇന്ത്യൻ സമ്പദ്‌വ്യവസ്ഥയും കേരള സമ്പദ്‌വ്യവസ്ഥയും — PSC Tips &amp; Tricks</title>", 1)
        (ROOT/"book.html").write_text(doc, encoding="utf-8")
        to_pdf(str(ROOT/"book.html"), str(ROOT/"out"/"book.pdf"))
        anchors = []
        for kind, label, a in toc:
            if kind == "part": needle = PARTS[a[4:]][1]
            elif a.startswith("ch"): needle = label.split(": ", 1)[1].split(" ")[0] if False else None
            anchors.append((a, label, kind))
        # locate by distinctive heading text
        newpn, n = {}, 0
        total = int(re.search(r"Pages:\s+(\d+)", subprocess.check_output(["pdfinfo", str(ROOT/"out"/"book.pdf")]).decode()).group(1))
        txt = [subprocess.check_output(["pdftotext", "-f", str(i), "-l", str(i), str(ROOT/"out"/"book.pdf"), "-"]).decode() for i in range(1, total+1)]
        tocend = max(i for i, t in enumerate(txt) if "ഉള്ളടക്കപ്പട്ടിക" in t)
        # chapter-head pages: those containing 'അധ്യായം N' + title; use sequential scan
        pos = tocend + 1
        for kind, label, a in toc:
            if kind == "part": needle = PARTS[a[4:]][1]
            elif a.startswith("ch") and a[2:].isdigit(): needle = None
            else: needle = None
            if a.startswith("ch") and a[2:].isdigit():
                ml = re.search(r"അധ്യായം (\d+): (.+)", label); needle = f"അധ്യായം {ml.group(1)}"
            elif a.startswith("t") and a[1:].isdigit(): needle = f"Test {int(a[1:])}"
            elif a == "gloss": needle = "Glossary (A–Z)"
            elif a == "abbr": needle = "Abbreviations"
            elif a == "src": needle = "ഉറവിടങ്ങളും പരിമിതികളും"
            for i in range(pos, total):
                if needle and needle in txt[i]:
                    newpn[a] = i + 1; pos = i; break
        if newpn == pn: break
        pn = newpn
    print("pages", total, "MCQs", nq, "glossary", gn, "toc pages end at", tocend + 1, "rounds", rnd + 1)
    missing = [a for _, _, a in toc if a not in pn]; print("missing anchors", missing)

if __name__ == "__main__": main()
