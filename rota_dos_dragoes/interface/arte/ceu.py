"""Fundo do mapa: céu de fim de tarde com estrelas e nuvens macias."""
import random

from PIL import Image, ImageDraw, ImageFilter

TOPO, MEIO, BASE = "#13234a", "#2b5a90", "#7fb2d8"


def _degrade(largura: int, altura: int) -> Image.Image:
    g = Image.linear_gradient("L").resize((largura, altura))
    metade = altura // 2
    cima = Image.composite(Image.new("RGB", (largura, altura), MEIO),
                           Image.new("RGB", (largura, altura), TOPO),
                           g.point(lambda v: min(255, v * 2)))
    baixo = Image.composite(Image.new("RGB", (largura, altura), BASE),
                            Image.new("RGB", (largura, altura), MEIO),
                            g.point(lambda v: max(0, v * 2 - 255)))
    mascara = Image.new("L", (largura, altura), 0)
    ImageDraw.Draw(mascara).rectangle((0, metade, largura, altura), fill=255)
    return Image.composite(baixo, cima, mascara).convert("RGBA")


def renderizar_ceu(largura: int, altura: int, semente: int = 11) -> Image.Image:
    rng = random.Random(semente)
    img = _degrade(largura, altura)

    estrelas = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(estrelas)
    for _ in range(90):
        x, y = rng.uniform(0, largura), rng.uniform(0, altura * 0.45)
        r = rng.choice((0.6, 0.8, 1.1))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 255, 255, rng.randint(60, 200)))
    img.alpha_composite(estrelas)

    for camada in range(2):                      # nuvens: ao fundo mais desfocadas
        nuvens = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(nuvens)
        for _ in range(9 if camada == 0 else 6):
            cx = rng.uniform(-50, largura + 50)
            cy = rng.uniform(altura * 0.35, altura * 1.0)
            for _ in range(rng.randint(4, 7)):
                rx, ry = rng.uniform(40, 90), rng.uniform(14, 30)
                ox, oy = rng.uniform(-80, 80), rng.uniform(-12, 12)
                alfa = rng.randint(35, 70) if camada == 0 else rng.randint(60, 110)
                d.ellipse((cx + ox - rx, cy + oy - ry, cx + ox + rx, cy + oy + ry),
                          fill=(255, 255, 255, alfa))
        img.alpha_composite(nuvens.filter(ImageFilter.GaussianBlur(14 if camada == 0 else 7)))
    return img.convert("RGB")
