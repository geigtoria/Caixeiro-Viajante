"""Dragão-mensageiro visto de lado, olhando para a direita.

Gera uma sequência de quadros com o bater de asas; quem usa espelha e
inclina o quadro conforme a direção do voo.
"""
import math
from typing import List, Sequence

from PIL import Image

from .paleta import DRAGAO as C
from .pincel import Ponto, Tela, faixa_afilada, suavizar

LARGURA, ALTURA = 150, 130
DESLOCAMENTO = (13, 19)        # leva o centro do corpo ao centro da imagem


class RenderizadorDeDragao:
    QUADROS = 12

    def __init__(self, escala: float = 0.72) -> None:
        self.escala = escala

    def quadros(self) -> List[Image.Image]:
        return [self.quadro(2 * math.pi * i / self.QUADROS) for i in range(self.QUADROS)]

    # ------------------------------------------------------------ apoio
    def _p(self, pontos: Sequence[Ponto]) -> List[Ponto]:
        ox, oy = DESLOCAMENTO
        return [(x + ox, y + oy + self._balanco) for x, y in pontos]

    def _xy(self, x: float, y: float) -> Ponto:
        return self._p([(x, y)])[0]

    # ------------------------------------------------------------ quadro
    def quadro(self, fase: float) -> Image.Image:
        self._balanco = 1.6 * math.sin(fase + math.pi / 2)
        tela = Tela(LARGURA, ALTURA)
        angulo_asa = -8 + 44 * math.sin(fase)          # positivo = asa mais erguida

        self._asa(tela, -8 + 44 * math.sin(fase - 0.5) - 14, traseira=True)
        self._cauda(tela, fase)
        self._perna(tela, [(45, 54), (54, 55), (50, 63), (43, 65), (40, 60)], escura=True)
        mascara_corpo = self._corpo(tela)
        self._barriga(tela, mascara_corpo)
        self._perna(tela, [(70, 55), (79, 54), (77, 63), (70, 66), (66, 62)])
        self._espinhos(tela)
        self._cabeca(tela)
        self._asa(tela, angulo_asa, traseira=False)
        return tela.finalizar(self.escala)

    # ------------------------------------------------------------ partes
    def _corpo(self, tela):
        contorno = self._p(suavizar([
            (38, 42), (50, 33), (64, 30), (74, 30), (80, 22), (86, 15), (96, 12), (105, 15),
            (111, 22), (115, 29), (112, 35), (102, 38), (92, 38), (84, 42), (82, 50),
            (76, 58), (62, 62), (48, 60), (38, 54)], passos=8))
        m = tela.gradiente_poligono(contorno, C["corpo_claro"], C["corpo_escuro"], angulo=0)
        tela.luz_de_borda(m, (255, 255, 255), 3, 4, desfoque=2.5, opacidade=0.45)
        tela.luz_de_borda(m, (0, 40, 40), 0, -4, desfoque=2, opacidade=0.4)
        for x, y, r in ((56, 40, 2.2), (66, 37, 1.8), (48, 45, 1.6), (88, 24, 1.5)):   # escamas
            tela.elipse(*self._xy(x, y), r, r * 0.8, (255, 255, 255, 45))
        tela.linha(contorno + [contorno[0]], C["contorno"], 1.5)
        return m

    def _barriga(self, tela, mascara_corpo):
        barriga = self._p(suavizar([(86, 40), (83, 50), (76, 58), (62, 62), (48, 60),
                                    (52, 55), (64, 55), (74, 50), (79, 42)], passos=6))
        m = tela.gradiente_poligono(barriga, C["barriga_clara"], C["barriga_escura"], angulo=0,
                                    recorte=mascara_corpo)
        for t in (0.2, 0.38, 0.56, 0.74):                     # placas da barriga
            x = 82 - t * 34
            tela.linha(self._p([(x + 4, 44 + t * 12), (x - 1, 52 + t * 8)]),
                       (190, 100, 40, 140), 0.9, recorte=m)

    def _cauda(self, tela, fase):
        centro = []
        base = [(42, 50), (31, 57), (21, 57), (13, 50), (11, 40), (16, 32)]
        for i, (x, y) in enumerate(base):
            centro.append((x, y + math.sin(fase + i * 0.7) * 1.6 * i / len(base)))
        centro = self._p(suavizar(centro, fechado=False, passos=5))
        faixa = faixa_afilada(centro, 11, 3)
        tela.gradiente_poligono(faixa, C["corpo_claro"], C["corpo_escuro"], angulo=0,
                                contorno=C["contorno"], largura=1.3)
        tx, ty = centro[-1]
        ponta = suavizar([(tx, ty + 2), (tx - 8, ty - 2), (tx - 3, ty - 9),
                          (tx + 2, ty - 12), (tx + 6, ty - 4)], passos=4)
        tela.gradiente_poligono(ponta, C["espinho_claro"], C["espinho_escuro"], angulo=0,
                                contorno="#a8461d", largura=1)

    def _perna(self, tela, pontos, escura=False):
        perna = self._p(suavizar(pontos, passos=5))
        claro = C["corpo_escuro"] if escura else C["corpo_claro"]
        tela.gradiente_poligono(perna, claro, "#0f5f55", angulo=0,
                                contorno=C["contorno"], largura=1.2)
        x, y = self._xy(sum(p[0] for p in pontos) / len(pontos), max(p[1] for p in pontos))
        for dx in (-3.5, 0, 3.5):                             # garras
            tela.elipse(x + dx, y - 0.5, 1.4, 1.8, C["chifre_claro"], contorno="#9c7a4c", largura=0.5)

    def _espinhos(self, tela):
        for x, y, h in ((42, 39, 5), (51, 33, 6), (60, 30.5, 6.5), (69, 29.5, 6), (78, 24, 5.5),
                        (84, 17, 5)):
            px, py = self._xy(x, y)
            tela.gradiente_poligono([(px - 3.2, py + 1), (px - 1.5, py - h), (px + 3.2, py + 1)],
                                    C["espinho_claro"], C["espinho_escuro"], angulo=0,
                                    contorno="#a8461d", largura=0.7)

    def _cabeca(self, tela):
        for pontos in ([(97, 13), (95, 6), (91, 1), (98, 5), (102, 12)],          # chifres
                       [(89, 15), (85, 7), (79, 2), (86, 5), (94, 12)]):
            tela.gradiente_poligono(self._p(suavizar(pontos, passos=4)), C["chifre_claro"],
                                    C["chifre_escuro"], angulo=0, contorno="#8a6a3c", largura=0.8)
        crista = self._p(suavizar([(84, 19), (75, 16), (78, 22), (73, 25), (83, 25)], passos=4))
        tela.gradiente_poligono(crista, C["espinho_claro"], C["espinho_escuro"], angulo=90,
                                contorno="#a8461d", largura=0.7)

        ex, ey = self._xy(100, 23)                              # olho
        tela.elipse(ex, ey, 5.4, 6.2, "#ffffff", contorno=C["contorno"], largura=0.9)
        tela.gradiente_elipse(ex + 1.2, ey + 0.6, 3.7, 4.6, C["iris_clara"], C["iris_escura"], angulo=0)
        tela.elipse(ex + 1.6, ey + 0.8, 1.7, 3.1, "#1a1208")
        tela.elipse(ex + 0.2, ey - 1.6, 1.4, 1.4, "#ffffff")
        tela.elipse(ex + 2.6, ey + 2.6, 0.6, 0.6, "#ffffff")
        tela.linha(self._p(suavizar([(94, 18.5), (99, 15.8), (105, 17.5)], fechado=False, passos=4)),
                   C["contorno"], 1.3)

        tela.elipse(*self._xy(111.5, 26.5), 1.0, 0.8, "#0d3b35")          # narina
        tela.linha(self._p(suavizar([(113.5, 33), (108, 35.2), (101, 34.6)], fechado=False,
                                    passos=4)), C["contorno"], 1.0)
        fx, fy = self._xy(107, 35)
        tela.poligono([(fx - 1.2, fy), (fx + 1.2, fy), (fx, fy + 2.4)], "#fff8ea")
        tela.brilho(*self._xy(105, 31), 3.2, 2, (255, 140, 150), 0.45, 1)  # bochecha

    def _asa(self, tela, angulo_graus, traseira):
        ombro = (64, 33)
        ossos = {"cotovelo": (-8, -22), "d1": (-30, -38), "d2": (-42, -24),
                 "d3": (-38, -8), "d4": (-22, 2)}
        a = math.radians(angulo_graus)
        achatar = 0.72 + 0.28 * abs(math.cos(a + 0.3))

        def girar(dx, dy):
            x = dx * math.cos(a) + dy * math.sin(a)
            y = -dx * math.sin(a) + dy * math.cos(a)
            return (ombro[0] + x, ombro[1] + y * achatar)

        deslocamento = (10, -3) if traseira else (0, 0)
        reduz = 0.85 if traseira else 1.0
        p = {k: girar(dx * reduz, dy * reduz) for k, (dx, dy) in ossos.items()}
        p = {k: (x + deslocamento[0], y + deslocamento[1]) for k, (x, y) in p.items()}
        o = (ombro[0] + deslocamento[0], ombro[1] + deslocamento[1])

        def recorte_entre(a_, b_):                           # membrana côncava entre dedos
            mx, my = (a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2
            return (mx + (o[0] - mx) * 0.2, my + (o[1] - my) * 0.2)

        membrana = [o, p["cotovelo"], p["d1"], recorte_entre(p["d1"], p["d2"]), p["d2"],
                    recorte_entre(p["d2"], p["d3"]), p["d3"], recorte_entre(p["d3"], p["d4"]),
                    p["d4"], (o[0] - 4, o[1] + 4)]
        membrana = self._p(suavizar(membrana, passos=4))
        clara = C["asa_tras_clara"] if traseira else C["asa_clara"]
        escura = C["asa_tras_escura"] if traseira else C["asa_escura"]
        m = tela.gradiente_poligono(membrana, clara, escura, angulo=40)
        tela.luz_de_borda(m, (255, 255, 255), 2, 2, desfoque=1.5, opacidade=0.3)
        tela.linha(membrana + [membrana[0]], "#8a2c3a", 0.9)

        osso = C["osso"] if not traseira else "#0d4f47"
        braco = self._p([o, p["cotovelo"], p["d1"]])
        tela.linha(braco, osso, 2.4)
        for dedo in ("d2", "d3", "d4"):
            tela.linha(self._p([p["cotovelo"], p[dedo]]), osso, 1.3)
        cx, cy = self._p([p["cotovelo"]])[0]
        tela.elipse(cx, cy, 1.8, 1.8, osso)
        garra = self._p([p["d1"]])[0]
        tela.poligono([(garra[0] - 1.2, garra[1]), (garra[0] + 1.2, garra[1]),
                       (garra[0] - 1.5, garra[1] - 3)], C["chifre_claro"])
