"""Cover page for the eBook.  If assets/cover.(png|jpg) exists it is used as a full-bleed image;
otherwise a vector recreation of the supplied design is used."""
import pathlib
ROOT = pathlib.Path(__file__).parent

BLUE, NAVY, GREEN, RED, YEL = "#0E3C94", "#0B2A6B", "#0F7B3F", "#C4161C", "#F5C400"

def logo(x, y, s=1.0, dark=False):
    c1 = "#FFFFFF" if not dark else BLUE
    return f'''<g transform="translate({x},{y}) scale({s})">
  <path d="M0 6 Q14 0 28 8 L28 34 Q14 26 0 32 Z" fill="{c1}" opacity=".95"/>
  <path d="M30 8 Q44 0 58 6 L58 32 Q44 26 30 34 Z" fill="{YEL}"/>
  <path d="M29 8 L29 36" stroke="{BLUE}" stroke-width="2"/></g>'''

def icon_circle(cx, cy, color, glyph):
    return f'<circle cx="{cx}" cy="{cy}" r="4.6" fill="{color}"/><g transform="translate({cx},{cy}) scale(.58) translate({-cx},{-cy})">' + glyph(cx, cy) + '</g>'

def g_chart(cx, cy):
    return f'<g fill="#fff"><rect x="{cx-4.5}" y="{cy}" width="2" height="4"/><rect x="{cx-1}" y="{cy-2.5}" width="2" height="6.5"/><rect x="{cx+2.5}" y="{cy-5}" width="2" height="9"/></g>'
def g_doc(cx, cy):
    return f'<g fill="#fff"><rect x="{cx-3.5}" y="{cy-4.5}" width="7" height="9" rx="1"/></g><g stroke="#E8891B" stroke-width=".8"><line x1="{cx-2}" y1="{cy-2}" x2="{cx+2}" y2="{cy-2}"/><line x1="{cx-2}" y1="{cy}" x2="{cx+2}" y2="{cy}"/><line x1="{cx-2}" y1="{cy+2}" x2="{cx+1}" y2="{cy+2}"/></g>'
def g_bulb(cx, cy):
    return f'<circle cx="{cx}" cy="{cy-1}" r="3.6" fill="#fff"/><rect x="{cx-1.6}" y="{cy+2.5}" width="3.2" height="2.4" fill="#fff"/>'
def g_list(cx, cy):
    return f'<g fill="#fff"><rect x="{cx-3.8}" y="{cy-4.5}" width="7.6" height="9" rx="1"/></g><g stroke="#5B2C9E" stroke-width=".9"><line x1="{cx-2.2}" y1="{cy-2}" x2="{cx+2.4}" y2="{cy-2}"/><line x1="{cx-2.2}" y1="{cy+.3}" x2="{cx+2.4}" y2="{cy+.3}"/><line x1="{cx-2.2}" y1="{cy+2.6}" x2="{cx+1}" y2="{cy+2.6}"/></g>'
def g_target(cx, cy):
    return f'<circle cx="{cx}" cy="{cy}" r="4.6" fill="none" stroke="#fff" stroke-width="1.1"/><circle cx="{cx}" cy="{cy}" r="2.2" fill="none" stroke="#fff" stroke-width="1.1"/><circle cx="{cx}" cy="{cy}" r=".9" fill="#fff"/>'
def g_book(cx, cy):
    return f'<path d="M{cx-4.6} {cy-3} Q{cx-2.3} {cy-4} {cx} {cy-2.5} Q{cx+2.3} {cy-4} {cx+4.6} {cy-3} L{cx+4.6} {cy+3.6} Q{cx+2.3} {cy+2.6} {cx} {cy+4} Q{cx-2.3} {cy+2.6} {cx-4.6} {cy+3.6} Z" fill="#fff"/>'

def bottom_icon(cx, kind):
    st = 'fill="none" stroke="#fff" stroke-width="1.1" stroke-linecap="round" stroke-linejoin="round"'
    if kind == "gdp":
        return f'<g {st}><path d="M{cx-5} 177 v6 M{cx-1.6} 175 v8 M{cx+1.8} 171 v12 M{cx+5.2} 168 v15"/><path d="M{cx-6} 172 L{cx-1} 167 L{cx+2} 169 L{cx+6} 163"/></g>'
    if kind == "bank":
        return f'<g {st}><path d="M{cx-6.5} 172 L{cx} 166 L{cx+6.5} 172 Z"/><path d="M{cx-5} 174 v8 M{cx-1.7} 174 v8 M{cx+1.7} 174 v8 M{cx+5} 174 v8 M{cx-7} 184 h14"/></g>'
    if kind == "budget":
        return f'<g {st}><ellipse cx="{cx}" cy="168" rx="5" ry="2"/><path d="M{cx-5} 168 v4 c0 1.2 2.2 2 5 2 s5 -.8 5 -2 v-4"/><path d="M{cx-5} 172 v4 c0 1.2 2.2 2 5 2 s5 -.8 5 -2 v-4"/><path d="M{cx-5} 176 v4 c0 1.2 2.2 2 5 2 s5 -.8 5 -2 v-4"/></g>'
    if kind == "agri":
        return f'<g {st}><circle cx="{cx}" cy="175" r="3"/><path d="M{cx} 167 v3 M{cx} 180 v3 M{cx-8} 175 h3 M{cx+5} 175 h3 M{cx-5.6} 169.6 l2 2 M{cx+3.6} 178.4 l2 2 M{cx-5.6} 180.4 l2 -2 M{cx+3.6} 171.6 l2 -2"/></g>'
    if kind == "trade":
        return f'<g {st}><circle cx="{cx}" cy="175" r="7"/><path d="M{cx-7} 175 h14 M{cx} 168 c-3 3 -3 11 0 14 M{cx} 168 c3 3 3 11 0 14"/></g>'
    if kind == "kerala":
        return f'<g {st}><path d="M{cx-7} 182 h14"/><path d="M{cx} 182 c0 -6 1 -9 3 -12"/><path d="M{cx+3} 170 q-5 -3 -8 1 M{cx+3} 170 q5 -3 8 1 M{cx+3} 170 q-3 -5 -6 -4 M{cx+3} 170 q3 -5 6 -4"/></g>'

def labels(items):
    out = []
    for cx, l1, l2 in items:
        out.append(f'<text x="{cx}" y="188.2" text-anchor="middle" font-size="2.35" font-weight="700" fill="#fff" font-family="NSL">{l1}</text>')
        out.append(f'<text x="{cx}" y="191.0" text-anchor="middle" font-size="2.35" font-weight="700" fill="#fff" font-family="NSL">{l2}</text>')
    return "\n".join(out)

def scene():
    """simple vector illustration: dome building, coins, rupee, bars, ship, palms, water"""
    s = []
    # water
    s.append('<path d="M60 150 Q100 143 148 150 L148 163 L60 163 Z" fill="#3AA7E0" opacity=".55"/>')
    # bars
    for i, (x, h) in enumerate([(84, 14), (90, 20), (96, 28), (102, 38), (108, 46)]):
        s.append(f'<rect x="{x}" y="{136-h}" width="4.6" height="{h}" fill="#5CA8E8" opacity=".75"/>')
    s.append('<path d="M78 124 L112 96 L110 100 L118 94 L117 102" fill="none" stroke="#2E86DE" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
    # coin stacks
    for cx, n in ((125, 7), (133, 5), (118, 3)):
        for k in range(n):
            y = 150 - k * 2.6
            s.append(f'<ellipse cx="{cx}" cy="{y}" rx="5.6" ry="2" fill="#D9A21B"/><rect x="{cx-5.6}" y="{y}" width="11.2" height="2.2" fill="#F2B824"/><ellipse cx="{cx}" cy="{y}" rx="5.6" ry="2" fill="#F7D15A"/>')
    # rupee coin
    s.append('<circle cx="98" cy="104" r="14.5" fill="#F2B824"/><circle cx="98" cy="104" r="11.8" fill="none" stroke="#C98F0B" stroke-width=".9"/>')
    s.append('<text x="98" y="110.2" text-anchor="middle" font-size="19" font-weight="700" fill="#8A5A00" font-family="NSL">₹</text>')
    # building (dome + colonnade)
    s.append('<path d="M70 118 Q86 100 102 118 Z" fill="#E6C9A4"/><rect x="85" y="108" width="2" height="12" fill="#C49A68"/>')
    s.append('<rect x="62" y="120" width="52" height="30" fill="#D9B78A"/>')
    for i in range(10):
        s.append(f'<rect x="{64+i*5}" y="123" width="2.6" height="25" fill="#B98F5E"/>')
    s.append('<rect x="60" y="148" width="56" height="3.5" fill="#B98F5E"/>')
    # ship
    s.append('<path d="M92 156 L146 156 L141 162 L97 162 Z" fill="#1B2F5E"/>')
    cols = ["#E4572E", "#2E86DE", "#F2B824", "#3BB273", "#E4572E", "#2E86DE"]
    for r in range(3):
        for c in range(6):
            s.append(f'<rect x="{99+c*6.4}" y="{149.5-r*3.6+4}" width="6" height="3.4" fill="{cols[(c+r)%6]}"/>')
    s.append('<rect x="136" y="148" width="7" height="8" fill="#fff"/><rect x="138" y="144" width="3" height="4" fill="#fff"/>')
    # palms
    for px, py, sc in ((142, 148, 1.0), (133, 150, .75)):
        s.append(f'<g transform="translate({px},{py}) scale({sc})"><path d="M0 0 C1 -14 -1 -22 -3 -30" stroke="#6B4B2A" stroke-width="1.6" fill="none"/>'
                 '<g fill="#2F9E44"><path d="M-3 -30 q-12 -2 -16 6 q8 -6 16 -2z"/><path d="M-3 -30 q12 -2 16 6 q-8 -6 -16 -2z"/><path d="M-3 -30 q-6 -9 -14 -8 q8 0 14 8z"/><path d="M-3 -30 q6 -9 14 -8 q-8 0 -14 8z"/><path d="M-3 -30 q0 -9 -2 -12 q4 4 2 12z"/></g></g>')
    return "\n".join(s)

def cover_html():
    for ext in ("png", "jpg", "jpeg", "webp"):
        p = ROOT / "assets" / f"cover.{ext}"
        if p.exists():
            return (f'<section class="cover"><img src="assets/{p.name}" style="width:148mm;height:210mm;object-fit:cover;display:block"></section>')
    feats = [("#1E6BD6", g_chart, "സുലഭമായ", "പഠനക്കുറിപ്പുകൾ"),
             ("#F29A1F", g_doc, "പ്രധാന വസ്തുതകളും", "വർഷങ്ങളും"),
             ("#169B52", g_bulb, "ഓർമക്കുറിപ്പുകളും", "പരീക്ഷാ ടിപ്പുകളും"),
             ("#6A2FB5", g_list, "ഒറിജിനൽ MCQ-കൾ", "ഉത്തരങ്ങളോടെ"),
             ("#D3262E", g_target, "പരീക്ഷയിൽ തെറ്റാൻ", "സാധ്യതയുള്ള വസ്തുതകൾ"),
             ("#9A5B13", g_book, "ഫോർമുലകളും", "സംഗ്രഹവും")]
    fs = []
    for i, (col, gl, a, b) in enumerate(feats):
        cy = 110 + i * 9.6
        fs.append(icon_circle(11, cy, col, gl))
        fs.append(f'<text x="19" y="{cy-.9}" font-size="3.2" font-weight="600" fill="#17274F" font-family="NSM">{a}</text>')
        fs.append(f'<text x="19" y="{cy+3}" font-size="3.2" font-weight="600" fill="#17274F" font-family="NSM">{b}</text>')
    xs = [14, 36, 58, 80, 102, 128]
    bl = [(xs[0], "GDP", "NATIONAL INCOME"), (xs[1], "BANKING", "&amp; FINANCE"), (xs[2], "BUDGET", "&amp; TAXATION"),
          (xs[3], "AGRICULTURE", "&amp; INDUSTRY"), (xs[4], "FOREIGN TRADE", "&amp; GLOBAL ECONOMY"), (xs[5], "KERALA", "ECONOMY")]
    kinds = ["gdp", "bank", "budget", "agri", "trade", "kerala"]
    art = '<image href="assets/art.png" x="76" y="97" width="72" height="82.6"/>' if (ROOT/'assets'/'art.png').exists() else '<g transform="translate(19,25) scale(.82)">'+scene()+'</g>'
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 148 210" width="148mm" height="210mm" style="display:block">
<defs><clipPath id="pg"><rect width="148" height="210"/></clipPath></defs>
<g clip-path="url(#pg)">
<rect width="148" height="210" fill="#fff"/>
<path d="M0 0 H148 V44 Q100 30 60 40 Q20 50 0 60 Z" fill="{BLUE}"/>
<rect x="0" y="0" width="3" height="210" fill="{BLUE}"/>
{art}
<path d="M0 168 Q50 160 100 168 Q130 172 148 166 V210 H0 Z" fill="{BLUE}"/>
<path d="M0 170 Q60 164 118 172 Q136 175 148 172 V176 Q130 180 110 177 Q55 169 0 176 Z" fill="#17A24F"/>
{logo(11, 12, .5)}
<text x="43" y="19.5" font-size="5.6" font-weight="700" fill="#fff" font-family="NSL">PSC Tips &amp; Tricks</text>
<text x="43" y="24.4" font-size="2.2" fill="#DDE8FF" font-family="NSM">നിങ്ങളുടെ PSC വിജയ യാത്രയിലെ വിശ്വസനീയ കൂട്ടായി</text>
<rect x="103" y="7" width="40" height="23" rx="1.4" fill="{YEL}"/>
<text x="123" y="14.2" text-anchor="middle" font-size="5.4" font-weight="700" fill="#1B1B1B" font-family="NSL">KERALA PSC</text>
<text x="123" y="19.4" text-anchor="middle" font-size="2.3" font-weight="700" fill="#1B1B1B" font-family="NSL">LDC | LGS | DEGREE LEVEL</text>
<text x="123" y="22.8" text-anchor="middle" font-size="2.3" font-weight="700" fill="#1B1B1B" font-family="NSL">SECRETARIAT | UNIVERSITY</text>
<text x="123" y="26.2" text-anchor="middle" font-size="2.3" font-weight="700" fill="#1B1B1B" font-family="NSL">&amp; OTHER EXAMS</text>
<text x="74" y="52" text-anchor="middle" font-size="9.2" font-weight="700" fill="{NAVY}" font-family="NSM">ഇന്ത്യൻ</text>
<text x="74" y="64.5" text-anchor="middle" font-size="9.2" font-weight="700" fill="{NAVY}" font-family="NSM">സമ്പദ്‌വ്യവസ്ഥയും</text>
<text x="74" y="77.5" text-anchor="middle" font-size="9.6" font-weight="700" fill="{GREEN}" font-family="NSM">കേരള സമ്പദ്‌വ്യവസ്ഥയും</text>
<rect x="30" y="79.5" width="88" height=".6" fill="{YEL}"/>
<rect x="9" y="82" width="130" height="19" rx="4.5" fill="{RED}"/>
<text x="74" y="89.8" text-anchor="middle" font-size="5.0" font-weight="700" fill="#fff" font-family="NSM">സമ്പൂർണ്ണ പഠനക്കുറിപ്പുകൾ</text>
<text x="74" y="97.6" text-anchor="middle" font-size="4.15" font-weight="700" fill="#FFE27A" font-family="NSM">ചോദ്യങ്ങൾ, ഉത്തരങ്ങൾ, വിശദീകരണങ്ങൾ</text>
{"".join(fs)}
{"".join(bottom_icon(x, k) for x, k in zip(xs, kinds))}
{labels(bl)}
{logo(36, 196, .5)}
<text x="68" y="203" font-size="5" font-weight="700" fill="#fff" font-family="NSL">PSC Tips &amp; Tricks</text>
<text x="68" y="207" font-size="2.7" fill="#DDE8FF" font-family="NSL">psctipsandtricks.online</text>
</g></svg>'''
    return f'<section class="cover">{svg}</section>'

COVER_CSS = """
@page :first { size:148mm 210mm; margin:0; @bottom-center { content:none; } }
.cover { width:148mm; height:210mm; overflow:hidden; break-after:page; page-break-after:always; }
"""
