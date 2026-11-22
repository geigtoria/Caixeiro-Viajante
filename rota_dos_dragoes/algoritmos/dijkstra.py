import heapq

def dijkstra(graph, origin):
    distances = {vertex: float("inf") for vertex in graph}
    predecessors = {vertex: None for vertex in graph}

    distances[origin] = 0
    priority_queue = [(0, origin)]

    while priority_queue:
        current_distance, current_vertex = heapq.heappop(priority_queue)

        if current_distance > distances[current_vertex]:
            continue

        for edge in graph[current_vertex]:
            neighbor = edge["vertex"]
            weight = edge["weight"]
            new_distance = current_distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_vertex
                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor),
                )

    return distances, predecessors


def reconstruct_path(predecessors, origin, destination):
    path = []
    current = destination

    while current is not None:
        path.append(current)

        if current == origin:
            return list(reversed(path))

        current = predecessors[current]

    return None


def tsp_dijkstra(graph, origin):
    if len(graph) == 1:
        return [origin], 0

    visited = {origin}
    route = [origin]
    total_cost = 0
    current = origin

    while len(visited) < len(graph):
        distances, predecessors = dijkstra(graph, current)

        unvisited = [
            vertex
            for vertex in graph
            if vertex not in visited
        ]

        next_vertex = min(
            unvisited,
            key=lambda vertex: distances[vertex],
        )

        if distances[next_vertex] == float("inf"):
            return None, float("inf")

        path = reconstruct_path(
            predecessors,
            current,
            next_vertex,
        )

        route.extend(path[1:])
        visited.update(path)
        total_cost += distances[next_vertex]
        current = next_vertex

    distances, predecessors = dijkstra(graph, current)

    if distances[origin] == float("inf"):
        return None, float("inf")

    return_path = reconstruct_path(
        predecessors,
        current,
        origin,
    )

    route.extend(return_path[1:])
    total_cost += distances[origin]

    return route, total_cost
