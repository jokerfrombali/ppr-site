# -*- coding: utf-8 -*-
"""Движок сборки статического сайта ППР ПРО."""
import os, re, html, shutil, datetime, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content.company import C, STEPS, WHY, DELIVERY, REVIEWS, CASES

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, os.environ.get('OUT', 'dist'))
BASE = os.environ.get('BASE', '').rstrip('/') or os.environ.get('BASE', '')          # префикс пути, напр. /ppr-pro-site
if os.environ.get('SITE'):
    C['site'] = os.environ['SITE'].rstrip('/') + ('' if BASE in ('', 'rel') else BASE)
if os.environ.get('FORM_ACTION'):
    C['form_action'] = os.environ['FORM_ACTION']
FORM_METHOD = os.environ.get('FORM_METHOD', 'post')
TODAY = '2026-09-12'
e = html.escape
ASSET_VER = hashlib.md5(open(os.path.join(ROOT, 'assets', 'style.css'), 'rb').read()).hexdigest()[:8]

NAV = [('/ppr/', 'ППР по видам работ'), ('/pprk/', 'ППРк на краны'),
       ('/oati/', 'Ордера ОАТИ'), ('/uslugi/', 'Услуги'),
       ('/ceny/', 'Цены'), ('/primery-ppr/', 'Примеры'), ('/blog/', 'Блог'), ('/kontakty/', 'Контакты')]

PAGES = {}   # url -> {'title','h1',...} — заполняется при регистрации, нужно для крошек и перелинковки

# ---------------------------------------------------------------- формы
def form(fid, title, note, btn='Рассчитать стоимость', variant='', page_url='', extra_work=True):
    opts = ''
    if extra_work:
        opts = ('<div class="field"><label for="%s-w">Вид работ или объект</label>'
                '<input type="text" id="%s-w" name="work" placeholder="например: монтаж металлоконструкций, ТЦ в Химках"></div>' % (fid, fid))
    return f'''<div class="form-card{variant}">
<h3>{e(title)}</h3>
<p class="fnote">{e(note)}</p>
<form action="{C['form_action']}" method="{FORM_METHOD}" novalidate>
<input type="hidden" name="page" value="{e(page_url)}">
<input type="hidden" name="form" value="{e(fid)}">
<div class="field"><label for="{fid}-n">Ваше имя</label><input type="text" id="{fid}-n" name="name" required autocomplete="name" placeholder="Как к вам обращаться"></div>
<div class="field"><label for="{fid}-p">Телефон</label><input type="tel" id="{fid}-p" name="phone" required autocomplete="tel" placeholder="+7 (___) ___-__-__"></div>
{opts}<div class="field"><label for="{fid}-c">Комментарий <span style="font-weight:400;color:var(--ink-3)">— не обязательно</span></label><textarea id="{fid}-c" name="comment" placeholder="Сроки, особенности объекта, что уже есть из документов"></textarea></div>
<button type="submit" class="btn btn-w">{e(btn)}</button>
<p class="agree">Нажимая кнопку, вы соглашаетесь с <a href="/politika-konfidencialnosti/">политикой конфиденциальности</a> и даёте согласие на обработку персональных данных.</p>
</form>
<div class="form-alt"><span>Есть готовые документы?</span>
<a href="mailto:{C['email']}">Пришлите на {e(C['email'])}</a><span>·</span>
<a href="{C['whatsapp']}" rel="nofollow noopener" target="_blank">WhatsApp</a></div>
</div>'''

def cta_band(h2, text, page_url, fid='mid', btn='Рассчитать стоимость'):
    return f'''<section class="cta-band">
<div><h2>{e(h2)}</h2><p>{e(text)}</p></div>
{form(fid, 'Расчёт стоимости', 'Ответим в течение рабочего дня. Точная цена — в договоре, до начала работы.', btn, page_url=page_url)}
</section>'''

# ---------------------------------------------------------------- элементы
def ul(items):
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'

def table(headers, rows, cls=''):
    th = ''.join(f'<th>{h}</th>' for h in headers)
    tr = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'

def faq(items):
    if not items: return ''
    out = ['<section class="section"><h2>Частые вопросы</h2><div class="faq">']
    for q, a in items:
        body = a if a.lstrip().startswith('<') else '<p>' + a.replace('\n\n', '</p><p>') + '</p>'
        out.append(f'<details><summary><h3>{e(q)}</h3></summary><div class="a">{body}</div></details>')
    out.append('</div></section>')
    return ''.join(out)

def cards(items, more='Подробнее'):
    """items: (url, h1, text)"""
    out = ['<div class="cols c3">']
    for u, t, d in items:
        out.append(f'<a class="card card-l" href="{u}"><h3>{e(t)}</h3><p>{e(d)}</p><span class="more">{more} →</span></a>')
    out.append('</div>')
    return ''.join(out)

def linklist(items):
    return '<ul class="linklist">' + ''.join(f'<li><a href="{u}">{e(t)}</a></li>' for u, t in items) + '</ul>'

def steps_block(h2='Как мы работаем'):
    li = ''.join(f'<li><div><h3>{e(t)}</h3><p>{e(d)}</p></div></li>' for t, d in STEPS)
    return f'<section class="section"><h2>{e(h2)}</h2><ol class="steps">{li}</ol></section>'

def why_block(h2='Почему заказывают у нас'):
    c = ''.join(f'<div class="card"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in WHY)
    return f'<section class="section"><h2>{e(h2)}</h2><div class="cols c4">{c}</div></section>'

def delivery_block(h2='Что вы получаете'):
    return ('<section class="section"><h2>' + e(h2) + '</h2>'
            '<p>Состав комплекта зависит от вида работ и требований заказчика. В базовую поставку входит:</p>'
            + ul([e(x) for x in DELIVERY]) + '</section>')

def price_block(page_url, h2='Сроки и стоимость'):
    return f'''<section class="section"><h2>{e(h2)}</h2>
<p>Стоимость зависит от объёма работ, типа объекта, количества разделов и срочности. Базовый ориентир — <strong>от {C['price_from']}</strong>, срок разработки — <strong>от {C['term_from']}</strong>. Точную цену называем после просмотра исходных данных, до подписания договора, и фиксируем в нём.</p>
<div class="cols c3">
<div class="tile"><b>от {C['price_from']}</b><span>стоимость разработки комплекта</span></div>
<div class="tile"><b>от {C['term_from']}</b><span>срок разработки</span></div>
<div class="tile"><b>0 ₽</b><span>правки по замечаниям согласующих</span></div>
</div>
<p>На что влияет цена: площадь и сложность объекта, количество видов работ в одном комплекте, необходимость расчётов (устойчивость, грузоподъёмность, крепление стенок выемок), требования конкретного заказчика или владельца объекта, сроки. Полный прайс — на странице <a href="/ceny/">цен</a>.</p>
</section>'''

def contacts_inline():
    return f'''<section class="section"><h2>Контакты</h2>
<div class="cols c3">
<div class="card"><h3>Телефон</h3><p><a href="tel:{C['phone_href']}">{e(C['phone'])}</a></p><p>{e(C['hours'])}</p></div>
<div class="card"><h3>Почта и мессенджеры</h3><p><a href="mailto:{C['email']}">{e(C['email'])}</a></p><p><a href="{C['whatsapp']}" rel="nofollow noopener" target="_blank">WhatsApp</a> · <a href="{C['telegram']}" rel="nofollow noopener" target="_blank">Telegram</a></p></div>
<div class="card"><h3>Офис</h3><p>{e(C['address'])}</p><p>Работаем по {e(C['region'])}, {e(C['region_wide'])}.</p></div>
</div></section>'''

# ---------------------------------------------------------------- каркас
def crumbs(url):
    if url == '/': return ''
    parts, acc, out = [p for p in url.strip('/').split('/')], '', [('/', 'Главная')]
    for p in parts:
        acc += '/' + p
        u = acc + '/'
        t = PAGES.get(u, {}).get('crumb') or PAGES.get(u, {}).get('h1') or p
        out.append((u, t))
    li = []
    for i, (u, t) in enumerate(out):
        last = i == len(out) - 1
        li.append(f'<li>{e(t)}</li>' if last else f'<li><a href="{u}">{e(t)}</a></li>')
    return f'<nav class="crumbs" aria-label="Хлебные крошки"><div class="wrap"><ol>{"".join(li)}</ol></div></nav>'

def header(url):
    def _cls(u):
        return ' class="on"' if u != '/' and url.startswith(u) else ''
    nav = ''.join('<a href="%s"%s>%s</a>' % (u, _cls(u), e(t)) for u, t in NAV)
    return f'''<div class="topbar"><div class="wrap">
<span>Разработка ППР, ППРк и ТК — {e(C['region'])}</span>
<span class="sp">{e(C['hours'])}</span>
<a href="mailto:{C['email']}">{e(C['email'])}</a></div></div>
<header class="site"><div class="wrap">
<a class="logo" href="/"><span aria-hidden="true" style="font-size:28px;line-height:1;color:var(--blue)">▤</span><span style="font-size:20px;font-weight:700;color:var(--ink)">ППР<b style="color:var(--cta)">1</b><b>.РФ</b><span>проекты производства работ</span></span></a>
<button class="burger" id="burger" aria-label="Меню" aria-expanded="false">Меню</button>
<nav class="main" id="nav">{nav}</nav>
<div class="hd-phone"><a href="tel:{C['phone_href']}" style="color:inherit">{e(C['phone'])}</a><small>{e(C['hours'])}</small></div>
</div></header>'''

def footer_html():
    def col(title, items):
        return f'<div><h3>{e(title)}</h3><ul>' + ''.join(f'<li><a href="{u}">{e(t)}</a></li>' for u, t in items) + '</ul></div>'
    return f'''<footer class="site"><div class="wrap"><div class="f-grid">
{col('Услуги', [('/ppr/','ППР по видам работ'),('/pprk/','ППРк на краны'),('/uslugi/pos/','ПОС'),('/uslugi/tehnologicheskie-karty/','Технологические карты'),('/uslugi/strojgenplan/','Стройгенплан'),('/uslugi/proekt-organizacii-demontazha/','ПОД на снос и демонтаж')])}
{col('Москва', [('/oati/ppr-dlya-ordera/','ППР для ордера ОАТИ'),('/oati/order-na-zemlyanye-raboty/','Ордер на земляные работы'),('/oati/poluchenie-ordera/','Получение ордера'),('/oati/zakrytie-ordera/','Закрытие ордера'),('/uslugi/strojgenplan/soglasovanie/','Согласование СГП в ОПС')])}
{col('Компания', [('/o-kompanii/','О компании'),('/o-kompanii/licenzii-i-sro/','Лицензии и СРО'),('/portfolio/','Портфолио'),('/otzyvy/','Отзывы'),('/kak-my-rabotaem/','Как мы работаем'),('/ceny/','Цены'),('/faq/','Вопросы и ответы')])}
{col('Полезное', [('/blog/chto-takoe-ppr/','Что такое ППР'),('/blog/pos-i-ppr-otlichiya/','ПОС и ППР: отличия'),('/blog/kto-razrabatyvaet-ppr/','Кто разрабатывает ППР'),('/blog/normativy-ppr/','Нормативы'),('/primery-ppr/','Примеры ППР'),('/skachat/','Скачать бланки')])}
<div><h3>Контакты</h3><ul>
<li><a href="tel:{C['phone_href']}">{e(C['phone'])}</a></li>
<li><a href="mailto:{C['email']}">{e(C['email'])}</a></li>
<li>{e(C['address'])}</li>
<li><a href="{C['whatsapp']}" rel="nofollow noopener" target="_blank">WhatsApp</a> · <a href="{C['telegram']}" rel="nofollow noopener" target="_blank">Telegram</a></li>
</ul></div>
</div>
<div class="f-bottom"><span>© {e(C['brand'])}, {datetime.date.today().year}</span>
<a href="/politika-konfidencialnosti/">Политика конфиденциальности</a>
<a href="/soglasie-na-obrabotku/">Согласие на обработку данных</a>
<a href="/karta-sajta/">Карта сайта</a>
<span>Информация на сайте не является публичной офертой.</span></div>
</div></footer>
<div class="mbar"><a class="c" href="#zayavka">Рассчитать стоимость</a><a class="p" href="tel:{C['phone_href']}">Позвонить</a></div>
<script>
document.getElementById('burger').addEventListener('click',function(){{var n=document.getElementById('nav');n.classList.toggle('open');this.setAttribute('aria-expanded',n.classList.contains('open'))}});
</script>'''

def ld_json(page):
    import json as _j
    g = [{"@context":"https://schema.org","@type":"Organization","name":C['brand'],"url":C['site'],
          "telephone":C['phone'],"email":C['email'],
          "address":{"@type":"PostalAddress","addressLocality":"Москва","streetAddress":"ул. Бутлерова, д. 17","addressCountry":"RU"},
          "areaServed":"Москва и Московская область"}]
    if page['url'] != '/':
        items, acc = [{"@type":"ListItem","position":1,"name":"Главная","item":C['site']+"/"}], ''
        for i, p in enumerate([x for x in page['url'].strip('/').split('/')], start=2):
            acc += '/' + p
            nm = PAGES.get(acc+'/', {}).get('crumb') or PAGES.get(acc+'/', {}).get('h1') or p
            items.append({"@type":"ListItem","position":i,"name":nm,"item":C['site']+acc+'/'})
        g.append({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items})
    if page.get('faq'):
        g.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":re.sub(r'<[^>]+>','',a)}} for q, a in page['faq']]})
    return ''.join('<script type="application/ld+json">%s</script>' % _j.dumps(x, ensure_ascii=False) for x in g)

def render(page):
    url = page['url']
    body = page['body']
    fin = '' if page.get('no_final_form') else f'''<section class="section" id="zayavka"><h2>{e(page.get("final_h2","Рассчитать стоимость разработки"))}</h2>
<div class="cols c2"><div>
<p>{e(page.get("final_text", "Пришлите задание — посчитаем объём разделов, назовём срок и цену. Расчёт бесплатный, ни к чему не обязывает."))}</p>
<p>Если не хватает исходных данных — подскажем, что именно нужно и где это взять. Работаем по {e(C['region'])}, {e(C['region_wide'])}.</p>
<p><strong>Телефон:</strong> <a href="tel:{C['phone_href']}">{e(C['phone'])}</a><br><strong>Почта:</strong> <a href="mailto:{C['email']}">{e(C['email'])}</a></p>
</div>{form('fin', 'Расчёт стоимости', 'Ответим в течение рабочего дня.', 'Рассчитать стоимость', page_url=url)}</div></section>'''
    canon = C['site'] + url
    metrika = ''
    if C['metrika']:
        metrika = f'<script>(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym({C["metrika"]},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});</script>'
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(page['title'])}</title>
<meta name="description" content="{e(page['desc'])}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(page['title'])}">
<meta property="og:description" content="{e(page['desc'])}">
<meta property="og:url" content="{canon}">
<meta property="og:site_name" content="{e(C['brand'])}">
<meta property="og:locale" content="ru_RU">
<link rel="stylesheet" href="/assets/style.css?v={ASSET_VER}">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
{ld_json(page)}
</head>
<body>
{header(url)}
{crumbs(url)}
<main><div class="wrap"><article>
{body}
{fin}
</article></div></main>
{footer_html()}
{metrika}
</body>
</html>'''

_ATTR = re.compile(r'((?:href|src|action)=")/(?!/)')

def rebase(html_text, url='/'):
    """BASE='rel' — относительные ссылки (работают и в корне, и в подпапке);
       BASE='/prefix' — абсолютные с префиксом; пусто — как есть."""
    if not BASE:
        return html_text
    if BASE == 'rel':
        depth = 0 if url == '/' else url.strip('/').count('/') + 1
        pref = '../' * depth if depth else './'
        return _ATTR.sub(lambda m: m.group(1) + pref, html_text)
    return _ATTR.sub(r'\1' + BASE + '/', html_text)

def write(page):
    url = page['url']
    path = os.path.join(DIST, url.strip('/'), 'index.html') if url != '/' else os.path.join(DIST, 'index.html')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(rebase(render(page), url))
    return path
