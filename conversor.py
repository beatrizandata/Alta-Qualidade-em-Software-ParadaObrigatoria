"""Conversor de moedas simples (USD, EUR, BRL).

Regras principais (ver docs/criterios_de_aceitacao.md):
- o usuário escolhe moeda de origem, moeda de destino e informa um valor;
- o resultado é exibido com duas casas decimais, arredondado corretamente
  (ROUND_HALF_UP, o arredondamento "comercial");
- os cálculos usam Decimal para evitar erros de ponto flutuante.

Uso pela linha de comando:
    python conversor.py          # usa taxas pré-definidas
    python conversor.py --api    # tenta buscar taxas atualizadas na API
"""

import json
import sys
import urllib.request
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

MOEDAS_SUPORTADAS = ("USD", "EUR", "BRL")

# Taxas pré-definidas, expressas em "unidades da moeda por 1 USD".
# São valores ilustrativos; para taxas reais use a opção --api.
TAXAS_PADRAO = {
    "USD": Decimal("1"),
    "EUR": Decimal("0.92"),
    "BRL": Decimal("5.00"),
}

URL_API = "https://open.er-api.com/v6/latest/USD"
DUAS_CASAS = Decimal("0.01")


class ErroConversao(ValueError):
    """Erro base para qualquer falha de conversão."""


class MoedaInvalidaError(ErroConversao):
    """Moeda não suportada ou código inválido."""


class ValorInvalidoError(ErroConversao):
    """Valor não numérico, negativo ou fora do limite aceito."""


class TaxaInvalidaError(ErroConversao):
    """Taxa de câmbio ausente ou inválida."""


class ErroApiTaxas(ErroConversao):
    """Falha ao obter taxas da API externa."""


# ----------------------------------------------------------------- validações
def _validar_valor(valor):
    """Converte a entrada para Decimal e garante que seja finita e >= 0."""
    if isinstance(valor, bool):
        raise ValorInvalidoError("O valor deve ser numérico.")
    try:
        if isinstance(valor, (int, Decimal, str)):
            quantia = Decimal(valor)
        elif isinstance(valor, float):
            quantia = Decimal(str(valor))
        else:
            raise ValorInvalidoError("O valor deve ser numérico.")
    except InvalidOperation as exc:
        raise ValorInvalidoError("O valor deve ser numérico.") from exc
    if not quantia.is_finite():
        raise ValorInvalidoError("O valor deve ser um número finito.")
    if quantia < 0:
        raise ValorInvalidoError("O valor não pode ser negativo.")
    return quantia


def _validar_moeda(codigo, taxas):
    """Normaliza o código (ex.: ' usd ' -> 'USD') e confere se é suportado."""
    if not isinstance(codigo, str):
        raise MoedaInvalidaError("O código da moeda deve ser texto.")
    codigo = codigo.strip().upper()
    if codigo not in MOEDAS_SUPORTADAS or codigo not in taxas:
        raise MoedaInvalidaError(
            f"Moeda '{codigo}' não suportada. "
            f"Use: {', '.join(MOEDAS_SUPORTADAS)}."
        )
    return codigo


def _taxa(taxas, moeda):
    """Retorna a taxa da moeda como Decimal positivo."""
    try:
        taxa = Decimal(str(taxas[moeda]))
    except (InvalidOperation, KeyError) as exc:
        raise TaxaInvalidaError(f"Taxa inválida para {moeda}.") from exc
    if not taxa.is_finite() or taxa <= 0:
        raise TaxaInvalidaError(f"Taxa inválida para {moeda}.")
    return taxa


# ---------------------------------------------------------------- conversão
def converter(valor, origem, destino, taxas=None):
    """Converte `valor` de `origem` para `destino`.

    Retorna Decimal com duas casas decimais (ROUND_HALF_UP).
    Lança uma subclasse de ErroConversao se a entrada for inválida.
    """
    taxas = TAXAS_PADRAO if taxas is None else taxas
    quantia = _validar_valor(valor)
    origem = _validar_moeda(origem, taxas)
    destino = _validar_moeda(destino, taxas)
    try:
        resultado = quantia / _taxa(taxas, origem) * _taxa(taxas, destino)
        return resultado.quantize(DUAS_CASAS, rounding=ROUND_HALF_UP)
    except InvalidOperation as exc:
        raise ValorInvalidoError("Valor grande demais para converter.") from exc


def interpretar_valor(texto):
    """Interpreta o texto digitado ('10.5' ou '10,5') como Decimal."""
    texto = str(texto).strip()
    if "," in texto and "." not in texto:
        texto = texto.replace(",", ".")
    return _validar_valor(texto)


# --------------------------------------------------------------- API externa
def buscar_taxas_api(url=URL_API, timeout=5):
    """Busca taxas (base USD) na API e retorna dict {moeda: Decimal}."""
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            dados = json.load(resposta)
    except (OSError, ValueError) as exc:
        raise ErroApiTaxas("Não foi possível acessar a API de taxas.") from exc

    if not isinstance(dados, dict) or dados.get("result") != "success":
        raise ErroApiTaxas("A API retornou uma resposta inesperada.")
    rates = dados.get("rates")
    if not isinstance(rates, dict):
        raise ErroApiTaxas("A API retornou uma resposta inesperada.")
    try:
        return {m: Decimal(str(rates[m])) for m in MOEDAS_SUPORTADAS}
    except (KeyError, InvalidOperation) as exc:
        raise ErroApiTaxas("A API não retornou todas as moedas.") from exc


def obter_taxas(usar_api=False):
    """Retorna (taxas, fonte). Se a API falhar, cai para as taxas padrão."""
    if usar_api:
        try:
            return buscar_taxas_api(), "API"
        except ErroApiTaxas:
            return dict(TAXAS_PADRAO), "PADRAO (API indisponível)"
    return dict(TAXAS_PADRAO), "PADRAO"


# ------------------------------------------------------------------ interface
def executar_cli(entrada=input, saida=print, taxas=None):
    """Interface de texto. `entrada` e `saida` são injetáveis para teste.

    Retorna o Decimal convertido, ou None se houve erro de entrada.
    """
    saida("=== Conversor de Moedas ===")
    saida(f"Moedas disponíveis: {', '.join(MOEDAS_SUPORTADAS)}")
    try:
        origem = entrada("Moeda de origem: ")
        destino = entrada("Moeda de destino: ")
        texto_valor = entrada("Valor a converter: ")
        quantia = interpretar_valor(texto_valor)
        resultado = converter(quantia, origem, destino, taxas)
    except ErroConversao as erro:
        saida(f"Erro: {erro}")
        return None
    saida(
        f"{quantia:.2f} {origem.strip().upper()} = "
        f"{resultado:.2f} {destino.strip().upper()}"
    )
    return resultado


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    taxas, fonte = obter_taxas(usar_api="--api" in argv)
    print(f"Fonte das taxas: {fonte}")
    resultado = executar_cli(taxas=taxas)
    return 0 if resultado is not None else 1


if __name__ == "__main__":
    sys.exit(main())
