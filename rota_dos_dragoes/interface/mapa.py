import tkinter as tk
from typing import Iterable, Optional, Set, Tuple

from ..dominio.arquipelago import Arquipelago, Ilha
from ..dominio.geometria import Ponto
from ..dominio.rota import Rota
from ..util.formatacao import formatar_numero
from .sprites import BibliotecaDeSprites
from .tema import (ALTURA_MAPA, COR, FONTE_ROTULO, FONTE_SELO,
                   LARGURA_MAPA)

Trecho = Tuple[float, float, float, float]


class MapaView(tk.Canvas):
    """Desenha o céu, as ilhas flutuantes, a rota e o dragão. Só exibe estado."""

    TAG_VOO = "voo"
    LIMITE_PARA_NOMES = 30     # acima disso só o ninho mostra o nome
    ALTURA_DO_VOO = 8          # o dragão voa um pouco acima do topo das ilhas

    def __init__(self, pai: tk.Misc) -> None:
        super().__init__(pai, width=LARGURA_MAPA, height=ALTURA_MAPA, highlightthickness=0,
                         bg=COR["ceu"])
        self.largura, self.altura = LARGURA_MAPA, ALTURA_MAPA
        self._sprites = BibliotecaDeSprites()

    # ------------------------------------------------------- cena completa
    def renderizar(self, arquipelago: Arquipelago, grafo, rota: Optional[Rota],
                   rastro: Iterable[Trecho], visitadas: Set[int]) -> None:
        self.delete("all")
        self.create_image(0, 0, image=self._sprites.ceu(self.largura, self.altura), anchor="nw")
        self._desenhar_arestas(arquipelago, grafo)
        if rota:
            self._desenhar_rota(arquipelago, rota)
        for trecho in rastro:
            self.create_line(*trecho, fill=COR["rastro"], width=3)

        escala = self._escala_para(len(arquipelago))
        mostrar_nomes = len(arquipelago) <= self.LIMITE_PARA_NOMES
        ordem = rota.posicoes_na_rota() if rota else {}
        # de trás para a frente: ilhas mais abaixo ficam por cima
        for indice in sorted(range(len(arquipelago)), key=lambda i: arquipelago[i].y):
            ilha = arquipelago[indice]
            self._desenhar_ilha(ilha, ordem.get(indice), indice in visitadas, escala,
                                mostrar_nome=mostrar_nomes or ilha.eh_ninho)

    def _desenhar_arestas(self, arquipelago: Arquipelago, grafo) -> None:
        pontos = dict(zip(grafo, arquipelago.posicoes()))
        for origem, arestas in grafo.items():
            x1, y1 = pontos[origem]
            for aresta in arestas:
                destino = aresta["vertex"]
                if origem >= destino:
                    continue
                x2, y2 = pontos[destino]
                self.create_line(x1, y1, x2, y2, fill="#8693ac")
                self.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 10,
                                 text=formatar_numero(aresta["weight"], 0),
                                 fill="#ffffff", font=FONTE_SELO)

    @staticmethod
    def _escala_para(quantidade: int) -> float:
        """Ilhas menores quando o arquipélago fica lotado."""
        if quantidade <= 12:
            return 1.0
        if quantidade <= 20:
            return 0.8
        if quantidade <= 30:
            return 0.62
        return 0.48

    # ------------------------------------------------------- camada de voo
    def desenhar_voo(self, origem: Ponto, atual: Ponto, angulo: float, quadro: int) -> None:
        self.apagar_voo()
        if origem != atual:
            self.create_line(*origem, *atual, fill=COR["rastro"], width=3, tags=self.TAG_VOO)
        imagem = self._sprites.dragao(quadro, angulo)
        self.create_image(atual[0], atual[1] - self.ALTURA_DO_VOO, image=imagem, tags=self.TAG_VOO)

    def apagar_voo(self) -> None:
        self.delete(self.TAG_VOO)

    # ------------------------------------------------------------ partes
    def _desenhar_rota(self, arquipelago: Arquipelago, rota: Rota) -> None:
        pontos = [arquipelago[i].posicao for i in rota.ordem]
        for i, (x1, y1) in enumerate(pontos):
            x2, y2 = pontos[(i + 1) % len(pontos)]
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.create_line(x1, y1, mx, my, fill=COR["rota"], width=2,
                             dash=(6, 4), arrow="last", arrowshape=(10, 12, 4))
            self.create_line(mx, my, x2, y2, fill=COR["rota"], width=2, dash=(6, 4))

    def _desenhar_ilha(self, ilha: Ilha, posicao: Optional[int], visitada: bool,
                       escala: float, mostrar_nome: bool = True) -> None:
        x, y = ilha.posicao
        imagem, sprite = self._sprites.ilha(ilha, escala)
        ax, ay = sprite.ancora
        self.create_image(x - ax, y - ay, image=imagem, anchor="nw")
        W, H = sprite.meia_largura, sprite.meia_altura

        if visitada:
            self.create_oval(x - W * 1.12, y - H * 1.2, x + W * 1.12, y + H * 1.3,
                             outline=COR["ouro"], width=2, dash=(6, 3))

        if mostrar_nome:
            rotulo_y = y + sprite.base * 0.62
            self.create_text(x + 1, rotulo_y + 1, text=ilha.nome, fill="#000000", font=FONTE_ROTULO)
            self.create_text(x, rotulo_y, text=ilha.nome, fill="#ffffff", font=FONTE_ROTULO)

        if posicao is not None and not ilha.eh_ninho:
            bx, by = x + W * 0.95, y - H * 1.05
            self.create_oval(bx - 9, by - 9, bx + 9, by + 9, fill=COR["painel"], outline=COR["ouro"])
            self.create_text(bx, by, text=str(posicao), fill=COR["ouro"], font=FONTE_SELO)
