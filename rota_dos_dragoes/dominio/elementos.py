from enum import Enum
from typing import List


class Elemento(Enum):
    """Tipo de habitat de cada ilha. O ninho é o ponto de partida do dragão."""

    NINHO = "Ninho"
    FOGO = "Fogo"
    GELO = "Gelo"
    NATUREZA = "Natureza"
    TERRA = "Terra"
    TEMPESTADE = "Tempestade"
    MAR = "Mar"

    @classmethod
    def habitats(cls) -> List["Elemento"]:
        return [e for e in cls if e is not cls.NINHO]
