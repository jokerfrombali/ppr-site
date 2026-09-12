# -*- coding: utf-8 -*-
"""Рендер страниц раздела «ППР по видам работ» (категории и виды работ)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import (C, e, form, cta_band, ul, table, faq, cards, linklist,
                    steps_block, why_block, delivery_block, price_block, PAGES)

def hero(h1, lead, usp, url, btn='Заказать смету'):
    return f'''</article></div></main>
<section class="hero"><div class="wrap">
<div><h1>{e(h1)}</h1><p class="lead">{e(lead)}</p>
<ul class="usp">{''.join(f'<li>{e(x)}</li>' for x in usp)}</ul>
<div class="hero-act"><a class="btn" href="#zayavka">{e(btn)}</a><a class="btn btn-o" href="tel:{C['phone_href']}">{e(C['phone'])}</a></div>
</div>
{form('hero', 'Расчёт сметы за 1 рабочий день', 'Пришлите вид работ и объект — посчитаем объём, срок и цену.', btn, page_url=url)}
</div></section>
<main><div class="wrap"><article>'''

DEF_USP = ['Фиксированная цена в договоре — смета до начала работы',
           'Правки по замечаниям согласующих — бесплатно',
           f'Срок от {C["term_from"]}, стоимость от {C["price_from"]}',
           'Проект ведёт профильный инженер по вашему виду работ']

def norms_table(norms):
    if not norms: return ''
    return ('<section class="section"><h2>Нормативная база</h2>'
            '<p>Разрабатываем комплект по действующим документам. Перечень зависит от вида работ и типа объекта — в вашем случае основными будут:</p>'
            + table(['Документ', 'Что регулирует'], [[f'<strong>{e(a)}</strong>', e(b)] for a, b in norms])
            + '<p>Полный разбор нормативов — в статье <a href="/blog/normativy-ppr/">«Нормативы по ППР»</a>. Актуальность документов проверяем на дату разработки проекта.</p></section>')

def risk_table(risks, what):
    if not risks: return ''
    return (f'<section class="section"><h2>Опасные факторы и проектные решения</h2>'
            f'<p>Главная практическая задача ППР — не описать работы, а показать, как вы защищаете людей и конструкции. По разделу «{e(what)}» в проекте разбираем:</p>'
            + table(['Опасный фактор', 'Что предусматриваем в ППР'], [[e(a), e(b)] for a, b in risks]) + '</section>')

def render_category(cat, subs, url_base):
    d = cat['d']
    u = url_base
    b = [hero(cat['h1'], d['lead'], d.get('usp') or DEF_USP, u)]
    for p in d['intro']: b.append(f'<p>{p}</p>')
    b.append(f'<section class="section"><h2>Когда нужен {e(d["when_title"])}</h2>'
             f'<p>{d.get("when_lead","Разработка проекта производства работ обязательна в следующих случаях:")}</p>' + ul(d['when']) +
             '<div class="note"><p>Сомневаетесь, нужен ли вам полный ППР или достаточно технологической карты? '
             'Опишите объект — ответим по существу и бесплатно. Разбор различий — в статье '
             '<a href="/blog/ppr-ili-tk/">«ППР или технологическая карта»</a>.</p></div></section>')
    if subs:
        b.append('<section class="section"><h2>' + e(d.get('subs_title', 'Виды работ, на которые разрабатываем ППР')) + '</h2>'
                 '<p>Выберите нужный вид работ — на странице описан состав проекта, нормативы и сроки. Если вашего варианта нет в списке, напишите: разрабатываем ППР и на нестандартные процессы.</p>'
                 + cards([(u + s['slug'] + '/', s['h1'], s['d']['lead'][:150]) for s in subs]))
    if d.get('works'):
        b.append('<section class="section"><h3>Какие процессы закрывает проект</h3>' + ul(d['works']) + '</section>')
    b.append('<section class="section"><h2>' + e(d['comp_title']) + '</h2>'
             f'<p>{d.get("comp_lead","Комплект собирается под конкретный объект, но структура остаётся постоянной:")}</p>')
    for h3, items in d['comp']:
        b.append(f'<h3>{e(h3)}</h3>' + ul(items))
    b.append('</section>')
    b.append(cta_band(d.get('cta_h2', 'Нужен расчёт стоимости?'),
                      d.get('cta_text', 'Пришлите исходные данные — посчитаем объём разделов, срок и цену в течение рабочего дня. Смета бесплатная.'), u))
    b.append(norms_table(d.get('norms')))
    b.append(risk_table(d.get('risk'), d.get('risk_what', cat['h1'])))
    if d.get('msk'):
        b.append('<section class="section"><h2>Особенности в Москве</h2>'
                 '<p>В Москве к этим работам добавляются городские процедуры, которых нет в регионах. На них чаще всего теряют время:</p>'
                 + ul(d['msk']) + '</section>')
    if d.get('mist'):
        b.append('<section class="section"><h2>Типовые ошибки, из-за которых проект возвращают</h2>'
                 '<p>Собрали то, что чаще всего приходится исправлять в чужих комплектах:</p>' + ul(d['mist']) + '</section>')
    b.append(price_block(u))
    b.append(steps_block())
    b.append(delivery_block())
    b.append(why_block())
    b.append(faq(d['faq']))
    if d.get('rel'):
        b.append('<section class="section"><h2>Смежные услуги</h2>' + linklist(d['rel']) + '</section>')
    return ''.join(b)

def render_sub(sub, cat, url, parent_url):
    d = sub['d']
    b = [hero(sub['h1'], d['lead'], d.get('usp') or DEF_USP, url)]
    for p in d['intro']: b.append(f'<p>{p}</p>')
    b.append(f'<section class="section"><h2>{e(d["when_title"])}</h2>'
             f'<p>{d.get("when_lead","Проект нужен, если выполняется хотя бы одно из условий:")}</p>' + ul(d['when']) + '</section>')
    b.append(f'<section class="section"><h2>{e(d["comp_title"])}</h2>'
             f'<p>{d.get("comp_lead","В комплект входят разделы, которые закрывают именно этот процесс:")}</p>' + ul(d['comp']) + '</section>')
    b.append(cta_band(d.get('cta_h2', 'Посчитать стоимость проекта'),
                      d.get('cta_text', 'Опишите объект и объём работ — назовём срок и цену в течение рабочего дня.'), url))
    b.append(norms_table(d.get('norms')))
    b.append(risk_table(d.get('risk'), d.get('risk_what', sub['h1'])))
    if d.get('msk'):
        b.append('<section class="section"><h2>Особенности в Москве</h2>' + ul(d['msk']) + '</section>')
    b.append(price_block(url))
    b.append(steps_block())
    b.append(faq(d['faq']))
    rel = d.get('rel') or []
    rel = [(parent_url, cat['h1'])] + list(rel)
    b.append('<section class="section"><h2>Смежные разделы</h2>' + linklist(rel) + '</section>')
    return ''.join(b)

INFO_USP = ['Отвечаем по нормативам, а не «по опыту знакомых»',
            'Указываем, на какой документ опирается каждый вывод',
            'Если нужен проект — разработаем: срок от 3 дней, цена от 30 000 ₽',
            'Бесплатно разберём вашу ситуацию по телефону']

def render_article(a, url):
    """a: {'lead','intro':[..],'sections':[(h2,[блоки])],'faq':[(q,a)],'rel':[(u,t)],'cta':(h2,text)}"""
    b = [hero(a['h1'], a['lead'], a.get('usp') or INFO_USP, url, a.get('btn', 'Заказать ППР'))]
    for p in a['intro']: b.append(f'<p>{p}</p>')
    mid = a.get('cta_after', 2)
    for i, (h2, blocks) in enumerate(a['sections']):
        b.append(f'<section class="section"><h2>{e(h2)}</h2>')
        for blk in blocks:
            if isinstance(blk, tuple):
                kind, val = blk
                if kind == 'h3': b.append(f'<h3>{e(val)}</h3>')
                elif kind == 'ul': b.append(ul(val))
                elif kind == 'ol': b.append('<ol>' + ''.join(f'<li>{x}</li>' for x in val) + '</ol>')
                elif kind == 'note': b.append(f'<div class="note"><p>{val}</p></div>')
                elif kind == 'warn': b.append(f'<div class="note warn"><p>{val}</p></div>')
                elif kind == 'table': b.append(table(val[0], val[1]))
            else:
                b.append(f'<p>{blk}</p>')
        b.append('</section>')
        if i == mid:
            c = a.get('cta') or ('Нужен проект производства работ?',
                                 'Разработаем ППР под ваш объект: срок от 3 дней, фиксированная цена в договоре, правки по замечаниям бесплатно.')
            b.append(cta_band(c[0], c[1], url, btn='Заказать смету'))
    b.append(faq(a['faq']))
    b.append(steps_block('Если нужен проект — как мы работаем'))
    b.append(why_block())
    if a.get('rel'):
        b.append('<section class="section"><h2>Читайте также</h2>' + linklist(a['rel']) + '</section>')
    return ''.join(b)
