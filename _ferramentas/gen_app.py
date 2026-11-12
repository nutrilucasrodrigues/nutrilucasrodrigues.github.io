"""Gera o app do plano de um paciente: python3 gen_app.py pacientes/moises.py
Saída em /home/claude/nutrilucasrodrigues.github.io/p/<slug>/ (index.html, manifest.json, sw.js, lembretes.ics, retorno.ics)."""
import sys, json, pathlib, runpy, datetime
sys.path.insert(0, '/home/claude/icons'); from ico import ico

P = runpy.run_path(sys.argv[1])['P']
OUT = pathlib.Path('/home/claude/nutrilucasrodrigues.github.io/p') / P['slug']; OUT.mkdir(parents=True, exist_ok=True)
G = '#005102'
NAMES = ['check', 'repeat-2', 'x', 'smile', 'meh', 'frown', 'calendar', 'calendar-check', 'bell', 'send', 'message-circle',
         'chart-line', 'clipboard-list', 'clipboard-check', 'list-checks', 'chef-hat', 'wifi-off', 'info', 'scale', 'glass-water', 'cup-soda', 'target']
NAMES += sorted({m[0] for m in P['medidas']} | {r[1] for r in P['receitas']} | {f[0] for f in P['fora']} | {t[0] for t in P['tips']})
IC = {n: ico(n, 20) for n in NAMES}
NAV = [('plano', 'utensils', 'Plano'), ('trocas', 'arrow-left-right', 'Trocas'), ('compras', 'shopping-cart', 'Compras'),
       ('evolucao', 'chart-line', 'Evolução'), ('dicas', 'lightbulb', 'Dicas')]

# ---------- arquivos de calendário ----------
VTZ = ["BEGIN:VTIMEZONE", "TZID:America/Sao_Paulo", "BEGIN:STANDARD", "DTSTART:19700101T000000", "TZOFFSETFROM:-0300", "TZOFFSETTO:-0300", "TZNAME:-03", "END:STANDARD", "END:VTIMEZONE"]
start = datetime.date.today() + datetime.timedelta(days=1)
ev = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//nutrilucas//plano//PT", "CALSCALE:GREGORIAN"] + VTZ
for i, m in enumerate(P['meals']):
    if m.get('opc'): continue
    hh, mm = map(int, m['h'].split(':'))
    st = f"{start:%Y%m%d}T{hh:02d}{mm:02d}00"; en = f"{start:%Y%m%d}T{hh:02d}{(mm+15)%60:02d}00" if mm + 15 < 60 else f"{start:%Y%m%d}T{hh+1:02d}{(mm+15)%60:02d}00"
    ev += ["BEGIN:VEVENT", f"UID:{P['slug']}-ref{i}@nutrilucas", f"DTSTAMP:{start:%Y%m%d}T000000Z", f"DTSTART;TZID=America/Sao_Paulo:{st}",
           f"DTEND;TZID=America/Sao_Paulo:{en}", "RRULE:FREQ=DAILY", f"SUMMARY:{m['n']} (plano)", "DESCRIPTION:" + " · ".join(m['i']).replace(",", "\\,"),
           "BEGIN:VALARM", "TRIGGER:PT0M", "ACTION:DISPLAY", f"DESCRIPTION:Hora do {m['n'].lower()}", "END:VALARM", "END:VEVENT"]
ev += ["END:VCALENDAR"]
(OUT / 'lembretes.ics').write_text("\r\n".join(ev) + "\r\n")
(OUT / 'manifest.json').write_text(json.dumps({"name": f"Meu plano · {P['nome']}", "short_name": "Meu plano", "start_url": "./", "scope": "./",
    "display": "standalone", "background_color": "#F4F8EF", "theme_color": G,
    "icons": [{"src": "../../assets/icon-192.png", "sizes": "192x192", "type": "image/png"}, {"src": "../../assets/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, ensure_ascii=False))
VER = datetime.datetime.now().strftime('%Y%m%d%H%M')
(OUT / 'sw.js').write_text(f"""const C='plano-{P['slug']}-{VER}';
const F=['./','./index.html','./manifest.json','./lembretes.ics','../../assets/logo.png','../../assets/icon-192.png'];
self.addEventListener('install',e=>{{self.skipWaiting();e.waitUntil(caches.open(C).then(c=>c.addAll(F)).catch(()=>{{}}))}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))}});
self.addEventListener('fetch',e=>{{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).then(r=>{{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp)).catch(()=>{{}});return r}}).catch(()=>caches.match(e.request,{{ignoreSearch:true}}).then(r=>r||caches.match('./index.html'))))}});
""")

P.setdefault('metas', {})
P['metas'] = {'plano': 5, 'agua': 5, 'treino': None, **P['metas']}
DATA = {k: P[k] for k in ['nome', 'key', 'retorno', 'agua_l', 'refri', 'meals', 'groups', 'medidas', 'buys', 'preparo', 'receitas', 'fora', 'tips', 'metas']}

CSS = """:root{--dark:#005102;--leaf:#8AC243;--bg:#F4F8EF;--soft:#E3EFD3;--ink:#1E2B22;--muted:#5B6B5F;--line:#DCE6D2;--card:#fff;--warn:#B4561B}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);padding-bottom:92px;-webkit-tap-highlight-color:transparent}
svg{flex:none}
header{background:var(--dark);color:#fff;padding:calc(18px + env(safe-area-inset-top)) 16px 22px;border-radius:0 0 26px 26px}
header .row{display:flex;align-items:center;justify-content:space-between;gap:12px}
header img{height:40px;background:#fff;border-radius:10px;padding:4px 8px}
header h1{font-size:24px;margin-top:16px}header p{opacity:.9;font-size:14px;margin-top:4px}
.prog{margin-top:14px;background:rgba(255,255,255,.18);border-radius:99px;height:10px;overflow:hidden}.prog i{display:block;height:100%;width:0;background:var(--leaf);transition:width .3s}
.progt{font-size:13px;margin-top:6px;opacity:.9}
.off{display:none;align-items:center;gap:6px;font-size:12.5px;margin-top:8px;opacity:.9}
main{max-width:640px;margin:0 auto;padding:16px}
.tab{display:none}.tab.on{display:block}
h2{color:var(--dark);font-size:19px;margin:20px 2px 10px}
.box{background:var(--card);border-radius:18px;padding:14px;margin-bottom:12px;border:1px solid var(--line)}
.ih{display:flex;align-items:center;gap:8px;color:var(--dark);font-size:16px;margin-bottom:8px}
.sub{font-size:13.5px;color:var(--muted);margin:0 2px 12px;line-height:1.4}
.meal{background:var(--card);border-radius:18px;padding:14px;margin-bottom:12px;border:1px solid var(--line)}
.mh{display:flex;align-items:center;gap:12px}.mh .t{font-weight:800;color:var(--dark);font-size:17px;min-width:52px}
.mh .n{flex:1}.mh .n b{display:block;font-size:16px}.mh .n small{color:var(--muted);font-size:13px}
.st{font-size:12px;font-weight:700;border-radius:99px;padding:4px 9px;white-space:nowrap}
.st.ok{background:var(--leaf);color:#103b06}.st.troca{background:#DDEBFA;color:#1d4f86}.st.fora{background:#FBE7DA;color:var(--warn)}
.meal ul{list-style:none;margin:10px 0 8px}.meal li{padding:6px 0 6px 18px;position:relative;font-size:15px;border-bottom:1px dashed var(--line)}
.meal li:last-child{border:0}.meal li:before{content:"";position:absolute;left:2px;top:13px;width:7px;height:7px;border-radius:50%;background:var(--leaf)}
.swap{background:var(--soft);border-radius:12px;padding:9px 11px;font-size:13.5px;color:#23401c}.swap b{color:var(--dark)}
.acts{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:10px}
.acts button,.hun button{display:flex;align-items:center;justify-content:center;gap:4px;white-space:nowrap;letter-spacing:-.01em;border:1px solid var(--line);background:#fff;border-radius:12px;padding:9px 4px;font:inherit;font-size:13px;font-weight:600;color:var(--ink);cursor:pointer}
.acts button.on[data-v=ok]{background:var(--leaf);border-color:var(--leaf);color:#103b06}
.acts button.on[data-v=troca]{background:#DDEBFA;border-color:#9fc3ea;color:#1d4f86}
.acts button.on[data-v=fora]{background:#FBE7DA;border-color:#f0b894;color:var(--warn)}
.hun{margin-top:8px;font-size:12.5px;color:var(--muted)}.hun div{display:grid;grid-template-columns:repeat(3,1fr);gap:6px;margin-top:5px}
.hun button.on{background:var(--dark);color:#fff;border-color:var(--dark)}
.meal.done{border-color:#cfe3b7}
.cups{display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:10px}
.cup{aspect-ratio:3/4;border:2px solid #b9d7f0;border-radius:6px 6px 12px 12px;background:#fff;cursor:pointer}
.cup.ok{background:linear-gradient(to top,#6cb6ea 85%,#fff 85%)}
.goal{background:var(--dark);color:#fff;border-radius:18px;padding:14px;margin-bottom:14px}.goal h3{font-size:16px;display:flex;align-items:center;gap:8px;color:#fff;margin:0 0 2px}.goal .gs{font-size:12px;opacity:.85;margin-bottom:8px}.goal .gr{margin-top:9px}.goal .gl{display:flex;justify-content:space-between;font-size:13.5px}.goal .gl b{color:var(--leaf)}.goal .gb{height:8px;border-radius:99px;background:rgba(255,255,255,.18);margin-top:4px;overflow:hidden}.goal .gb i{display:block;height:100%;background:var(--leaf);border-radius:99px}.goal .gp{font-size:12px;opacity:.85;margin-top:10px;border-top:1px solid rgba(255,255,255,.18);padding-top:8px}
.toggle{display:flex;align-items:center;gap:12px;cursor:pointer}
.ck{width:30px;height:30px;border-radius:50%;border:2px solid var(--leaf);display:grid;place-items:center;flex:none;color:transparent}
.ck.ok{background:var(--leaf);color:#103b06}
.btn{display:inline-flex;align-items:center;gap:7px;background:var(--soft);color:var(--dark);border:0;border-radius:999px;padding:10px 14px;font:inherit;font-size:13.5px;font-weight:700;text-decoration:none;cursor:pointer;margin:8px 6px 0 0}
.wa{display:flex;align-items:center;justify-content:center;gap:8px;background:var(--dark);color:#fff;text-decoration:none;font-weight:700;border-radius:999px;padding:14px;margin:16px 0}
.appt{background:var(--card);border:2px solid var(--leaf);border-radius:18px;padding:14px;margin-bottom:12px}
.appt .top{display:flex;gap:12px;align-items:center}.appt .ic{display:grid;place-items:center;width:48px;height:48px;border-radius:50%;background:var(--soft);flex:none}
.appt .tx{flex:1}.appt .tx b{display:block;color:var(--dark);font-size:16px}.appt .tx small b{display:inline;font-size:13px}.appt small{color:var(--muted);font-size:13px}
.appt .cd{background:var(--dark);color:#fff;border-radius:12px;padding:8px 10px;text-align:center;font-weight:800;font-size:20px;line-height:1}.appt .cd span{display:block;font-size:10px;font-weight:600;margin-top:3px}
.pre{margin-top:12px;border-top:1px dashed var(--line);padding-top:10px}.pre p{font-size:13px;font-weight:700;color:var(--dark);margin-bottom:6px}
.li{display:flex;align-items:center;gap:10px;padding:8px 0;border-bottom:1px dashed var(--line);font-size:14.5px;cursor:pointer}.li:last-child{border:0}
.bx{width:22px;height:22px;border-radius:7px;border:2px solid var(--leaf);flex:none;display:grid;place-items:center;color:transparent}
.li.ok .bx{background:var(--leaf);color:#103b06}.li.ok .tx{text-decoration:line-through;color:var(--muted)}.li .tx{flex:1}.li .q{font-size:12.5px;color:var(--muted);text-align:right}
.grp h3{color:var(--dark);font-size:16px}.grp .por{font-size:12.5px;color:var(--muted);margin:2px 0 8px}
table{width:100%;border-collapse:collapse;font-size:14px}td{padding:7px 0;border-bottom:1px dashed var(--line);vertical-align:top}td.m{text-align:right;color:var(--dark);font-weight:600;padding-left:10px}tr:last-child td{border:0}
.med{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-bottom:1px dashed var(--line)}.med:last-child{border:0}
.med .ic,.rc .ic{width:40px;height:40px;border-radius:50%;background:var(--soft);display:grid;place-items:center;flex:none}
.med b{display:block;font-size:14.5px}.med span{font-size:13.5px;color:var(--muted);line-height:1.35}
details{background:var(--card);border:1px solid var(--line);border-radius:18px;margin-bottom:10px;overflow:hidden}
summary{list-style:none;display:flex;align-items:center;gap:12px;padding:12px 14px;cursor:pointer;font-weight:700;color:var(--ink)}summary::-webkit-details-marker{display:none}
details ol,details ul{margin:0 16px 14px 34px}details li{font-size:14.5px;margin:6px 0;line-height:1.4}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px}
.kpi{background:var(--dark);color:#fff;border-radius:14px;padding:10px 6px;text-align:center}.kpi b{display:block;font-size:20px;color:var(--leaf)}.kpi span{font-size:11.5px;opacity:.9}
.week{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;align-items:end;height:120px;margin-top:6px}
.week div{display:flex;flex-direction:column;align-items:center;gap:4px;height:100%;justify-content:flex-end}
.week i{display:block;width:100%;border-radius:6px 6px 3px 3px;background:var(--leaf);min-height:3px}.week i.today{background:var(--dark)}
.week span{font-size:11px;color:var(--muted)}.week em{font-style:normal;font-size:10px;color:#1d4f86}
.note{font-size:12.5px;color:var(--muted);line-height:1.4;margin-top:8px}
.form{display:grid;grid-template-columns:1fr 1fr;gap:8px}.form label{font-size:12.5px;color:var(--muted);display:flex;flex-direction:column;gap:4px}
.form input{font:inherit;font-size:16px;padding:10px;border:1px solid var(--line);border-radius:10px;background:#fff;width:100%}.form .full{grid-column:1/3}
.save{background:var(--dark);color:#fff;border:0;border-radius:999px;padding:12px;font:inherit;font-weight:700;width:100%;margin-top:10px;cursor:pointer}
.hist button{background:none;border:0;color:#b33;cursor:pointer}
.foot{font-size:12.5px;color:var(--muted);text-align:center;margin:18px 8px}
.hint{background:#fff7e6;border:1px solid #f1d39b;border-radius:14px;padding:10px 12px;font-size:13px;margin-bottom:12px;display:none}
nav{position:fixed;left:0;right:0;bottom:0;background:#fff;border-top:1px solid var(--line);display:grid;grid-template-columns:repeat(5,1fr);padding:6px 4px calc(6px + env(safe-area-inset-bottom))}
nav button{background:none;border:0;font:inherit;font-size:11.5px;color:var(--muted);display:flex;flex-direction:column;align-items:center;gap:3px;padding:6px 0;cursor:pointer}
nav button.on{color:var(--dark);font-weight:700}"""

nav = "".join(f'<button class="{"on" if i == 0 else ""}" data-t="{t}">{ico(ic, 22)}{lb}</button>' for i, (t, ic, lb) in enumerate(NAV))
HTML = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex,nofollow"><meta name="theme-color" content="{G}">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Meu plano">
<title>Meu plano · {P['nome']}</title>
<link rel="manifest" href="manifest.json"><link rel="apple-touch-icon" href="../../assets/icon-192.png"><link rel="icon" href="../../assets/icon-192.png">
<style>{CSS}</style></head>
<body>
<header><div class="row"><img src="../../assets/logo.png" alt="Logo Lucas Rodrigues"><span style="font-size:13px;opacity:.9" id="hoje"></span></div>
<h1>Olá, {P['nome']}</h1><p>Seu plano do dia, do jeito da sua rotina.</p>
<div class="prog"><i id="bar"></i></div><div class="progt" id="progt"></div>
<div class="off" id="off">{ico('wifi-off', 15, '#fff')} Sem internet: tudo continua funcionando.</div></header>
<main>
<div id="appt"></div>
<div class="hint" id="hint">Dica: toque em <b>Compartilhar → Adicionar à Tela de Início</b> (iPhone) ou <b>⋮ → Adicionar à tela inicial</b> (Android) para abrir como app.</div>

<section class="tab on" id="t-plano">
 <div class="goal" id="goal"></div>
 <h2>Refeições de hoje</h2>
 <p class="sub">Marque cada refeição: <b>Comi</b> (igual ao plano), <b>Troquei</b> (usei a lista de trocas) ou <b>Saí do plano</b>. Sem culpa: é para ajustarmos juntos.</p>
 <div id="meals"></div>
 <h2>Água</h2>
 <div class="box"><b>Meta: cerca de {str(P['agua_l']).replace('.', ',')} litros</b> · cada copo = 250 ml<div class="cups" id="cups"></div><p class="note">Toque em cada copo que beber. Tudo zera sozinho no dia seguinte.</p></div>
 {'<div class="box toggle" onclick="tgR()"><div class="ck" id="sodachk">' + ico('check', 18) + '</div><div><b>Hoje fiquei sem refrigerante</b><br><small style="color:var(--muted)">Marque no fim do dia. Vale para suco de caixinha também.</small></div></div>' if P['refri'] else ''}
 {('<div class="box toggle" onclick="tgT()"><div class="ck" id="treinochk">' + ico('check', 18) + '</div><div><b>Hoje treinei</b><br><small style="color:var(--muted)">' + P['metas']['treino'][0] + ' conta para a sua meta da semana.</small></div></div>') if P['metas']['treino'] else ''}
 <div class="box"><div class="ih">{ico('bell', 20, G)}<b>Lembretes das refeições</b></div><p class="note" style="margin-top:0">Coloca um alarme diário no horário de cada refeição, direto na agenda do seu celular.</p>
  <a class="btn" href="lembretes.ics">{ico('calendar-check', 16, G)} Ativar lembretes</a></div>
</section>

<section class="tab" id="t-trocas">
 <h2>Como é essa medida?</h2><div class="box" id="medidas"></div>
 <h2>Troque dentro do mesmo grupo</h2><p class="sub">Cada linha vale 1 porção. Troque um alimento por outro do mesmo grupo, na medida indicada.</p>
 <div id="groups"></div>
</section>

<section class="tab" id="t-compras">
 <h2>Preparo da semana</h2><p class="sub">Uma hora no domingo deixa a semana pronta. A lista zera toda semana.</p><div class="box" id="prep"></div>
 <h2>Lista de compras do mês</h2><p class="sub">Toque para marcar o que já comprou. {P['compras_obs']}</p><div class="box" id="buys"></div>
 <button class="btn" onclick="clearBuys()">Desmarcar tudo</button>
</section>

<section class="tab" id="t-evolucao">
 <h2>Minha semana</h2><div class="kpis" id="kpis"></div>
 <div class="box"><div class="ih">{ico('list-checks', 20, G)}<b>Refeições do plano nos últimos 7 dias</b></div><div class="week" id="week"></div><p class="note" id="hungerNote"></p></div>
 <h2>Meu peso</h2>
 <div class="box"><div class="ih">{ico('chart-line', 20, G)}<b>Evolução</b></div><div id="chart"></div><table class="hist" id="hist"></table></div>
 <div class="box"><div class="ih">{ico('scale', 20, G)}<b>Registrar</b></div>
  <div class="form"><label>Data<input type="date" id="fd"></label><label>Peso (kg)<input type="number" inputmode="decimal" step="0.1" min="30" max="300" id="fp" placeholder="ex.: 98,5"></label>
  <label class="full">Cintura (cm), opcional<input type="number" inputmode="decimal" step="0.5" min="40" max="200" id="fc" placeholder="fita na altura do umbigo"></label></div>
  <button class="save" onclick="addW()">Salvar registro</button>
  <p class="note">Pese <b>1 vez por semana</b>, no mesmo dia, de manhã, em jejum e depois de ir ao banheiro. O peso oscila de um dia para o outro: olhe a tendência. Os resultados variam de pessoa para pessoa.</p></div>
 <a class="wa" id="sendev" href="#">{ico('send', 20, '#fff')} Enviar minha semana para o Lucas</a>
 <p class="note" style="text-align:center">Seus registros ficam salvos só neste celular. Se trocar de aparelho ou limpar o navegador, eles somem.</p>
</section>

<section class="tab" id="t-dicas">
 <h2>Receitas rápidas</h2><div id="rec"></div>
 <h2>Comendo fora de casa</h2><div id="fora"></div>
 <h2>Para o seu dia a dia</h2><div id="tips"></div>
</section>

<a class="wa" href="https://wa.me/5561992308296?text=Oi%20Lucas%2C%20tenho%20uma%20d%C3%BAvida%20sobre%20meu%20plano">{ico('message-circle', 20, '#fff')} Falar com o Lucas no WhatsApp</a>
<p class="foot">Nutricionista Lucas Rodrigues · CRN-1 15.957<br>Plano individual: não use para outras pessoas. Os resultados variam de pessoa para pessoa.<br>Atualizado em {P['atualizado']}</p>
</main>
<nav>{nav}</nav>
<script>
const P={json.dumps(DATA, ensure_ascii=False)};
const IC={json.dumps(IC, ensure_ascii=False)};
const ymd=d=>d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");
const today=ymd(new Date());
function load(k,d){{try{{const v=localStorage.getItem(P.key+k);return v?JSON.parse(v):d}}catch(e){{return d}}}}
function save(k,v){{try{{localStorage.setItem(P.key+k,JSON.stringify(v))}}catch(e){{}}}}
const esc=s=>String(s).replace(/[&<>"]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));
const br=(n,d=1)=>n.toFixed(d).replace(".",",");
const fmtD=k=>{{const p=k.split("-");return p[2]+"/"+p[1]}};
const ic=(n,s)=>(IC[n]||"").replace(/width="20"/,'width="'+(s||20)+'"').replace(/height="20"/,'height="'+(s||20)+'"');
const MAIN=P.meals.map((m,i)=>m.opc?null:i).filter(i=>i!==null);
let hist=load("historico",{{}});
const old=load("dia",null); if(old&&old.d&&!hist[old.d]) hist[old.d]={{m:old.m||[],w:old.w||0}};
for(const k in hist){{const h=hist[k]; if(Array.isArray(h.m)){{const o={{}};h.m.forEach(i=>o[i]="ok");h.m=o}} h.f=h.f||{{}}; h.w=h.w||0}}
Object.keys(hist).sort().slice(0,-120).forEach(k=>delete hist[k]);
if(!hist[today]) hist[today]={{m:{{}},f:{{}},w:0,r:false}};
let day=hist[today];
function saveDay(){{hist[today]=day;save("historico",hist)}}
let pesos=load("pesos",[]), buys=load("compras",[]);
const wk=(()=>{{const d=new Date();d.setDate(d.getDate()-d.getDay());return ymd(d)}})();
let prep=load("preparo",{{w:wk,i:[]}}); if(prep.w!==wk) prep={{w:wk,i:[]}};
const ST={{ok:"Comi",troca:"Troquei",fora:"Saí do plano"}};
const HU=[["ok","smile","Satisfeito"],["fome","frown","Com fome"],["cheio","meh","Exagerei"]];
function renderMeals(){{
 document.getElementById("meals").innerHTML=P.meals.map((m,i)=>{{const s=day.m[i], f=day.f[i];
  return `<div class="meal ${{s?"done":""}}"><div class="mh"><div class="t">${{m.h}}</div><div class="n"><b>${{esc(m.n)}}</b><small>${{esc(m.s)}}</small></div>${{s?`<span class="st ${{s}}">${{ST[s]}}</span>`:""}}</div>
  <ul>${{m.i.map(x=>`<li>${{esc(x)}}</li>`).join("")}}</ul><div class="swap"><b>Pode trocar:</b> ${{esc(m.t)}}</div>
  <div class="acts">${{[["ok","check"],["troca","repeat-2"],["fora","x"]].map(([v,n])=>`<button data-v="${{v}}" class="${{s===v?"on":""}}" onclick="setM(${{i}},'${{v}}')">${{ic(n,16)}}${{ST[v]}}</button>`).join("")}}</div>
  ${{s?`<div class="hun">Como ficou a fome depois?<div>${{HU.map(([v,n,l])=>`<button class="${{f===v?"on":""}}" onclick="setF(${{i}},'${{v}}')">${{ic(n,16)}}${{l}}</button>`).join("")}}</div></div>`:""}}</div>`}}).join("");
}}
function render(){{
 renderMeals();
 const cups=Math.round(P.agua_l*4);
 document.getElementById("cups").innerHTML=Array.from({{length:cups}},(_,i)=>`<div class="cup ${{i<day.w?"ok":""}}" onclick="tgW(${{i}})" aria-label="Copo ${{i+1}}"></div>`).join("");
 const sc=document.getElementById("sodachk"); if(sc) sc.classList.toggle("ok",!!day.r);
 const done=MAIN.filter(i=>day.m[i]==="ok"||day.m[i]==="troca").length;
 document.getElementById("bar").style.width=Math.round(((done/MAIN.length)*0.7+(Math.min(day.w,cups)/cups)*0.3)*100)+"%";
 document.getElementById("progt").textContent=`${{done}} de ${{MAIN.length}} refeições · ${{br(day.w*0.25,day.w%4?2:0)}} L de água`;
 document.getElementById("buys").innerHTML=P.buys.map((b,i)=>`<div class="li ${{buys.includes(i)?"ok":""}}" onclick="tgB(${{i}})"><div class="bx">${{ic("check",14)}}</div><div class="tx">${{esc(b[0])}}</div><div class="q">${{esc(b[1])}}</div></div>`).join("");
 document.getElementById("prep").innerHTML=P.preparo.map((t,i)=>`<div class="li ${{prep.i.includes(i)?"ok":""}}" onclick="tgP(${{i}})"><div class="bx">${{ic("check",14)}}</div><div class="tx">${{esc(t)}}</div></div>`).join("");
 renderEv(); renderAppt(); renderGoal();
}}
function setM(i,v){{if(day.m[i]===v){{delete day.m[i];delete day.f[i]}}else day.m[i]=v;saveDay();render()}}
function setF(i,v){{day.f[i]=day.f[i]===v?undefined:v;saveDay();renderMeals()}}
function tgW(i){{day.w=(i+1===day.w)?i:i+1;saveDay();render()}}
function tgR(){{day.r=!day.r;saveDay();render()}}
function tgT(){{day.t=!day.t;saveDay();render()}}
function weekDays(){{const d=new Date();const off=(d.getDay()+6)%7;const out=[];for(let k=0;k<=off;k++){{const x=new Date(d);x.setDate(d.getDate()-off+k);out.push(hist[ymd(x)])}}return out}}
function metas(){{const W=weekDays();const need=Math.max(1,MAIN.length-1);
 return {{plano:W.filter(h=>h&&MAIN.filter(i=>h.m[i]==="ok"||h.m[i]==="troca").length>=need).length,agua:W.filter(h=>h&&h.w*0.25>=P.agua_l).length,treino:W.filter(h=>h&&h.t).length}}}}
function renderGoal(){{const M=P.metas,g=metas();
 const row=(l,v,n)=>`<div class="gr"><div class="gl"><span>${{l}}</span><b>${{Math.min(v,n)}} de ${{n}}${{v>=n?" ✓":""}}</b></div><div class="gb"><i style="width:${{Math.min(100,v/n*100)}}%"></i></div></div>`;
 document.getElementById("goal").innerHTML=`<h3>${{ic("target",20)}} Minha meta até o retorno</h3><div class="gs">Progresso desta semana (zera toda segunda)</div>`+
  row("Dias seguindo o plano",g.plano,M.plano)+row("Dias com a água completa",g.agua,M.agua)+(M.treino?row(M.treino[0]+" na semana",g.treino,M.treino[1]):"")+
  `<div class="gp">${{M.peso_txt?esc(M.peso_txt):"A meta de peso combinada na consulta está no seu plano em PDF."}} Registre o peso 1 vez por semana na aba Evolução. Os resultados variam de pessoa para pessoa.</div>`;
 const tc=document.getElementById("treinochk"); if(tc) tc.classList.toggle("ok",!!day.t);}}
function tgB(i){{buys=buys.includes(i)?buys.filter(x=>x!==i):[...buys,i];save("compras",buys);render()}}
function tgP(i){{prep.i=prep.i.includes(i)?prep.i.filter(x=>x!==i):[...prep.i,i];save("preparo",prep);render()}}
function clearBuys(){{buys=[];save("compras",buys);render()}}
function last7(){{const out=[];const d=new Date();for(let k=6;k>=0;k--){{const x=new Date(d);x.setDate(d.getDate()-k);const key=ymd(x);out.push([key,x,hist[key]])}}return out}}
function stats(){{
 let streak=0;const d=new Date(); if(!(hist[ymd(d)]&&hist[ymd(d)].r)) d.setDate(d.getDate()-1);
 while(hist[ymd(d)]&&hist[ymd(d)].r){{streak++;d.setDate(d.getDate()-1)}}
 const L=last7(); const used=L.filter(([k,x,h])=>h&&(Object.keys(h.m).length||h.w));
 let ok=0,troca=0,fora=0,water=0; const fome={{}};
 L.forEach(([k,x,h])=>{{if(!h)return; water+=h.w; MAIN.forEach(i=>{{const s=h.m[i]; if(s==="ok")ok++; else if(s==="troca")troca++; else if(s==="fora")fora++}});
   for(const i in h.f) if(h.f[i]==="fome") fome[i]=(fome[i]||0)+1}});
 const base=Math.max(1,used.length)*MAIN.length;
 return {{streak,ok,troca,fora,ade:Math.round((ok+troca)/base*100),agua:water*0.25/Math.max(1,used.length),dias:used.length,fome}};
}}
function renderEv(){{
 const st=stats(); const ps=[...pesos].sort((a,b)=>a.d.localeCompare(b.d));
 document.getElementById("kpis").innerHTML=`<div class="kpi"><b>${{st.dias?st.ade+"%":"—"}}</b><span>seguindo o plano (7 dias)</span></div>`+
  (P.refri?`<div class="kpi"><b>${{st.streak}}</b><span>dia(s) seguidos sem refri</span></div>`:`<div class="kpi"><b>${{st.troca}}</b><span>trocas na semana</span></div>`)+
  `<div class="kpi"><b>${{br(st.agua)}} L</b><span>média de água por dia</span></div>`;
 const W=["D","S","T","Q","Q","S","S"];
 document.getElementById("week").innerHTML=last7().map(([k,x,h],j)=>{{const n=h?MAIN.filter(i=>h.m[i]==="ok"||h.m[i]==="troca").length:0;
   return `<div><em>${{n||""}}</em><i class="${{j===6?"today":""}}" style="height:${{Math.max(3,n/MAIN.length*90)}}px"></i><span>${{W[x.getDay()]}}</span></div>`}}).join("");
 const fm=Object.entries(st.fome).sort((a,b)=>b[1]-a[1])[0];
 document.getElementById("hungerNote").innerHTML=(st.troca||st.fora?`Na semana: ${{st.ok}} refeições iguais ao plano, ${{st.troca}} com troca e ${{st.fora}} fora do plano. `:"")+(fm?`Mais fome depois de: <b>${{esc(P.meals[fm[0]].n)}}</b> (${{fm[1]}}x). Conte isso no retorno.`:"");
 const ch=document.getElementById("chart");
 if(ps.length<2) ch.innerHTML=`<p class="note">${{ps.length?"Registre de novo na próxima semana para ver o gráfico.":"Faça seu primeiro registro abaixo."}}</p>`;
 else{{const Wd=320,H=150,Pd=28,vs=ps.map(x=>x.p),lo=Math.min(...vs)-1,hi=Math.max(...vs)+1;
  const X=i=>Pd+(Wd-Pd-10)*i/(ps.length-1),Y=v=>10+(H-30)*(1-(v-lo)/(hi-lo));
  ch.innerHTML=`<svg viewBox="0 0 ${{Wd}} ${{H}}" width="100%" role="img" aria-label="Gráfico do peso"><line x1="${{Pd}}" y1="${{H-20}}" x2="${{Wd-10}}" y2="${{H-20}}" stroke="#DCE6D2"/>
   <text x="2" y="${{Y(hi-1)+4}}" font-size="10" fill="#5B6B5F">${{br(hi-1)}}</text><text x="2" y="${{Y(lo+1)+4}}" font-size="10" fill="#5B6B5F">${{br(lo+1)}}</text>
   <polyline points="${{ps.map((x,i)=>X(i)+","+Y(x.p)).join(" ")}}" fill="none" stroke="#005102" stroke-width="2.5" stroke-linejoin="round"/>
   ${{ps.map((x,i)=>`<circle cx="${{X(i)}}" cy="${{Y(x.p)}}" r="4" fill="#8AC243" stroke="#005102" stroke-width="1.5"/>`).join("")}}
   <text x="${{X(0)}}" y="${{H-5}}" font-size="10" fill="#5B6B5F">${{fmtD(ps[0].d)}}</text><text x="${{X(ps.length-1)}}" y="${{H-5}}" font-size="10" fill="#5B6B5F" text-anchor="end">${{fmtD(ps[ps.length-1].d)}}</text></svg>`;}}
 document.getElementById("hist").innerHTML=[...ps].reverse().map(x=>`<tr><td>${{fmtD(x.d)}}</td><td>${{br(x.p)}} kg</td><td>${{x.c?br(x.c)+" cm":""}}</td><td class="m"><button onclick="delW('${{x.d}}')" aria-label="Apagar">${{ic("x",16)}}</button></td></tr>`).join("");
 let t=`Oi Lucas! Minha semana (${{P.nome}}):\\n• Seguindo o plano: ${{st.dias?st.ade+"%":"sem registros"}} (${{st.ok}} iguais, ${{st.troca}} com troca, ${{st.fora}} fora)\\n• Água: ${{br(st.agua)}} L por dia\\n`;
 if(P.refri) t+=`• Dias seguidos sem refri: ${{st.streak}}\\n`;
 {{const g=metas(),M=P.metas; t+=`• Metas desta semana: plano ${{g.plano}}/${{M.plano}} dias · água ${{g.agua}}/${{M.agua}} dias`+(M.treino?` · ${{M.treino[0].toLowerCase()}} ${{g.treino}}/${{M.treino[1]}}`:"")+`\\n`}}
 if(fm) t+=`• Mais fome depois de: ${{P.meals[fm[0]].n}} (${{fm[1]}}x)\\n`;
 if(ps.length){{t+="Peso:\\n";ps.slice(-6).forEach(x=>t+=`• ${{fmtD(x.d)}}: ${{br(x.p)}} kg${{x.c?" · cintura "+br(x.c)+" cm":""}}\\n`)}}
 document.getElementById("sendev").href="https://wa.me/5561992308296?text="+encodeURIComponent(t);
}}
function addW(){{const d=document.getElementById("fd").value||today,p=parseFloat(String(document.getElementById("fp").value).replace(",",".")),c=parseFloat(String(document.getElementById("fc").value).replace(",","."));
 const e=document.getElementById("fp"); if(!(p>=30&&p<=300)){{e.style.borderColor="#b33";setTimeout(()=>e.style.borderColor="",2500);return}}
 pesos=pesos.filter(x=>x.d!==d);pesos.push({{d,p,c:(c>=40&&c<=200)?c:null}});save("pesos",pesos);e.value="";document.getElementById("fc").value="";render()}}
function delW(d){{pesos=pesos.filter(x=>x.d!==d);save("pesos",pesos);render()}}
const PRE=["Combinar o dia e o horário com o Lucas","Pesar em jejum, no dia do retorno ou na véspera","Separar exames novos (se tiver)","Anotar dúvidas e o que foi difícil","Enviar sua semana pelo botão da aba Evolução"];
function renderAppt(){{const R=P.retorno; const el=document.getElementById("appt"); if(!R||!R.data){{el.innerHTML="";return}}
 const [y,m,d]=R.data.split("-").map(Number),dt=new Date(y,m-1,d),t0=new Date();t0.setHours(0,0,0,0);const dias=Math.round((dt-t0)/864e5);
 const wa="https://wa.me/5561992308296?text="+encodeURIComponent("Oi Lucas! Quero agendar meu retorno ("+P.nome+").");
 const txt=dias>0?`Faltam <b>${{dias}} ${{dias===1?"dia":"dias"}}</b> para o seu retorno.`:`Chegou a hora do seu retorno.`;
 let pre=""; if(dias<=7){{const k="pre-"+R.data; const done=load(k,[]);
  pre=`<div class="pre"><p>Checklist para o retorno</p>${{PRE.map((t,i)=>`<div class="li ${{done.includes(i)?"ok":""}}" onclick="tgPre('${{k}}',${{i}})"><div class="bx">${{ic("check",14)}}</div><div class="tx">${{t}}</div></div>`).join("")}}</div>`}}
 el.innerHTML=`<div class="appt"><div class="top"><div class="ic">${{ic("calendar",26)}}</div><div class="tx"><b>Seu retorno</b><small>${{txt}}<br>Fale com o Lucas para combinar o dia e o horário.</small></div>${{dias>0?`<div class="cd">${{dias}}<span>${{dias===1?"dia":"dias"}}</span></div>`:""}}</div>
  <a class="btn" href="${{wa}}">${{ic("message-circle",16)}} Agendar meu retorno</a>${{pre}}</div>`;
}}
function tgPre(k,i){{let d=load(k,[]);d=d.includes(i)?d.filter(x=>x!==i):[...d,i];save(k,d);renderAppt()}}
document.getElementById("medidas").innerHTML=P.medidas.map(m=>`<div class="med"><div class="ic">${{ic(m[0],20)}}</div><div><b>${{esc(m[1])}}</b><span>${{esc(m[2])}}</span></div></div>`).join("");
document.getElementById("groups").innerHTML=P.groups.map(g=>`<div class="box grp"><h3>${{esc(g[0])}}</h3><div class="por">${{esc(g[1])}}</div><table>${{g[2].map(r=>`<tr><td>${{esc(r[0])}}</td><td class="m">${{esc(r[1])}}</td></tr>`).join("")}}</table></div>`).join("");
document.getElementById("rec").innerHTML=P.receitas.map(r=>`<details><summary><span class="ic" style="width:36px;height:36px;border-radius:50%;background:var(--soft);display:grid;place-items:center">${{ic(r[1],18)}}</span>${{esc(r[0])}}</summary><ol>${{r[2].map(x=>`<li>${{esc(x)}}</li>`).join("")}}</ol></details>`).join("");
document.getElementById("fora").innerHTML=P.fora.map(r=>`<details><summary><span style="width:36px;height:36px;border-radius:50%;background:var(--soft);display:grid;place-items:center">${{ic(r[0],18)}}</span>${{esc(r[1])}}</summary><ul>${{r[2].map(x=>`<li>${{esc(x)}}</li>`).join("")}}</ul></details>`).join("");
document.getElementById("tips").innerHTML=P.tips.map(t=>`<div class="box"><div class="ih">${{ic(t[0],20)}}<b>${{esc(t[1])}}</b></div><ul style="margin-left:18px">${{t[2].map(x=>`<li style="font-size:14.5px;margin:6px 0;line-height:1.4">${{esc(x)}}</li>`).join("")}}</ul></div>`).join("");
document.querySelectorAll("nav button").forEach(b=>b.onclick=()=>{{document.querySelectorAll("nav button").forEach(x=>x.classList.toggle("on",x===b));document.querySelectorAll(".tab").forEach(t=>t.classList.toggle("on",t.id==="t-"+b.dataset.t));window.scrollTo(0,0)}});
document.getElementById("hoje").textContent=new Date().toLocaleDateString("pt-BR",{{weekday:"long",day:"numeric",month:"short"}});
document.getElementById("fd").value=today;
if(!(window.matchMedia&&matchMedia("(display-mode: standalone)").matches)&&!navigator.standalone) document.getElementById("hint").style.display="block";
const offEl=document.getElementById("off"); const net=()=>offEl.style.display=navigator.onLine?"none":"flex"; addEventListener("online",net); addEventListener("offline",net); net();
if("serviceWorker" in navigator && location.protocol==="https:") navigator.serviceWorker.register("sw.js").catch(()=>{{}});
render();
</script>
</body></html>"""
(OUT / 'index.html').write_text(HTML, encoding='utf-8')
print('ok', OUT)
