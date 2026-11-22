import math

from ..dominio.arquipelago import NOME_NINHO, Ilha
from ..dominio.elementos import Elemento


def graph_layout(graph):
    """Distribui os vértices em coordenadas entre 0 e 1."""
    vertices = list(graph)
    count = len(vertices)
    if count == 1:
        return {vertices[0]: (0.5, 0.5)}

    positions = {
        vertex: [
            0.5 + 0.38 * math.cos(2 * math.pi * index / count),
            0.5 + 0.38 * math.sin(2 * math.pi * index / count),
        ]
        for index, vertex in enumerate(vertices)
    }
    if count <= 5:
        return positions

    # Uma disposição por forças deixa o grafo maior mais legível.
    edges = {
        frozenset((origin, edge["vertex"]))
        for origin in graph
        for edge in graph[origin]
        if origin != edge["vertex"]
    }
    spacing = 0.5 / math.sqrt(count)
    for step in range(180):
        movement = {vertex: [0.0, 0.0] for vertex in vertices}

        for index, origin in enumerate(vertices):
            for destination in vertices[index + 1:]:
                dx = positions[origin][0] - positions[destination][0]
                dy = positions[origin][1] - positions[destination][1]
                distance = max(math.hypot(dx, dy), 0.001)
                force = spacing * spacing / distance
                fx, fy = dx / distance * force, dy / distance * force
                movement[origin][0] += fx
                movement[origin][1] += fy
                movement[destination][0] -= fx
                movement[destination][1] -= fy

        for endpoints in edges:
            origin, destination = tuple(endpoints)
            dx = positions[origin][0] - positions[destination][0]
            dy = positions[origin][1] - positions[destination][1]
            distance = max(math.hypot(dx, dy), 0.001)
            force = distance * distance / spacing
            fx, fy = dx / distance * force, dy / distance * force
            movement[origin][0] -= fx
            movement[origin][1] -= fy
            movement[destination][0] += fx
            movement[destination][1] += fy

        limit = 0.035 * (1 - step / 180) + 0.002
        for vertex in vertices:
            dx, dy = movement[vertex]
            length = max(math.hypot(dx, dy), 0.001)
            positions[vertex][0] = min(
                0.94, max(0.06, positions[vertex][0] + dx / length * min(length, limit))
            )
            positions[vertex][1] = min(
                0.94, max(0.06, positions[vertex][1] + dy / length * min(length, limit))
            )

    return positions


def ilhas_do_grafo(grafo, largura, altura):
    """Usa as posições apenas para desenhar. Os pesos vêm do grafo."""
    habitats = Elemento.habitats()
    return [
        Ilha(70 + x * (largura - 140), 60 + y * (altura - 120),
             NOME_NINHO if vertice == 1 else f"Ilha {vertice}",
             Elemento.NINHO if vertice == 1 else habitats[(vertice - 2) % len(habitats)])
        for vertice, (x, y) in graph_layout(grafo).items()
    ]
