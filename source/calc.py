# -*- coding: utf-8 -*-
"""Калькулятор-ориентир стоимости: блок разметки и клиентский скрипт."""
import html
from content.company import C
e = html.escape

CALC_DOCS = [('ППР — проект производства работ', 30000, 3), ('ППРк — работы кранами', 35000, 4),
             ('ППР для ордера ОАТИ', 40000, 5), ('Технологическая карта', 15000, 2),
             ('ПОС — организация строительства', 60000, 10), ('ПОД — снос и демонтаж', 45000, 5)]
CALC_OBJ = [('Небольшой объект, частный дом, помещение', 1.0), ('Коммерческое здание, ЖК до 9 этажей', 1.4),
            ('Линейный объект: сети, дороги', 1.6), ('Промышленный, высотный, действующее производство', 1.9)]

def calc_block(doc=0, h2='Сколько стоит — ориентир за 10 секунд'):
    d = ''.join(f'<option value="{p}|{t}"{" selected" if i == doc else ""}>{e(n)}</option>'
                for i, (n, p, t) in enumerate(CALC_DOCS))
    o = ''.join(f'<option value="{k}">{e(n)}</option>' for n, k in CALC_OBJ)
    return f'''<section class="section calc" data-calc><h2>{e(h2)}</h2>
<div class="calc-g"><div class="calc-f">
<div class="field"><label>Что нужно</label><select name="c_doc">{d}</select></div>
<div class="field"><label>Объект</label><select name="c_obj">{o}</select></div>
<div class="field"><label>Сколько видов работ в проекте</label><select name="c_n"><option value="1">Один</option><option value="1.5">2–3</option><option value="2.2">4 и больше</option></select></div>
<label class="chk"><input type="checkbox" name="c_calc"> Нужны расчёты: устойчивость крана, крепление котлована, лесов</label>
<label class="chk"><input type="checkbox" name="c_fast"> Срочно — нужен за 1–3 дня</label>
</div><div class="calc-r">
<span class="calc-k">Ориентир стоимости</span><b class="calc-p">—</b>
<span class="calc-k">Срок разработки</span><b class="calc-t">—</b>
<p>Точную цену назовём после просмотра исходных данных и зафиксируем в договоре.</p>
<a class="btn btn-w calc-go" href="#zayavka">Получить точный расчёт</a>
</div></div></section>'''

CALC_JS = """<script>
document.querySelectorAll('[data-calc]').forEach(function(b){
 function r(x){return Math.round(x/1000)*1000}
 function f(x){return x.toLocaleString('ru-RU')+' ₽'}
 function q(n){return b.querySelector('[name='+n+']')}
 function upd(){
  var d=q('c_doc').value.split('|'),p=+d[0],t=+d[1],k=+q('c_obj').value,n=+q('c_n').value;
  var c=q('c_calc').checked,u=q('c_fast').checked;
  var lo=p*k*n+(c?15000:0); if(u)lo*=1.5; var hi=lo*1.35;
  var t1=Math.ceil(t*Math.sqrt(k*n)+(c?2:0)); if(u)t1=Math.max(1,Math.ceil(t1/2));
  b.querySelector('.calc-p').textContent=f(r(lo))+' – '+f(r(hi));
  b.querySelector('.calc-t').textContent=t1+'–'+(t1+Math.ceil(t1*.6))+' раб. дн.';
  b.dataset.sum=q('c_doc').selectedOptions[0].text+'; '+q('c_obj').selectedOptions[0].text+'; видов работ: '+q('c_n').selectedOptions[0].text+(c?'; нужны расчёты':'')+(u?'; срочно':'')+' → '+b.querySelector('.calc-p').textContent;
 }
 b.addEventListener('change',upd);upd();
 b.querySelector('.calc-go').addEventListener('click',function(){
  document.querySelectorAll('input[name=calc]').forEach(function(i){i.value=b.dataset.sum});
  if(window.ym)ym(%s,'reachGoal','calc');
 });
});
</script>""" % (C['metrika'] or 0)


# ---------------------------------------------------------------- фото разделов (Wikimedia Commons, свободные лицензии)
import json as _json, os as _os
from PIL import Image as _Image
_IMG = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'assets', 'img')
_CRED = _json.load(open(_os.path.join(_IMG, 'credits.json'), encoding='utf-8'))
_ALIAS = {'kamennye-raboty': 'kapremont-rekonstrukciya', 'okna-vitrazhi': 'fasadnye-raboty',
          'vnutrennie-seti': 'lifty', 'blagoustrojstvo': 'avtodorogi', 'uslugi': 'home', 'ppr': 'home',
          'razrabotka-ppr-moskva': 'home', 'kalkulyator': 'home'}

def photo(url, alt):
    parts = [p for p in url.strip('/').split('/') if p] or ['home']
    key = None
    for p in reversed(parts):
        k = _ALIAS.get(p, p)
        if k in _CRED: key = k; break
    if not key: return ''
    c = _CRED[key]
    w, h = _Image.open(_os.path.join(_IMG, key + '.jpg')).size
    return (f'<figure class="ph"><img src="/assets/img/{key}.jpg" alt="{e(alt)}" width="{w}" height="{h}" loading="lazy" decoding="async">'
            f'<figcaption>Фото: {e(c["author"])}, <a href="{e(c["src"])}" rel="nofollow noopener" target="_blank">{e(c["license"])}</a></figcaption></figure>')
