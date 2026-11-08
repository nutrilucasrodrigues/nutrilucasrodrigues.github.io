import re, pathlib
D = pathlib.Path('/home/claude/icons/node_modules/lucide-static/icons')
def ico(name, size=24, color='currentColor', sw=2):
    s = (D / f'{name}.svg').read_text()
    s = re.sub(r'<!--.*?-->', '', s, flags=re.S).strip()
    s = re.sub(r'\swidth="\d+"', f' width="{size}"', s, 1)
    s = re.sub(r'\sheight="\d+"', f' height="{size}"', s, 1)
    s = s.replace('stroke="currentColor"', f'stroke="{color}"').replace('stroke-width="2"', f'stroke-width="{sw}"')
    s = s.replace('class="lucide', 'aria-hidden="true" class="lucide')
    return ' '.join(s.split())
