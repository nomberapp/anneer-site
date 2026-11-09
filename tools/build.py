#!/usr/bin/env python3
"""Builds the static Anneer Center website.

Run from the repository root:  python3 tools/build.py
Article text lives in content/articles.json; page copy and metadata live below.
"""
import json, re, html, os, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://anneer.org"
EMAIL = "contact@anneer.org"
CONTENT = json.loads((ROOT / "content" / "articles.json").read_text())

TOPICS = {
    "energy": ("Energy and Climate", "الطاقة والمناخ",
               "How the energy transition redistributes wealth, power and risk between and within countries."),
    "cities": ("Cities and Infrastructure", "المدن والبنية التحتية",
               "Urban systems, public investment and the infrastructure that underpins growth."),
    "technology": ("Technology and the Digital Economy", "التقنية والاقتصاد الرقمي",
                   "Computing, data and artificial intelligence as instruments of national strategy."),
    "economy": ("Economy and Public Finance", "الاقتصاد والمالية العامة",
                "Fiscal choices, markets and the distribution of costs and benefits."),
    "resources": ("Food, Water and Resources", "الغذاء والمياه والموارد",
                  "Securing the essentials in a hotter, more crowded world."),
    "governance": ("Governance and Institutions", "الحوكمة والمؤسسات",
                   "How states organise, decide and deliver."),
}

ARTICLES = [
    dict(key="haqel", slug="haqel-the-saudi-monaco",
         title="Haqel: The Saudi Monaco",
         dek="At the northern tip of the Saudi Red Sea coast, a small town at the meeting point of three nations could become the Kingdom's most distinctive coastal destination, and the living northern gateway to NEOM.",
         author="Saif Matrook", date="2026-11-09",
         topics=["cities", "economy"], kind="Essay",
         image="/assets/img/haqel-monaco.jpg", image_size=(1280, 853),
         image_alt="Monaco's illuminated coastline and harbour at dusk, with a mountain rising behind the town",
         image_caption="Monaco at dusk: a small town, a harbour and a mountain backdrop turned into one of the world's most admired coastal destinations.",
         pdf=None),
    dict(key="adriatic", slug="adriatic-ionian-manufacturing-council",
         title="An Adriatic\u2013Ionian Manufacturing Council: Making Southern Europe a Global Factory",
         dek="Seven countries on the Adriatic and Ionian seas sit on the shortest route from Asia and the Gulf into central Europe. A council devoted solely to manufacturing could turn them into one integrated production system.",
         author="Salman Al Dalbahi and Yazeed Al Rougi", date="2026-11-09",
         topics=["economy", "governance"], kind="Policy paper",
         image=None, image_alt="",
         pdf="/assets/pdf/adriatic-ionian-manufacturing-council.pdf",
         og="/assets/img/adriatic-og.jpg"),
    dict(key="dc", slug="governments-investing-in-data-centres",
         title="Is it a good idea for governments to be investing massively in data centers?",
         dek="Our answer is yes. Computing is becoming as fundamental as electricity, but public money carries a duty private money does not: it must not leave citizens worse off.",
         author="Anneer Center research team", date="2026-11-04",
         topics=["technology", "energy", "economy"], kind="Analysis",
         image="/assets/img/dc-campus.jpg",
         image_alt="A data centre campus in the desert, powered by a solar farm and a high-voltage transmission line",
         pdf="/assets/pdf/governments-investing-in-data-centres.pdf"),
    dict(key="cities", slug="saudi-arabia-national-strategy-great-cities",
         title="Saudi Arabia Needs a National Strategy for Great Cities",
         dek="Where new jobs, universities and public investment settle will shape the Kingdom for longer than almost any sectoral programme. That choice should be made deliberately.",
         author="Sanad Falhan", date="2026-10-31",
         topics=["cities", "governance", "economy"], kind="Essay",
         image=None, image_alt="",
         pdf="/assets/pdf/saudi-arabia-national-strategy-great-cities.pdf",
         old="great-cities.html"),
    dict(key="green", slug="who-is-benefiting-from-green-energy",
         title="Who Is Benefiting from Green Energy?",
         dek="Renewable power is a deflationary technology. Its gains flow not to whoever owns the resource, but to whoever owns the constraint.",
         author="Anneer Center research team", date="2026-10-29",
         topics=["energy", "economy"], kind="Analysis",
         image=None, image_alt="", pdf=None,
         old="green-energy.html"),
]

FIGURES = {  # data-centre essay illustrations: inserted after the paragraph whose text starts with the key
    "Artificial intelligence runs on computing power": ("/assets/img/dc-server-hall.jpg",
        "Inside a server hall: long rows of server racks with a single technician in the aisle",
        "Inside the server hall: the hardware is replaced every few years, while the buildings and grid around it last for decades."),
    "First, markets will not build the foundations": ("/assets/img/dc-grid.jpg",
        "Transmission towers, a substation and an underground fibre route feeding a data centre",
        "The ground a data centre stands on: transmission, substations and fibre are where public investment lasts longest."),
    "The second is to": ("/assets/img/dc-cooling.jpg",
        "A data centre with cooling towers and water tanks fed by a desalinated water pipeline",
        "Cooling in a hot climate: evaporative systems save electricity but draw on scarce, desalinated water."),
}

def esc(s): return html.escape(s, quote=True)
def fmt_date(d, ar=False):
    dt = datetime.date.fromisoformat(d)
    if ar:
        months = ["يناير","فبراير","مارس","أبريل","مايو","يونيو","يوليو","أغسطس","سبتمبر","أكتوبر","نوفمبر","ديسمبر"]
        return f"{dt.day} {months[dt.month-1]} {dt.year}"
    return dt.strftime("%-d %B %Y")
def url_of(a): return f"/research/{a['slug']}/"
def words(a):
    return sum(len(re.sub("<[^>]+>", "", b["html"]).split()) for b in CONTENT[a["key"]]["body"])

# --------------------------------------------------------------------------- layout
CSS = """
@font-face{font-family:"Plex Serif";src:url(/assets/fonts/PlexSerif-Regular.woff) format("woff");font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:"Plex Serif";src:url(/assets/fonts/PlexSerif-Italic.woff) format("woff");font-weight:400;font-style:italic;font-display:swap}
@font-face{font-family:"Plex Serif";src:url(/assets/fonts/PlexSerif-Bold.woff) format("woff");font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:"Plex Serif";src:url(/assets/fonts/PlexSerif-BoldItalic.woff) format("woff");font-weight:700;font-style:italic;font-display:swap}
@font-face{font-family:"Inter";src:url(/assets/fonts/Inter-Regular.woff) format("woff");font-weight:400;font-display:swap}
@font-face{font-family:"Inter";src:url(/assets/fonts/Inter-Medium.woff) format("woff");font-weight:500;font-display:swap}
@font-face{font-family:"Inter";src:url(/assets/fonts/Inter-SemiBold.woff) format("woff");font-weight:600;font-display:swap}
@font-face{font-family:"Inter";src:url(/assets/fonts/Inter-Bold.woff) format("woff");font-weight:700;font-display:swap}
:root{--navy:#0C2850;--navy-2:#08203A;--blue:#1D5FA8;--gold:#B08D3C;--ink:#151A21;--muted:#5E6773;--line:#DDE1E6;--tint:#F3F5F8;
--serif:"Plex Serif",Georgia,serif;--sans:"Inter",system-ui,-apple-system,"Segoe UI",Arial,sans-serif;--ar:"IBM Plex Sans Arabic","Noto Naskh Arabic",Tahoma,sans-serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:#fff;color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.55}
img{max-width:100%;height:auto;display:block}
a{color:inherit;text-decoration:none}a:hover{color:var(--blue)}
.prose a,.sources a,.inline a{color:var(--blue);text-decoration:underline;text-underline-offset:3px;text-decoration-thickness:1px}
.wrap{max-width:1240px;margin:0 auto;padding:0 32px}
@media (max-width:600px){.wrap{padding:0 20px}}
.skip{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.skip:focus{width:auto;height:auto;clip:auto;top:12px;inset-inline-start:16px;background:#fff;padding:8px 12px;z-index:10}
/* header */
header.site{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:5}
.bar{display:flex;align-items:center;justify-content:space-between;gap:28px;min-height:66px}
.brand{display:flex;align-items:center;gap:14px;color:var(--navy)}
.brand:hover{color:var(--navy)}
.brand .mark{width:40px;height:40px;flex:none}
.brand .logo{width:120px;height:auto;display:block}
.brand .t2{display:none}
nav.main{display:flex;align-items:center;gap:30px}
nav.main a{font-size:15px;font-weight:500;color:var(--ink);padding:8px 0;border-bottom:2px solid transparent}
nav.main a:hover,nav.main a[aria-current]{color:var(--navy);border-bottom-color:var(--navy)}
nav.main .lang{font-family:var(--ar);font-size:15px;color:var(--muted);border:0}
nav.main a.btn{color:#fff;padding:0 18px;border:1px solid var(--navy)}nav.main a.btn:hover{color:#fff;border-color:var(--blue)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;padding:0 20px;font:600 14.5px var(--sans);border:1px solid var(--navy);background:var(--navy);color:#fff;border-radius:2px}
.btn:hover{background:var(--blue);border-color:var(--blue);color:#fff}
.btn.out{background:#fff;color:var(--navy)}.btn.out:hover{background:var(--navy);color:#fff}
.btn.light{background:#fff;color:var(--navy);border-color:#fff}.btn.light:hover{background:transparent;color:#fff}
.menu-btn{display:none;background:none;border:1px solid var(--line);border-radius:2px;padding:0 14px;min-height:44px;font:600 14px var(--sans);color:var(--navy)}
.topicbar{border-bottom:1px solid var(--line);background:#fff}
.topicbar .wrap{display:flex;gap:24px;align-items:center;min-height:46px;overflow-x:auto;white-space:nowrap;font-size:13.5px;scrollbar-width:none}
.topicbar b{font-weight:700;color:var(--navy);text-transform:uppercase;letter-spacing:.08em;font-size:12px}
.topicbar a{color:#39424D}.topicbar a:hover{color:var(--blue)}
@media (max-width:960px){.menu-btn{display:block}nav.main{display:none;position:absolute;left:0;right:0;top:100%;background:#fff;border-bottom:1px solid var(--line);flex-direction:column;align-items:stretch;gap:0;padding:8px 20px 16px}nav.main.open{display:flex}nav.main a{padding:14px 0;border-bottom:1px solid var(--line)}nav.main .btn{margin-top:12px}.bar{min-height:72px;position:relative}.brand .logo{width:108px}.brand .t2{font-size:9px;letter-spacing:.08em}}
/* type */
.label{font:700 12px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--blue)}
.label a:hover{text-decoration:underline}
h1,h2,h3{font-family:var(--serif);font-weight:700;color:var(--ink);line-height:1.15;margin:0;letter-spacing:-.005em}
.byline{font-size:14px;color:var(--muted)}.byline b{color:var(--ink);font-weight:600}
.dek{font-family:var(--serif);color:#3B4552}
/* home lead */
.lead-grid{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:56px;padding:48px 0 56px;border-bottom:1px solid var(--line)}
@media (max-width:960px){.lead-grid{grid-template-columns:1fr;gap:40px;padding:32px 0 40px}}
.lead h1{font-size:clamp(34px,4.4vw,56px);line-height:1.08;margin:14px 0 18px}
.lead h1 a:hover{color:var(--blue)}
.lead .dek{font-size:21px;line-height:1.5;margin:0 0 20px;max-width:760px}
.lead .img{margin-bottom:26px}
.side h2{font:700 13px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--ink);padding-bottom:12px;border-bottom:3px solid var(--navy);margin-bottom:6px}
.side .it{padding:18px 0;border-bottom:1px solid var(--line)}
.side .it h3{font-size:19px;line-height:1.3;margin:8px 0 8px}
/* sections */
section.block{padding:64px 0}section.tint{background:var(--tint)}
.sec-head{display:flex;justify-content:space-between;align-items:baseline;gap:16px;border-top:3px solid var(--navy);padding-top:14px;margin-bottom:28px;flex-wrap:wrap}
.sec-head h2{font:700 14px var(--sans);letter-spacing:.1em;text-transform:uppercase}
.sec-head a{font-size:14px;font-weight:600;color:var(--blue)}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:40px}
@media (max-width:960px){.cards{grid-template-columns:1fr;gap:28px}}
.card{display:flex;flex-direction:column;gap:10px}
.card h3{font-size:23px;line-height:1.25}.card p{margin:0;color:#3B4552;font-size:15.5px}
.card .thumb{aspect-ratio:16/9;background:var(--tint);margin-bottom:6px;overflow:hidden}
.card .thumb img{width:100%;height:100%;object-fit:cover}
.statement{background:var(--navy);color:#C9D3DF;padding:72px 0}
.statement .grid{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:64px;align-items:center}
@media (max-width:960px){.statement .grid{grid-template-columns:1fr;gap:24px}}
.statement p.big{font-family:var(--serif);font-size:clamp(24px,2.6vw,32px);line-height:1.35;color:#fff;margin:0}
.statement p{margin:0 0 18px;font-size:17px}
.topics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));border-top:1px solid var(--line);border-left:1px solid var(--line)}
@media (max-width:960px){.topics{grid-template-columns:1fr}}
.topic{padding:28px;border-right:1px solid var(--line);border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:8px}
.topic h3{font-size:21px}.topic p{margin:0;color:#3B4552;font-size:15px}.topic .n{margin-top:6px;font-size:13px;font-weight:600;color:var(--blue)}
.topic:hover{background:var(--tint);color:inherit}
.signup{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:32px;align-items:center}
@media (max-width:800px){.signup{grid-template-columns:1fr}}
.signup h2{font-size:30px;margin-bottom:8px}.signup p{margin:0;color:#3B4552}
/* footer */
footer.site{background:var(--navy-2);color:#A9B5C3;padding:60px 0 28px;font-size:14.5px}
footer.site .cols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px}
@media (max-width:820px){footer.site .cols{grid-template-columns:1fr 1fr}}
footer.site h4{color:#fff;font:700 12px var(--sans);letter-spacing:.12em;text-transform:uppercase;margin:0 0 16px}
footer.site ul{list-style:none;margin:0;padding:0}footer.site li{margin:0 0 10px}
footer.site a{color:#DDE4EC}footer.site a:hover{color:#fff;text-decoration:underline}
footer.site .fname{font-family:var(--serif);font-weight:700;color:#fff;font-size:24px;letter-spacing:.16em}
footer.site .ar{font-family:var(--ar);color:#C9D3DF;margin-top:6px}
footer.site .social,.contact-box .social{display:flex;gap:14px;margin-top:20px}.social a{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border:1px solid rgba(255,255,255,.25);border-radius:50%}.contact-box .social a{border-color:var(--line)}.social a:hover{background:rgba(255,255,255,.08)}.contact-box .social a:hover{background:var(--tint)}
footer.site .copy{border-top:1px solid rgba(255,255,255,.14);margin-top:44px;padding-top:20px;font-size:13px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
/* page head */
.page-head{padding:56px 0 40px;border-bottom:1px solid var(--line)}
.page-head h1{font-size:clamp(36px,4.4vw,54px);margin:10px 0 14px}
.page-head p{font-family:var(--serif);font-size:20px;color:#3B4552;max-width:780px;margin:0}
.crumbs{font-size:13px;color:var(--muted)}.crumbs a{color:var(--muted);text-decoration:underline;text-underline-offset:2px}
/* lists */
.filters{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:24px}
.filters button{font:500 14px var(--sans);border:1px solid var(--line);background:#fff;color:var(--ink);padding:0 14px;min-height:40px;border-radius:2px;cursor:pointer}
.filters button[aria-pressed=true]{background:var(--navy);border-color:var(--navy);color:#fff}
.list .item{display:grid;grid-template-columns:150px minmax(0,1fr);gap:32px;padding:28px 0;border-bottom:1px solid var(--line)}
@media (max-width:700px){.list .item{grid-template-columns:1fr;gap:6px}}
.list .item h2{font-size:25px;line-height:1.25;margin:8px 0 10px}.list .item p{margin:0 0 10px;color:#3B4552}
.tags{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}.tag{font-size:12.5px;font-weight:600;color:var(--blue);border:1px solid #C9D7EA;border-radius:2px;padding:3px 9px}
.tag:hover{background:#EEF3FA}
/* article */
.art-head{padding:48px 0 32px}
.art-head .inner{max-width:860px}
.art-head h1{font-size:clamp(34px,4.4vw,52px);line-height:1.1;margin:14px 0 18px}
.art-head .dek{font-size:22px;line-height:1.45;margin:0 0 28px}
.authors{display:flex;align-items:center;gap:14px;padding:18px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);flex-wrap:wrap;justify-content:space-between}
.authors .who{display:flex;align-items:center;gap:12px}
.avatar{width:44px;height:44px;border-radius:50%;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font:600 15px var(--sans);flex:none}
.share{display:flex;gap:8px}.share a{font-size:13px;font-weight:600;border:1px solid var(--line);padding:0 12px;min-height:36px;display:inline-flex;align-items:center;border-radius:2px;color:var(--navy)}
.share a:hover{border-color:var(--navy)}
.art-body{display:grid;grid-template-columns:minmax(0,720px) minmax(0,1fr);gap:72px;padding:40px 0 24px}
@media (max-width:1000px){.art-body{grid-template-columns:minmax(0,1fr);gap:24px}}
.hero-img{margin:0 0 32px}.hero-img figcaption{font-size:13.5px;color:var(--muted);margin-top:10px}
.prose{font-family:var(--serif);font-size:19.5px;line-height:1.72;color:#1C222B}
.prose p{margin:0 0 1.3em}.prose h2{font-size:27px;margin:1.7em 0 .7em}
.prose ul{padding-left:1.2em;margin:0 0 1.3em}.prose li{margin:0 0 .6em}
.prose h3{font-size:21px;margin:1.5em 0 .5em}
.prose ol{padding-left:1.4em;margin:0 0 1.3em}
.prose figure img{width:100%;height:auto;border:1px solid var(--line)}
.prose .tbl{overflow-x:auto;margin:0 0 1.6em}
.prose table{border-collapse:collapse;width:100%;min-width:600px;font-family:var(--sans);font-size:14.5px;line-height:1.45}
.prose th{background:var(--navy);color:#fff;text-align:left;font-weight:600;padding:10px 12px;vertical-align:bottom}
.prose td{border-bottom:1px solid var(--line);padding:10px 12px;vertical-align:top}
.prose td p,.prose th p{margin:0}
.prose figure{margin:2em 0}.prose figcaption{font-family:var(--sans);font-size:13.5px;color:var(--muted);margin-top:10px}
.rail{position:sticky;top:120px;align-self:start;display:flex;flex-direction:column;gap:28px}
@media (max-width:1000px){.rail{position:static}}
.rail .box{border-top:3px solid var(--navy);padding-top:14px}
.rail .box h4{font:700 12px var(--sans);letter-spacing:.1em;text-transform:uppercase;margin:0 0 12px}
.rail .box a.t{display:block;font-family:var(--serif);font-weight:700;font-size:17px;line-height:1.3;padding:10px 0;border-bottom:1px solid var(--line)}
.sources{border-top:1px solid var(--line);margin-top:24px;padding-top:24px;font-size:14px;color:#3B4552;font-family:var(--sans)}
.sources h2{font:700 13px var(--sans);letter-spacing:.1em;text-transform:uppercase;margin:0 0 14px}
.sources ol{padding-left:1.3em;margin:0}.sources li{margin:0 0 8px;overflow-wrap:anywhere}
.cite{margin:28px 0 0;padding:18px 20px;background:var(--tint);font-size:13.5px;color:#3B4552;font-family:var(--sans)}
.art-foot{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0 56px}
/* misc */
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.3fr);gap:64px}@media (max-width:900px){.two{grid-template-columns:1fr;gap:20px}}
.lede{font-family:var(--serif);font-size:21px;line-height:1.6;color:#1C222B;margin:0 0 20px}
.pillars{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:40px}@media (max-width:900px){.pillars{grid-template-columns:1fr;gap:24px}}
.pillar{border-top:1px solid var(--line);padding-top:18px}.pillar h3{font-size:21px;margin:0 0 8px}.pillar p{margin:0;color:#3B4552}
.contact-box{border-top:3px solid var(--navy);padding-top:18px}.contact-box h3{font-size:21px;margin:0 0 8px}.contact-box p{margin:0 0 12px;color:#3B4552}.contact-box a{color:var(--blue);font-weight:600}
[dir=rtl] body,[dir=rtl] h1,[dir=rtl] h2,[dir=rtl] h3,[dir=rtl] .dek,[dir=rtl] .lede,[dir=rtl] .statement p.big,[dir=rtl] .page-head p{font-family:var(--ar)}
[dir=rtl] .label,[dir=rtl] .sec-head h2,[dir=rtl] .side h2,[dir=rtl] .brand .t2{letter-spacing:0}
"""

FONTS = ('<link rel="preload" href="/assets/fonts/PlexSerif-Bold.woff" as="font" type="font/woff" crossorigin>')
FONTS_AR = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">')

MARK = ('<svg class="mark" viewBox="0 0 44 44" aria-hidden="true"><rect width="44" height="44" fill="#0B2B4E"/>'
        '<path d="M5 34 L17 15 L23 24 L28 17 L39 34 Z" fill="#fff"/>'
        '<circle cx="31" cy="10" r="2.6" fill="#B08D3C"/></svg>')

NAV_EN = [("Research", "/research/"), ("Topics", "/topics/"), ("About", "/about/"), ("Contact", "/contact/")]
NAV_AR = [("الأبحاث", "/ar/research/"), ("المجالات", "/ar/topics/"), ("عن المركز", "/ar/about/"), ("تواصل معنا", "/ar/contact/")]

import hashlib
CSS_VER = hashlib.md5(CSS.encode()).hexdigest()[:8]

def mins(a): return max(1, round(words(a) / 230))
def initials(name):
    if "team" in name: return "AC"
    if " and " in name: return "".join(n.strip()[0] for n in name.split(" and ")[:2]).upper()
    return "".join(w[0] for w in name.split()[:2]).upper()

def page(path, title, desc, body, active=None, ar=False, og_image="/assets/img/og-default.jpg", og_type="website", extra_head=""):
    lang = "ar" if ar else "en"
    nav = NAV_AR if ar else NAV_EN
    navhtml = "".join(f'<a href="{u}"{" aria-current=\"page\"" if u == active else ""}>{t}</a>' for t, u in nav)
    navhtml += (f'<a class="btn" href="/ar/contact/#subscribe">اشترك</a>' if ar else '<a class="btn" href="/contact/#subscribe">Subscribe</a>')
    full_title = title if title.startswith(("Anneer", "مركز")) else f"{title} | {'مركز النير' if ar else 'Anneer Center'}"
    brand_t1 = "النير" if ar else "ANNEER"
    brand_t2 = "مركز النير للسياسات والدراسات الاستراتيجية" if ar else "Center for Policy and Strategic Studies"
    tb_base = "/ar/topics/" if ar else "/topics/"
    topicbar = (f'<div class="topicbar"><div class="wrap"><b>{"المجالات" if ar else "Topics"}</b>'
                + "".join(f'<a href="{tb_base}#{k}">{v[1] if ar else v[0]}</a>' for k, v in TOPICS.items()) + "</div></div>")
    return f"""<!DOCTYPE html>
<html lang="{lang}"{' dir="rtl"' if ar else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{SITE}{path}">
<meta name="theme-color" content="#0B2B4E">
<meta property="og:site_name" content="Anneer Center">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{SITE}{path}">
<meta property="og:type" content="{og_type}">
<meta property="og:image" content="{SITE}{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}{og_image}">
<meta name="twitter:site" content="@anneercenter">
<link rel="icon" href="/assets/favicon.ico" sizes="any"><link rel="icon" href="/assets/icon-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="/assets/icon-180.png">
<link rel="alternate" type="application/rss+xml" title="Anneer Center research" href="/feed.xml">
{FONTS}{FONTS_AR if ar else ''}
<link rel="stylesheet" href="/assets/site.css?v={CSS_VER}">
{extra_head}
</head>
<body>
<a class="skip" href="#content">{'تخطَّ إلى المحتوى' if ar else 'Skip to content'}</a>
<header class="site"><div class="wrap bar">
  <a class="brand" href="{'/ar/' if ar else '/'}" aria-label="{'مركز النير، الصفحة الرئيسية' if ar else 'Anneer Center home'}"><span><img class="logo" src="/assets/img/logo-navy.png" alt="Anneer" width="800" height="145"><div class="t2">{brand_t2}</div></span></a>
  <button class="menu-btn" aria-expanded="false" aria-controls="nav" onclick="var n=document.getElementById('nav');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))">{'القائمة' if ar else 'Menu'}</button>
  <nav class="main" id="nav" aria-label="{'القائمة الرئيسية' if ar else 'Main'}">{navhtml}</nav>
</div></header>
{topicbar}
<main id="content">
{body}
</main>
{footer_html(ar)}
</body>
</html>
"""

SOCIAL = [("X", "https://x.com/anneercenter", '<path d="M18.9 2H22l-7.6 8.7L23.3 22h-7l-5.5-7.2L4.5 22H1.4l8.1-9.3L1 2h7.1l5 6.6L18.9 2zm-1.2 18h1.7L7.1 3.9H5.3L17.7 20z"/>'),
          ("Instagram", "https://www.instagram.com/anneercenter", '<path d="M12 2.2c3.2 0 3.6 0 4.8.1 3.3.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 3.9 3.9 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2zM12 0C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0zm0 5.8a6.2 6.2 0 100 12.4 6.2 6.2 0 000-12.4zM12 16a4 4 0 110-8 4 4 0 010 8zm6.4-11.8a1.4 1.4 0 100 2.9 1.4 1.4 0 000-2.9z"/>'),
          ("TikTok", "https://www.tiktok.com/@anneercenter", '<path d="M19.6 6.7a4.8 4.8 0 01-3.8-4.2V2h-3.4v13.6a2.9 2.9 0 11-2-2.8V9.3a6.3 6.3 0 105.4 6.3V8.7a8.2 8.2 0 004.8 1.5V6.8z"/>')]

def social_icons(color="#DDE4EC"):
    return '<div class="social">' + "".join(f'<a href="{u}" target="_blank" rel="noopener" aria-label="Anneer Center on {n}"><svg viewBox="0 0 24 24" width="20" height="20" fill="{color}" aria-hidden="true">{d}</svg></a>' for n, u, d in SOCIAL) + '</div>'

def footer_html(ar):
    y = datetime.date.today().year
    if ar:
        return f"""<footer class="site"><div class="wrap">
<div class="cols">
<div><img src="/assets/img/logo-white.png" alt="Anneer" width="800" height="146" style="width:130px;height:auto"><div class="fname" style="font-family:var(--ar);letter-spacing:0;font-size:20px;margin-top:12px">مركز النير</div><div class="ar">للسياسات والدراسات الاستراتيجية</div><p style="margin-top:16px;max-width:340px">مركز أبحاث مستقل يقدّم تحليلاً رصيناً للقضايا التي تشكّل مستقبل الدول والمجتمعات.</p></div>
<div><h4>المركز</h4><ul><li><a href="/ar/about/">عن المركز</a></li><li><a href="/ar/about/#approach">منهجنا</a></li><li><a href="/ar/contact/">تواصل معنا</a></li></ul></div>
<div><h4>الأبحاث</h4><ul><li><a href="/ar/research/">جميع الأبحاث</a></li><li><a href="/ar/topics/">مجالات البحث</a></li></ul></div>
<div><h4>تواصل</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/">English</a></li></ul></div>
</div>
<div class="copy"><span>© {y} مركز النير للسياسات والدراسات الاستراتيجية. جميع الحقوق محفوظة.</span></div>
</div></footer>"""
    return f"""<footer class="site"><div class="wrap">
<div class="cols">
<div><img src="/assets/img/logo-white.png" alt="Anneer" width="800" height="146" style="width:130px;height:auto"><div style="margin-top:6px">Center for Policy and Strategic Studies</div><div class="ar" lang="ar" dir="rtl" style="text-align:left">مركز النير للسياسات والدراسات الاستراتيجية</div><p style="margin-top:16px;max-width:340px">Independent research and analysis on the questions that shape nations and societies.</p>{social_icons()}</div>
<div><h4>Institution</h4><ul><li><a href="/about/">About</a></li><li><a href="/about/#approach">Our approach</a></li><li><a href="/about/#standards">Research standards</a></li><li><a href="/contact/">Contact</a></li></ul></div>
<div><h4>Research</h4><ul><li><a href="/research/">All research</a></li><li><a href="/topics/">Topics</a></li><li><a href="/feed.xml">RSS feed</a></li></ul></div>
<div><h4>Connect</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/contact/#media">Media inquiries</a></li><li><a href="/contact/#subscribe">Subscribe</a></li><li><a href="https://x.com/anneercenter" target="_blank" rel="noopener">X (Twitter)</a></li><li><a href="https://www.instagram.com/anneercenter" target="_blank" rel="noopener">Instagram</a></li><li><a href="https://www.tiktok.com/@anneercenter" target="_blank" rel="noopener">TikTok</a></li></ul></div>
</div>
<div class="copy"><span>© {y} Anneer Center for Policy and Strategic Studies. All rights reserved.</span><span>Views expressed in Anneer publications are those of their authors.</span></div>
</div></footer>"""

def topic_label(a, ar=False):
    t = a["topics"][0]
    base = "/ar/topics/" if ar else "/topics/"
    return f'<div class="label"><a href="{base}#{t}">{TOPICS[t][1] if ar else TOPICS[t][0]}</a></div>'

def tags(a, ar=False):
    base = "/ar/topics/" if ar else "/topics/"
    return '<div class="tags">' + "".join(f'<a class="tag" href="{base}#{t}">{TOPICS[t][1] if ar else TOPICS[t][0]}</a>' for t in a["topics"]) + "</div>"

def card(a, thumb=True):
    img = (f'<a class="thumb" href="{url_of(a)}"><img src="{a["image"]}" alt="" loading="lazy" width="1600" height="900"></a>' if (thumb and a.get("image")) else "")
    return f"""<article class="card">{img}{topic_label(a)}<h3><a href="{url_of(a)}">{esc(a['title'])}</a></h3><p>{esc(a['dek'])}</p><div class="byline"><b>{esc(a['author'])}</b> · {fmt_date(a['date'])}</div></article>"""

def list_item(a, ar=False):
    note = ' <span class="byline" style="font-family:var(--ar)">(بالإنجليزية)</span>' if ar else ""
    kind = a['kind'] if not ar else ('تحليل' if a['kind'] == 'Analysis' else 'مقالة')
    return f"""<article class="item" data-topics="{' '.join(a['topics'])}"><div class="byline">{fmt_date(a['date'], ar)}<div class="label" style="margin-top:6px;color:var(--muted)">{kind}</div></div>
<div>{topic_label(a, ar)}<h2><a href="{url_of(a)}" lang="en" dir="ltr">{esc(a['title'])}</a>{note}</h2><p lang="en" dir="ltr">{esc(a['dek'])}</p><div class="byline" style="margin-bottom:4px"><b>{esc(a['author'])}</b> · {mins(a)} min read</div>{tags(a, ar)}</div></article>"""

def topics_count(k):
    n = sum(k in a["topics"] for a in ARTICLES)
    return f"{n} publication{'s' if n != 1 else ''} →" if n else "Research in preparation"

# --------------------------------------------------------------------------- pages
def home():
    lead = ARTICLES[0]
    side = "".join(f'<div class="it">{topic_label(a)}<h3><a href="{url_of(a)}">{esc(a["title"])}</a></h3><div class="byline">{esc(a["author"])} · {fmt_date(a["date"])}</div></div>' for a in ARTICLES[1:])
    topic_html = "".join(f'<a class="topic" href="/topics/#{k}"><h3>{v[0]}</h3><p>{v[2]}</p><span class="n">{topics_count(k)}</span></a>' for k, v in TOPICS.items())
    body = f"""
<div class="wrap"><div class="lead-grid">
  <article class="lead">
    {topic_label(lead)}
    <h1><a href="{url_of(lead)}">{esc(lead['title'])}</a></h1>
    <p class="dek">{esc(lead['dek'])}</p>
    <div class="byline"><b>{esc(lead['author'])}</b> · {fmt_date(lead['date'])} · {mins(lead)} min read</div>
    <p style="margin:26px 0 0"><a class="btn" href="{url_of(lead)}">Read the {'essay' if lead['kind'] == 'Essay' else 'analysis'}</a></p>
    {f'<a href="{url_of(lead)}" style="display:block;margin-top:32px"><img src="{lead["image"]}" alt="{esc(lead["image_alt"])}" width="{lead.get("image_size", (1600, 900))[0]}" height="{lead.get("image_size", (1600, 900))[1]}"></a>' if lead.get("image") else ""}
  </article>
  <aside class="side" aria-label="Latest research"><h2>Latest research</h2>{side}<p style="margin:18px 0 0"><a href="/research/" style="color:var(--blue);font-weight:600;font-size:14px">All research →</a></p></aside>
</div></div>

<section class="block"><div class="wrap">
  <div class="sec-head"><h2>Featured research</h2><a href="/research/">View all →</a></div>
  <div class="cards">{''.join(card(a, thumb=False) for a in ARTICLES)}</div>
</div></section>

<section class="statement"><div class="wrap grid">
  <p class="big">Anneer Center is an independent think tank. We study the choices that shape nations and ask, of every policy, who gains and who pays.</p>
  <div><p>Named after Jabal Al-Nir, the landmark mountain of Najd, the Center is based in Saudi Arabia and global in scope. Our research spans energy, cities, technology, the economy, resources and governance.</p>
  <a class="btn light" href="/about/">About the Center</a></div>
</div></section>

<section class="block"><div class="wrap">
  <div class="sec-head"><h2>Research topics</h2><a href="/topics/">All topics →</a></div>
  <div class="topics">{topic_html}</div>
</div></section>

<section class="block tint" id="subscribe"><div class="wrap signup">
  <div><h2>Get Anneer research in your inbox</h2><p>New publications and analysis from the Center, sent when they are released.</p></div>
  <div><a class="btn" href="mailto:{EMAIL}?subject=Subscribe%20to%20Anneer%20research">Subscribe by email</a> <a class="btn out" href="/feed.xml">RSS feed</a></div>
</div></section>
"""
    return page("/", "Anneer Center for Policy and Strategic Studies",
                "Anneer Center is an independent think tank publishing rigorous research on energy, cities, technology and the economy, with a global outlook.", body)

def research_index():
    buttons = '<button type="button" aria-pressed="true" data-f="all">All topics</button>' + "".join(
        f'<button type="button" aria-pressed="false" data-f="{k}">{v[0]}</button>' for k, v in TOPICS.items() if any(k in a["topics"] for a in ARTICLES))
    body = f"""
<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/">Home</a> / Research</div>
<h1>Research</h1><p>Analysis, essays and policy research from Anneer Center. Every publication is fully sourced and free to read.</p></section></div>
<section style="padding:32px 0 72px"><div class="wrap">
<div class="filters" role="group" aria-label="Filter by topic">{buttons}</div>
<div class="list" id="list">{''.join(list_item(a) for a in ARTICLES)}</div>
</div></section>
<script>
document.querySelectorAll('.filters button').forEach(function(b){{b.addEventListener('click',function(){{
 var f=b.dataset.f;document.querySelectorAll('.filters button').forEach(function(x){{x.setAttribute('aria-pressed',x===b)}});
 document.querySelectorAll('#list .item').forEach(function(it){{it.style.display=(f==='all'||it.dataset.topics.split(' ').indexOf(f)>-1)?'':'none'}});
}})}});
</script>"""
    return page("/research/", "Research", "All research and analysis published by Anneer Center.", body, active="/research/")

def topics_page(ar=False):
    secs = ""
    for k, v in TOPICS.items():
        items = [a for a in ARTICLES if k in a["topics"]]
        inner = "".join(list_item(a, ar) for a in items) if items else (
            f'<p class="byline" style="padding:8px 0 20px">{"قريباً: أبحاث جديدة في هذا المجال." if ar else "New research in this area is in preparation."}</p>')
        desc = "" if ar else f'<p style="margin:-14px 0 4px;color:#3B4552;font-family:var(--serif);font-size:18px">{v[2]}</p>'
        secs += f'<section id="{k}" style="margin-bottom:56px;scroll-margin-top:140px"><div class="sec-head"><h2>{v[1] if ar else v[0]}</h2></div>{desc}<div class="list">{inner}</div></section>'
    if ar:
        body = f"""<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/ar/">الرئيسية</a> / المجالات</div><h1>مجالات البحث</h1><p>يركّز مركز النير على ستة مجالات مترابطة تتقاطع فيها السياسات العامة مع الاقتصاد والمجتمع. الأبحاث المنشورة حالياً متاحة باللغة الإنجليزية.</p></section></div>
<section style="padding:40px 0 40px"><div class="wrap">{secs}</div></section>"""
        return page("/ar/topics/", "مجالات البحث", "مجالات البحث في مركز النير.", body, active="/ar/topics/", ar=True)
    body = f"""<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/">Home</a> / Topics</div><h1>Topics</h1><p>Anneer's research is organised around six connected areas where public policy meets economics and society.</p></section></div>
<section style="padding:40px 0 40px"><div class="wrap">{secs}</div></section>"""
    return page("/topics/", "Topics", "Anneer Center research topics: energy, cities, technology, economy, resources and governance.", body, active="/topics/")

def article(a):
    c = CONTENT[a["key"]]
    out = []
    for b in c["body"]:
        t = re.sub("<[^>]+>", "", b["html"]).strip()
        if b["kind"] == "h1": continue
        if t.startswith("By [Analyst") or t in ("Sanad Falhan ·", "Anneer Center research team ·"): continue
        if a["key"] == "dc" and b["html"].startswith("<em>") and b["html"].endswith("</em>"): continue
        out.append(b)
    parts = []; in_list = False
    for b in out:
        if b["kind"] == "html":
            parts.append(b["html"]); continue
        if b["kind"] == "li":
            if not in_list: parts.append("<ul>"); in_list = True
            parts.append(f"<li>{b['html']}</li>"); continue
        if in_list: parts.append("</ul>"); in_list = False
        if b["kind"] == "h2": parts.append(f"<h2>{b['html']}</h2>")
        else:
            parts.append(f"<p>{b['html']}</p>")
            if a["key"] == "dc":
                t = re.sub("<[^>]+>", "", b["html"])
                for k, (src, alt, cap) in FIGURES.items():
                    if t.startswith(k):
                        parts.append(f'<figure><img src="{src}" alt="{esc(alt)}" width="1600" height="900" loading="lazy"><figcaption>{esc(cap)}</figcaption></figure>')
    if in_list: parts.append("</ul>")
    src_items = "".join(f"<li>{s}</li>" for s in c["sources"])
    url = SITE + url_of(a)
    share = (f'<div class="share"><a href="https://twitter.com/intent/tweet?url={url}&amp;text={esc(a["title"])}&amp;via=anneercenter" target="_blank" rel="noopener">Share on X</a>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={url}" target="_blank" rel="noopener">LinkedIn</a>'
             f'<a href="mailto:?subject={esc(a["title"])}&amp;body={url}">Email</a></div>')
    iw, ih = a.get("image_size", (1600, 900))
    hero = (f'<figure class="hero-img"><img src="{a["image"]}" alt="{esc(a["image_alt"])}" width="{iw}" height="{ih}"><figcaption>{esc(a.get("image_caption", "Illustration: Anneer Center"))}</figcaption></figure>' if a["image"] else "")
    pdf = f'<a class="btn" href="{a["pdf"]}" download>Download PDF</a>' if a["pdf"] else ""
    related = "".join(f'<a class="t" href="{url_of(x)}">{esc(x["title"])}</a>' for x in ARTICLES if x is not a)
    topics_box = "".join(f'<a class="tag" href="/topics/#{t}">{TOPICS[t][0]}</a>' for t in a["topics"])
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["dek"],
                     "datePublished": a["date"], "author": {"@type": "Organization" if "team" in a["author"] else "Person", "name": a["author"]},
                     "publisher": {"@type": "Organization", "name": "Anneer Center for Policy and Strategic Studies", "url": SITE},
                     "mainEntityOfPage": url, **({"image": SITE + a["image"]} if a["image"] else {})}, ensure_ascii=False)
    body = f"""
<article><div class="wrap">
<header class="art-head"><div class="inner">
  <div class="crumbs"><a href="/">Home</a> / <a href="/research/">Research</a></div>
  <div style="margin-top:22px">{topic_label(a)}</div>
  <h1>{esc(a['title'])}</h1>
  <p class="dek">{esc(a['dek'])}</p>
  <div class="authors"><div class="who"><span class="avatar" aria-hidden="true">{initials(a['author'])}</span><div><div style="font-weight:600">{esc(a['author'])}</div><div class="byline">{a['kind']} · {fmt_date(a['date'])} · {mins(a)} min read</div></div></div>{share}</div>
</div></header>
<div class="art-body">
  <div>
    {hero}
    <div class="prose">{''.join(parts)}</div>
    <section class="sources"><h2>{c['sources_title']}</h2><ol>{src_items}</ol></section>
    <div class="cite"><b>Cite this publication:</b> {esc(a['author'])}, “{esc(a['title'])}”, Anneer Center for Policy and Strategic Studies, {fmt_date(a['date'])}, {url}</div>
    <div class="art-foot">{pdf}<a class="btn out" href="/research/">More research</a></div>
  </div>
  <aside class="rail">
    <div class="box"><h4>Topics</h4><div class="tags">{topics_box}</div></div>
    <div class="box"><h4>Related research</h4>{related}</div>
    <div class="box"><h4>Stay informed</h4><p style="margin:0 0 12px;color:#3B4552;font-size:15px">Get new Anneer research by email.</p><a class="btn" href="/contact/#subscribe">Subscribe</a></div>
  </aside>
</div>
</div></article>"""
    return page(url_of(a), a["title"], a["dek"], body, active="/research/",
                og_image=a.get("og") or a["image"] or "/assets/img/og-default.jpg", og_type="article",
                extra_head=f'<meta property="article:published_time" content="{a["date"]}"><script type="application/ld+json">{ld}</script>')

def about():
    body = f"""
<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/">Home</a> / About</div>
<h1>About Anneer Center</h1><p>An independent think tank for policy and strategic studies, based in Saudi Arabia and global in scope.</p></section></div>
<section class="block"><div class="wrap two">
<div class="label">Our mission</div>
<div><p class="lede">Anneer Center for Policy and Strategic Studies exists to improve the quality of public decisions. We study the questions that will shape economies and societies for decades, from energy and infrastructure to technology and the organisation of the state, and we publish analysis that decision-makers and citizens can trust.</p>
<p class="lede">We work globally. Saudi Arabia is our home and an important subject of our research, but the questions we study are shared by countries everywhere, and the best answers usually come from comparing them.</p></div>
</div></section>
<section class="block tint"><div class="wrap two">
<div><div class="label">Our name</div><h2 style="font-size:34px;margin-top:12px">Jabal Al-Nir</h2><div lang="ar" dir="rtl" style="font-family:var(--ar);font-size:26px;color:var(--navy);margin-top:8px;text-align:left">النير</div></div>
<div><p class="lede">Anneer takes its name from Jabal Al-Nir, a landmark mountain of Najd. A mountain is rooted and steady, and from its summit the view is long and clear. Those are the qualities we want in our work: grounded in evidence, independent of passing pressures, and able to see further than the immediate debate.</p></div>
</div></section>
<section class="block" id="approach" style="scroll-margin-top:140px"><div class="wrap">
<div class="sec-head"><h2>Our approach</h2></div>
<div class="pillars">
<div class="pillar"><h3>Start with the question</h3><p>Every publication answers a question that matters to real decisions, and states its answer in the opening paragraph.</p></div>
<div class="pillar"><h3>Compare across countries</h3><p>We test ideas against the experience of other places, learning from both successes and failures before drawing conclusions.</p></div>
<div class="pillar"><h3>Ask who gains and who pays</h3><p>Policies have winners and losers. We make the distribution of costs and benefits explicit, and propose ways to make it fairer.</p></div>
</div></div></section>
<section class="block tint" id="standards" style="scroll-margin-top:140px"><div class="wrap two">
<div class="label">Research standards</div>
<div class="inline">
<p class="lede" style="font-size:19px"><b>Sourcing.</b> Every factual claim in an Anneer publication is linked to its source, so readers can check our work for themselves.</p>
<p class="lede" style="font-size:19px"><b>Balance.</b> When we take a position, we present the strongest arguments against it and explain why we reached our conclusion.</p>
<p class="lede" style="font-size:19px"><b>Independence.</b> Our conclusions are our own. The views in each publication are those of its authors.</p>
<p class="lede" style="font-size:19px"><b>Corrections.</b> If we get something wrong, we correct it openly. Please write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></div></section>
<section class="block"><div class="wrap signup">
<div><h2>Work with Anneer</h2><p>We welcome enquiries from researchers, institutions and media.</p></div>
<div><a class="btn" href="/contact/">Contact the Center</a> <a class="btn out" href="/research/">Read our research</a></div>
</div></section>"""
    return page("/about/", "About", "About Anneer Center for Policy and Strategic Studies: mission, name, approach and research standards.", body, active="/about/")

def contact():
    body = f"""
<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/">Home</a> / Contact</div>
<h1>Contact</h1><p>We would be glad to hear from you.</p></section></div>
<section class="block"><div class="wrap"><div class="cards">
<div class="contact-box"><h3>General enquiries</h3><p>Questions about the Center, our research or partnerships.</p><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="contact-box" id="media" style="scroll-margin-top:140px"><h3>Media</h3><p>Interview requests and media enquiries about our publications.</p><a href="mailto:{EMAIL}?subject=Media%20enquiry">{EMAIL}</a></div>
<div class="contact-box" id="subscribe" style="scroll-margin-top:140px"><h3>Subscribe</h3><p>Receive new research from Anneer by email.</p><a href="mailto:{EMAIL}?subject=Subscribe%20to%20Anneer%20research">Subscribe by email</a></div>
</div>
<div class="contact-box" style="margin-top:40px;max-width:420px"><h3>Follow us</h3><p>@anneercenter on X, Instagram and TikTok.</p>{social_icons("#0C2850")}</div>
</div></section>"""
    return page("/contact/", "Contact", "Contact Anneer Center for Policy and Strategic Studies.", body, active="/contact/")

def ar_home():
    lead = ARTICLES[0]
    body = f"""
<div class="wrap"><div class="lead-grid">
  <div class="lead"><div class="label">مركز النير للسياسات والدراسات الاستراتيجية</div>
  <h1>تحليل مستقل للخيارات التي تصنع مستقبل الدول.</h1>
  <p class="dek">ينشر مركز النير أبحاثاً رصينة قائمة على الأدلة في مجالات الطاقة والمدن والتقنية والاقتصاد، بنظرة عالمية وسؤال حاضر في كل بحث: من يستفيد، ومن يتحمّل الكلفة؟</p>
  <p style="margin:6px 0 0"><a class="btn" href="/ar/research/">تصفّح الأبحاث</a> <a class="btn out" href="/ar/about/">عن المركز</a></p></div>
  <aside class="side"><h2>أحدث الأبحاث</h2>{''.join(f'<div class="it">{topic_label(a, True)}<h3 lang="en" dir="ltr" style="text-align:right;font-family:var(--serif)"><a href="{url_of(a)}">{esc(a["title"])}</a></h3><div class="byline">{fmt_date(a["date"], True)} · بالإنجليزية</div></div>' for a in ARTICLES)}</aside>
</div></div>
<section class="statement"><div class="wrap grid">
  <p class="big">اسمٌ من جبل، ورؤيةٌ واضحة.</p>
  <div><p>يستمد المركز اسمه من جبل النير، أحد أبرز معالم نجد. وكما يمنح الجبلُ من يعتليه رؤيةً بعيدة وواضحة، نسعى إلى عمل بحثي راسخ ومستقل وبعيد النظر.</p><a class="btn light" href="/ar/about/">عن المركز</a></div>
</div></section>"""
    return page("/ar/", "مركز النير للسياسات والدراسات الاستراتيجية", "مركز النير: مركز أبحاث مستقل يقدّم تحليلاً رصيناً في الطاقة والمدن والتقنية والاقتصاد.", body, ar=True)

def ar_research():
    body = f"""<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/ar/">الرئيسية</a> / الأبحاث</div><h1>الأبحاث</h1><p>تحليلات ومقالات وأبحاث سياسات من مركز النير. الأبحاث المنشورة حالياً متاحة باللغة الإنجليزية.</p></section></div>
<section style="padding:24px 0 72px"><div class="wrap"><div class="list">{''.join(list_item(a, True) for a in ARTICLES)}</div></div></section>"""
    return page("/ar/research/", "الأبحاث", "أبحاث مركز النير.", body, active="/ar/research/", ar=True)

def ar_about():
    body = f"""<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/ar/">الرئيسية</a> / عن المركز</div><h1>عن مركز النير</h1><p>مركز أبحاث مستقل للسياسات والدراسات الاستراتيجية، مقره المملكة العربية السعودية ونطاقه عالمي.</p></section></div>
<section class="block"><div class="wrap two"><div class="label">رسالتنا</div>
<div><p class="lede">يعمل مركز النير على رفع جودة القرار العام، فيدرس القضايا التي ستشكّل الاقتصادات والمجتمعات لعقود قادمة، من الطاقة والبنية التحتية إلى التقنية وتنظيم الدولة، وينشر تحليلات يثق بها صانعو القرار والمواطنون.</p>
<p class="lede">نعمل بنظرة عالمية؛ فالمملكة العربية السعودية موطننا ومحور مهم من أبحاثنا، غير أن الأسئلة التي ندرسها مشتركة بين الدول، وأفضل الإجابات تأتي غالباً من المقارنة بينها.</p></div></div></section>
<section class="block tint"><div class="wrap two"><div><div class="label">اسمنا</div><h2 style="font-size:32px;margin-top:12px">جبل النير</h2></div>
<div><p class="lede">يستمد المركز اسمه من جبل النير، أحد أبرز معالم نجد. الجبل راسخٌ ثابت، ومن قمته تمتد الرؤية بعيدة وواضحة. وتلك هي الصفات التي ننشدها في عملنا: أن يستند إلى الدليل، وأن يستقل عن الضغوط العابرة، وأن يرى أبعد من الجدل الآني.</p></div></div></section>
<section class="block" id="approach"><div class="wrap"><div class="sec-head"><h2>منهجنا</h2></div>
<div class="pillars">
<div class="pillar"><h3>نبدأ بالسؤال</h3><p>يجيب كل بحث عن سؤال يهمّ قرارات حقيقية، ويعلن إجابته في فقرته الأولى.</p></div>
<div class="pillar"><h3>نقارن بين الدول</h3><p>نختبر الأفكار في ضوء تجارب الدول الأخرى، ونتعلّم من نجاحاتها وإخفاقاتها قبل أن نصل إلى استنتاجاتنا.</p></div>
<div class="pillar"><h3>نسأل: من يستفيد ومن يدفع؟</h3><p>للسياسات رابحون وخاسرون، ونحرص على إبراز توزيع التكاليف والمنافع واقتراح ما يجعله أكثر عدلاً.</p></div>
</div></div></section>"""
    return page("/ar/about/", "عن المركز", "عن مركز النير للسياسات والدراسات الاستراتيجية.", body, active="/ar/about/", ar=True)

def ar_contact():
    body = f"""<div class="wrap"><section class="page-head"><div class="crumbs"><a href="/ar/">الرئيسية</a> / تواصل معنا</div><h1>تواصل معنا</h1><p>يسعدنا تواصلكم.</p></section></div>
<section class="block"><div class="wrap"><div class="cards">
<div class="contact-box"><h3>الاستفسارات العامة</h3><p>أسئلة عن المركز أو أبحاثه أو الشراكات.</p><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="contact-box"><h3>الإعلام</h3><p>طلبات المقابلات والاستفسارات الإعلامية.</p><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="contact-box" id="subscribe"><h3>القائمة البريدية</h3><p>استقبل أبحاث المركز الجديدة عبر البريد الإلكتروني.</p><a href="mailto:{EMAIL}?subject=Subscribe">اشترك عبر البريد</a></div>
</div></div></section>"""
    return page("/ar/contact/", "تواصل معنا", "تواصل مع مركز النير.", body, active="/ar/contact/", ar=True)

def not_found():
    body = """<div class="wrap"><section class="page-head" style="padding:120px 0;border:0"><div class="label">Page not found</div><h1>We could not find that page.</h1><p>It may have moved. Try our <a href="/research/" style="color:var(--blue)">research</a> or return to the <a href="/" style="color:var(--blue)">home page</a>.</p></section></div>"""
    return page("/404.html", "Page not found", "Page not found.", body)

def redirect(target):
    return f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title><link rel="canonical" href="{SITE}{target}"><meta http-equiv="refresh" content="0; url={target}"></head><body><p><a href="{target}">Continue</a></p></body></html>'

def feed():
    items = "".join(f"<item><title>{esc(a['title'])}</title><link>{SITE}{url_of(a)}</link><guid>{SITE}{url_of(a)}</guid><pubDate>{datetime.date.fromisoformat(a['date']).strftime('%a, %d %b %Y')} 08:00:00 +0300</pubDate><description>{esc(a['dek'])}</description></item>" for a in ARTICLES)
    return f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Anneer Center</title><link>{SITE}/</link><description>Research from Anneer Center for Policy and Strategic Studies</description>{items}</channel></rss>'

def write(rel, text):
    p = ROOT / rel.lstrip("/")
    if rel.endswith("/"): p = p / "index.html"
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text)
    return rel

def main():
    (ROOT / "assets" / "site.css").write_text(CSS.strip() + "\n")
    urls = [write("/", home()), write("/research/", research_index()), write("/topics/", topics_page()),
            write("/about/", about()), write("/contact/", contact()),
]
    for a in ARTICLES:
        urls.append(write(url_of(a), article(a)))
        if a.get("old"): write("/" + a["old"], redirect(url_of(a)))
    write("/404.html", not_found())
    write("/feed.xml", feed())
    (ROOT / "CNAME").write_text("anneer.org\n")
    (ROOT / ".nojekyll").write_text("")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    sm = "".join(f"<url><loc>{SITE}{u}</loc></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
    print("built", len(urls), "pages")

if __name__ == "__main__":
    main()
