import math
import tkinter as tk
from typing import Callable, List, Optional, Tuple

from ..dominio.geometria import Ponto

AoQuadro = Callable[[Ponto, Ponto, float, int], None]
AoChegar = Callable[[int, Tuple[float, float, float, float]], None]


class AnimadorDeVoo:
    """Move um ponto ao longo de uma sequência de pontos usando ``after``.

    Não desenha nada: avisa a cada quadro e a cada chegada por callbacks,
    deixando o desenho para a view e o estado para o controlador.
    """

    INTERVALO_MS = 16
    PIXELS_POR_NIVEL = 1.4

    def __init__(self, widget: tk.Misc, obter_velocidade: Callable[[], int],
                 ao_quadro: AoQuadro, ao_chegar: AoChegar,
                 ao_terminar: Callable[[], None]) -> None:
        self._widget = widget
        self._obter_velocidade = obter_velocidade
        self._ao_quadro = ao_quadro
        self._ao_chegar = ao_chegar
        self._ao_terminar = ao_terminar
        self._tarefa: Optional[str] = None
        self._pontos: List[Ponto] = []
        self._segmento = 0
        self._progresso = 0.0
        self._quadro = 0

    @property
    def ativo(self) -> bool:
        return self._tarefa is not None

    def iniciar(self, pontos: List[Ponto]) -> None:
        self.parar()
        self._pontos = pontos
        self._segmento, self._progresso, self._quadro = 0, 0.0, 0
        self._passo()

    def parar(self) -> bool:
        """Interrompe o voo. Retorna True se havia um voo em andamento."""
        if self._tarefa is None:
            return False
        self._widget.after_cancel(self._tarefa)
        self._tarefa = None
        return True

    def _passo(self) -> None:
        self._tarefa = None
        if self._segmento >= len(self._pontos) - 1:
            self._ao_terminar()
            return

        origem = self._pontos[self._segmento]
        destino = self._pontos[self._segmento + 1]
        comprimento = max(math.dist(origem, destino), 1e-6)
        self._progresso += self._obter_velocidade() * self.PIXELS_POR_NIVEL / comprimento
        self._quadro += 1
        angulo = math.atan2(destino[1] - origem[1], destino[0] - origem[0])

        if self._progresso >= 1:
            self._segmento += 1
            self._progresso = 0.0
            self._ao_chegar(self._segmento, (*origem, *destino))
            origem = atual = destino
        else:
            t = self._progresso
            atual = (origem[0] + (destino[0] - origem[0]) * t,
                     origem[1] + (destino[1] - origem[1]) * t)

        self._ao_quadro(origem, atual, angulo, self._quadro)
        self._tarefa = self._widget.after(self.INTERVALO_MS, self._passo)
