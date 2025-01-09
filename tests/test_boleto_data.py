
import unittest

from pyboleto.data import BoletoData
from datetime import date

NEXT_MAX_PAYMENT_FACTOR_NUMBER = 10000


class TestBoletoData(unittest.TestCase):
    def setUp(self):
        self.dados = []
        for i in range(3):
            d = BoletoData()
            d.carteira = '157'
            d.agencia_cedente = '0293'
            d.conta_cedente = '01328'
            d.data_vencimento = date(2009, 10, 19)
            d.data_documento = date(2009, 10, 19)
            d.data_processamento = date(2009, 10, 19)
            d.valor_documento = 29.80
            d.nosso_numero = str(157 + i)
            d.numero_documento = str(456 + i)
            self.dados.append(d)

    def test_as_reached_payment_factor_max_limit(self):
        result = self.dados[0]._as_reached_payment_factor_max_limit(NEXT_MAX_PAYMENT_FACTOR_NUMBER)
        self.assertTrue(result)

    def test_calculate_due_date_days_from_factor(self):
        result = self.dados[0]._calculate_due_date_days_from_factor(NEXT_MAX_PAYMENT_FACTOR_NUMBER + 1, 1000)
        self.assertEqual(result, 1001)

suite = unittest.TestLoader().loadTestsFromTestCase(TestBoletoData)

if __name__ == '__main__':
    unittest.main()
