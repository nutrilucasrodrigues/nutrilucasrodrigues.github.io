# Ferramentas do app dos pacientes

Pasta não publicada no site (começa com "_").

- `pacientes/<nome>.py`: dados do plano de cada paciente (só primeiro nome e dieta).
- `gen_app.py`: gera `p/<slug>/` (index.html, manifest, sw.js, lembretes.ics, retorno.ics).
- `ico.py`: ícones Lucide. Antes de usar: `mkdir -p /home/claude/icons && cd /home/claude/icons && npm install lucide-static@0.460.0` e copiar `ico.py` para lá.

Uso: copiar `gen_app.py` para `/home/claude/apps/`, os pacientes para `/home/claude/apps/pacientes/` e rodar `python3 gen_app.py pacientes/<nome>.py`.
