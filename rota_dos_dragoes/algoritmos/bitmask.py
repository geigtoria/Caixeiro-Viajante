import heapq


def tsp_dijkstra_bitmask(graph, origin):
    vertices = list(graph)
    n = len(vertices)

    if n == 1:
        return [origin], 0

    # Associa cada vértice a uma posição na máscara
    indexes = {
        vertex: index
        for index, vertex in enumerate(vertices)
    }

    # Máscara com todas as cidades visitadas
    all_visited = (1 << n) - 1

    # Estado inicial: origem visitada
    initial_mask = 1 << indexes[origin]
    initial_state = (origin, initial_mask)

    distances = {initial_state: 0}
    predecessors = {initial_state: None}

    priority_queue = [(0, origin, initial_mask)]

    while priority_queue:
        cost, current, visited = heapq.heappop(priority_queue)
        state = (current, visited)

        if cost > distances[state]:
            continue

        # Todas visitadas e retorno à origem
        if current == origin and visited == all_visited:
            route = []
            while state is not None:
                route.append(state[0])
                state = predecessors[state]

            return list(reversed(route)), cost

        for edge in graph[current]:
            neighbor = edge["vertex"]
            weight = edge["weight"]
            bit = 1 << indexes[neighbor]

            if neighbor == origin:
                # Só permite retornar no final
                if visited != all_visited:
                    continue

                new_visited = visited

            else:
                # Impede revisitar cidades
                if visited & bit:
                    continue

                new_visited = visited | bit

            new_cost = cost + weight
            new_state = (neighbor, new_visited)

            if new_cost < distances.get(new_state, float("inf")):
                distances[new_state] = new_cost
                predecessors[new_state] = state

                heapq.heappush(
                    priority_queue,
                    (new_cost, neighbor, new_visited),
                )

    return None, float("inf")
