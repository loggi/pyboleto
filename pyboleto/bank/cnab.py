# encoding: utf-8
"""Backport `cnab` module from python-boleto to our fork of pyboleto."""
import sys
from decimal import Decimal

from datetime import datetime


DATE_PARSE_FORMAT = '%d%m%y'
CURRENCY_PARSE_FORMAT = '%d.%.2d'

def _currency(decimal):
    """ Return xxx.yy as xxxyy. """
    return int(decimal * 100)

def _parse_date(s):
    """ Parse CNAB400 date. """
    try:
        return datetime.strptime(s, DATE_PARSE_FORMAT).date()
    except ValueError:
        return None


def _parse_currency(s):
    """ Parse CNAB400 currency. """
    return Decimal(CURRENCY_PARSE_FORMAT % (int(s[:-2]), int(s[-2:])))


class CNABParsingError(Exception):

    """ Default exception for any error while parsing CNAB file. """

    pass


class CNABParser(object):

    """ Parser for CNAB file. """

    def __init__(self, filename):
        """ CNAB file structure and loading. """
        self.header = None
        self.transactions = None
        self.trailer = None
        with open(filename, 'r') as fd:
            self._parse(fd.readlines())

    def _parse(self, data):
        """ Automatically parses.  """
        try:
            self.header = self._parse_header(data[0])
            self.transactions = self._parse_transactions(data[1:-1])
            self.trailer = self._parse_trailer(data[-1])
        except Exception, e:
            raise CNABParsingError(unicode(e)), None, sys.exc_info()[2]

    @staticmethod
    def _parse_header(h):
        """ Get header info. """
        return {
            'agencia': int(h[26:30]),
            'conta': int(h[33:38]),
            'data_geracao': _parse_date(h[94:100]),
            'data_credito': _parse_date(h[113:119]),
            'num_arquivo_retorno': int(h[108:113]),
        }

    def _parse_transactions(self, transactions):
        """ Get transactions for each transaction line. """
        return [self._parse_transaction(t) for t in transactions]

    @staticmethod
    def _parse_transaction(t):
        """ Get transaction info. """
        return {
            'nosso_numero': int(t[62:70]),
            'carteira': int(t[82:85]),
            'valor_documento': _parse_currency(t[152:165]),
            'valor_tarifa': _parse_currency(t[175:188]),
            'valor_descontos': _parse_currency(t[240:253]),
            'valor_credito': _parse_currency(t[253:266]),
            'valor_juros': _parse_currency(t[266:279]),
            'data_vencimento': _parse_date(t[146:152]),
            'data_ocorrencia': _parse_date(t[110:116]),
            'data_credito': _parse_date(t[295:301]),
        }

    @staticmethod
    def _parse_trailer(t):
        """ Get trailer info. """
        return {
            'registros_total': int(t[212:220]),
            'valor_total_documento': _parse_currency(t[220:234]),
        }


class CNABWriter(object):

    """ Write CNAB 240 files.

    This writer is designed to work with CNAB 400 standard files
    """

    def __init__(self, banco):  # noqa
        self.id_banco = banco.id
        self.nome_banco = banco.nome
        self.versao_header = banco.versao_cnab_header
        self.versao_lote = banco.versao_cnab_lote

    def write_header(self, info):
        """ Write header record.

        This writes the 400 bytes record for the header.
        """
        header = "01{}01{}{0:04d}00{0:05d}{0:01d}{}{}{0:03d}{}{}{}{0:06}"
        header = header.format(
            info.remessa.rjust(7), info.cobranca.rjust(15),
            info.agencia, info.conta, info.dac, ''.rjust(8),
            info.nome_empr.rjust(30), self.id_banco, self.nome_banco.rjust(30),
            info.tt.strftime("%d%m%y"), ''.rjust(294), info.seq
        )

        assert len(header) == 240
        return header

    def write_record(self, boleto, info):
        """ Based on a boleto, write a record.

        Give me an already built boleto to write the record.
        """
        header = '1{0:02d}{0:14d}{0:04d}00{0:05d}{0:01d}{}{}{0:08d}{}{0:03d}'
        header += '{0:08d}{0:01d}{}{}{0:02d}{0:06d}{}{0:08d}{0:01d}{}{}{0:02d}'
        header += '{0:06d}{}{0:08d}{}{0:06d}{0:13d}{0:03d}{0:04d}{0:01d}{0:02d}'
        header += '{0:13d}{}{0:13d}{0:13d}{0:13d}{0:13d}{0:13d}{0:13d}{}{}{}'
        header += '{0:04d}{}{0:13d}{}{}{}{}{}{0:06d}'

        header = header.format(
            info.tipo_documento, boleto.cedente_documento,

