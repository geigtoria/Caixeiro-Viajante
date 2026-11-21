from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class Rota:
    """Resultado imutável de um cálculo de rota."""

    ordem: Tuple[int, ...]
    comprimento: float      # soma dos pesos
    algoritmo: str
    tempo_ms: float

    def __len__(self) -> int:
        return len(self.ordem)

    def posicoes_na_rota(self) -> Dict[int, int]:
        """Mapeia índice da ilha -> posição em que é visitada."""
        return {ilha: posicao for posicao, ilha in reversed(tuple(enumerate(self.ordem)))}
