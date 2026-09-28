# Revisão de Código e Documentação

**Escopo:** `conversor.py`, `test_conversor.py` e a pasta `docs/`.
**Revisor:** _(seu nome)_  **Data:** _(preencher)_

> Adapte os itens abaixo ao que você observar ao reler o projeto. Registre também um resumo no cartão "Revisão de código e documentação" do Trello.

## Checklist
- [x] O código roda sem erros (`python conversor.py`).
- [x] Todos os testes passam (`python -m unittest -v`: 40 testes).
- [x] Cada critério de aceitação tem ao menos um teste (ver tabela em `criterios_de_aceitacao.md`).
- [x] Cenários negativos cobertos (valor negativo, texto, vazio, NaN/infinito, moeda inválida, taxa inválida, API fora do ar).
- [x] Funções com docstrings e nomes descritivos.
- [x] Sem dependências externas.
- [x] Documentação inclui descrição, diagrama, interfaces, armazenamento e APIs.

## Pontos positivos
1. Uso de `Decimal` e `ROUND_HALF_UP` garante precisão e arredondamento corretos, com teste específico para o caso 1,005.
2. Separação clara entre regra de negócio (`converter`), obtenção de taxas e interface, o que facilita o teste.
3. Hierarquia de exceções própria, que permite à interface tratar todos os erros esperados em um único `except`.
4. Testes da API isolados com `mock`, sem depender da internet.

## Melhorias sugeridas
| # | Sugestão | Prioridade |
|---|----------|------------|
| 1 | As taxas padrão são valores fixos e ilustrativos, e ficarão desatualizadas. Exibir a data da taxa ou mover os valores para um arquivo de configuração. | Média |
| 2 | Não há cache das taxas da API; cada execução faz uma nova chamada. Um cache com validade curta reduziria requisições. | Baixa |
| 3 | A CLI faz uma única conversão por execução. Adicionar um laço "converter outra?" melhoraria a usabilidade. | Baixa |
| 4 | Valores com separador de milhar (`1.234,56`) são rejeitados. Documentar essa limitação ou tratar o formato. | Baixa |
| 5 | Adicionar mais moedas exige alterar `MOEDAS_SUPORTADAS` e `TAXAS_PADRAO`. Unificar em uma única estrutura evitaria inconsistências. | Média |
| 6 | Configurar integração contínua (GitHub Actions) para rodar os testes a cada push e medir cobertura (`coverage.py`). | Média |
| 7 | Sem testes de integração reais com a API; seria preciso um teste opcional, marcado para não rodar por padrão. | Baixa |
| 8 | Documentação: incluir exemplos de erro na seção de interfaces e a versão mínima de Python testada. | Baixa |

## Conclusão
A entrega atende aos critérios de aceitação definidos. As melhorias 1, 5 e 6 são as mais relevantes para uma próxima sprint.
