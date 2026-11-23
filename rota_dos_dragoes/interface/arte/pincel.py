"""Ferramentas de desenho com superamostragem (antialiasing), degradês,
brilhos desfocados e luz de borda. As coordenadas são sempre em pixels
da imagem final; a superamostragem é interna."""
import math
from typing import List, Optional, Sequence, Tuple, Union

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REAMOSTRAGEM = getattr(Image, "Resampling", Image)
SUPERAMOSTRAGEM = 3

Ponto = Tuple[float, float]
Cor = Union[str, Tuple[int, ...]]


def suavizar(pontos: Sequence[Ponto], fechado: bool = True, passos: int = 6) -> List[Ponto]:
    """Curva Catmull-Rom passando por todos os pontos."""
    n = len(pontos)
    if n < 3:
        return list(pontos)
    saida: List[Ponto] = []
    trechos = range(n) if fechado else range(n - 1)
    for i in trechos:
        if fechado:
            p0, p1, p2, p3 = (pontos[(i - 1) % n], pontos[i],
                              pontos[(i + 1) % n], pontos[(i + 2) % n])
        else:
            p0, p1 = pontos[max(i - 1, 0)], pontos[i]
            p2, p3 = pontos[i + 1], pontos[min(i + 2, n - 1)]
        for s in range(passos):
            t = s / passos
            t2, t3 = t * t, t * t * t
            saida.append(tuple(
                0.5 * (2 * p1[k] + (-p0[k] + p2[k]) * t
                       + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2
                       + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3)
                for k in (0, 1)))
    if not fechado:
        saida.append(tuple(pontos[-1]))
    return saida


def faixa_afilada(centro: Sequence[Ponto], largura_ini: float, largura_fim: float) -> List[Ponto]:
    """Polígono de uma 'fita' que afina ao longo da linha central (caudas, troncos)."""
    esquerda, direita = [], []
    n = len(centro)
    for i, (x, y) in enumerate(centro):
        ax, ay = centro[max(i - 1, 0)]
        bx, by = centro[min(i + 1, n - 1)]
        dx, dy = bx - ax, by - ay
        comp = math.hypot(dx, dy) or 1
        nx, ny = -dy / comp, dx / comp
        w = (largura_ini + (largura_fim - largura_ini) * i / max(n - 1, 1)) / 2
        esquerda.append((x + nx * w, y + ny * w))
        direita.append((x - nx * w, y - ny * w))
    return esquerda + direita[::-1]


class Tela:
    def __init__(self, largura: float, altura: float, ss: int = SUPERAMOSTRAGEM) -> None:
        self.largura, self.altura, self.ss = largura, altura, ss
        self.img = Image.new("RGBA", (max(1, int(largura * ss)), max(1, int(altura * ss))),
                             (0, 0, 0, 0))

    # ----------------------------------------------------------- apoio
    def _esc(self, pontos: Sequence[Ponto]) -> List[Ponto]:
        return [(x * self.ss, y * self.ss) for x, y in pontos]

    def _caixa(self, pontos: Sequence[Ponto], margem: float = 0) -> Tuple[int, int, int, int]:
        xs, ys = [p[0] for p in pontos], [p[1] for p in pontos]
        return (max(0, int(min(xs) - margem)), max(0, int(min(ys) - margem)),
                min(self.img.width, int(max(xs) + margem) + 1),
                min(self.img.height, int(max(ys) + margem) + 1))

    def _compor(self, camada: Image.Image, destino: Tuple[int, int],
                recorte: Optional[Image.Image] = None) -> None:
        if recorte is not None:
            x, y = destino
            r = recorte.crop((x, y, x + camada.width, y + camada.height))
            camada.putalpha(ImageChops.multiply(camada.getchannel("A"), r))
        self.img.alpha_composite(camada, dest=destino)

    # ---------------------------------------------------------- máscaras
    def mascara(self, pontos: Sequence[Ponto]) -> Image.Image:
        m = Image.new("L", self.img.size, 0)
        ImageDraw.Draw(m).polygon(self._esc(pontos), fill=255)
        return m

    def mascara_elipse(self, cx: float, cy: float, rx: float, ry: float) -> Image.Image:
        m = Image.new("L", self.img.size, 0)
        s = self.ss
        ImageDraw.Draw(m).ellipse(((cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s),
                                  fill=255)
        return m

    @staticmethod
    def intersecao(a: Image.Image, b: Image.Image) -> Image.Image:
        return ImageChops.multiply(a, b)

    # ---------------------------------------------------------- primitivas
    def poligono(self, pontos: Sequence[Ponto], cor: Cor, contorno: Optional[Cor] = None,
                 largura: float = 0, recorte: Optional[Image.Image] = None) -> None:
        P = self._esc(pontos)
        x0, y0, x1, y1 = self._caixa(P, largura * self.ss + 2)
        if x1 <= x0 or y1 <= y0:
            return
        camada = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        d = ImageDraw.Draw(camada)
        Q = [(x - x0, y - y0) for x, y in P]
        d.polygon(Q, fill=cor)
        if contorno and largura:
            d.line(Q + [Q[0]], fill=contorno, width=max(1, int(largura * self.ss)), joint="curve")
        self._compor(camada, (x0, y0), recorte)

    def elipse(self, cx: float, cy: float, rx: float, ry: float, cor: Cor,
               contorno: Optional[Cor] = None, largura: float = 0,
               recorte: Optional[Image.Image] = None) -> None:
        s = self.ss
        x0, y0, x1, y1 = self._caixa([((cx - rx) * s, (cy - ry) * s), ((cx + rx) * s, (cy + ry) * s)],
                                     largura * s + 2)
        if x1 <= x0 or y1 <= y0:
            return
        camada = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        ImageDraw.Draw(camada).ellipse(
            ((cx - rx) * s - x0, (cy - ry) * s - y0, (cx + rx) * s - x0, (cy + ry) * s - y0),
            fill=cor, outline=contorno, width=max(0, int(largura * s)))
        self._compor(camada, (x0, y0), recorte)

    def linha(self, pontos: Sequence[Ponto], cor: Cor, largura: float,
              recorte: Optional[Image.Image] = None) -> None:
        P = self._esc(pontos)
        x0, y0, x1, y1 = self._caixa(P, largura * self.ss + 2)
        if x1 <= x0 or y1 <= y0:
            return
        camada = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
        w = max(1, int(largura * self.ss))
        Q = [(x - x0, y - y0) for x, y in P]
        d = ImageDraw.Draw(camada)
        d.line(Q, fill=cor, width=w, joint="curve")
        for x, y in (Q[0], Q[-1]):          # pontas arredondadas
            d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=cor)
        self._compor(camada, (x0, y0), recorte)

    # ---------------------------------------------------------- efeitos
    @staticmethod
    def _gradiente_l(largura: int, altura: int, angulo: float) -> Image.Image:
        g = Image.linear_gradient("L").resize((512, 512))
        if angulo:
            g = g.rotate(angulo, resample=REAMOSTRAGEM.BICUBIC)
        return g.crop((75, 75, 437, 437)).resize((max(1, largura), max(1, altura)))

    def gradiente(self, mascara: Image.Image, cor_a: Cor, cor_b: Cor,
                  angulo: float = 0, opacidade: float = 1.0) -> None:
        """Preenche a máscara de cor_a até cor_b. angulo=0: de cima para baixo;
        45: do canto superior esquerdo; 90: da esquerda para a direita."""
        caixa = mascara.getbbox()
        if not caixa:
            return
        x0, y0, x1, y1 = caixa
        w, h = x1 - x0, y1 - y0
        g = self._gradiente_l(w, h, angulo)
        camada = Image.composite(Image.new("RGBA", (w, h), cor_b),
                                 Image.new("RGBA", (w, h), cor_a), g)
        alfa = mascara.crop(caixa)
        if opacidade < 1:
            alfa = alfa.point(lambda v: int(v * opacidade))
        camada.putalpha(ImageChops.multiply(camada.getchannel("A"), alfa))
        self.img.alpha_composite(camada, dest=(x0, y0))

    def gradiente_poligono(self, pontos: Sequence[Ponto], cor_a: Cor, cor_b: Cor,
                           angulo: float = 0, contorno: Optional[Cor] = None,
                           largura: float = 0, recorte: Optional[Image.Image] = None) -> Image.Image:
        m = self.mascara(pontos)
        if recorte is not None:
            m = self.intersecao(m, recorte)
        self.gradiente(m, cor_a, cor_b, angulo)
        if contorno and largura:
            self.linha(list(pontos) + [pontos[0]], contorno, largura, recorte=recorte)
        return m

    def gradiente_elipse(self, cx, cy, rx, ry, cor_a, cor_b, angulo=0,
                         contorno=None, largura=0) -> Image.Image:
        m = self.mascara_elipse(cx, cy, rx, ry)
        self.gradiente(m, cor_a, cor_b, angulo)
        if contorno and largura:
            self.elipse(cx, cy, rx, ry, (0, 0, 0, 0), contorno=contorno, largura=largura)
        return m

    def brilho(self, cx: float, cy: float, rx: float, ry: float, cor: Cor,
               opacidade: float = 0.5, desfoque: float = 4,
               recorte: Optional[Image.Image] = None) -> None:
        s = self.ss
        pad = desfoque * s * 3
        x0, y0, x1, y1 = self._caixa([((cx - rx) * s, (cy - ry) * s), ((cx + rx) * s, (cy + ry) * s)], pad)
        if x1 <= x0 or y1 <= y0:
            return
        m = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(m).ellipse(((cx - rx) * s - x0, (cy - ry) * s - y0,
                                   (cx + rx) * s - x0, (cy + ry) * s - y0),
                                  fill=int(255 * opacidade))
        if desfoque:
            m = m.filter(ImageFilter.GaussianBlur(desfoque * s))
        camada = Image.new("RGBA", m.size, cor)
        camada.putalpha(m)
        self._compor(camada, (x0, y0), recorte)

    def luz_de_borda(self, mascara: Image.Image, cor: Cor, dx: float, dy: float,
                     desfoque: float = 2, opacidade: float = 0.5) -> None:
        """Ilumina (ou escurece) a borda da forma oposta ao deslocamento,
        criando a impressão de volume."""
        deslocada = ImageChops.offset(mascara, int(dx * self.ss), int(dy * self.ss))
        borda = ImageChops.subtract(mascara, deslocada)
        if desfoque:
            borda = borda.filter(ImageFilter.GaussianBlur(desfoque * self.ss))
        borda = ImageChops.multiply(borda, mascara)
        if opacidade < 1:
            borda = borda.point(lambda v: int(v * opacidade))
        camada = Image.new("RGBA", self.img.size, cor)
        camada.putalpha(borda)
        self.img.alpha_composite(camada)

    def finalizar(self, escala: float = 1.0) -> Image.Image:
        largura = max(1, round(self.largura * escala))
        altura = max(1, round(self.altura * escala))
        return self.img.resize((largura, altura), REAMOSTRAGEM.LANCZOS)
