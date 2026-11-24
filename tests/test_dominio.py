import unittest

from rota_dos_dragoes.dominio import NOME_NINHO, Arquipelago, Elemento, Ilha


def ilha(x, y, nome="Ilha", elemento=Elemento.FOGO):
    return Ilha(x, y, nome, elemento)


class TestArquipelago(unittest.TestCase):
    def test_primeira_ilha_vira_ninho(self):
        a = Arquipelago()
        a.adicionar(ilha(10, 10, "Ilha Brasa"))
        self.assertTrue(a[0].eh_ninho)
        self.assertEqual(a[0].nome, NOME_NINHO)

    def test_remover_ninho_promove_a_proxima(self):
        a = Arquipelago()
        a.substituir([ilha(0, 0), ilha(50, 50, "Ilha Coral", Elemento.MAR)])
        a.remover(0)
        self.assertEqual(len(a), 1)
        self.assertTrue(a[0].eh_ninho)

    def test_observador_e_notificado(self):
        a = Arquipelago()
        chamadas = []
        a.inscrever(lambda: chamadas.append(1))
        a.adicionar(ilha(0, 0))
        a.adicionar(ilha(100, 0))
        a.remover(1)
        a.limpar()
        self.assertEqual(len(chamadas), 4)

    def test_indice_mais_proximo_respeita_raio(self):
        a = Arquipelago()
        a.substituir([ilha(0, 0), ilha(100, 100)])
        self.assertEqual(a.indice_mais_proximo(95, 98, 10), 1)
        self.assertIsNone(a.indice_mais_proximo(50, 50, 10))
