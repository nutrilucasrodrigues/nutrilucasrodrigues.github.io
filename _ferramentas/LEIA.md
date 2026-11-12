# Ferramentas do app dos pacientes

Pasta não publicada no site (começa com "_").

- `pacientes/<nome>.py`: dados do plano de cada paciente (só primeiro nome e dieta).
- `gen_app.py`: gera `p/<slug>/` (index.html, manifest, sw.js, lembretes.ics, retorno.ics).
- `ico.py`: ícones Lucide. Antes de usar: `mkdir -p /home/claude/icons && cd /home/claude/icons && npm install lucide-static@0.460.0` e copiar `ico.py` para lá.

Uso: copiar `gen_app.py` para `/home/claude/apps/`, os pacientes para `/home/claude/apps/pacientes/` e rodar `python3 gen_app.py pacientes/<nome>.py`.

## Metas até o retorno (padrão)
- Cada paciente tem `metas` no arquivo dele: `plano` (dias por semana seguindo o plano, padrão 5), `agua` (dias com a água completa, padrão 5) e `treino` (ex.: `('Musculação', 2)` ou `None`).
- O app mostra o card "Minha meta até o retorno" no topo da aba Plano, com o progresso da semana (zera toda segunda). Um dia conta como "seguindo o plano" quando no máximo 1 refeição principal ficou sem marcar "Comi" ou "Troquei".
- A meta de peso nunca vai para o app (privacidade): fica no PDF e na planilha (aba Evolução, observações).
