# Critérios de Aceitação: Conversor de Moedas

**Funcionalidade:** conversão de valores entre USD, EUR e BRL.

| # | Critério | Como é verificado (testes em `test_conversor.py`) |
|---|----------|---------------------------------------------------|
| CA1 | O usuário seleciona a moeda de origem e a de destino (USD, EUR, BRL). | `TestConversoesCorretas`, `TestInterface.test_lista_moedas_disponiveis` |
| CA2 | O usuário informa a quantidade da moeda de origem (aceita `10.5` e `10,5`). | `TestInterpretarValor`, `TestInterface.test_aceita_virgula` |
| CA3 | O sistema exibe o valor equivalente na moeda de destino. | `TestInterface.test_fluxo_feliz` |
| CA4 | O resultado tem precisão de, no mínimo, duas casas decimais. | `TestPrecisaoEArredondamento.test_resultado_tem_sempre_duas_casas` |
| CA5 | O resultado é arredondado corretamente (metade para cima). | `test_arredonda_metade_para_cima`, `test_arredonda_para_baixo_quando_abaixo_da_metade` |
| CA6 | Entradas inválidas (valor negativo, texto, vazio; moeda inexistente) são rejeitadas com mensagem clara, sem travar o programa. | `TestEntradasInvalidas`, `TestInterface.test_moeda_invalida_mostra_erro`, `test_valor_invalido_mostra_erro` |
| CA7 | As taxas podem vir de uma API externa; se a API falhar, o sistema usa taxas pré-definidas. | `TestApiDeTaxas` |

## Cenários (formato Dado / Quando / Então)

**CA3 e CA4:** Dado que a taxa é 1 USD = 5,00 BRL, quando o usuário converte 100 USD para BRL, então o sistema exibe `500.00 BRL`.

**CA5:** Dado que o resultado exato é 1,005, quando o sistema arredonda, então exibe `1.01`.

**CA6:** Dado que o usuário digita um valor negativo, quando o sistema valida a entrada, então exibe `Erro: O valor não pode ser negativo.`

**CA7:** Dado que a API está fora do ar, quando o programa é iniciado com `--api`, então usa as taxas pré-definidas e informa a fonte usada.

## Definição de Pronto (Definition of Done)
- Todos os critérios acima cobertos por pelo menos um teste automatizado.
- `python -m unittest` executa sem falhas.
- Documentação técnica atualizada e revisão de código registrada.
