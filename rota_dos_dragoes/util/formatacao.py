def formatar_numero(numero: float, casas: int = 1) -> str:
    """Formata no padrão brasileiro: 1.234,5"""
    texto = f"{numero:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")
