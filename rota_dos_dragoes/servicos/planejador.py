import time

from ..dominio.rota import Rota


class ErroDePlanejamento(Exception):
    pass


class LimiteDoAlgoritmoExcedido(ErroDePlanejamento):
    pass


class PlanejadorDeRota:
    def planejar(self, grafo, algoritmo):
        if not algoritmo.suporta(len(grafo)):
            raise LimiteDoAlgoritmoExcedido(
                f"{algoritmo.nome} pode ser usado em grafos de até {algoritmo.limite_ilhas} ilhas."
            )

        inicio = time.perf_counter()
        caminho, custo = algoritmo.resolver(grafo, 1)
        tempo_ms = (time.perf_counter() - inicio) * 1000
        if caminho is None:
            raise ErroDePlanejamento("Nenhuma rota foi encontrada.")

        # O mapa trabalha com índices e acrescenta o retorno ao desenhar o circuito.
        indices = {vertice: indice for indice, vertice in enumerate(grafo)}
        ordem = tuple(indices[vertice] for vertice in caminho[:-1])
        return Rota(ordem, custo, algoritmo.nome, tempo_ms)
