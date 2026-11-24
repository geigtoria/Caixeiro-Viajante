"""A arte é gerada com Pillow, sem janela; dá para testar sem Tkinter."""
import unittest

from rota_dos_dragoes.dominio import Elemento, Ilha
from rota_dos_dragoes.interface.arte import (RenderizadorDeDragao, RenderizadorDeIlhaFlutuante,
                                             renderizar_ceu)


class TestArte(unittest.TestCase):
    def test_cada_habitat_gera_sprite_visivel(self):
        renderizador = RenderizadorDeIlhaFlutuante()
        for elemento in Elemento:
            with self.subTest(elemento=elemento):
                sprite = renderizador.renderizar(Ilha(100, 100, f"Ilha {elemento.value}", elemento))
                self.assertEqual(sprite.imagem.mode, "RGBA")
                self.assertIsNotNone(sprite.imagem.getchannel("A").getbbox())
                ax, ay = sprite.ancora
                self.assertTrue(0 < ax < sprite.imagem.width and 0 < ay < sprite.imagem.height)

    def test_mesma_ilha_gera_mesma_imagem(self):
        renderizador = RenderizadorDeIlhaFlutuante()
        ilha = Ilha(321, 123, "Ilha Coral", Elemento.MAR)
        a = renderizador.renderizar(ilha).imagem
        b = renderizador.renderizar(ilha).imagem
        self.assertEqual(a.tobytes(), b.tobytes())

    def test_escala_reduz_o_sprite(self):
        renderizador = RenderizadorDeIlhaFlutuante()
        ilha = Ilha(50, 50, "Ilha Geada", Elemento.GELO)
        grande = renderizador.renderizar(ilha, 1.0).imagem
        pequena = renderizador.renderizar(ilha, 0.5).imagem
        self.assertLess(pequena.width, grande.width)

    def test_dragao_tem_todos_os_quadros_do_mesmo_tamanho(self):
        quadros = RenderizadorDeDragao().quadros()
        self.assertEqual(len(quadros), RenderizadorDeDragao.QUADROS)
        self.assertEqual(len({q.size for q in quadros}), 1)
        self.assertNotEqual(quadros[0].tobytes(), quadros[3].tobytes())   # as asas se movem

    def test_ceu_tem_o_tamanho_pedido(self):
        self.assertEqual(renderizar_ceu(200, 100).size, (200, 100))


if __name__ == "__main__":
    unittest.main()
