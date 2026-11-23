"""Ponte entre a arte (imagens Pillow) e o Tkinter, com cache.

O Tkinter exige que as PhotoImage continuem referenciadas enquanto estão
na tela; guardá-las aqui resolve isso e evita renderizar duas vezes.
"""
import math
from typing import Dict, List, Optional, Tuple

from PIL import Image, ImageOps, ImageTk

from ..dominio.arquipelago import Ilha
from .arte import RenderizadorDeDragao, RenderizadorDeIlhaFlutuante, SpriteIlha, renderizar_ceu
from .arte.pincel import REAMOSTRAGEM


class BibliotecaDeSprites:
    LIMITE_CACHE_ILHAS = 400
    PASSO_INCLINACAO = 5
    INCLINACAO_MAXIMA = 35
    QUADROS_POR_BATIDA = 2       # quadros de animação por quadro do sprite

    def __init__(self) -> None:
        self._renderizador_ilha = RenderizadorDeIlhaFlutuante()
        self._renderizador_dragao = RenderizadorDeDragao()
        self._ilhas: Dict[tuple, Tuple[ImageTk.PhotoImage, SpriteIlha]] = {}
        self._dragao: Dict[tuple, ImageTk.PhotoImage] = {}
        self._quadros_dragao: Optional[List[Image.Image]] = None
        self._ceu: Optional[Tuple[Tuple[int, int], ImageTk.PhotoImage]] = None

    def ceu(self, largura: int, altura: int) -> ImageTk.PhotoImage:
        if self._ceu is None or self._ceu[0] != (largura, altura):
            self._ceu = ((largura, altura), ImageTk.PhotoImage(renderizar_ceu(largura, altura)))
        return self._ceu[1]

    def ilha(self, ilha: Ilha, escala: float) -> Tuple[ImageTk.PhotoImage, SpriteIlha]:
        chave = (ilha.nome, round(ilha.x), round(ilha.y), ilha.elemento, escala)
        if chave not in self._ilhas:
            if len(self._ilhas) >= self.LIMITE_CACHE_ILHAS:
                self._ilhas.clear()
            sprite = self._renderizador_ilha.renderizar(ilha, escala)
            self._ilhas[chave] = (ImageTk.PhotoImage(sprite.imagem), sprite)
        return self._ilhas[chave]

    def dragao(self, quadro: int, angulo: float) -> ImageTk.PhotoImage:
        """Quadro do bater de asas, espelhado e inclinado na direção do voo."""
        if self._quadros_dragao is None:
            self._quadros_dragao = self._renderizador_dragao.quadros()
        indice = (quadro // self.QUADROS_POR_BATIDA) % len(self._quadros_dragao)

        dx, dy = math.cos(angulo), math.sin(angulo)
        espelhar = dx < 0
        inclinacao = math.degrees(math.atan2(dy, abs(dx)))
        inclinacao = max(-self.INCLINACAO_MAXIMA, min(self.INCLINACAO_MAXIMA, inclinacao))
        inclinacao = round(inclinacao / self.PASSO_INCLINACAO) * self.PASSO_INCLINACAO

        chave = (indice, espelhar, inclinacao)
        if chave not in self._dragao:
            imagem = self._quadros_dragao[indice]
            if espelhar:
                imagem = ImageOps.mirror(imagem)
            giro = inclinacao if espelhar else -inclinacao
            imagem = imagem.rotate(giro, resample=REAMOSTRAGEM.BICUBIC, expand=True)
            self._dragao[chave] = ImageTk.PhotoImage(imagem)
        return self._dragao[chave]
