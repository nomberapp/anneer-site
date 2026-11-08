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
:root{--navy:#0B2B4E;--navy-2:#071D35;--gold:#B08D3C;--gold-l:#D8C08A;--ink:#1A1F26;--muted:#5B6470;--line:#E3E6EA;--paper:#FFFFFF;--tint:#F5F6F8;
--serif:"Source Serif 4",Georgia,"Times New Roman",serif;--sans:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;--ar:"IBM Plex Sans Arabic","Noto Naskh Arabic",sans-serif}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:17px;line-height:1.6}
img{max-width:100%;height:auto;display:block}
a{color:var(--navy);text-decoration-thickness:1px;text-underline-offset:3px}a:hover{color:var(--gold)}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px}
.skip{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.skip:focus{width:auto;height:auto;clip:auto;top:12px;inset-inline-start:16px;background:#fff;padding:8px 12px;z-index:10}
.util{background:var(--navy-2);color:#C9D2DC;font-size:13px}
.util .wrap{display:flex;justify-content:space-between;align-items:center;min-height:36px;gap:16px}
.util a{color:#fff;text-decoration:none}.util a:hover{color:var(--gold-l)}
.util .ar{font-family:var(--ar)}
header.site{border-bottom:1px solid var(--line);background:#fff;position:sticky;top:0;z-index:5}
header.site .wrap{display:flex;align-items:center;justify-content:space-between;min-height:84px;gap:24px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:14px;text-decoration:none;color:var(--navy)}
.brand .mark{width:44px;height:44px;flex:none}
.brand .t1{font-family:var(--serif);font-size:26px;letter-spacing:.18em;font-weight:600;line-height:1}
.brand .t2{font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-top:6px}
nav.main{display:flex;gap:30px;flex-wrap:wrap}
nav.main a{text-decoration:none;color:var(--ink);font-size:15px;font-weight:500;padding:6px 0;border-bottom:2px solid transparent}
nav.main a:hover,nav.main a[aria-current]{color:var(--navy);border-bottom-color:var(--gold)}
.menu-btn{display:none;background:none;border:1px solid var(--line);border-radius:4px;padding:10px 14px;font:500 14px var(--sans);color:var(--navy);min-height:44px}
@media (max-width:820px){.menu-btn{display:block}nav.main{display:none;width:100%;flex-direction:column;gap:0;padding-bottom:12px}nav.main.open{display:flex}nav.main a{padding:12px 0;border-bottom:1px solid var(--line)}}
.kicker{font-size:12.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
h1,h2,h3{font-family:var(--serif);font-weight:600;color:var(--navy);line-height:1.15;margin:0}
.hero{background:var(--navy);color:#fff;padding:88px 0 96px;position:relative;overflow:hidden}
.hero h1{color:#fff;font-size:clamp(38px,5.4vw,64px);max-width:900px;margin:18px 0 22px;font-weight:500}
.hero p{font-size:20px;color:#D4DBE3;max-width:700px;margin:0 0 34px}
.hero .ar-line{font-family:var(--ar);font-size:18px;color:var(--gold-l);margin-bottom:10px;text-align:left}
.hero:after{content:"";position:absolute;right:-120px;bottom:-160px;width:520px;height:520px;border:1px solid rgba(216,192,138,.25);border-radius:50%}
.btn{display:inline-flex;align-items:center;gap:10px;min-height:46px;padding:0 22px;border-radius:2px;font-weight:600;font-size:15px;text-decoration:none;border:1px solid var(--gold);background:var(--gold);color:#fff}
.btn:hover{background:#9A7A30;color:#fff}.btn.ghost{background:transparent;color:#fff;border-color:rgba(255,255,255,.5)}.btn.ghost:hover{border-color:#fff}
.btn.line{background:#fff;color:var(--navy);border-color:var(--navy)}.btn.line:hover{background:var(--navy);color:#fff}
section.block{padding:80px 0}section.tint{background:var(--tint)}
.sec-head{display:flex;justify-content:space-between;align-items:end;gap:20px;border-bottom:2px solid var(--navy);padding-bottom:14px;margin-bottom:36px;flex-wrap:wrap}
.sec-head h2{font-size:32px}.sec-head a{font-weight:600;font-size:15px;text-decoration:none}
.feature{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:48px;align-items:center}
@media (max-width:900px){.feature{grid-template-columns:1fr;gap:24px}}
.feature h3{font-size:clamp(28px,3.2vw,40px);margin:12px 0 16px}.feature h3 a{text-decoration:none}
.feature p.dek{font-family:var(--serif);font-size:20px;color:#3A4350;margin:0 0 18px}
.meta{font-size:14px;color:var(--muted)}.meta b{color:var(--ink);font-weight:600}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px}
@media (max-width:900px){.cards{grid-template-columns:1fr}}
.card{border-top:3px solid var(--gold);padding-top:18px;display:flex;flex-direction:column;gap:10px}
.card h3{font-size:23px}.card h3 a{text-decoration:none}.card p{margin:0;color:#3A4350}
.topics{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
@media (max-width:900px){.topics{grid-template-columns:1fr}}
.topic{background:#fff;padding:30px 28px;text-decoration:none;color:var(--ink);display:flex;flex-direction:column;gap:8px;min-height:180px}
.topic:hover{background:var(--tint);color:var(--ink)}.topic h3{font-size:22px}.topic .n{margin-top:auto;font-size:13px;font-weight:600;color:var(--gold)}
.band{background:var(--navy);color:#D4DBE3;padding:80px 0}
.band .grid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:56px}
@media (max-width:900px){.band .grid{grid-template-columns:1fr;gap:28px}}
.band h2{color:#fff;font-size:36px;margin:12px 0 0}.band p{margin:0 0 16px;font-size:18px}.band a{color:var(--gold-l)}
.pillars{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:32px;margin-top:8px}
@media (max-width:900px){.pillars{grid-template-columns:1fr}}
.pillar h3{font-size:22px;margin:10px 0 8px}.pillar p{margin:0;color:#3A4350}
.pillar .num{font-family:var(--serif);color:var(--gold);font-size:30px}
footer.site{background:var(--navy-2);color:#AEB9C6;padding:64px 0 28px;font-size:15px}
footer.site .cols{display:grid;grid-template-columns:2fr 1fr 1fr 1fr;gap:40px}
@media (max-width:820px){footer.site .cols{grid-template-columns:1fr 1fr}}
footer.site h4{color:#fff;font:600 13px var(--sans);letter-spacing:.12em;text-transform:uppercase;margin:0 0 14px}
footer.site ul{list-style:none;margin:0;padding:0}footer.site li{margin:0 0 10px}
footer.site a{color:#DCE3EA;text-decoration:none}footer.site a:hover{color:var(--gold-l)}
footer.site .fname{font-family:var(--serif);color:#fff;font-size:24px;letter-spacing:.18em}
footer.site .ar{font-family:var(--ar);color:var(--gold-l);margin-top:6px}
footer.site .copy{border-top:1px solid rgba(255,255,255,.12);margin-top:48px;padding-top:22px;font-size:13px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
/* page header */
.page-head{background:var(--tint);border-bottom:1px solid var(--line);padding:64px 0 48px}
.page-head h1{font-size:clamp(34px,4.4vw,52px);margin:12px 0 14px;max-width:900px}
.page-head p{font-size:19px;color:#3A4350;max-width:760px;margin:0}
.crumbs{font-size:13px;color:var(--muted)}.crumbs a{color:var(--muted)}
/* research list */
.filters{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:32px}
.filters button{font:500 14px var(--sans);border:1px solid var(--line);background:#fff;color:var(--ink);padding:0 16px;min-height:40px;border-radius:20px;cursor:pointer}
.filters button[aria-pressed=true]{background:var(--navy);border-color:var(--navy);color:#fff}
.list .item{display:grid;grid-template-columns:160px minmax(0,1fr);gap:28px;padding:30px 0;border-bottom:1px solid var(--line)}
@media (max-width:700px){.list .item{grid-template-columns:1fr;gap:8px}}
.list .item h2{font-size:26px;margin:6px 0 10px}.list .item h2 a{text-decoration:none}.list .item p{margin:0 0 10px;color:#3A4350}
.tags{display:flex;gap:8px;flex-wrap:wrap}.tag{font-size:12.5px;font-weight:600;color:var(--navy);background:#EEF1F5;border-radius:2px;padding:3px 9px;text-decoration:none}
/* article */
.art-head{padding:64px 0 36px;border-bottom:1px solid var(--line)}
.art-head .wrap{max-width:900px}
.art-head h1{font-size:clamp(34px,4.6vw,54px);margin:14px 0 18px}
.art-head .dek{font-family:var(--serif);font-size:22px;color:#3A4350;margin:0 0 24px;line-height:1.45}
.art-meta{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.art-meta .by{color:var(--ink);font-weight:600}
.share{display:flex;gap:8px;flex-wrap:wrap}.share a{font-size:13px;font-weight:600;text-decoration:none;border:1px solid var(--line);padding:0 12px;min-height:36px;display:inline-flex;align-items:center;border-radius:2px}
.hero-img{max-width:1100px;margin:36px auto 0;padding:0 28px}.hero-img figcaption{font-size:14px;color:var(--muted);margin-top:10px}
.prose{max-width:720px;margin:0 auto;padding:48px 28px 24px;font-family:var(--serif);font-size:20px;line-height:1.7;color:#1F252D}
.prose p{margin:0 0 1.25em}.prose h2{font-size:28px;margin:1.8em 0 .7em}
.prose ul{padding-left:1.2em;margin:0 0 1.25em}.prose li{margin:0 0 .6em}
.prose figure{margin:2em -60px}.prose figcaption{font-family:var(--sans);font-size:14px;color:var(--muted);margin-top:10px;padding:0 60px}
@media (max-width:860px){.prose figure{margin:2em 0}.prose figcaption{padding:0}}
.prose strong{color:var(--ink)}
.sources{max-width:720px;margin:0 auto;padding:12px 28px 40px;font-size:14.5px;color:#3A4350}
.sources h2{font-size:20px;margin:0 0 12px;border-top:1px solid var(--line);padding-top:28px}
.sources ol{padding-left:1.3em;margin:0}.sources li{margin:0 0 8px;overflow-wrap:anywhere}
.art-foot{max-width:720px;margin:0 auto 72px;padding:0 28px;display:flex;gap:12px;flex-wrap:wrap}
.cite{max-width:720px;margin:0 auto 40px;padding:20px 28px;background:var(--tint);font-size:14px;color:#3A4350}
/* misc */
.two{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:56px}@media (max-width:900px){.two{grid-template-columns:1fr;gap:28px}}
.lead{font-family:var(--serif);font-size:22px;line-height:1.55;color:#1F252D}
.contact-box{border:1px solid var(--line);padding:32px;border-top:3px solid var(--gold)}
.contact-box h3{font-size:22px;margin:0 0 8px}.contact-box p{margin:0 0 14px;color:#3A4350}
[dir=rtl] body,[dir=rtl] .prose,[dir=rtl] h1,[dir=rtl] h2,[dir=rtl] h3,[dir=rtl] .lead,[dir=rtl] .dek{font-family:var(--ar)}
[dir=rtl] .kicker,[dir=rtl] .brand .t2{letter-spacing:0}
[dir=rtl] .hero:after{right:auto;left:-120px}
@media (max-width:600px){.util .wrap>span:first-child{display:none}.util .wrap{justify-content:flex-end}.brand{gap:10px}.brand .mark{width:38px;height:38px}.brand .t1{font-size:21px}.brand .t2{font-size:9px;letter-spacing:.06em;max-width:190px}header.site .wrap{min-height:70px;gap:12px}.hero{padding:56px 0 64px}.btn{margin-bottom:8px}section.block{padding:56px 0}.prose{font-size:19px}}
"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&family=Inter:wght@400;500;600&family=IBM+Plex+Sans+Arabic:wght@400;500;600&display=swap" rel="stylesheet">')

MARK = ('<svg class="mark" viewBox="0 0 44 44" aria-hidden="true"><rect width="44" height="44" fill="#0B2B4E"/>'
        '<path d="M6 34 L17 16 L23 25 L28 18 L38 34 Z" fill="none" stroke="#D8C08A" stroke-width="2"/>'
        '<circle cx="31" cy="11" r="3" fill="#B08D3C"/></svg>')

NAV_EN = [("Research", "/research/"), ("Topics", "/topics/"), ("About", "/about/"), ("Contact", "/contact/")]
NAV_AR = [("الأبحاث", "/ar/research/"), ("المجالات", "/ar/topics/"), ("عن المركز", "/ar/about/"), ("تواصل معنا", "/ar/contact/")]

def page(path, title, desc, body, active=None, ar=False, og_image="/assets/img/og-default.jpg", og_type="website", extra_head=""):
    lang = "ar" if ar else "en"
    nav = NAV_AR if ar else NAV_EN
    navhtml = "".join(f'<a href="{u}"{" aria-current=\"page\"" if u==active else ""}>{t}</a>' for t, u in nav)
    alt_link = ("/" if ar else "/ar/")
    alt_label = ("English" if ar else '<span class="ar" lang="ar">العربية</span>')
    full_title = title if title.startswith("Anneer") or title.startswith("مركز") else f"{title} | {'مركز النير' if ar else 'Anneer Center'}"
    brand_t1 = "النير" if ar else "ANNEER"
    brand_t2 = "مركز النير للسياسات والدراسات الاستراتيجية" if ar else "Center for Policy and Strategic Studies"
    util_left = "مركز سياسات مستقل" if ar else "Independent policy research"
    footer = footer_html(ar)
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
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="Anneer Center research" href="/feed.xml">
{FONTS}
<link rel="stylesheet" href="/assets/site.css">
{extra_head}
</head>
<body>
<a class="skip" href="#content">{'تخطَّ إلى المحتوى' if ar else 'Skip to content'}</a>
<div class="util"><div class="wrap"><span>{util_left}</span><span><a href="/contact/" style="margin-inline-end:18px">{'' if ar else 'Media inquiries'}</a><a href="{alt_link}">{alt_label}</a></span></div></div>
<header class="site"><div class="wrap">
  <a class="brand" href="{'/ar/' if ar else '/'}" aria-label="{'مركز النير، الصفحة الرئيسية' if ar else 'Anneer Center home'}">{MARK}<span><div class="t1">{brand_t1}</div><div class="t2">{brand_t2}</div></span></a>
  <button class="menu-btn" aria-expanded="false" aria-controls="nav" onclick="var n=document.getElementById('nav');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))">{'القائمة' if ar else 'Menu'}</button>
  <nav class="main" id="nav" aria-label="{'القائمة الرئيسية' if ar else 'Main'}">{navhtml}</nav>
</div></header>
<main id="content">
{body}
</main>
{footer}
</body>
</html>
"""

def footer_html(ar):
    if ar:
        return f"""<footer class="site"><div class="wrap">
<div class="cols">
<div><div class="fname" style="font-family:var(--ar);letter-spacing:0">مركز النير</div><div class="ar">للسياسات والدراسات الاستراتيجية</div><p style="margin-top:16px;max-width:340px">مركز أبحاث مستقل يقدّم تحليلاً رصيناً للقضايا التي تشكّل مستقبل الدول والمجتمعات.</p></div>
<div><h4>المركز</h4><ul><li><a href="/ar/about/">عن المركز</a></li><li><a href="/ar/about/#approach">منهجنا</a></li><li><a href="/ar/contact/">تواصل معنا</a></li></ul></div>
<div><h4>الأبحاث</h4><ul><li><a href="/ar/research/">جميع الأبحاث</a></li><li><a href="/ar/topics/">مجالات البحث</a></li></ul></div>
<div><h4>تواصل</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/">English</a></li></ul></div>
</div>
<div class="copy"><span>© {datetime.date.today().year} مركز النير للسياسات والدراسات الاستراتيجية. جميع الحقوق محفوظة.</span></div>
</div></footer>"""
    return f"""<footer class="site"><div class="wrap">
<div class="cols">
<div><div class="fname">ANNEER</div><div>Center for Policy and Strategic Studies</div><div class="ar" lang="ar" dir="rtl">مركز النير للسياسات والدراسات الاستراتيجية</div><p style="margin-top:16px;max-width:340px">Independent research and analysis on the questions that shape nations and societies.</p></div>
<div><h4>Institution</h4><ul><li><a href="/about/">About</a></li><li><a href="/about/#approach">Our approach</a></li><li><a href="/about/#standards">Research standards</a></li><li><a href="/contact/">Contact</a></li></ul></div>
<div><h4>Research</h4><ul><li><a href="/research/">All research</a></li><li><a href="/topics/">Topics</a></li><li><a href="/feed.xml">RSS feed</a></li></ul></div>
<div><h4>Connect</h4><ul><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li><a href="/contact/#media">Media inquiries</a></li><li><a href="/ar/" lang="ar">العربية</a></li></ul></div>
</div>
<div class="copy"><span>© {datetime.date.today().year} Anneer Center for Policy and Strategic Studies. All rights reserved.</span><span>Views expressed in Anneer publications are those of their authors.</span></div>
</div></footer>"""

def tags(a, ar=False):
    base = "/ar/topics/" if ar else "/topics/"
    return '<div class="tags">' + "".join(f'<a class="tag" href="{base}#{t}">{TOPICS[t][1] if ar else TOPICS[t][0]}</a>' for t in a["topics"]) + "</div>"

def card(a):
    return f"""<article class="card"><div class="kicker">{a['kind']}</div><h3><a href="{url_of(a)}">{esc(a['title'])}</a></h3><p>{esc(a['dek'])}</p><div class="meta"><b>{esc(a['author'])}</b> · {fmt_date(a['date'])}</div></article>"""

def list_item(a, ar=False):
    note = ' <span class="meta">(بالإنجليزية)</span>' if ar else ""
    return f"""<article class="item" data-topics="{' '.join(a['topics'])}"><div class="meta">{fmt_date(a['date'], ar)}<br><span class="kicker">{a['kind'] if not ar else ('تحليل' if a['kind']=='Analysis' else 'مقالة')}</span></div>
<div><h2><a href="{url_of(a)}" lang="en" dir="ltr">{esc(a['title'])}</a>{note}</h2><p lang="en" dir="ltr">{esc(a['dek'])}</p><div class="meta" style="margin-bottom:10px">{esc(a['author'])} · {max(1, round(words(a)/230))} min read</div>{tags(a, ar)}</div></article>"""

# --------------------------------------------------------------------------- pages
def home():
    lead, rest = ARTICLES[0], ARTICLES[1:]
    topic_html = "".join(
        f'<a class="topic" href="/topics/#{k}"><h3>{v[0]}</h3><p style="margin:0;color:#3A4350">{v[2]}</p><span class="n">{(str(sum(k in a["topics"] for a in ARTICLES))+" publication"+("s" if sum(k in a["topics"] for a in ARTICLES)!=1 else "")+" →") if any(k in a["topics"] for a in ARTICLES) else "Research in preparation"}</span></a>'
        for k, v in TOPICS.items())
    body = f"""
<section class="hero"><div class="wrap">
  <div class="ar-line" lang="ar" dir="rtl">مركز النير للسياسات والدراسات الاستراتيجية</div>
  <div class="kicker">Anneer Center for Policy and Strategic Studies</div>
  <h1>Independent analysis of the choices that shape nations.</h1>
  <p>Anneer Center publishes rigorous, evidence-based research on energy, cities, technology and the economy, with a global outlook and a clear question at the heart of every piece: who gains, and who pays.</p>
  <a class="btn" href="/research/">Explore our research</a> <a class="btn ghost" href="/about/">About the Center</a>
</div></section>

<section class="block"><div class="wrap">
  <div class="sec-head"><h2>Featured research</h2><a href="/research/">All research →</a></div>
  <div class="feature">
    <a href="{url_of(lead)}"><img src="{lead['image']}" alt="{esc(lead['image_alt'])}" width="1600" height="900"></a>
    <div><div class="kicker">{lead['kind']} · {TOPICS[lead['topics'][0]][0]}</div>
      <h3><a href="{url_of(lead)}">{esc(lead['title'])}</a></h3>
      <p class="dek">{esc(lead['dek'])}</p>
      <div class="meta"><b>{esc(lead['author'])}</b> · {fmt_date(lead['date'])} · {max(1, round(words(lead)/230))} min read</div>
      <p style="margin-top:22px"><a class="btn line" href="{url_of(lead)}">Read the analysis</a></p>
    </div>
  </div>
</div></section>

<section class="block tint"><div class="wrap">
  <div class="sec-head"><h2>Latest publications</h2><a href="/research/">View all →</a></div>
  <div class="cards">{''.join(card(a) for a in ARTICLES)}</div>
</div></section>

<section class="block"><div class="wrap">
  <div class="sec-head"><h2>Research topics</h2><a href="/topics/">All topics →</a></div>
  <div class="topics">{topic_html}</div>
</div></section>

<section class="band"><div class="wrap grid">
  <div><div class="kicker">About Anneer</div><h2>Named for a mountain. Built for clear sight.</h2></div>
  <div><p>Anneer takes its name from Jabal Al-Nir, the landmark mountain of Najd. Like a summit, a good think tank should offer a long view: steady, independent and clear about what it sees.</p>
  <p>Based in Saudi Arabia and global in scope, the Center studies the policy questions that matter most to governments, businesses and citizens, and asks how their costs and benefits are shared.</p>
  <p><a href="/about/">Learn about our mission and approach →</a></p></div>
</div></section>

<section class="block"><div class="wrap">
  <div class="sec-head"><h2>Our approach</h2><a href="/about/#approach">How we work →</a></div>
  <div class="pillars">
    <div class="pillar"><div class="num">01</div><h3>Independent</h3><p>Our conclusions follow the evidence. We state our positions plainly and show the strongest arguments against them.</p></div>
    <div class="pillar"><div class="num">02</div><h3>Rigorous</h3><p>Every claim is sourced and every figure can be checked. We compare cases across countries before drawing conclusions.</p></div>
    <div class="pillar"><div class="num">03</div><h3>Distributional</h3><p>We ask not only whether a policy works, but who gains, who pays and how the balance can be made fairer.</p></div>
  </div>
</div></section>

<section class="block tint"><div class="wrap two" style="align-items:center">
  <div><div class="kicker">Stay informed</div><h2 style="font-size:32px;margin-top:10px">Receive new research from Anneer</h2></div>
  <div><p style="margin:0 0 18px;color:#3A4350">Follow new publications through our RSS feed, or write to us to be added to our mailing list for new research and events.</p>
  <a class="btn" href="mailto:{EMAIL}?subject=Subscribe%20to%20Anneer%20research">Join the mailing list</a> <a class="btn line" href="/feed.xml">RSS feed</a></div>
</div></section>
"""
    return page("/", "Anneer Center for Policy and Strategic Studies",
                "Anneer Center is an independent think tank publishing rigorous research on energy, cities, technology and the economy, with a global outlook.",
                body)

def research_index():
    buttons = '<button type="button" aria-pressed="true" data-f="all">All</button>' + "".join(
        f'<button type="button" aria-pressed="false" data-f="{k}">{v[0]}</button>' for k, v in TOPICS.items() if any(k in a["topics"] for a in ARTICLES))
    body = f"""
<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / Research</div>
<h1>Research</h1><p>Analysis, essays and policy research from Anneer Center. Each publication is fully sourced and open to read.</p></div></section>
<section class="block" style="padding-top:48px"><div class="wrap">
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
            f'<p class="meta" style="padding:20px 0">{"قريباً: أبحاث جديدة في هذا المجال." if ar else "New research in this area is in preparation."}</p>')
        secs += f'<section id="{k}" style="margin-bottom:56px;scroll-margin-top:110px"><div class="sec-head"><h2>{v[1] if ar else v[0]}</h2></div>{"" if ar else f"<p style=\"margin:-18px 0 8px;color:#3A4350\">{v[2]}</p>"}<div class="list">{inner}</div></section>'
    if ar:
        body = f"""<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/ar/">الرئيسية</a> / المجالات</div><h1>مجالات البحث</h1><p>يركّز مركز النير على ستة مجالات مترابطة تتقاطع فيها السياسات العامة مع الاقتصاد والمجتمع. الأبحاث المنشورة حالياً متاحة باللغة الإنجليزية.</p></div></section>
<section class="block" style="padding-top:48px"><div class="wrap">{secs}</div></section>"""
        return page("/ar/topics/", "مجالات البحث", "مجالات البحث في مركز النير.", body, active="/ar/topics/", ar=True)
    body = f"""<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / Topics</div><h1>Topics</h1><p>Anneer's research is organised around six connected areas where public policy meets economics and society.</p></div></section>
<section class="block" style="padding-top:48px"><div class="wrap">{secs}</div></section>"""
    return page("/topics/", "Topics", "Anneer Center research topics: energy, cities, technology, economy, resources and governance.", body, active="/topics/")

def article(a):
    c = CONTENT[a["key"]]
    blocks = c["body"]
    # drop title, byline, standfirst and stray captions (re-added as figures)
    out = []; skip_em = a["key"] == "dc"
    for i, b in enumerate(blocks):
        t = re.sub("<[^>]+>", "", b["html"]).strip()
        if b["kind"] == "h1": continue
        if t.startswith("By [Analyst") or t in ("Sanad Falhan ·", "Anneer Center research team ·"): continue
        if skip_em and b["html"].startswith("<em>") and b["html"].endswith("</em>"): continue
        out.append(b)
    parts = []; in_list = False
    for b in out:
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
    share = (f'<div class="share"><a href="https://twitter.com/intent/tweet?url={url}&text={html.escape(a["title"])}" target="_blank" rel="noopener">Share on X</a>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={url}" target="_blank" rel="noopener">LinkedIn</a>'
             f'<a href="mailto:?subject={html.escape(a["title"])}&body={url}">Email</a></div>')
    hero = (f'<figure class="hero-img"><img src="{a["image"]}" alt="{esc(a["image_alt"])}" width="1600" height="900"></figure>' if a["image"] else "")
    pdf = f'<a class="btn line" href="{a["pdf"]}" download>Download PDF</a>' if a["pdf"] else ""
    year = a["date"][:4]
    cite = f'<div class="cite"><b>Cite this publication:</b> {esc(a["author"])}, “{esc(a["title"])}”, Anneer Center for Policy and Strategic Studies, {fmt_date(a["date"])}, {url}</div>'
    ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["dek"],
                     "datePublished": a["date"], "author": {"@type": "Organization" if "team" in a["author"] else "Person", "name": a["author"]},
                     "publisher": {"@type": "Organization", "name": "Anneer Center for Policy and Strategic Studies", "url": SITE},
                     "mainEntityOfPage": url, **({"image": SITE + a["image"]} if a["image"] else {})}, ensure_ascii=False)
    body = f"""
<article>
<header class="art-head"><div class="wrap">
  <div class="crumbs"><a href="/">Home</a> / <a href="/research/">Research</a> / {TOPICS[a['topics'][0]][0]}</div>
  <div class="kicker" style="margin-top:22px">{a['kind']} · {TOPICS[a['topics'][0]][0]}</div>
  <h1>{esc(a['title'])}</h1>
  <p class="dek">{esc(a['dek'])}</p>
  <div class="art-meta"><div><span class="by">{esc(a['author'])}</span> · {fmt_date(a['date'])} · {max(1, round(words(a)/230))} min read</div>{share}</div>
</div></header>
{hero}
<div class="prose">{''.join(parts)}</div>
<section class="sources"><h2>{c['sources_title']}</h2><ol>{src_items}</ol></section>
{cite}
<div class="art-foot">{pdf}<a class="btn line" href="/research/">More research</a></div>
</article>
<section class="block tint"><div class="wrap"><div class="sec-head"><h2>Related research</h2></div>
<div class="cards">{''.join(card(x) for x in ARTICLES if x is not a)}</div></div></section>"""
    return page(url_of(a), a["title"], a["dek"], body, active="/research/",
                og_image=a["image"] or "/assets/img/og-default.jpg", og_type="article",
                extra_head=f'<meta property="article:published_time" content="{a["date"]}"><script type="application/ld+json">{ld}</script>')

def about():
    body = f"""
<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / About</div>
<h1>About Anneer Center</h1><p>An independent think tank for policy and strategic studies, based in Saudi Arabia and global in scope.</p></div></section>
<section class="block"><div class="wrap two">
<div><div class="kicker">Our mission</div><h2 style="font-size:34px;margin-top:10px">Clear, independent analysis for decisions that last.</h2></div>
<div><p class="lead">Anneer Center for Policy and Strategic Studies exists to improve the quality of public decisions. We study the questions that will shape economies and societies for decades, from energy and infrastructure to technology and the organisation of the state, and we publish analysis that decision-makers and citizens can trust.</p>
<p>We work globally. Saudi Arabia is our home and an important subject of our research, but the questions we study are shared by countries everywhere, and the best answers usually come from comparing them.</p></div>
</div></section>
<section class="block tint"><div class="wrap two">
<div><div class="kicker">Our name</div><h2 style="font-size:34px;margin-top:10px">Jabal Al-Nir</h2><p class="ar-line" lang="ar" dir="rtl" style="font-family:var(--ar);font-size:24px;color:var(--gold);margin-top:10px">النير</p></div>
<div><p class="lead">Anneer takes its name from Jabal Al-Nir, a landmark mountain of Najd. A mountain is rooted and steady, and from its summit the view is long and clear. Those are the qualities we want in our work: grounded in evidence, independent of passing pressures, and able to see further than the immediate debate.</p></div>
</div></section>
<section class="block" id="approach" style="scroll-margin-top:110px"><div class="wrap">
<div class="sec-head"><h2>Our approach</h2></div>
<div class="pillars">
<div class="pillar"><div class="num">01</div><h3>Start with the question</h3><p>Every publication answers a question that matters to real decisions, and states its answer in the opening paragraph.</p></div>
<div class="pillar"><div class="num">02</div><h3>Compare across countries</h3><p>We test ideas against the experience of other places, learning from both successes and failures before drawing conclusions.</p></div>
<div class="pillar"><div class="num">03</div><h3>Ask who gains and who pays</h3><p>Policies have winners and losers. We make the distribution of costs and benefits explicit, and propose ways to make it fairer.</p></div>
</div></div></section>
<section class="block tint" id="standards" style="scroll-margin-top:110px"><div class="wrap two">
<div><div class="kicker">Research standards</div><h2 style="font-size:34px;margin-top:10px">How we keep our work trustworthy</h2></div>
<div>
<p><b>Sourcing.</b> Every factual claim in an Anneer publication is linked to its source, so readers can check our work for themselves.</p>
<p><b>Balance.</b> When we take a position, we present the strongest arguments against it and explain why we reached our conclusion.</p>
<p><b>Independence.</b> Our conclusions are our own. The views in each publication are those of its authors.</p>
<p><b>Corrections.</b> If we get something wrong, we correct it openly. Please write to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></div></section>
<section class="block"><div class="wrap two" style="align-items:center">
<div><h2 style="font-size:30px">Work with Anneer</h2><p style="color:#3A4350">We welcome enquiries from researchers, institutions and media.</p></div>
<div><a class="btn" href="/contact/">Contact the Center</a> <a class="btn line" href="/research/">Read our research</a></div>
</div></section>"""
    return page("/about/", "About", "About Anneer Center for Policy and Strategic Studies: mission, name, approach and research standards.", body, active="/about/")

def contact():
    body = f"""
<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/">Home</a> / Contact</div>
<h1>Contact</h1><p>We would be glad to hear from you.</p></div></section>
<section class="block"><div class="wrap"><div class="cards">
<div class="contact-box"><h3>General enquiries</h3><p>Questions about the Center, our research or partnerships.</p><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="contact-box" id="media" style="scroll-margin-top:110px"><h3>Media</h3><p>Interview requests and media enquiries about our publications.</p><a href="mailto:{EMAIL}?subject=Media%20enquiry">{EMAIL}</a></div>
<div class="contact-box"><h3>Mailing list</h3><p>Receive new research from Anneer by email.</p><a href="mailto:{EMAIL}?subject=Subscribe%20to%20Anneer%20research">Subscribe by email</a></div>
</div></div></section>"""
    return page("/contact/", "Contact", "Contact Anneer Center for Policy and Strategic Studies.", body, active="/contact/")

def ar_home():
    body = f"""
<section class="hero"><div class="wrap">
<div class="kicker" style="font-family:var(--ar)">مركز النير للسياسات والدراسات الاستراتيجية</div>
<h1>تحليل مستقل للخيارات التي تصنع مستقبل الدول.</h1>
<p>ينشر مركز النير أبحاثاً رصينة قائمة على الأدلة في مجالات الطاقة والمدن والتقنية والاقتصاد، بنظرة عالمية وسؤال حاضر في كل بحث: من يستفيد، ومن يتحمّل الكلفة؟</p>
<a class="btn" href="/ar/research/">تصفّح الأبحاث</a> <a class="btn ghost" href="/ar/about/">عن المركز</a>
</div></section>
<section class="block"><div class="wrap">
<div class="sec-head"><h2>أحدث الأبحاث</h2><a href="/ar/research/">جميع الأبحاث ←</a></div>
<p class="meta" style="margin-top:-18px">الأبحاث المنشورة حالياً متاحة باللغة الإنجليزية، وتصدر نسخها العربية تباعاً.</p>
<div class="list">{''.join(list_item(a, True) for a in ARTICLES)}</div>
</div></section>
<section class="band"><div class="wrap grid">
<div><div class="kicker">عن النير</div><h2>اسمٌ من جبل، ورؤيةٌ واضحة.</h2></div>
<div><p>يستمد المركز اسمه من جبل النير، أحد أبرز معالم نجد. وكما يمنح الجبلُ من يعتليه رؤيةً بعيدة وواضحة، نسعى إلى عمل بحثي راسخ ومستقل وبعيد النظر.</p><p><a href="/ar/about/">تعرّف على رسالتنا ومنهجنا ←</a></p></div>
</div></section>"""
    return page("/ar/", "مركز النير للسياسات والدراسات الاستراتيجية", "مركز النير: مركز أبحاث مستقل يقدّم تحليلاً رصيناً في الطاقة والمدن والتقنية والاقتصاد.", body, ar=True)

def ar_research():
    body = f"""<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/ar/">الرئيسية</a> / الأبحاث</div><h1>الأبحاث</h1><p>تحليلات ومقالات وأبحاث سياسات من مركز النير. الأبحاث المنشورة حالياً متاحة باللغة الإنجليزية.</p></div></section>
<section class="block" style="padding-top:48px"><div class="wrap"><div class="list">{''.join(list_item(a, True) for a in ARTICLES)}</div></div></section>"""
    return page("/ar/research/", "الأبحاث", "أبحاث مركز النير.", body, active="/ar/research/", ar=True)

def ar_about():
    body = f"""<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/ar/">الرئيسية</a> / عن المركز</div><h1>عن مركز النير</h1><p>مركز أبحاث مستقل للسياسات والدراسات الاستراتيجية، مقره المملكة العربية السعودية ونطاقه عالمي.</p></div></section>
<section class="block"><div class="wrap two">
<div><div class="kicker">رسالتنا</div><h2 style="font-size:32px;margin-top:10px">تحليل واضح ومستقل لقرارات تدوم.</h2></div>
<div><p class="lead">يعمل مركز النير على رفع جودة القرار العام، فيدرس القضايا التي ستشكّل الاقتصادات والمجتمعات لعقود قادمة، من الطاقة والبنية التحتية إلى التقنية وتنظيم الدولة، وينشر تحليلات يثق بها صانعو القرار والمواطنون.</p>
<p>نعمل بنظرة عالمية؛ فالمملكة العربية السعودية موطننا ومحور مهم من أبحاثنا، غير أن الأسئلة التي ندرسها مشتركة بين الدول، وأفضل الإجابات تأتي غالباً من المقارنة بينها.</p></div>
</div></section>
<section class="block tint"><div class="wrap two"><div><div class="kicker">اسمنا</div><h2 style="font-size:32px;margin-top:10px">جبل النير</h2></div>
<div><p class="lead">يستمد المركز اسمه من جبل النير، أحد أبرز معالم نجد. الجبل راسخٌ ثابت، ومن قمته تمتد الرؤية بعيدة وواضحة. وتلك هي الصفات التي ننشدها في عملنا: أن يستند إلى الدليل، وأن يستقل عن الضغوط العابرة، وأن يرى أبعد من الجدل الآني.</p></div></div></section>
<section class="block" id="approach"><div class="wrap"><div class="sec-head"><h2>منهجنا</h2></div>
<div class="pillars">
<div class="pillar"><div class="num">٠١</div><h3>نبدأ بالسؤال</h3><p>يجيب كل بحث عن سؤال يهمّ قرارات حقيقية، ويعلن إجابته في فقرته الأولى.</p></div>
<div class="pillar"><div class="num">٠٢</div><h3>نقارن بين الدول</h3><p>نختبر الأفكار في ضوء تجارب الدول الأخرى، ونتعلّم من نجاحاتها وإخفاقاتها قبل أن نصل إلى استنتاجاتنا.</p></div>
<div class="pillar"><div class="num">٠٣</div><h3>نسأل: من يستفيد ومن يدفع؟</h3><p>للسياسات رابحون وخاسرون، ونحرص على إبراز توزيع التكاليف والمنافع واقتراح ما يجعله أكثر عدلاً.</p></div>
</div></div></section>"""
    return page("/ar/about/", "عن المركز", "عن مركز النير للسياسات والدراسات الاستراتيجية.", body, active="/ar/about/", ar=True)

def ar_contact():
    body = f"""<section class="page-head"><div class="wrap"><div class="crumbs"><a href="/ar/">الرئيسية</a> / تواصل معنا</div><h1>تواصل معنا</h1><p>يسعدنا تواصلكم.</p></div></section>
<section class="block"><div class="wrap"><div class="cards">
<div class="contact-box"><h3>الاستفسارات العامة</h3><p>أسئلة عن المركز أو أبحاثه أو الشراكات.</p><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="contact-box"><h3>الإعلام</h3><p>طلبات المقابلات والاستفسارات الإعلامية.</p><a href="mailto:{EMAIL}">{EMAIL}</a></div>
<div class="contact-box"><h3>القائمة البريدية</h3><p>استقبل أبحاث المركز الجديدة عبر البريد الإلكتروني.</p><a href="mailto:{EMAIL}?subject=Subscribe">اشترك عبر البريد</a></div>
</div></div></section>"""
    return page("/ar/contact/", "تواصل معنا", "تواصل مع مركز النير.", body, active="/ar/contact/", ar=True)

def not_found():
    body = """<section class="page-head" style="padding:120px 0"><div class="wrap"><div class="kicker">Page not found</div><h1>We could not find that page.</h1><p>It may have moved. Try our <a href="/research/">research</a> or return to the <a href="/">home page</a>.</p></div></section>"""
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
    (ROOT / "assets" / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 44 44"><rect width="44" height="44" fill="#0B2B4E"/><path d="M6 34 L17 16 L23 25 L28 18 L38 34 Z" fill="none" stroke="#D8C08A" stroke-width="2.5"/><circle cx="31" cy="11" r="3.5" fill="#B08D3C"/></svg>')
    urls = [write("/", home()), write("/research/", research_index()), write("/topics/", topics_page()),
            write("/about/", about()), write("/contact/", contact()),
            write("/ar/", ar_home()), write("/ar/research/", ar_research()), write("/ar/topics/", topics_page(True)),
            write("/ar/about/", ar_about()), write("/ar/contact/", ar_contact())]
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
