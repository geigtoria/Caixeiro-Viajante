"""Desenho vetorial do dragão, rotacionado na direção do voo."""
import math
import tkinter as tk
from typing import List, Sequence, Tuple

from .tema import COR, COR_DRAGAO

Forma = Sequence[Tuple[float, float]]


def girar(pontos: Forma, angulo: float, cx: float, cy: float) -> List[float]:
    """Rotaciona uma forma local e a posiciona em (cx, cy)."""
    c, s = math.cos(angulo), math.sin(angulo)
    saida: List[float] = []
    for x, y in pontos:
        saida += [cx + x * c - y * s, cy + x * s + y * c]
    return saida


def espelhar(forma: Forma) -> List[Tuple[float, float]]:
    return [(x, -y) for x, y in forma]


class SpriteDragao:
    """Formas definidas com o dragão olhando para +x, centro em (0, 0)."""

    CAUDA = [(-14, -3), (-30, -2), (-40, -9), (-37, 0), (-40, 9), (-30, 2), (-14, 3)]
    CORPO = [(-18, 0), (-8, -8), (10, -7), (18, 0), (10, 7), (-8, 8)]
    BARRIGA = [(-10, 0), (0, -3), (12, 0), (0, 3)]
    CABECA = [(14, -6), (25, -5), (31, 0), (25, 5), (14, 6)]
    CHIFRE = [(18, -5), (15, -13), (22, -6)]
    CHAMA = [(31, 0), (44, -6), (40, 0), (48, 0), (40, 2), (44, 6)]

    def __init__(self, tag: str = "dragao") -> None:
        self.tag = tag

    @staticmethod
    def _asa(abertura: float) -> List[Tuple[float, float]]:
        return [(-6, -4), (-14, -30 * abertura), (-2, -22 * abertura),
                (6, -34 * abertura), (10, -5)]

    def desenhar(self, canvas: tk.Canvas, x: float, y: float, angulo: float, quadro: int) -> None:
        t = self.tag
        cor = COR_DRAGAO
        abertura = 0.35 + 0.65 * abs(math.sin(quadro * 0.22))

        canvas.create_oval(x - 16, y + 14, x + 16, y + 22, fill=COR["sombra"], outline="", tags=t)

        asa = self._asa(abertura)
        for forma in (asa, espelhar(asa)):
            canvas.create_polygon(girar(forma, angulo, x, y), fill=cor["asa"],
                                  outline=cor["contorno"], width=2, tags=t)

        canvas.create_polygon(girar(self.CAUDA, angulo, x, y), fill=cor["corpo"],
                              outline=cor["contorno"], tags=t)
        for forma in (self.CORPO, self.CABECA):
            canvas.create_polygon(girar(forma, angulo, x, y), fill=cor["corpo"],
                                  outline=cor["contorno"], width=2, tags=t)
        canvas.create_polygon(girar(self.BARRIGA, angulo, x, y), fill=cor["barriga"],
                              outline="", tags=t)
        for forma in (self.CHIFRE, espelhar(self.CHIFRE)):
            canvas.create_polygon(girar(forma, angulo, x, y), fill=COR["ouro"],
                                  outline="", tags=t)

        for lado in (-1, 1):
            ox, oy = girar([(24, 2.5 * lado)], angulo, x, y)
            canvas.create_oval(ox - 1.8, oy - 1.8, ox + 1.8, oy + 1.8,
                               fill=cor["olho"], outline="", tags=t)

        if quadro % 30 < 8:   # baforada de fogo
            canvas.create_polygon(girar(self.CHAMA, angulo, x, y), fill=cor["chama"],
                                  outline=cor["chama_borda"], tags=t)
