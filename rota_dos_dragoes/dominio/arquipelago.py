import math
from dataclasses import dataclass
from typing import Callable, Iterator, List, Optional, Set

from .elementos import Elemento
from .geometria import Ponto

NOME_NINHO = "Ninho do Dragão"

Observador = Callable[[], None]


@dataclass
class Ilha:
    x: float
    y: float
    nome: str
    elemento: Elemento

    @property
    def posicao(self) -> Ponto:
        return (self.x, self.y)

    @property
    def eh_ninho(self) -> bool:
        return self.elemento is Elemento.NINHO

    def distancia_ate(self, x: float, y: float) -> float:
        return math.dist(self.posicao, (x, y))


class Arquipelago:
    """Coleção ordenada de ilhas; a de índice 0 é sempre o ninho.

    Implementa o padrão Observer: quem se inscreve é avisado a cada mudança,
    o que permite à interface reagir sem que o modelo conheça a interface.
    """

    def __init__(self) -> None:
        self._ilhas: List[Ilha] = []
        self._observadores: List[Observador] = []

    # -- observer
    def inscrever(self, observador: Observador) -> None:
        self._observadores.append(observador)

    def _notificar(self) -> None:
        for observador in list(self._observadores):
            observador()

    # -- consulta
    def __len__(self) -> int:
        return len(self._ilhas)

    def __iter__(self) -> Iterator[Ilha]:
        return iter(self._ilhas)

    def __getitem__(self, indice: int) -> Ilha:
        return self._ilhas[indice]

    @property
    def nomes(self) -> Set[str]:
        return {ilha.nome for ilha in self._ilhas}

    def posicoes(self) -> List[Ponto]:
        return [ilha.posicao for ilha in self._ilhas]

    def indice_mais_proximo(self, x: float, y: float, raio: float) -> Optional[int]:
        """Índice da ilha mais próxima de (x, y) dentro do raio, ou None."""
        if not self._ilhas:
            return None
        indice = min(range(len(self._ilhas)), key=lambda k: self._ilhas[k].distancia_ate(x, y))
        return indice if self._ilhas[indice].distancia_ate(x, y) <= raio else None

    def ha_ilha_perto(self, x: float, y: float, raio: float) -> bool:
        return self.indice_mais_proximo(x, y, raio) is not None

    # -- alteração
    def adicionar(self, ilha: Ilha) -> None:
        self._ilhas.append(ilha)
        self._garantir_ninho()
        self._notificar()

    def remover(self, indice: int) -> Ilha:
        removida = self._ilhas.pop(indice)
        self._garantir_ninho()
        self._notificar()
        return removida

    def substituir(self, ilhas: List[Ilha]) -> None:
        self._ilhas = list(ilhas)
        self._garantir_ninho()
        self._notificar()

    def limpar(self) -> None:
        self.substituir([])

    def _garantir_ninho(self) -> None:
        if self._ilhas and not self._ilhas[0].eh_ninho:
            self._ilhas[0].nome = NOME_NINHO
            self._ilhas[0].elemento = Elemento.NINHO
