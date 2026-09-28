"""Testes unitários do conversor de moedas (unittest).

Executar:  python -m unittest -v
"""

import io
import json
import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import conversor
from conversor import (
    ErroApiTaxas,
    MoedaInvalidaError,
    TaxaInvalidaError,
    ValorInvalidoError,
    converter,
)

TAXAS_TESTE = {"USD": Decimal("1"), "EUR": Decimal("1"), "BRL": Decimal("1.005")}


class TestConversoesCorretas(unittest.TestCase):
    """Critérios 1-3: escolher moedas, informar valor, ver o equivalente."""

    def test_usd_para_brl(self):
        self.assertEqual(converter(100, "USD", "BRL"), Decimal("500.00"))

    def test_brl_para_usd(self):
        self.assertEqual(converter(500, "BRL", "USD"), Decimal("100.00"))

    def test_usd_para_eur(self):
        self.assertEqual(converter(100, "USD", "EUR"), Decimal("92.00"))

    def test_eur_para_usd(self):
        self.assertEqual(converter(92, "EUR", "USD"), Decimal("100.00"))

    def test_eur_para_brl_passando_pelo_usd(self):
        # 10 / 0.92 * 5 = 54,3478... -> 54,35
        self.assertEqual(converter(10, "EUR", "BRL"), Decimal("54.35"))

    def test_mesma_moeda_retorna_o_mesmo_valor(self):
        self.assertEqual(converter(42.5, "BRL", "BRL"), Decimal("42.50"))

    def test_zero_retorna_zero(self):
        self.assertEqual(converter(0, "USD", "BRL"), Decimal("0.00"))

    def test_codigo_minusculo_e_com_espacos(self):
        self.assertEqual(converter(100, " usd ", "brl"), Decimal("500.00"))

    def test_aceita_texto_float_e_decimal(self):
        esperado = Decimal("52.50")
        for entrada in ("10.5", 10.5, Decimal("10.5")):
            with self.subTest(entrada=entrada):
                self.assertEqual(converter(entrada, "USD", "BRL"), esperado)


class TestPrecisaoEArredondamento(unittest.TestCase):
    """Critérios 4 e 5: duas casas decimais e arredondamento correto."""

    def test_resultado_tem_sempre_duas_casas(self):
        resultado = converter(1, "USD", "EUR")
        self.assertEqual(resultado.as_tuple().exponent, -2)

    def test_arredonda_metade_para_cima(self):
        # 1,005 deve virar 1,01 (com float puro daria 1,00)
        self.assertEqual(converter(1, "USD", "BRL", TAXAS_TESTE), Decimal("1.01"))

    def test_arredonda_para_baixo_quando_abaixo_da_metade(self):
        taxas = {**TAXAS_TESTE, "BRL": Decimal("1.004")}
        self.assertEqual(converter(1, "USD", "BRL", taxas), Decimal("1.00"))

    def test_valor_grande(self):
        self.assertEqual(
            converter(1_000_000_000, "USD", "BRL"), Decimal("5000000000.00")
        )


class TestEntradasInvalidas(unittest.TestCase):
    """Cenários negativos."""

    def test_valor_negativo(self):
        with self.assertRaises(ValorInvalidoError):
            converter(-1, "USD", "BRL")

    def test_valor_texto_nao_numerico(self):
        with self.assertRaises(ValorInvalidoError):
            converter("abc", "USD", "BRL")

    def test_valor_vazio(self):
        with self.assertRaises(ValorInvalidoError):
            converter("", "USD", "BRL")

    def test_valor_none(self):
        with self.assertRaises(ValorInvalidoError):
            converter(None, "USD", "BRL")

    def test_valor_booleano(self):
        with self.assertRaises(ValorInvalidoError):
            converter(True, "USD", "BRL")

    def test_valor_nan_e_infinito(self):
        for entrada in ("NaN", "Infinity", float("nan"), float("inf")):
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValorInvalidoError):
                    converter(entrada, "USD", "BRL")

    def test_valor_absurdamente_grande(self):
        with self.assertRaises(ValorInvalidoError):
            converter("9" * 40, "USD", "BRL")

    def test_moeda_origem_invalida(self):
        with self.assertRaises(MoedaInvalidaError):
            converter(10, "XXX", "BRL")

    def test_moeda_destino_invalida(self):
        with self.assertRaises(MoedaInvalidaError):
            converter(10, "USD", "JPY")

    def test_moeda_vazia_ou_nao_texto(self):
        for codigo in ("", None, 123):
            with self.subTest(codigo=codigo):
                with self.assertRaises(MoedaInvalidaError):
                    converter(10, codigo, "BRL")

    def test_taxa_zero_negativa_ou_nan(self):
        for taxa in (Decimal("0"), Decimal("-1"), Decimal("NaN")):
            with self.subTest(taxa=taxa):
                taxas = {**TAXAS_TESTE, "BRL": taxa}
                with self.assertRaises(TaxaInvalidaError):
                    converter(1, "USD", "BRL", taxas)


class TestInterpretarValor(unittest.TestCase):
    def test_virgula_como_decimal(self):
        self.assertEqual(conversor.interpretar_valor("10,5"), Decimal("10.5"))

    def test_ponto_como_decimal(self):
        self.assertEqual(conversor.interpretar_valor(" 10.5 "), Decimal("10.5"))

    def test_texto_invalido(self):
        with self.assertRaises(ValorInvalidoError):
            conversor.interpretar_valor("dez")


class TestInterface(unittest.TestCase):
    """A interface responde de forma adequada (entrada/saída simuladas)."""

    def _executar(self, respostas):
        mensagens = []
        respostas = iter(respostas)
        resultado = conversor.executar_cli(
            entrada=lambda _prompt: next(respostas), saida=mensagens.append
        )
        return resultado, "\n".join(mensagens)

    def test_fluxo_feliz(self):
        resultado, texto = self._executar(["usd", "brl", "100"])
        self.assertEqual(resultado, Decimal("500.00"))
        self.assertIn("100.00 USD = 500.00 BRL", texto)

    def test_aceita_virgula(self):
        resultado, _ = self._executar(["USD", "BRL", "10,5"])
        self.assertEqual(resultado, Decimal("52.50"))

    def test_lista_moedas_disponiveis(self):
        _, texto = self._executar(["USD", "BRL", "1"])
        for moeda in conversor.MOEDAS_SUPORTADAS:
            self.assertIn(moeda, texto)

    def test_moeda_invalida_mostra_erro(self):
        resultado, texto = self._executar(["XXX", "BRL", "10"])
        self.assertIsNone(resultado)
        self.assertIn("Erro:", texto)

    def test_valor_invalido_mostra_erro(self):
        resultado, texto = self._executar(["USD", "BRL", "abc"])
        self.assertIsNone(resultado)
        self.assertIn("Erro:", texto)


def _resposta_api(dados):
    """Simula o retorno de urllib.request.urlopen (context manager)."""
    contexto = MagicMock()
    contexto.__enter__.return_value = io.BytesIO(json.dumps(dados).encode())
    return contexto


class TestApiDeTaxas(unittest.TestCase):
    """As taxas estão atualizadas / a API é acessada corretamente."""

    DADOS_OK = {"result": "success", "rates": {"USD": 1, "EUR": 0.9, "BRL": 5.5}}

    @patch("conversor.urllib.request.urlopen")
    def test_api_ok_retorna_taxas_decimal(self, urlopen):
        urlopen.return_value = _resposta_api(self.DADOS_OK)
        taxas = conversor.buscar_taxas_api()
        self.assertEqual(taxas["BRL"], Decimal("5.5"))
        urlopen.assert_called_once_with(conversor.URL_API, timeout=5)

    @patch("conversor.urllib.request.urlopen")
    def test_conversao_usa_taxas_da_api(self, urlopen):
        urlopen.return_value = _resposta_api(self.DADOS_OK)
        taxas = conversor.buscar_taxas_api()
        self.assertEqual(converter(10, "USD", "BRL", taxas), Decimal("55.00"))

    @patch("conversor.urllib.request.urlopen", side_effect=URLError("sem rede"))
    def test_falha_de_rede(self, _urlopen):
        with self.assertRaises(ErroApiTaxas):
            conversor.buscar_taxas_api()

    @patch("conversor.urllib.request.urlopen")
    def test_resposta_com_erro(self, urlopen):
        urlopen.return_value = _resposta_api({"result": "error"})
        with self.assertRaises(ErroApiTaxas):
            conversor.buscar_taxas_api()

    @patch("conversor.urllib.request.urlopen")
    def test_resposta_sem_todas_as_moedas(self, urlopen):
        urlopen.return_value = _resposta_api(
            {"result": "success", "rates": {"USD": 1, "EUR": 0.9}}
        )
        with self.assertRaises(ErroApiTaxas):
            conversor.buscar_taxas_api()

    @patch("conversor.urllib.request.urlopen")
    def test_resposta_nao_json(self, urlopen):
        contexto = MagicMock()
        contexto.__enter__.return_value = io.BytesIO(b"<html>")
        urlopen.return_value = contexto
        with self.assertRaises(ErroApiTaxas):
            conversor.buscar_taxas_api()

    @patch("conversor.urllib.request.urlopen", side_effect=URLError("sem rede"))
    def test_obter_taxas_faz_fallback(self, _urlopen):
        taxas, fonte = conversor.obter_taxas(usar_api=True)
        self.assertEqual(taxas, conversor.TAXAS_PADRAO)
        self.assertIn("indisponível", fonte)

    def test_obter_taxas_sem_api(self):
        taxas, fonte = conversor.obter_taxas(usar_api=False)
        self.assertEqual(fonte, "PADRAO")
        self.assertEqual(taxas, conversor.TAXAS_PADRAO)


if __name__ == "__main__":
    unittest.main()
