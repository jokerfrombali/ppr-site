# -*- coding: utf-8 -*-
"""Сборка сайта. Запуск: python3 build.py"""
import os, sys, shutil, importlib
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import engine
from engine import C, e, DIST, PAGES, write, ul, table, faq, cards, linklist, form, cta_band, \
                   steps_block, why_block, delivery_block, price_block, contacts_inline
import render_ppr
from redirects import MAP as REDIRECTS
from render_ppr import render_category, render_sub, hero, DEF_USP, norms_table, risk_table

def mod(name):
    try: return importlib.import_module('content.' + name)
    except ModuleNotFoundError: return None

kb_ppr    = mod('kb_ppr')
kb_pprk   = mod('kb_pprk')
kb_oati   = mod('kb_oati')
kb_uslugi = mod('kb_uslugi')
kb_dlya   = mod('kb_dlya')
kb_blog   = mod('kb_blog')
kb_trust  = mod('kb_trust')

ALL = []          # список страниц для сборки
def reg(url, title, desc, h1, body_fn, crumb=None, faq_items=None, prio='0.7', **kw):
    PAGES[url] = {'url': url, 'title': title, 'desc': desc, 'h1': h1, 'crumb': crumb or h1, 'prio': prio}
    ALL.append({'url': url, 'title': title, 'desc': desc, 'h1': h1, 'body_fn': body_fn,
                'faq': faq_items, 'prio': prio, **kw})

# ---------------------------------------------------------------- регистрация: ППР
if kb_ppr:
    reg('/ppr/', 'ППР по видам работ — разработка проектов в Москве | ППР ПРО',
        'Разработка ППР на любые виды строительных работ: земляные, кровельные, демонтаж, сети, высота, краны. 27 направлений. От 30 000 ₽, срок от 3 дней.',
        'ППР по видам работ', lambda: hub_ppr(), crumb='ППР по видам работ', prio='0.9')
    for cat in kb_ppr.CATS:
        cu = f"/ppr/{cat['slug']}/"
        reg(cu, cat['title'], cat['desc'], cat['h1'],
            (lambda c: (lambda: render_category(c, c['subs'], f"/ppr/{c['slug']}/")))(cat),
            faq_items=cat['d']['faq'], prio='0.8')
        for s in cat['subs']:
            su = cu + s['slug'] + '/'
            reg(su, s['title'], s['desc'], s['h1'],
                (lambda ss, cc, uu, pu: (lambda: render_sub(ss, cc, uu, pu)))(s, cat, su, cu),
                faq_items=s['d']['faq'], prio='0.6')

def hub_ppr():
    b = [hero('ППР по видам работ',
              'Разрабатываем проекты производства работ на 27 направлений — от земляных работ и кровли до монтажа оборудования и работ на высоте. Выберите свой вид работ или напишите нам.',
              DEF_USP, '/ppr/')]
    b.append('<p>Проект производства работ пишется не «вообще», а под конкретный процесс: у земляных работ своя нормативная база и свои опасные факторы, у монтажа металлоконструкций — другие, у работ на высоте — третьи. Поэтому и страницы здесь разделены по видам работ: на каждой описан состав комплекта, нормативы, типовые ошибки и сроки.</p>'
             '<p>Если на объекте несколько видов работ, комплект обычно собирается один — с разделами по каждому процессу. Это дешевле и удобнее в согласовании, чем несколько отдельных ППР. Напишите, что именно выполняется, — подскажем, как лучше разбить.</p>')
    b.append('<section class="section"><h2>Выберите направление</h2>'
             + cards([(f"/ppr/{c['slug']}/", c['h1'], c['d']['lead'][:145]) for c in kb_ppr.CATS]) + '</section>')
    b.append(cta_band('Не нашли свой вид работ?',
                      'Разрабатываем ППР и на нестандартные процессы. Опишите задачу — скажем, что потребуется и сколько это стоит.', '/ppr/'))
    b.append('<section class="section"><h2>Все виды работ списком</h2><p>Полный перечень страниц раздела:</p>'
             + linklist([(f"/ppr/{c['slug']}/{s['slug']}/", s['h1']) for c in kb_ppr.CATS for s in c['subs']]) + '</section>')
    b.append(price_block('/ppr/'))
    b.append(steps_block()); b.append(delivery_block()); b.append(why_block())
    b.append('<section class="section"><h2>Смежные услуги</h2>' + linklist([
        ('/pprk/', 'ППРк на краны и подъёмные сооружения'),
        ('/uslugi/pos/', 'ПОС — проект организации строительства'),
        ('/uslugi/tehnologicheskie-karty/', 'Технологические карты'),
        ('/uslugi/strojgenplan/', 'Разработка стройгенплана'),
        ('/oati/ppr-dlya-ordera/', 'ППР для ордера ОАТИ'),
        ('/uslugi/proekt-organizacii-demontazha/', 'ПОД на снос и демонтаж')]) + '</section>')
    return ''.join(b)

# ---------------------------------------------------------------- прочие разделы (подключаются по мере наличия KB)
for m in (kb_pprk, kb_oati, kb_uslugi, kb_dlya, kb_blog, kb_trust):
    if m and hasattr(m, 'register'):
        m.register(reg, globals())

# ---------------------------------------------------------------- сборка
def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    os.makedirs(DIST)
    shutil.copytree(os.path.join(ROOT, 'assets'), os.path.join(DIST, 'assets'))
    open(os.path.join(DIST, '.nojekyll'), 'w').close()
    st = os.path.join(ROOT, 'static')
    if os.path.isdir(st):
        for f in os.listdir(st):
            shutil.copy2(os.path.join(st, f), os.path.join(DIST, f))
    for p in ALL:
        page = {'url': p['url'], 'title': p['title'], 'desc': p['desc'], 'h1': p['h1'],
                'body': p['body_fn'](), 'faq': p.get('faq'),
                'no_final_form': p.get('no_final_form'),
                'final_h2': p.get('final_h2', 'Заказать смету на разработку'),
                'final_text': p.get('final_text', 'Пришлите задание — посчитаем объём разделов, назовём срок и цену. Смета бесплатная, ни к чему не обязывает.')}
        write(page)
    # sitemap
    urls = ''.join(f'  <url><loc>{C["site"]}{p["url"]}</loc><lastmod>{engine.TODAY}</lastmod>'
                   f'<changefreq>monthly</changefreq><priority>{p["prio"]}</priority></url>' for p in ALL)
    open(os.path.join(DIST, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        urls.replace('</url>', '</url>\n') + '</urlset>\n')
    open(os.path.join(DIST, 'robots.txt'), 'w', encoding='utf-8').write(
        f"User-agent: *\nDisallow: /send.php\nDisallow: /spasibo/\nClean-param: utm_source&utm_medium&utm_campaign&utm_term&utm_content&yclid&ysclid&from\n\nSitemap: {C['site']}/sitemap.xml\n")
    # 404
    from engine import render as _render
    body404 = open(os.path.join(ROOT, 'static_404.html'), encoding='utf-8').read()
    open(os.path.join(DIST, '404.html'), 'w', encoding='utf-8').write(_render({
        'url': '/404/', 'title': 'Страница не найдена | ' + C['brand'],
        'desc': 'Страница не найдена. Основные разделы сайта ППР ПРО.',
        'h1': 'Страница не найдена', 'body': body404, 'faq': None,
        'final_h2': 'Заказать смету на разработку',
        'final_text': 'Пришлите задание — посчитаем объём разделов, назовём срок и цену.'})
        if not engine.BASE else engine.rebase(_render({
        'url': '/404/', 'title': 'Страница не найдена | ' + C['brand'],
        'desc': 'Страница не найдена. Основные разделы сайта ППР ПРО.',
        'h1': 'Страница не найдена', 'body': body404, 'faq': None,
        'final_h2': 'Заказать смету на разработку',
        'final_text': 'Пришлите задание — посчитаем объём разделов, назовём срок и цену.'})))
    # .htaccess: 301 со старых адресов, 404, сжатие, кеш
    ht = ['# Сгенерировано build.py. Apache 2.4+', 'Options -Indexes', 'DirectoryIndex index.html',
          'ErrorDocument 404 /404.html', '', 'RewriteEngine On',
          '# Убрать www и перевести на https',
          'RewriteCond %{HTTP_HOST} ^www\\.(.*)$ [NC]', 'RewriteRule ^(.*)$ https://%1/$1 [R=301,L]',
          'RewriteCond %{HTTPS} off', 'RewriteRule ^(.*)$ https://%{HTTP_HOST}/$1 [R=301,L]', '',
          '# 301 со старых адресов на новую структуру']
    for old, new in REDIRECTS:
        if old == '/index.html':
            # Redirect 301 тут зациклится: DirectoryIndex внутренне резолвит "/" в
            # index.html, и это же правило перехватывает внутренний ре-запрос.
            # THE_REQUEST хранит исходную строку запроса клиента и не подменяется.
            ht.append('RewriteCond %{THE_REQUEST} \\s/index\\.html[\\s?] [NC]')
            ht.append(f'RewriteRule ^index\\.html$ {new} [R=301,L]')
        else:
            ht.append(f'Redirect 301 {old} {new}')
    ht += ['', '# Слеш в конце адреса', 'RewriteCond %{REQUEST_FILENAME} !-f',
           'RewriteCond %{REQUEST_URI} !(/$|\\.)', 'RewriteRule (.*) %{REQUEST_URI}/ [R=301,L]', '',
           '<IfModule mod_deflate.c>', '  AddOutputFilterByType DEFLATE text/html text/css application/javascript image/svg+xml text/xml',
           '</IfModule>', '<IfModule mod_expires.c>', '  ExpiresActive On',
           '  ExpiresByType text/css "access plus 1 month"', '  ExpiresByType image/svg+xml "access plus 1 month"',
           '</IfModule>']
    open(os.path.join(DIST, '.htaccess'), 'w', encoding='utf-8').write('\n'.join(ht) + '\n')
    with open(os.path.join(ROOT, 'redirects.csv'), 'w', encoding='utf-8') as f:
        f.write('Старый URL;Новый URL;Код\n')
        for old, new in REDIRECTS: f.write(f'{old};{new};301\n')
    print(f'Собрано страниц: {len(ALL)} | редиректов: {len(REDIRECTS)}')
    return len(ALL)

if __name__ == '__main__':
    main()
