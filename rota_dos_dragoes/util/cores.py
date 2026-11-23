def misturar_cores(cor1: str, cor2: str, t: float) -> str:
    """Interpola duas cores hexadecimais (#rrggbb); t=0 dá cor1, t=1 dá cor2."""
    a = [int(cor1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(cor2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))
