"""Calculadora de trocas do app: tabela de alimentos (TACO/rótulos), leitura dos itens do plano e o JS/CSS da calculadora.
Cada grupo troca pelo nutriente principal: carnes, leite e leguminosas pela proteína; carboidratos e frutas pelo carboidrato; gorduras pela gordura."""
import re

# key: (nome, grupo, kcal, ptn, cho, lip por 100 g/ml, [(medida singular, plural, gramas)], palavras-chave)
FOODS = {
 'frango':    ("Frango (peito) grelhado", 'prot', 159, 32.0, 0, 2.5, [("filé médio", "filés médios", 120), ("colher de sopa cheia (desfiado)", "colheres de sopa cheias (desfiado)", 25)], r'frango(?! desfiado)|peito de frango|filé de frango'),
 'frango_desf': ("Frango desfiado", 'prot', 163, 31.5, 0, 3.2, [("colher de sopa cheia", "colheres de sopa cheias", 25)], r'frango desfiado'),
 'sobrecoxa': ("Sobrecoxa sem pele assada", 'prot', 233, 29.2, 0, 12.0, [("unidade", "unidades", 100)], r'sobrecoxa|coxa'),
 'patinho':   ("Carne magra (patinho) grelhada", 'prot', 219, 35.9, 0, 7.3, [("bife médio", "bifes médios", 100)], r'(?<!moída de )patinho|bife|carne magra|carne grelhada|espetinho de carne|alcatra|acém|carne(?! moída)'),
 'moida':     ("Carne moída refogada", 'prot', 212, 26.7, 0, 10.9, [("colher de sopa cheia", "colheres de sopa cheias", 25)], r'carne moída|moída'),
 'figado':    ("Fígado bovino grelhado", 'prot', 225, 29.9, 4.2, 9.0, [("bife médio", "bifes médios", 100)], r'fígado'),
 'sardinha':  ("Sardinha em lata (escorrida)", 'prot', 208, 24.0, 0, 12.0, [("lata (escorrida)", "latas (escorridas)", 84)], r'sardinha'),
 'peixe':     ("Peixe (tilápia, merluza) assado", 'prot', 122, 26.6, 0, 0.9, [("filé médio", "filés médios", 130)], r'peixe|tilápia|merluza'),
 'atum':      ("Atum em lata (em água, escorrido)", 'prot', 116, 26.0, 0, 1.0, [("lata (escorrida)", "latas (escorridas)", 120)], r'atum'),
 'ovo':       ("Ovo (cozido ou mexido)", 'prot', 146, 13.3, 0.6, 9.5, [("ovo", "ovos", 50)], r'\bovos?\b|omelete'),
 'whey':      ("Whey protein (dose de 30 g)", 'prot', 400, 80.0, 7.0, 6.0, [("dose (scoop)", "doses (scoops)", 30)], r'whey'),
 'arroz':     ("Arroz branco cozido", 'carb', 128, 2.5, 28.1, 0.2, [("colher de sopa cheia", "colheres de sopa cheias", 25)], r'arroz(?! integral)'),
 'arroz_int': ("Arroz integral cozido", 'carb', 124, 2.6, 25.8, 1.0, [("colher de sopa cheia", "colheres de sopa cheias", 25)], r'arroz integral'),
 'mandioca':  ("Mandioca cozida", 'carb', 125, 0.6, 30.1, 0.3, [("pedaço médio", "pedaços médios", 50)], r'mandioca|aipim'),
 'bdoce':     ("Batata-doce cozida", 'carb', 77, 0.6, 18.4, 0.1, [("unidade média", "unidades médias", 150)], r'batata-doce|batata doce'),
 'batata':    ("Batata inglesa cozida", 'carb', 52, 1.2, 11.9, 0.0, [("unidade média", "unidades médias", 90)], r'batata(?!-doce| doce)'),
 'macarrao':  ("Macarrão cozido", 'carb', 157, 5.8, 30.7, 0.9, [("escumadeira cheia", "escumadeiras cheias", 100)], r'macarrão'),
 'cuscuz':    ("Cuscuz de milho", 'carb', 113, 2.2, 25.3, 0.7, [("colher de sopa cheia", "colheres de sopa cheias", 25)], r'cuscuz'),
 'pao':       ("Pão francês", 'carb', 300, 8.0, 58.6, 3.1, [("unidade", "unidades", 50)], r'pão francês|\bpães?\b(?! de forma)'),
 'pao_forma': ("Pão de forma integral", 'carb', 253, 9.4, 49.9, 3.7, [("fatia", "fatias", 25)], r'pão de forma|pão integral|pães integrais'),
 'pao_queijo': ("Pão de queijo", 'carb', 363, 5.1, 34.2, 24.6, [("unidade pequena", "unidades pequenas", 20)], r'pão de queijo|pães de queijo'),
 'tapioca':   ("Tapioca (goma pronta)", 'carb', 240, 0.0, 59.0, 0.0, [("colher de sopa", "colheres de sopa", 15)], r'tapioca'),
 'aveia':     ("Aveia em flocos", 'carb', 394, 13.9, 66.6, 8.5, [("colher de sopa", "colheres de sopa", 10)], r'aveia'),
 'banana':    ("Banana prata", 'fruta', 98, 1.3, 26.0, 0.1, [("unidade média", "unidades médias", 80)], r'banana'),
 'maca':      ("Maçã", 'fruta', 56, 0.3, 15.2, 0.0, [("unidade média", "unidades médias", 130)], r'maçã'),
 'mamao':     ("Mamão (papaia ou formosa)", 'fruta', 42, 0.6, 11.0, 0.1, [("fatia média", "fatias médias", 150)], r'mamão'),
 'laranja':   ("Laranja", 'fruta', 37, 1.0, 8.9, 0.1, [("unidade média", "unidades médias", 180)], r'laranja'),
 'tangerina': ("Tangerina (mexerica)", 'fruta', 38, 0.8, 9.6, 0.1, [("unidade média", "unidades médias", 130)], r'tangerina|mexerica'),
 'melancia':  ("Melancia", 'fruta', 33, 0.9, 8.1, 0.0, [("fatia média", "fatias médias", 200)], r'melancia'),
 'melao':     ("Melão", 'fruta', 29, 0.7, 7.5, 0.0, [("fatia média", "fatias médias", 100)], r'melão'),
 'abacaxi':   ("Abacaxi", 'fruta', 48, 0.9, 12.3, 0.1, [("fatia média", "fatias médias", 75)], r'abacaxi'),
 'manga':     ("Manga", 'fruta', 64, 0.4, 16.7, 0.3, [("unidade pequena", "unidades pequenas", 120)], r'manga'),
 'goiaba':    ("Goiaba", 'fruta', 54, 1.1, 13.0, 0.4, [("unidade média", "unidades médias", 120)], r'goiaba(?!da)'),
 'pera':      ("Pera", 'fruta', 53, 0.6, 14.0, 0.1, [("unidade média", "unidades médias", 130)], r'\bpera\b'),
 'uva':       ("Uva", 'fruta', 53, 0.7, 13.6, 0.2, [("cacho pequeno", "cachos pequenos", 100)], r'\buvas?\b'),
 'leite_int': ("Leite integral", 'leite', 61, 2.9, 4.3, 3.2, [("copo (200 ml)", "copos (200 ml)", 200)], r'leite integral|café com leite|\bleite\b(?! semi| desn| em pó)'),
 'leite_semi': ("Leite semidesnatado", 'leite', 46, 3.0, 4.6, 1.5, [("copo (200 ml)", "copos (200 ml)", 200)], r'semidesnatado'),
 'leite_desn': ("Leite desnatado", 'leite', 35, 3.4, 4.9, 0.2, [("copo (200 ml)", "copos (200 ml)", 200)], r'desnatado'),
 'leite_po':  ("Leite em pó", 'leite', 497, 25.4, 39.2, 26.9, [("colher de sopa", "colheres de sopa", 10)], r'leite em pó'),
 'iogurte':   ("Iogurte natural", 'leite', 51, 4.1, 1.9, 3.0, [("pote (170 g)", "potes (170 g)", 170)], r'iogurte'),
 'queijo':    ("Queijo minas frescal", 'leite', 264, 17.4, 3.2, 20.2, [("fatia média (30 g)", "fatias médias (30 g)", 30)], r'queijo'),
 'feijao':    ("Feijão (carioca ou preto)", 'leg', 76, 4.8, 13.6, 0.5, [("concha média", "conchas médias", 100)], r'feijão'),
 'lentilha':  ("Lentilha cozida", 'leg', 93, 6.3, 16.3, 0.5, [("colher de sopa", "colheres de sopa", 25)], r'lentilha'),
 'grao':      ("Grão-de-bico cozido", 'leg', 164, 8.9, 27.4, 2.6, [("colher de sopa", "colheres de sopa", 25)], r'grão-de-bico|grão de bico'),
 'azeite':    ("Azeite ou óleo", 'gord', 884, 0, 0, 100, [("colher de chá (3 ml)", "colheres de chá (3 ml)", 3), ("colher de sobremesa (5 ml)", "colheres de sobremesa (5 ml)", 5), ("colher de sopa (8 ml)", "colheres de sopa (8 ml)", 8)], r'azeite|óleo'),
 'pasta_amend': ("Pasta de amendoim", 'gord', 588, 25.0, 20.0, 50.0, [("colher de sopa rasa", "colheres de sopa rasas", 10)], r'pasta de amendoim'),
 'abacate':   ("Abacate", 'gord', 96, 1.2, 6.0, 8.4, [("colher de sopa", "colheres de sopa", 30)], r'abacate'),
}
GROUPS = {'prot': ("Carnes, ovos e proteína", 3), 'carb': ("Arroz, raízes e pães", 4), 'fruta': ("Frutas", 4),
          'leite': ("Leite e derivados", 3), 'leg': ("Feijão e leguminosas", 3), 'gord': ("Gorduras", 5)}
# índice do nutriente usado para igualar (3=ptn, 4=cho, 5=lip na tupla)
_KW = [(k, re.compile(v[7], re.I)) for k, v in FOODS.items()]
_Q = re.compile(r'(\d+(?:[.,]\d+)?)\s*(g|ml)\b', re.I)
_N = {'meio': .5, 'meia': .5, 'um': 1, 'uma': 1, 'dois': 2, 'duas': 2, 'três': 3, 'tres': 3, 'quatro': 4, 'cinco': 5}


def components(text, excl=()):
    """Acha os alimentos trocáveis num item do plano e a quantidade em gramas de cada um. Retorna [[chave, gramas], ...]."""
    if re.search(r'creatina|polivitam|suplemento', text, re.I): return []
    text = re.sub(r'(\d)½', r'\1.5', text).replace('½', '0.5')
    hits = []
    for k, rx in _KW:
        for m in rx.finditer(text):
            if k in excl or re.search(r'\b(sem|pouco)\s+$', text[max(0, m.start() - 6):m.start()], re.I): continue
            hits.append((m.start(), m.end(), k))
    if re.search(r'leite em pó', text, re.I): hits = [h for h in hits if h[2] not in ('leite_int', 'leite_desn', 'leite_semi')]
    hits.sort()
    sel = []
    for h in hits:  # sobreposição: fica o trecho mais longo
        if sel and h[0] < sel[-1][1]:
            if h[1] - h[0] > sel[-1][1] - sel[-1][0]: sel[-1] = h
            continue
        sel.append(h)
    grp = []  # junta citações seguidas do mesmo alimento (ex.: "omelete de 3 ovos")
    for s, e, k in sel:
        if grp and grp[-1][2] == k: grp[-1][1] = e
        elif grp and FOODS[grp[-1][2]][1] == 'prot' and FOODS[k][1] == 'prot' and not _Q.search(text[grp[-1][1]:s]) and k != 'ovo' and grp[-1][2] != 'ovo':
            grp[-1][1] = e  # "carne moída de patinho", "bife de carne magra (patinho)": é um alimento só
        else: grp.append([s, e, k])
    if not grp: return []
    qs = [(m.start(), float(m.group(1).replace(',', '.'))) for m in _Q.finditer(text)]
    out, used = [], set()
    for i, (s, e, k) in enumerate(grp):
        nxt = grp[i + 1][0] if i + 1 < len(grp) else 10 ** 6
        prev_e = grp[i - 1][1] if i else 0
        g = None
        for j, (pos, val) in enumerate(qs):  # gramas dentro ou depois do alimento (até o próximo)
            if j not in used and s <= pos < nxt: g = val; used.add(j); break
        if g is None:
            for j, (pos, val) in enumerate(qs):  # "150 ml de leite"
                if j not in used and prev_e <= pos < s and re.search(r'(g|ml)\s+de\s+', text[pos:s], re.I): g = val; used.add(j); break
        if g is None:
            win = text[prev_e:e].lower(); wide = text[prev_e:min(nxt, len(text))].lower()
            units = FOODS[k][6]; u = units[0][2]
            for lab, _, gg in units:
                core = lab.split(' (')[0]
                if core.split()[0] in ('colher', 'fatia') and core in wide: u = gg; break
            NUM = r'(\d+(?:\.\d+)?)(?![\d.]*\s*(?:g|ml)\b)|\b(meio|meia|um|uma|dois|duas|três|tres|quatro|cinco)\b'
            n = re.findall(NUM, win) or re.findall(NUM, text[e:min(nxt, len(text))].lower())[:1]
            cnt = 1.0
            if n:
                a, b = n[-1]; cnt = float(a) if a else _N[b]
            if u >= 60 and re.search(r'grande', win): cnt *= 1.3
            elif u >= 60 and re.search(r'pequen', win): cnt *= 0.7
            g = u * cnt
        if k in [o[0] for o in out]: continue
        out.append([k, round(g)])
    return out


def data(excl=(), whey=False):
    foods = {k: [v[0], v[1], v[2], v[3], v[4], v[5], [list(u) for u in v[6]]] for k, v in FOODS.items()
             if k not in excl and (whey or k != 'whey')}
    return {'foods': foods, 'groups': {k: list(v) for k, v in GROUPS.items()}}


CSS = """
.li-sw{display:flex;align-items:flex-start;gap:8px}.li-sw span{flex:1}
.swb{flex:none;background:var(--soft,#E8F1DF);color:var(--dark,#005102);border:0;border-radius:999px;font:inherit;font-size:12px;font-weight:700;padding:4px 10px;cursor:pointer;display:inline-flex;align-items:center;gap:4px;margin-top:1px}
.sheet-bg{position:fixed;inset:0;background:rgba(15,20,25,.45);z-index:50;display:none}
.sheet{position:fixed;left:0;right:0;bottom:0;max-height:86vh;overflow:auto;background:#fff;border-radius:22px 22px 0 0;z-index:51;padding:16px 16px calc(18px + env(safe-area-inset-bottom));display:none;box-shadow:0 -10px 30px rgba(0,0,0,.15)}
.sheet.on,.sheet-bg.on{display:block}
.sheet .hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px}.sheet .hd b{font-size:17px}
.sheet .x{background:none;border:0;font-size:26px;line-height:1;cursor:pointer;color:var(--muted)}
.sheet .orig{background:var(--soft,#E8F1DF);border-radius:12px;padding:10px 12px;font-size:14px;margin:8px 0 10px}
.opt{display:flex;gap:10px;align-items:center;border:1px solid var(--line);border-radius:14px;padding:10px 12px;margin:7px 0;cursor:pointer}
.opt.sel{border-color:var(--dark,#005102);background:#F4F8EF}
.opt .ck2{width:22px;height:22px;border-radius:7px;border:2px solid var(--line);flex:none;display:grid;place-items:center;color:#fff}
.opt.sel .ck2{background:var(--dark,#005102);border-color:var(--dark,#005102)}
.opt .nm{font-weight:700;font-size:14.5px}.opt .qt{font-size:13.5px;color:var(--ink)}.opt .kc{font-size:11.5px;color:#9a5b00}
.mix{background:var(--dark,#005102);color:#fff;border-radius:14px;padding:12px;margin-top:10px;font-size:14px;display:none}.mix.on{display:block}
.calc{display:grid;grid-template-columns:1fr 1fr;gap:8px}.calc label{font-size:12.5px;color:var(--muted);display:flex;flex-direction:column;gap:4px}
.calc select,.calc input{font:inherit;font-size:16px;padding:10px;border:1px solid var(--line);border-radius:10px;background:#fff;width:100%}.calc .full{grid-column:1/3}
"""

JS = r"""
const TQ=P.trocas;let SW=null,SEL=[];
const ROUND=(x,u)=>{if(u>=60) return Math.max(.5,Math.round(x*2)/2);return Math.max(1,Math.round(x))};
const FRAC=n=>{const i=Math.floor(n),h=n-i>=.25&&n-i<.75;const r=n-i>=.75?i+1:i;return h?(i?i+" e meia":"meia"):String(r)};
function medida(k,g){const f=TQ.foods[k],u=f[6][0],n=ROUND(g/u[2],u[2]);return `${u[2]>=60?"cerca de ":""}${FRAC(n)} ${n>1?u[1]:u[0]} (${Math.round(g)} ${/^(leite|azeite)/.test(k)?"ml":"g"})`}
function equiv(k,g){const f=TQ.foods[k],ix=TQ.groups[f[1]][1],alvo=g*f[ix]/100,kc0=g*f[2]/100;
 return Object.entries(TQ.foods).filter(([k2,f2])=>k2!==k&&f2[1]===f[1]&&f2[ix]>0).map(([k2,f2])=>{let g2=alvo/f2[ix]*100;const u=f2[6][0];
  g2=Math.round(g2/5)*5||Math.round(g2);
  const kc=g2*f2[2]/100;return {k:k2,g:g2,kc,dif:kc0?Math.round((kc-kc0)/kc0*100):0}})}
function openSw(k,g){SW={k,g};SEL=[];drawSw();document.getElementById("sheet").classList.add("on");document.getElementById("sheetbg").classList.add("on")}
function closeSw(){document.getElementById("sheet").classList.remove("on");document.getElementById("sheetbg").classList.remove("on")}
function pick(k2){const i=SEL.indexOf(k2);if(i>=0)SEL.splice(i,1);else{SEL.push(k2);if(SEL.length>2)SEL.shift()}drawSw()}
function drawSw(){const {k,g}=SW,f=TQ.foods[k],gr=TQ.groups[f[1]],nut=["","","","proteína","carboidrato","gordura"][gr[1]];
 const ops=equiv(k,g);
 let h=`<div class="hd"><b>Trocar ${esc(f[0].toLowerCase())}</b><button class="x" onclick="closeSw()" aria-label="Fechar">×</button></div>
 <div class="orig">No plano: <b>${medida(k,g)}</b><br><small style="color:var(--muted)">As opções abaixo têm a mesma quantidade de ${nut}. Toque em 1 para trocar, ou em 2 para dividir meio a meio.</small></div>`;
 h+=ops.map(o=>`<div class="opt ${SEL.includes(o.k)?"sel":""}" onclick="pick('${o.k}')"><div class="ck2">${ic("check",14)}</div><div><div class="nm">${esc(TQ.foods[o.k][0])}</div><div class="qt">${medida(o.k,o.g)}</div>${Math.abs(o.dif)>15?`<div class="kc">${o.dif>0?"+":""}${o.dif}% de calorias</div>`:""}</div></div>`).join("");
 let mix="";if(SEL.length===2){const a=ops.find(o=>o.k===SEL[0]),b=ops.find(o=>o.k===SEL[1]);mix=`<b>Meio a meio:</b><br>${medida(a.k,a.g/2)} de ${esc(TQ.foods[a.k][0].toLowerCase())}<br>+ ${medida(b.k,b.g/2)} de ${esc(TQ.foods[b.k][0].toLowerCase())}`}
 else if(SEL.length===1){const a=ops.find(o=>o.k===SEL[0]);mix=`<b>Sua troca:</b> ${medida(a.k,a.g)} de ${esc(TQ.foods[a.k][0].toLowerCase())}. Marque <b>Troquei</b> na refeição.`}
 h+=`<div class="mix ${mix?"on":""}">${mix}</div><p class="note">Troca feita pelo nutriente principal do grupo. Medidas caseiras aproximadas.</p>`;
 document.getElementById("sheet").innerHTML=h}
function swItem(mi,ii,x){const c=(P.meals[mi].c||[])[ii]||[];if(!c.length)return `<li>${esc(x)}</li>`;
 return `<li class="li-sw"><span>${esc(x)}</span>${c.map(([k,g])=>`<button class="swb" onclick="openSw('${k}',${g})">${ic("repeat-2",13)}${c.length>1?esc(TQ.foods[k][0].split(" ")[0]):"Trocar"}</button>`).join("")}</li>`}
function calcInit(){const s=document.getElementById("cfood");if(!s)return;
 s.innerHTML=Object.entries(TQ.groups).map(([gk,g])=>{const fs=Object.entries(TQ.foods).filter(([k,f])=>f[1]===gk);return fs.length?`<optgroup label="${g[0]}">${fs.map(([k,f])=>`<option value="${k}">${esc(f[0])}</option>`).join("")}</optgroup>`:""}).join("");
 calcUnits()}
function calcUnits(){const k=document.getElementById("cfood").value,f=TQ.foods[k];
 document.getElementById("cunit").innerHTML=f[6].map((u,i)=>`<option value="${u[2]}">${esc(u[0])}</option>`).join("")+`<option value="1">${/^(leite|azeite)/.test(k)?"ml":"gramas"}</option>`;
 document.getElementById("cqty").value=1}
function calcGo(){const k=document.getElementById("cfood").value,g=parseFloat(document.getElementById("cunit").value)*parseFloat(String(document.getElementById("cqty").value).replace(",","."));if(!(g>0))return;openSw(k,g)}
"""

CALC_HTML = """
 <h2>Calculadora de trocas</h2><p class="sub">Escolha o que quer trocar e quanto: o app mostra as opções do mesmo grupo, já na quantidade certa.</p>
 <div class="box"><div class="calc">
  <label class="full">Alimento<select id="cfood" onchange="calcUnits()"></select></label>
  <label>Quantidade<input id="cqty" type="number" inputmode="decimal" step="0.5" min="0.5" value="1"></label>
  <label>Medida<select id="cunit"></select></label></div>
  <button class="save" onclick="calcGo()">Ver opções de troca</button></div>
"""
