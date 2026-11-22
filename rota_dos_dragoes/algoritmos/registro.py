from dataclasses import dataclass
from typing import Callable, Optional

from .bitmask import tsp_dijkstra_bitmask
from .dijkstra import tsp_dijkstra
from .forca_bruta import brute_force


@dataclass(frozen=True)
class AlgoritmoTSP:
    nome: str
    nome_curto: str
    resolver: Callable
    limite_ilhas: Optional[int] = None

    def suporta(self, quantidade: int) -> bool:
        return self.limite_ilhas is None or quantidade <= self.limite_ilhas


ALGORITMOS = {
    algoritmo.nome: algoritmo
    for algoritmo in (
        AlgoritmoTSP("Força Bruta", "Exato", brute_force, 10),
        AlgoritmoTSP("Dijkstra", "Dijkstra", tsp_dijkstra),
        AlgoritmoTSP("Dijkstra com controle de visitas", "Visitas", tsp_dijkstra_bitmask, 18),
    )
}
ALGORITMO_PADRAO = "Força Bruta"
