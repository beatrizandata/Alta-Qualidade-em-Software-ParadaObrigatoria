# Agile Docs & Code Sprint: Conversor de Moedas

Atividade que simula uma sprint Scrum: planejamento no Trello, documentação técnica, implementação em Python e testes unitários com `unittest`.

## Estrutura
```
.
├── conversor.py                          # código do conversor + interface CLI
├── test_conversor.py                     # testes unitários (unittest)
└── docs/
    ├── criterios_de_aceitacao.md
    ├── documentacao_tecnica.md           # inclui diagrama de fluxo
    └── revisao_codigo_e_documentacao.md
```

## Como executar
```bash
python conversor.py          # usa taxas pré-definidas
python conversor.py --api    # tenta buscar taxas atualizadas (com fallback)
python -m unittest -v        # roda os 40 testes
```
Requer Python 3.8+ (somente biblioteca padrão).

## Quadro Trello
(https://trello.com/invite/b/6abadef07935ebc765c87977/ATTI4d5151a7d5c0a948097a8a2027ec3cab274CE25C/agile-docs-code-sprint)

## Autor
Beatriz Oliveira
