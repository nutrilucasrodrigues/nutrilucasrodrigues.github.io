"""Pack Feed Nutri: gera as amostras editáveis (.pptx) e as prévias (.png)."""
import pathlib, subprocess, shutil
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

H = pathlib.Path(__file__).parent; OUT = H / 'amostras'; OUT.mkdir(exist_ok=True)
C = dict(bg='F6F4EF', dark='2F4A3A', acc='A7C4A0', soft='E4ECDF', ink='1F2A24', mut='5E6B63', white='FFFFFF')
rgb = lambda k: RGBColor.from_string(C.get(k, k))
FONT = 'Arial'

def new(w, h):
    p = Presentation(); p.slide_width = Inches(w); p.slide_height = Inches(h); return p
def slide(p):
    s = p.slides.add_slide(p.slide_layouts[6])
    bg = s.background.fill; bg.solid(); bg.fore_color.rgb = rgb('bg'); return s
def box(s, x, y, w, h, color, shape=MSO_SHAPE.ROUNDED_RECTANGLE, adj=0.12):
    r = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    r.fill.solid(); r.fill.fore_color.rgb = rgb(color); r.line.fill.background()
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE: r.adjustments[0] = adj
    r.shadow.inherit = False
    from pptx.oxml.ns import qn
    sp = r._element.spPr
    if sp.find(qn('a:effectLst')) is None: sp.append(sp.makeelement(qn('a:effectLst'), {}))
    return r
def text(s, x, y, w, h, t, size, color='ink', bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, lines=None):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame; tf.word_wrap = True
    tf.vertical_anchor = anchor; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    paras = lines or [(t, size, color, bold)]
    for i, (tt, sz, co, bo) in enumerate(paras):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.alignment = align
        if i: para.space_before = Pt(sz * 0.5)
        r = para.add_run(); r.text = tt; f = r.font; f.size = Pt(sz); f.bold = bo; f.color.rgb = rgb(co); f.name = FONT
    return tb
def header(s, x=0.8, y=0.8):
    c = box(s, x, y, 1.3, 1.3, 'acc', MSO_SHAPE.OVAL)
    tf = c.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    for i, t in enumerate(['SUA', 'FOTO']):
        para = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); para.alignment = PP_ALIGN.CENTER
        r = para.add_run(); r.text = t; r.font.size = Pt(13); r.font.bold = True; r.font.color.rgb = rgb('dark'); r.font.name = FONT
    text(s, x + 1.6, y + 0.12, 7, 0.6, 'Seu Nome · Nutricionista', 30, 'ink', True)
    text(s, x + 1.6, y + 0.68, 7, 0.5, '@seuperfil · CRN-0 00000', 24, 'mut')
def foot(s, w, h, n=None, tot=None):
    text(s, 0.8, h - 0.9, w - 1.6, 0.4, 'Os resultados variam de pessoa para pessoa', 16, 'mut')
    if n: text(s, w - 2.0, h - 0.9, 1.2, 0.4, f'{n}/{tot}', 18, 'mut', True, PP_ALIGN.RIGHT)
def tag(s, x, y, t):
    b = box(s, x, y, 0.32 * len(t) * 0.55 + 0.9, 0.62, 'acc', adj=0.5)
    tf = b.text_frame; tf.margin_left = tf.margin_right = Inches(0.2); tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    r = tf.paragraphs[0].add_run(); r.text = t; r.font.size = Pt(20); r.font.bold = True; r.font.color.rgb = rgb('dark'); r.font.name = FONT
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER

W, HF, HS = 10.8, 13.5, 19.2

def carrossel(nome, slides):
    p = new(W, HF); tot = len(slides)
    for i, sd in enumerate(slides, 1):
        s = slide(p); header(s)
        if sd.get('tag'): tag(s, 0.8, 2.6, sd['tag'])
        import math
        ts = sd.get('ts', 54); nl = max(1, math.ceil(len(sd['t']) * 0.52 * ts / 72 / 9.2))
        text(s, 0.8, 3.45, 9.2, 3.2, sd['t'], ts, 'dark', True)
        y = 3.45 + nl * ts * 1.2 / 72 + 0.6
        for item in sd.get('itens', []):
            hh = item.get('h', 2.35)
            b = box(s, 0.8, y, 9.2, hh, 'white', adj=0.08)
            text(s, 1.2, y + 0.35, 8.4, hh - 0.5, '', 0, lines=[(item['b'], 32, 'ink', True), (item['d'], 27, 'mut', False)])
            y += hh + 0.4
        if sd.get('nota'):
            b = box(s, 0.8, y + 0.1, 9.2, 1.9, 'dark', adj=0.1)
            text(s, 1.2, y + 0.45, 8.4, 1.3, sd['nota'], 29, 'white', True)
        foot(s, W, HF, i, tot)
    p.save(OUT / f'{nome}.pptx')

def tweet(nome, t, ts=44):
    p = new(W, HF); s = slide(p); header(s, 0.8, 3.0)
    text(s, 0.8, 4.9, 9.2, 6.5, t, ts, 'ink', False)
    foot(s, W, HF); p.save(OUT / f'{nome}.pptx')

def story(nome):
    p = new(W, HS); s = slide(p); header(s, 0.8, 1.6)
    tag(s, 0.8, 3.6, 'QUIZ DA SEMANA')
    text(s, 0.8, 4.5, 9.2, 2.6, 'Qual destes tem mais fibra?', 64, 'dark', True)
    y = 7.3
    for t in ['Pão francês', 'Pão de forma integral', 'Cuscuz de milho']:
        b = box(s, 0.8, y, 9.2, 1.25, 'white', adj=0.3)
        text(s, 1.3, y + 0.3, 8.2, 0.7, t, 34, 'ink', True); y += 1.55
    b = box(s, 0.8, 12.3, 9.2, 4.6, 'soft', adj=0.08)
    text(s, 1.1, 14.1, 8.6, 1.0, 'Espaço para o adesivo de QUIZ', 26, 'mut', True, PP_ALIGN.CENTER)
    text(s, 0.8, 17.6, 9.2, 0.8, 'Resposta amanhã nos stories', 26, 'dark', True, PP_ALIGN.CENTER)
    p.save(OUT / f'{nome}.pptx')

carrossel('01-carrossel-sobrou-arroz', [
 dict(tag='COZINHA DO DIA A DIA', t='Sobrou arroz? 5 jeitos de aproveitar sem desperdício', ts=66,
      nota='Salve este post para usar na próxima sobra.'),
 dict(tag='1 E 2', t='Do pote para o prato', ts=58, itens=[
      dict(b='1. Bolinho de arroz assado', d='Arroz + 1 ovo + cheiro-verde + 2 colheres de farinha. Forno por 25 minutos.'),
      dict(b='2. Arroz de forno com legumes', d='Arroz + frango desfiado + cenoura ralada + milho. 15 minutos no forno.')]),
 dict(tag='3 E 4', t='Rápido e com proteína', ts=58, itens=[
      dict(b='3. Omelete com arroz', d='2 ovos + 3 colheres de arroz + tomate. Pronto em 5 minutos.'),
      dict(b='4. Sopa mais encorpada', d='Junte 2 colheres de arroz no fim do cozimento da sopa de legumes.')]),
 dict(tag='5', t='Recheio de legumes', ts=58, itens=[
      dict(b='5. Abobrinha ou pimentão recheado', d='Arroz + carne moída ou frango + tomate. Forno por 20 minutos.')],
      nota='Arroz pronto: geladeira em até 2 horas, por até 3 dias. Reaqueça bem.'),
 dict(tag='SUA VEZ', t='Qual você vai testar primeiro?', ts=66,
      nota='Comenta o número aqui embaixo. Quer um plano que encaixe na sua rotina? Link na bio.'),
])
carrossel('02-carrossel-prato-3-passos', [
 dict(tag='PRATO DO DIA A DIA', t='Monte um prato equilibrado em 3 passos', ts=68,
      nota='Sem balança e sem contar caloria.'),
 dict(tag='PASSO 1', t='Metade do prato: salada e legumes', ts=58, itens=[
      dict(b='Folhas à vontade', d='Alface, couve, repolho, tomate, pepino.'),
      dict(b='Legumes cozidos ou refogados', d='Cenoura, abobrinha, chuchu, vagem, beterraba.')]),
 dict(tag='PASSO 2', t='Um quarto: proteína', ts=58, itens=[
      dict(b='Escolha uma', d='Frango, carne magra, ovos, peixe, sardinha ou fígado.'),
      dict(b='Feijão também ajuda', d='Ele soma proteína e fibra ao prato.')]),
 dict(tag='PASSO 3', t='Um quarto: arroz ou raízes', ts=58, itens=[
      dict(b='Escolha um', d='Arroz, mandioca, batata, inhame, macarrão ou cuscuz.'),
      dict(b='A medida', d='Cabe na mão em concha, sem montinho.')]),
 dict(tag='DICA', t='Comece pela salada e coma devagar', ts=62,
      nota='Qual passo é o mais difícil para você? Comenta aqui. Link na bio para agendar.'),
])
tweet('03-tweet-3-em-3-horas', 'Comer de 3 em 3 horas não é regra.\n\nO que importa é o total do dia e a sua fome real. Tem gente que vai muito bem com 3 refeições e tem gente que precisa de 5.\n\nO melhor horário é o que cabe na sua rotina.')
tweet('04-tweet-cafe-da-manha', 'Pular o café da manhã não engorda sozinho.\n\nO problema é chegar no almoço morrendo de fome e exagerar.\n\nAcordou sem fome? Tudo bem. Leve um lanche com proteína para mais tarde.')
story('05-story-quiz-fibra')

# prévias PNG
tmp = H / '_tmp'; shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir()
for f in sorted(OUT.glob('*.pptx')):
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(tmp), str(f)], check=True, capture_output=True)
    pdf = tmp / (f.stem + '.pdf')
    subprocess.run(['pdftoppm', '-png', '-r', '100', str(pdf), str(OUT / f.stem)], check=True)
print('ok')
