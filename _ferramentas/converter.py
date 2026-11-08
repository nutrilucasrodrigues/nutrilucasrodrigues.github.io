"""Cria pacientes/<nome>.py a partir do PDF já montado (pdf_<pasta>/build.py), tirando qualquer dado de saúde."""
import ast, re, secrets, pprint, pathlib, sys
K = re.compile(r'caneta|mounjaro|tirzepat|colesterol|ciclo|menstrua|horm|filhos|testost|\brins?\b|press[aã]o|glic|diabet|tireoid|arritm|exame|médic|enantato|clomif|remédio|azia|hematócr|ginecolog|nutrólog', re.I)
ICON = [('água', 'glass-water'), ('agua', 'glass-water'), ('treino', 'dumbbell'), ('sono', 'moon'), ('jantar', 'moon'), ('intestino', 'leaf'),
        ('bebida', 'cup-soda'), ('fim de semana', 'calendar'), ('casa', 'house'), ('dia a dia', 'house'), ('rotina', 'clock'), ('café', 'coffee'),
        ('fome', 'utensils'), ('barriga', 'leaf'), ('emagrec', 'target'), ('gordura', 'target'), ('massa', 'dumbbell')]
def icon(t):
    t = t.lower()
    for k, v in ICON:
        if k in t: return v
    return 'info'
MEDIDAS = [
 ["hand", "Colher de sopa cheia", "Como a comida fica na colher, sem apertar e sem montinho exagerado."],
 ["soup", "1 concha média de feijão", "Concha comum de cozinha, cheia de grão e caldo, sem montinho."],
 ["drumstick", "1 filé médio de frango", "Do tamanho e da grossura da palma da sua mão, sem os dedos."],
 ["beef", "1 bife médio", "Um pouco menor que a palma da mão e da grossura do dedo mindinho."],
 ["hand", "4 a 5 colheres de sopa de arroz", "Cabe na mão em concha, sem transbordar (cerca de 1 punho fechado)."],
 ["info", "1 colher de sopa rasa", "Passe o dedo por cima: o que fica no nível da colher."],
]
PREPARO = ["Desfiar o frango da semana e separar em potes", "Temperar e porcionar a carne: 1 porção por pote, no freezer",
           "Cozinhar o feijão e congelar em porções de 1 concha", "Cozinhar ovos para 2 ou 3 dias", "Lavar as frutas e deixar à vista na geladeira"]
RECEITAS = [
 ["Frango desfiado prático", "drumstick", ["Cozinhe o peito de frango na panela de pressão com água, alho e sal por 15 minutos.", "Escorra e desfie com dois garfos ainda morno.", "Refogue com 1 fio de óleo, cebola, tomate e cheiro-verde.", "Divida em potes: até 3 dias na geladeira ou 30 dias no freezer."]],
 ["Omelete de 2 ovos", "egg", ["Bata 2 ovos com sal, orégano e tomate picado.", "Unte a frigideira com 1 colher de chá de óleo.", "Fogo baixo, tampe e deixe 3 minutos.", "Dobre ao meio e sirva com salada."]],
 ["Carne grelhada macia", "beef", ["Tempere o bife com alho, sal e limão 15 minutos antes.", "Aqueça bem a frigideira com 1 colher de chá de óleo.", "Grelhe 2 a 3 minutos de cada lado, sem ficar virando.", "Descanse 2 minutos antes de cortar."]],
 ["Feijão da semana", "cooking-pot", ["Deixe 500 g de feijão de molho por 8 horas e descarte a água.", "Pressão por 25 minutos com água nova e folha de louro.", "Refogue alho e cebola com 1 colher de sopa de óleo e junte o feijão.", "Divida em potes de 1 concha e congele."]],
]
FORA = [
 ["party-popper", "Festa", ["Coma uma refeição do plano antes de sair.", "Monte 1 prato só, metade salada.", "Intercale cada bebida com 1 copo de água."]],
 ["sandwich", "Lanchonete", ["Prefira sanduíche natural ou misto quente, sem maionese extra.", "Suco natural sem açúcar ou refrigerante zero.", "Salgado assado no lugar do frito."]],
 ["utensils", "Self-service", ["Dê uma volta antes de servir.", "Salada primeiro, depois arroz, feijão e 1 carne.", "Fuja de 2 carnes e de frituras."]],
 ["flame", "Churrasco", ["Comece pela salada e vinagrete.", "Prefira frango, patinho ou alcatra sem gordura.", "Farofa e pão de alho: escolha um só."]],
]
def convert(pasta, nome, retorno, agua, refri, saida):
    src = open(f'/home/claude/pdf_{pasta}/build.py').read(); d = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('MEALS', 'GRUPOS', 'COMPRAS', 'ORIENT', 'PACIENTE', 'DATA'):
            try: d[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception: pass
    m = re.search(r'PACIENTE = "[^"]*"; DATA = "(\d+) de (\w+) de (\d+)"', src)
    meses = {'outubro': '10', 'novembro': '11', 'dezembro': '12'}
    atual = f"{int(m.group(1)):02d}/{meses[m.group(2)]}/{m.group(3)}"
    tot = re.search(r'Total aproximado</td><td></td><td class="v">([^<]+)<', src)
    meals = []
    for h, n, s, items, t in d['MEALS']:
        for x in [n, s, t] + list(items): assert not K.search(x), (pasta, x)
        meals.append(dict(h=h.replace('h', ':'), n=n, s=s, i=list(items), t=t))
    tips = []
    for title, items in d['ORIENT']:
        if K.search(title): continue
        it = [x for x in items if not K.search(x)]
        if it: tips.append([icon(title), title, it])
    P = dict(nome=nome, slug=f"{pasta if pasta != 'junior' else 'denilson'}-{secrets.token_hex(3)}", key=f"plano-{pasta}-", atualizado=atual,
             retorno=dict(data=retorno), agua_l=agua, refri=refri, meals=meals,
             groups=[[g[0], g[1], [list(x) for x in g[3]]] for g in d['GRUPOS']],
             medidas=MEDIDAS, buys=[[c[0], c[1]] for c in d['COMPRAS']],
             compras_obs=f"Estimativa: {tot.group(1)} no mês." if tot else "", preparo=PREPARO, receitas=RECEITAS, fora=FORA, tips=tips)
    pathlib.Path(saida).write_text('# Gerado a partir do PDF. Só primeiro nome e dieta: nada de peso, exames ou diagnóstico.\nP = ' + pprint.pformat(P, width=160, sort_dicts=False) + '\n')
    print(pasta, P['slug'], len(meals), 'refeições', len(tips), 'dicas', P['compras_obs'])

if __name__ == '__main__':
    L = [('waleska', 'Waleska', '2026-11-25', 2.8, False), ('isabelly', 'Isabelly', '2026-11-25', 2.5, True),
         ('alexandre', 'Alexandre', '2026-11-27', 3.8, False), ('junior', 'Denilson', '2026-11-27', 3.5, False), ('iasmin', 'Iasmin', '2026-11-30', 2.3, True)]
    for pasta, nome, ret, ag, rf in L:
        out = f"/home/claude/apps/pacientes/{'denilson' if pasta == 'junior' else pasta}.py"
        if pathlib.Path(out).exists(): print('já existe', out); continue
        convert(pasta, nome, ret, ag, rf, out)
