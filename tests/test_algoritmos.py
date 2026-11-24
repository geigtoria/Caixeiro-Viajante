import unittest

from rota_dos_dragoes.algoritmos import ALGORITMOS
from rota_dos_dragoes.dominio.grafos import GRAFOS, grafo_complexo, grafo_simples
from rota_dos_dragoes.servicos import PlanejadorDeRota, ilhas_do_grafo
from rota_dos_dragoes.servicos.planejador import ErroDePlanejamento


class TestAlgoritmos(unittest.TestCase):
    def test_rotas_usam_somente_arestas_do_grafo(self):
        planejador = PlanejadorDeRota()
        for grafo in GRAFOS.values():
            vertices = list(grafo)
            pesos = {(v, a["vertex"]): a["weight"] for v in grafo for a in grafo[v]}
            for algoritmo in ALGORITMOS.values():
                if not algoritmo.suporta(len(grafo)):
                    continue
                with self.subTest(algoritmo=algoritmo.nome, tamanho=len(grafo)):
                    rota = planejador.planejar(grafo, algoritmo)
                    caminho = [vertices[i] for i in rota.ordem]
                    self.assertEqual(caminho[0], 1)
                    self.assertEqual(set(caminho), set(vertices))
                    fechada = caminho + [1]
                    self.assertEqual(rota.comprimento,
                                     sum(pesos[u, v] for u, v in zip(fechada, fechada[1:])))

    def test_algoritmos_exatos_concordam_no_grafo_simples(self):
        grafo = GRAFOS["5 pontos"]
        planejador = PlanejadorDeRota()
        for nome in ("Força Bruta", "Dijkstra com controle de visitas"):
            self.assertEqual(planejador.planejar(grafo, ALGORITMOS[nome]).comprimento, 15)

    def test_catalogo_tem_todos_os_tamanhos_e_preserva_os_grafos_da_aula(self):
        self.assertEqual({nome: len(grafo) for nome, grafo in GRAFOS.items()},
                         {f"{n} pontos": n for n in range(5, 19)})
        self.assertIs(GRAFOS["5 pontos"], grafo_simples)
        self.assertIs(GRAFOS["18 pontos"], grafo_complexo)

    def test_forca_bruta_respeita_limite_no_grafo_de_18_pontos(self):
        with self.assertRaises(ErroDePlanejamento):
            PlanejadorDeRota().planejar(GRAFOS["18 pontos"], ALGORITMOS["Força Bruta"])

    def test_layout_mantem_ordem_dos_vertices(self):
        for grafo in GRAFOS.values():
            ilhas = ilhas_do_grafo(grafo, 820, 620)
            self.assertTrue(ilhas[0].eh_ninho)
            self.assertEqual([i.nome for i in ilhas[1:]], [f"Ilha {v}" for v in list(grafo)[1:]])
