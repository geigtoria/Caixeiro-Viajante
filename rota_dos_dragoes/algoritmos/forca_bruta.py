def get_weight(graph, origin, destiny):
    for edge in graph[origin]:
        if edge["vertex"] == destiny:
            return edge["weight"]
    return None

def brute_force(graph, origin):
    best_route = None
    lowest_cost = float("inf")

    def find_route(node, visited, route, cost):
        nonlocal best_route, lowest_cost

        if len(visited) == len(graph):
            weight = get_weight(graph, node, origin)

            if weight is not None:
                total_cost = cost + weight

                if total_cost < lowest_cost:
                    lowest_cost = total_cost
                    best_route = route + [origin]

            return

        for edge in graph[node]:
            neighbor = edge["vertex"]
            weight = edge["weight"]

            if neighbor not in visited:
                find_route(neighbor, visited | {neighbor}, route + [neighbor], cost + weight)

    find_route(origin, {origin}, [origin], 0)

    return best_route, lowest_cost
