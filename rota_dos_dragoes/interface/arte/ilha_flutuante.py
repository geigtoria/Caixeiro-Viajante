"""Ilhas flutuantes: topo gramado, penhasco rochoso com estratos, cipós,
cachoeira e um cenário próprio de cada habitat.

A aparência nasce de uma semente tirada do nome e da posição da ilha, então
a mesma ilha é sempre desenhada igual.
"""
import math
import random
import zlib
from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple

from PIL import Image

from ...dominio.arquipelago import Ilha
from ...dominio.elementos import Elemento
from .paleta import ROCHAS, TERRENO_DO_ELEMENTO, TERRENOS
from .pincel import Ponto, Tela, faixa_afilada, suavizar


@dataclass(frozen=True)
class SpriteIlha:
    imagem: Image.Image
    ancora: Tuple[float, float]   # pixel da imagem que corresponde à posição da ilha
    meia_largura: float           # do topo
    meia_altura: float            # do topo
    base: float                   # distância da âncora até a ponta do penhasco


def _ruido_suave(rng: random.Random, n: int, passo: int = 6) -> List[float]:
    controles = [rng.uniform(-1, 1) for _ in range(n // passo + 2)]
    saida = []
    for i in range(n):
        k, t = divmod(i, passo)
        t = t / passo
        t = (1 - math.cos(t * math.pi)) / 2
        saida.append(controles[k] * (1 - t) + controles[k + 1] * t)
    return saida


class RenderizadorDeIlhaFlutuante:
    PONTOS_CONTORNO = 72

    def __init__(self) -> None:
        self._cenarios: Dict[Elemento, Callable] = {
            Elemento.NINHO: self._ninho,
            Elemento.FOGO: self._vulcao,
            Elemento.GELO: self._geleira,
            Elemento.NATUREZA: self._floresta,
            Elemento.TERRA: self._canion,
            Elemento.TEMPESTADE: self._tempestade,
            Elemento.MAR: self._lagoa,
        }

    # ================================================================ geral
    def renderizar(self, ilha: Ilha, escala: float = 1.0) -> SpriteIlha:
        chave = repr((ilha.nome, round(ilha.x), round(ilha.y), ilha.elemento.value))
        rng = random.Random(zlib.crc32(chave.encode()))

        W = (rng.uniform(41, 45) if ilha.eh_ninho else rng.uniform(33, 39)) * escala
        H = W * 0.5
        D = W * rng.uniform(0.95, 1.2)
        margem_lado, margem_topo, margem_base = W * 0.3, W * 1.55, W * 0.45

        largura = 2 * W + 2 * margem_lado
        altura = margem_topo + 2 * H + D + margem_base
        cx, cy = margem_lado + W, margem_topo + H
        tela = Tela(largura, altura)

        nome_terreno, nome_rocha = TERRENO_DO_ELEMENTO[ilha.elemento]
        terreno, rocha = TERRENOS[nome_terreno], ROCHAS[nome_rocha]

        contorno = self._contorno(rng, cx, cy, W, H)
        frente = contorno[: self.PONTOS_CONTORNO // 2 + 1]
        fundo, profundidade = self._fundo_do_penhasco(rng, frente, cx, W, H, D)

        mascara_penhasco = self._penhasco(tela, rng, frente, fundo, rocha, H)

        cachoeira = ilha.elemento is Elemento.MAR or (
            ilha.elemento is Elemento.NATUREZA and rng.random() < 0.6)
        if cachoeira:
            ponto_queda = frente[rng.randint(len(frente) * 2 // 5, len(frente) * 3 // 5)]
            self._queda_dagua(tela, ponto_queda, W, H, D)

        mascara_topo = self._topo(tela, contorno, terreno, H)
        self._beirada(tela, rng, frente, terreno, H)
        if nome_terreno in ("grama", "tormenta"):
            self._cipos(tela, rng, frente, cx, W, H, D, mascara_penhasco)
        if cachoeira:
            self._riacho(tela, (cx + (ponto_queda[0] - cx) * 0.25, cy - H * 0.25), ponto_queda, W)

        self._detalhes_do_chao(tela, rng, cx, cy, W, H, nome_terreno)
        self._cenarios[ilha.elemento](tela, rng, cx, cy - H * 0.05, W)

        return SpriteIlha(tela.finalizar(), (cx, cy), W, H, H + profundidade)

    # ============================================================== formas
    def _contorno(self, rng, cx, cy, W, H) -> List[Ponto]:
        harmonicos = [(k, rng.uniform(0.02, 0.07), rng.uniform(0, 2 * math.pi)) for k in range(2, 7)]
        pontos = []
        for i in range(self.PONTOS_CONTORNO):
            t = 2 * math.pi * i / self.PONTOS_CONTORNO
            r = 1 + sum(a * math.sin(k * t + f) for k, a, f in harmonicos)
            pontos.append((cx + math.cos(t) * W * r, cy + math.sin(t) * H * r))
        return pontos

    def _fundo_do_penhasco(self, rng, frente, cx, W, H, D):
        ruido = _ruido_suave(rng, len(frente))
        centro_pico = rng.uniform(-0.25, 0.25)
        fundo, maior = [], 0.0
        for k, (x, y) in enumerate(frente):
            u = max(-1.0, min(1.0, (x - cx) / W))
            prof = (H * 0.2 + D * (1 - u * u) ** 0.8 * (0.85 + 0.22 * ruido[k])
                    + D * 0.32 * math.exp(-((u - centro_pico) / 0.16) ** 2))
            fundo.append((cx + (x - cx) * 0.9, y + prof))
            maior = max(maior, prof)
        return fundo, maior

    # ============================================================ penhasco
    def _penhasco(self, tela, rng, frente, fundo, rocha, H):
        claro, escuro = rocha
        base_suave = suavizar(fundo[::4] + [fundo[-1]], fechado=False, passos=4)
        poligono = frente + base_suave[::-1]
        m = tela.mascara(poligono)
        tela.gradiente(m, claro, escuro, angulo=0)
        tela.gradiente(m, (0, 0, 0, 0), (20, 0, 30, 120), angulo=90)       # lado direito na sombra

        for f in (0.28, 0.48, 0.68):                                        # estratos da rocha
            estrato = [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f)
                       for a, b in zip(frente, fundo)]
            tela.linha(estrato, (30, 10, 30, 70), 1.2, recorte=m)
            tela.linha([(x, y - 1.2) for x, y in estrato], (255, 230, 220, 50), 0.8, recorte=m)

        for _ in range(5):                                                  # rachaduras
            k = rng.randint(4, len(frente) - 5)
            x, y = frente[k]
            fim = fundo[k][1]
            pontos, yy = [(x, y + H * 0.3)], y + H * 0.3
            while yy < fim:
                yy += rng.uniform(4, 8)
                x += rng.uniform(-2.5, 2.5)
                pontos.append((x, yy))
            tela.linha(pontos, (25, 10, 25, 110), 1.0, recorte=m)

        tela.luz_de_borda(m, (255, 235, 220), H * 0.25, 0, desfoque=H * 0.15, opacidade=0.35)

        terra = frente + [(x, y + H * 0.3) for x, y in frente][::-1]       # camada de solo
        tela.gradiente(tela.intersecao(tela.mascara(terra), m), "#7b5334", "#4a2f1c", angulo=0)
        return m

    def _queda_dagua(self, tela, ponto, W, H, D):
        x, y = ponto
        w = W * 0.1
        fim = y + D * 1.05 + H
        faixa = [(x - w / 2, y), (x + w / 2, y), (x + w * 0.75, fim), (x - w * 0.75, fim)]
        m = tela.mascara(faixa)
        tela.gradiente(m, (150, 225, 255, 245), (150, 225, 255, 0), angulo=0)
        for dx in (-0.25, 0.05, 0.3):
            tela.linha([(x + dx * w, y + 2), (x + dx * w * 1.4, y + (fim - y) * 0.75)],
                       (255, 255, 255, 150), 0.8)
        tela.brilho(x, y + D * 0.85 + H * 0.6, w * 1.4, w * 0.6, (255, 255, 255), 0.35, 3)

    # ================================================================ topo
    def _topo(self, tela, contorno, terreno, H):
        m = tela.mascara(contorno)
        tela.gradiente(m, terreno["claro"], terreno["escuro"], angulo=40)
        tela.luz_de_borda(m, terreno["escuro"], 0, -H * 0.22, desfoque=H * 0.1, opacidade=0.6)
        tela.luz_de_borda(m, (255, 255, 255), H * 0.18, H * 0.18, desfoque=H * 0.12, opacidade=0.35)
        return m

    def _beirada(self, tela, rng, frente, terreno, H):
        """Faixa irregular de vegetação que transborda a borda da frente."""
        ondas = [H * (0.1 + 0.07 * math.sin(k * 1.3) + 0.05 * math.sin(k * 3.1))
                 for k in range(len(frente))]
        faixa = frente + [(x, y + o) for (x, y), o in zip(frente, ondas)][::-1]
        tela.poligono(faixa, terreno["borda"])
        for k, (x, y) in enumerate(frente):
            if rng.random() < 0.55:
                r = H * rng.uniform(0.07, 0.17)
                tela.elipse(x + rng.uniform(-1, 1), y + ondas[k] * 0.7 + r * 0.3, r * 1.2, r * 0.8,
                            terreno["borda"])
        for k in range(1, len(frente) - 1, 3):
            x, y = frente[k]
            tela.elipse(x, y + H * 0.02, H * 0.12, H * 0.05, terreno["borda_luz"])

    def _cipos(self, tela, rng, frente, cx, W, H, D, mascara_penhasco):
        for _ in range(rng.randint(3, 6)):
            k = rng.randint(len(frente) // 6, len(frente) * 5 // 6)
            x, y = frente[k]
            comprimento = D * rng.uniform(0.3, 0.8) * (1 - abs(x - cx) / W * 0.6)
            fase = rng.uniform(0, math.pi * 2)
            pontos = [(x + math.sin(s * 0.9 + fase) * 2, y + H * 0.15 + comprimento * s / 7)
                      for s in range(8)]
            tela.linha(suavizar(pontos, fechado=False, passos=3), "#2f6b2a", 1.3)
            for i, (px, py) in enumerate(pontos[1::2]):
                lado = 1 if i % 2 else -1
                tela.elipse(px + lado * 2, py, 2.2, 1.3, "#4fb83d")

    def _riacho(self, tela, inicio, fim, W):
        meio = ((inicio[0] + fim[0]) / 2 + W * 0.12, (inicio[1] + fim[1]) / 2)
        curva = suavizar([inicio, meio, fim], fechado=False, passos=8)
        tela.linha(curva, "#3aa7d9", W * 0.12)
        tela.linha(curva, "#7fdcff", W * 0.075)
        tela.linha([(x - 0.6, y - 0.6) for x, y in curva[:-3]], (255, 255, 255, 170), W * 0.02)
        tela.elipse(inicio[0], inicio[1], W * 0.1, W * 0.05, "#3aa7d9")

    def _detalhes_do_chao(self, tela, rng, cx, cy, W, H, nome_terreno):
        for _ in range(rng.randint(2, 4)):                                  # pedras
            a = rng.uniform(0, 2 * math.pi)
            d = rng.uniform(0.62, 0.82)
            x, y = cx + math.cos(a) * W * d, cy + math.sin(a) * H * d
            r = W * rng.uniform(0.045, 0.08)
            tela.elipse(x + r * 0.2, y + r * 0.5, r * 1.1, r * 0.45, (0, 0, 0, 60))
            tela.elipse(x, y, r, r * 0.75, "#8e7ba6")
            tela.elipse(x - r * 0.25, y - r * 0.25, r * 0.55, r * 0.35, "#c9b8dd")
        if nome_terreno == "grama":
            for _ in range(rng.randint(4, 7)):                              # flores e tufos
                a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.3, 0.85)
                x, y = cx + math.cos(a) * W * d, cy + math.sin(a) * H * d
                if rng.random() < 0.5:
                    tela.elipse(x, y, 1.6, 1.6, rng.choice(["#fff27a", "#ff9ad5", "#ffffff"]))
                else:
                    for dx in (-1.5, 0, 1.5):
                        tela.linha([(x, y), (x + dx, y - 3)], "#2f8a26", 0.8)

    # ============================================================ cenários
    @staticmethod
    def _sombra(tela, x, y, rx, ry, opacidade=70):
        tela.elipse(x, y, rx, ry, (10, 30, 10, opacidade))

    def _arvore(self, tela, x, y, s):
        self._sombra(tela, x + s * 0.15, y, s * 0.85, s * 0.3)
        tela.poligono([(x - s * 0.13, y), (x - s * 0.08, y - s * 0.95),
                       (x + s * 0.08, y - s * 0.95), (x + s * 0.13, y)], "#6d4c2f")
        tela.poligono([(x + s * 0.02, y), (x + s * 0.02, y - s * 0.95),
                       (x + s * 0.08, y - s * 0.95), (x + s * 0.13, y)], "#4e3420")
        for dx, dy, r in ((0, -1.3, 0.62), (-0.45, -1.02, 0.45), (0.45, -1.02, 0.45)):
            tela.elipse(x + dx * s, y + dy * s, r * s, r * s * 0.9, "#2a7a2e")
        for dx, dy, r in ((-0.12, -1.4, 0.48), (-0.42, -1.1, 0.3), (0.3, -1.12, 0.3)):
            tela.elipse(x + dx * s, y + dy * s, r * s, r * s * 0.85, "#45a83f")
        tela.elipse(x - s * 0.22, y - s * 1.55, s * 0.24, s * 0.18, "#86da5e")
        tela.brilho(x - s * 0.25, y - s * 1.6, s * 0.14, s * 0.1, (255, 255, 230), 0.5, 1)

    def _floresta(self, tela, rng, x, y, W):
        arvores = []
        for _ in range(rng.randint(4, 6)):
            a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0, 0.45)
            arvores.append((x + math.cos(a) * W * d, y + math.sin(a) * W * d * 0.32,
                            W * rng.uniform(0.2, 0.28)))
        for ax, ay, s in sorted(arvores, key=lambda a: a[1]):
            self._arvore(tela, ax, ay, s)
        for _ in range(3):                                                  # arbustos
            bx, by = x + rng.uniform(-0.6, 0.6) * W, y + rng.uniform(0.05, 0.25) * W
            tela.elipse(bx, by, W * 0.09, W * 0.06, "#2a7a2e")
            tela.elipse(bx - W * 0.02, by - W * 0.02, W * 0.05, W * 0.03, "#5cc048")

    def _vulcao(self, tela, rng, x, y, W):
        s = W * 0.58
        base = y + s * 0.12
        tela.brilho(x, base, s * 1.05, s * 0.3, (20, 5, 5), 0.5, 2)
        cone = suavizar([(x - s, base), (x - s * 0.55, y - s * 0.35), (x - s * 0.24, y - s * 0.95),
                         (x + s * 0.24, y - s * 0.95), (x + s * 0.55, y - s * 0.35), (x + s, base),
                         (x, base + s * 0.12)], passos=6)
        m = tela.gradiente_poligono(cone, "#8a5a50", "#2b1b1d", angulo=0,
                                    contorno="#1f1416", largura=1)
        tela.gradiente(m, (0, 0, 0, 0), (0, 0, 0, 120), angulo=90)
        tela.luz_de_borda(m, (255, 200, 170), s * 0.08, s * 0.08, desfoque=s * 0.05, opacidade=0.35)
        for lado, comp in ((-1, 0.8), (1, 0.55)):                           # rios de lava
            lava = suavizar([(x + lado * s * 0.06, y - s * 0.9), (x + lado * s * 0.25, y - s * 0.5),
                             (x + lado * s * 0.2, y - s * (0.9 - comp)),
                             (x + lado * s * 0.42, y - s * (0.9 - comp - 0.25))],
                            fechado=False, passos=5)
            tela.linha(lava, "#ff5a1a", s * 0.09, recorte=m)
            tela.linha(lava, "#ffcf4a", s * 0.04, recorte=m)
        tela.brilho(x, y - s * 0.95, s * 0.45, s * 0.22, (255, 120, 30), 0.7, s * 0.12)
        tela.elipse(x, y - s * 0.95, s * 0.26, s * 0.08, "#ff7a1a")
        tela.elipse(x, y - s * 0.97, s * 0.17, s * 0.045, "#ffe27a")
        for i, (dx, dy, r) in enumerate(((0.05, -1.25, 0.16), (0.2, -1.5, 0.2), (0.42, -1.72, 0.24))):
            tom = 120 + i * 25
            tela.elipse(x + dx * s, y + dy * s, r * s, r * s * 0.8, (tom, tom - 10, tom + 5, 200))
            tela.elipse(x + (dx - 0.05) * s, y + (dy - 0.05) * s, r * s * 0.5, r * s * 0.35,
                        (tom + 50, tom + 45, tom + 55, 160))
        for _ in range(4):
            a = rng.uniform(0, math.pi)
            tela.elipse(x + math.cos(a) * s * 1.05, base + math.sin(a) * s * 0.25,
                        s * 0.08, s * 0.05, "#1f1416")

    def _cristal(self, tela, bx, by, h, w, faces):
        clara_a, clara_b, escura_a, escura_b, brilho = faces
        topo = (bx, by - h)
        tela.gradiente_poligono([(bx - w, by), (bx - w, by - h * 0.78), topo, (bx, by)],
                                clara_a, clara_b, angulo=0)
        tela.gradiente_poligono([(bx, by), topo, (bx + w, by - h * 0.78), (bx + w, by)],
                                escura_a, escura_b, angulo=0)
        tela.linha([(bx - w, by), (bx - w, by - h * 0.78), topo, (bx + w, by - h * 0.78), (bx + w, by)],
                   brilho, 0.8)
        tela.linha([topo, (bx, by)], (255, 255, 255, 160), 0.7)

    def _geleira(self, tela, rng, x, y, W):
        faces = ("#f4fbff", "#b8e3ff", "#8ccbf0", "#4f93cf", (255, 255, 255, 220))
        tela.brilho(x, y, W * 0.55, W * 0.2, (160, 220, 255), 0.5, 3)
        for dx, h, w in ((-0.34, 0.45, 0.09), (0.3, 0.55, 0.1), (-0.17, 0.78, 0.12),
                         (0.1, 1.0, 0.14), (0.42, 0.32, 0.07), (-0.02, 0.5, 0.09)):
            self._cristal(tela, x + dx * W, y + W * 0.06 + abs(dx) * W * 0.05, h * W * 0.75, w * W,
                          faces)
        for _ in range(4):
            tela.elipse(x + rng.uniform(-0.6, 0.6) * W, y + rng.uniform(0.1, 0.25) * W,
                        W * 0.08, W * 0.035, "#ffffff")

    def _canion(self, tela, rng, x, y, W):
        for dx, w, h in ((-0.28, 0.3, 0.55), (0.25, 0.24, 0.38)):
            esq, dir_ = x + (dx - w) * W, x + (dx + w) * W
            base, topo = y + W * 0.1, y - h * W
            recuo = w * W * 0.18
            tela.brilho(x + dx * W + W * 0.06, base, w * W * 1.1, W * 0.08, (60, 30, 10), 0.5, 1.5)
            m = tela.gradiente_poligono([(esq, base), (esq + recuo, topo), (dir_ - recuo, topo),
                                         (dir_, base)], "#d0804a", "#7a4022", angulo=0,
                                        contorno="#5a2f17", largura=0.8)
            tela.gradiente(m, (0, 0, 0, 0), (40, 10, 0, 110), angulo=90)
            for f in (0.3, 0.55, 0.8):
                yy = topo + (base - topo) * f
                tela.linha([(esq, yy), (dir_, yy)], (255, 210, 160, 110), 0.9, recorte=m)
            tela.poligono([(esq + recuo, topo), (dir_ - recuo, topo),
                           (dir_ - recuo * 1.6, topo - W * 0.06), (esq + recuo * 1.6, topo - W * 0.06)],
                          "#f2b879")
        cx, cy, s = x + W * 0.02, y + W * 0.22, W * 0.3                       # cacto
        tela.elipse(cx, cy, s * 0.35, s * 0.1, (60, 30, 10, 80))
        tela.linha([(cx, cy), (cx, cy - s)], "#2f8a3a", s * 0.22)
        tela.linha([(cx - s * 0.05, cy - s * 0.5), (cx - s * 0.32, cy - s * 0.5),
                    (cx - s * 0.32, cy - s * 0.78)], "#2f8a3a", s * 0.14)
        tela.linha([(cx + s * 0.05, cy - s * 0.35), (cx + s * 0.28, cy - s * 0.35),
                    (cx + s * 0.28, cy - s * 0.6)], "#2f8a3a", s * 0.14)
        tela.linha([(cx - s * 0.04, cy - s * 0.1), (cx - s * 0.04, cy - s * 0.92)], "#6cc75a", s * 0.06)
        tela.elipse(cx, cy - s * 1.02, s * 0.08, s * 0.07, "#ff8fb8")

    def _tempestade(self, tela, rng, x, y, W):
        faces = ("#f0dcff", "#b98af0", "#8a4fd8", "#4a2390", (240, 220, 255, 220))
        tela.brilho(x, y - W * 0.2, W * 0.5, W * 0.35, (190, 120, 255), 0.45, 4)
        for dx, h, w in ((-0.3, 0.5, 0.09), (0.28, 0.6, 0.1), (-0.08, 0.95, 0.13), (0.12, 0.7, 0.1)):
            self._cristal(tela, x + dx * W, y + W * 0.06, h * W * 0.7, w * W, faces)
        nuvem_y = y - W * 1.05
        for dx, dy, r in ((-0.32, 0.05, 0.24), (0.3, 0.06, 0.22), (-0.08, -0.05, 0.3), (0.12, 0.02, 0.26)):
            tela.elipse(x + dx * W, nuvem_y + dy * W, r * W, r * W * 0.65, "#555a77")
        for dx, dy, r in ((-0.12, -0.1, 0.2), (0.15, -0.05, 0.16)):
            tela.elipse(x + dx * W, nuvem_y + dy * W, r * W, r * W * 0.55, "#858aa8")
        raio = [(0.06, 0.12), (-0.06, 0.38), (0.02, 0.38), (-0.08, 0.62),
                (0.14, 0.32), (0.06, 0.32), (0.14, 0.12)]
        tela.brilho(x, nuvem_y + W * 0.4, W * 0.18, W * 0.25, (255, 240, 150), 0.6, 3)
        tela.poligono([(x + dx * W, nuvem_y + dy * W) for dx, dy in raio], "#ffe45c",
                      contorno="#fff8c8", largura=0.6)

    def _palmeira(self, tela, x, y, s):
        self._sombra(tela, x + s * 0.3, y, s * 0.6, s * 0.18)
        tronco = suavizar([(x, y), (x + s * 0.12, y - s * 0.5), (x + s * 0.3, y - s * 1.05)],
                          fechado=False, passos=6)
        for i, (px, py) in enumerate(tronco):
            r = s * (0.11 - i * 0.003)
            tela.elipse(px, py, r, r * 0.55, "#a7743f" if i % 2 else "#7d5230")
        tx, ty = tronco[-1]
        for ang in (-175, -135, -95, -55, -15, 25):
            a = math.radians(ang)
            fim = (tx + math.cos(a) * s * 0.75, ty + math.sin(a) * s * 0.35 + s * 0.3)
            meio = (tx + math.cos(a) * s * 0.42, ty + math.sin(a) * s * 0.4 - s * 0.05)
            folha = suavizar([(tx, ty), meio, fim, (meio[0], meio[1] + s * 0.12)], passos=5)
            tela.poligono(folha, "#3fae4a", contorno="#24782d", largura=0.6)
            tela.linha([(tx, ty), meio, fim], (30, 110, 40, 200), 0.6)
        for dx in (-0.06, 0.06):
            tela.elipse(tx + dx * s, ty + s * 0.06, s * 0.06, s * 0.06, "#5a3a1e")

    def _lagoa(self, tela, rng, x, y, W):
        lx, ly = x - W * 0.15, y + W * 0.03
        tela.elipse(lx, ly, W * 0.4, W * 0.17, "#f3dc9c")
        m = tela.gradiente_elipse(lx, ly + W * 0.01, W * 0.34, W * 0.13, "#8ff0ff", "#1690c0", angulo=0)
        tela.luz_de_borda(m, (0, 60, 100), 0, W * 0.04, desfoque=1, opacidade=0.5)
        tela.linha([(lx - W * 0.15, ly - W * 0.02), (lx + W * 0.05, ly - W * 0.05)],
                   (255, 255, 255, 170), 1.0)
        for _ in range(3):
            tela.elipse(lx + rng.uniform(-0.2, 0.2) * W, ly + rng.uniform(-0.04, 0.06) * W,
                        W * 0.03, W * 0.02, "#ff8fa3")
        self._palmeira(tela, x + W * 0.35, y + W * 0.08, W * 0.55)

    def _ninho(self, tela, rng, x, y, W):
        s = W * 0.42
        self._sombra(tela, x + s * 0.1, y + s * 0.2, s * 1.1, s * 0.35, 90)
        tela.gradiente_elipse(x, y, s, s * 0.45, "#a4703e", "#5b3a1e", angulo=0,
                              contorno="#3e2612", largura=0.8)
        for _ in range(26):                                                  # gravetos trançados
            a = rng.uniform(0, 2 * math.pi)
            px, py = x + math.cos(a) * s * 0.85, y + math.sin(a) * s * 0.38
            comp = s * rng.uniform(0.25, 0.45)
            tela.linha([(px - comp / 2, py + rng.uniform(-2, 2)), (px + comp / 2, py)],
                       rng.choice(["#c08a4f", "#8a5a2f", "#d6a066"]), 0.9)
        tela.elipse(x, y - s * 0.1, s * 0.68, s * 0.24, "#3e2612")
        for dx, clara, escura in ((-0.34, "#ffe28a", "#e09a1a"), (0.0, "#e4c4ff", "#8a4fd8"),
                                  (0.34, "#b8f0ff", "#2f9fd0")):
            ex, ey = x + dx * s, y - s * 0.28 - (0.06 * s if dx == 0 else 0)
            m = tela.gradiente_elipse(ex, ey, s * 0.19, s * 0.27, clara, escura, angulo=40,
                                      contorno=(40, 20, 10, 200), largura=0.6)
            for _ in range(3):
                tela.elipse(ex + rng.uniform(-0.1, 0.1) * s, ey + rng.uniform(-0.12, 0.15) * s,
                            s * 0.03, s * 0.025, (255, 255, 255, 150))
            tela.brilho(ex - s * 0.06, ey - s * 0.1, s * 0.05, s * 0.07, (255, 255, 255), 0.8, 0.6)
        mx, my = x + W * 0.62, y + W * 0.02                                    # estandarte
        tela.linha([(mx, my), (mx, my - W * 1.0)], "#6b4a2b", W * 0.035)
        bandeira = suavizar([(mx, my - W * 0.98), (mx + W * 0.25, my - W * 1.0),
                             (mx + W * 0.5, my - W * 0.9), (mx + W * 0.45, my - W * 0.72),
                             (mx + W * 0.22, my - W * 0.66), (mx, my - W * 0.62)], passos=4)
        tela.gradiente_poligono(bandeira, "#ff8a5c", "#c93b3b", angulo=90,
                                contorno="#8a2424", largura=0.6)
        tela.elipse(mx, my - W * 1.02, W * 0.04, W * 0.04, "#f5c242")
