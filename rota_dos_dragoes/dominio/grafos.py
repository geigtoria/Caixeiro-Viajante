grafo_simples = {
  1: [
    {"vertex": 2, "weight": 2},
    {"vertex": 4, "weight": 3},
    {"vertex": 5, "weight": 6},
  ],
  2: [
    {"vertex": 1, "weight": 2},
    {"vertex": 3, "weight": 4},
    {"vertex": 4, "weight": 3},
  ],
  3: [
    {"vertex": 2, "weight": 4},
    {"vertex": 4, "weight": 7},
    {"vertex": 5, "weight": 3},
  ],
  4: [
    {"vertex": 1, "weight": 3},
    {"vertex": 2, "weight": 3},
    {"vertex": 3, "weight": 7},
    {"vertex": 5, "weight": 3},
  ],
  5: [
    {"vertex": 1, "weight": 6},
    {"vertex": 3, "weight": 3},
    {"vertex": 4, "weight": 3},
  ],
}

grafo_complexo = {
  1: [
    {"vertex": 2, "weight": 20},
    {"vertex": 8, "weight": 29},
    {"vertex": 12, "weight": 29},
    {"vertex": 13, "weight": 37},
  ],
  2: [
    {"vertex": 1, "weight": 20},
    {"vertex": 3, "weight": 25},
    {"vertex": 8, "weight": 28},
    {"vertex": 12, "weight": 39},
  ],
  3: [
    {"vertex": 2, "weight": 25},
    {"vertex": 4, "weight": 25},
    {"vertex": 8, "weight": 30},
    {"vertex": 13, "weight": 54},
  ],
  4: [
    {"vertex": 3, "weight": 25},
    {"vertex": 5, "weight": 39},
    {"vertex": 6, "weight": 32},
    {"vertex": 7, "weight": 42},
    {"vertex": 9, "weight": 23},
    {"vertex": 10, "weight": 33},
    {"vertex": 14, "weight": 56},
  ],
  5: [
    {"vertex": 4, "weight": 39},
    {"vertex": 6, "weight": 12},
    {"vertex": 7, "weight": 26},
    {"vertex": 10, "weight": 19},
  ],
  6: [
    {"vertex": 4, "weight": 32},
    {"vertex": 5, "weight": 12},
    {"vertex": 7, "weight": 17},
    {"vertex": 10, "weight": 35},
    {"vertex": 11, "weight": 30},
  ],
  7: [
    {"vertex": 4, "weight": 42},
    {"vertex": 5, "weight": 26},
    {"vertex": 6, "weight": 17},
    {"vertex": 11, "weight": 38},
  ],
  8: [
    {"vertex": 1, "weight": 29},
    {"vertex": 2, "weight": 28},
    {"vertex": 3, "weight": 30},
    {"vertex": 12, "weight": 25},
    {"vertex": 13, "weight": 22},
  ],
  9: [
    {"vertex": 4, "weight": 23},
    {"vertex": 10, "weight": 26},
    {"vertex": 13, "weight": 34},
    {"vertex": 14, "weight": 0},
    {"vertex": 16, "weight": 43},
  ],
  10: [
    {"vertex": 4, "weight": 33},
    {"vertex": 5, "weight": 19},
    {"vertex": 6, "weight": 35},
    {"vertex": 9, "weight": 26},
    {"vertex": 11, "weight": 24},
    {"vertex": 14, "weight": 30},
    {"vertex": 15, "weight": 19},
  ],
  11: [
    {"vertex": 6, "weight": 30},
    {"vertex": 7, "weight": 38},
    {"vertex": 10, "weight": 24},
    {"vertex": 15, "weight": 26},
    {"vertex": 18, "weight": 36},
  ],
  12: [
    {"vertex": 1, "weight": 29},
    {"vertex": 2, "weight": 39},
    {"vertex": 8, "weight": 25},
    {"vertex": 13, "weight": 27},
    {"vertex": 16, "weight": 43},
  ],
  13: [
    {"vertex": 1, "weight": 37},
    {"vertex": 3, "weight": 54},
    {"vertex": 8, "weight": 22},
    {"vertex": 9, "weight": 34},
    {"vertex": 12, "weight": 27},
    {"vertex": 14, "weight": 24},
    {"vertex": 16, "weight": 19},
  ],
  14: [
    {"vertex": 4, "weight": 56},
    {"vertex": 9, "weight": 0},
    {"vertex": 10, "weight": 30},
    {"vertex": 13, "weight": 24},
    {"vertex": 15, "weight": 20},
    {"vertex": 16, "weight": 19},
    {"vertex": 17, "weight": 17},
  ],
  15: [
    {"vertex": 10, "weight": 19},
    {"vertex": 11, "weight": 26},
    {"vertex": 14, "weight": 20},
    {"vertex": 17, "weight": 18},
    {"vertex": 18, "weight": 21},
  ],
  16: [
    {"vertex": 9, "weight": 43},
    {"vertex": 12, "weight": 43},
    {"vertex": 13, "weight": 19},
    {"vertex": 14, "weight": 19},
    {"vertex": 17, "weight": 26},
  ],
  17: [
    {"vertex": 14, "weight": 17},
    {"vertex": 15, "weight": 18},
    {"vertex": 16, "weight": 26},
    {"vertex": 18, "weight": 15},
  ],
  18: [
    {"vertex": 11, "weight": 36},
    {"vertex": 15, "weight": 21},
    {"vertex": 17, "weight": 15},
  ],
}

# Um circuito do grafo de 18 pontos serve de base para os tamanhos intermediarios.
_CIRCUITO = (1, 2, 3, 4, 9, 14, 15, 10, 5, 6, 7, 11, 18, 17, 16, 13, 8, 12)


def _grafo_intermediario(quantidade):
    vertices = _CIRCUITO[:quantidade]
    indices = {vertice: indice for indice, vertice in enumerate(vertices, 1)}
    grafo = {
        indices[origem]: [
            {"vertex": indices[aresta["vertex"]], "weight": aresta["weight"]}
            for aresta in grafo_complexo[origem]
            if aresta["vertex"] in indices
        ]
        for origem in vertices
    }
    if not any(aresta["vertex"] == 1 for aresta in grafo[quantidade]):
        # Resume o trecho do circuito pelos pontos retirados para fechar a volta.
        retorno = _CIRCUITO[quantidade - 1:] + (1,)
        peso = sum(
            next(aresta["weight"] for aresta in grafo_complexo[origem]
                 if aresta["vertex"] == destino)
            for origem, destino in zip(retorno, retorno[1:])
        )
        grafo[quantidade].append({"vertex": 1, "weight": peso})
        grafo[1].append({"vertex": quantidade, "weight": peso})
    return grafo


GRAFOS = {
    "5 pontos": grafo_simples,
    **{f"{n} pontos": _grafo_intermediario(n) for n in range(6, 18)},
    "18 pontos": grafo_complexo,
}
