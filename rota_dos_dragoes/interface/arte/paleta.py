"""Cores da arte das ilhas e do dragão."""
from ...dominio.elementos import Elemento

TERRENOS = {
    "grama": {"claro": "#a6e65f", "escuro": "#3d9a2c", "borda": "#2b7a22", "borda_luz": "#63c43c"},
    "neve": {"claro": "#ffffff", "escuro": "#b4d5f0", "borda": "#8fb8dd", "borda_luz": "#e8f5ff"},
    "cinzas": {"claro": "#86655f", "escuro": "#3a2b2a", "borda": "#2a1f1e", "borda_luz": "#634a46"},
    "areia": {"claro": "#f8dc96", "escuro": "#cf9a52", "borda": "#a8743c", "borda_luz": "#ebc177"},
    "tormenta": {"claro": "#a796cc", "escuro": "#52457a", "borda": "#3b305c", "borda_luz": "#8070ad"},
}

ROCHAS = {
    "quente": ("#d39a78", "#5a3540"),
    "fria": ("#a7c4de", "#3c5170"),
    "vulcanica": ("#74514c", "#1f1517"),
    "arenito": ("#df9f5f", "#6b3a22"),
    "ametista": ("#9a87bd", "#33264d"),
}

TERRENO_DO_ELEMENTO = {
    Elemento.NINHO: ("grama", "quente"),
    Elemento.NATUREZA: ("grama", "quente"),
    Elemento.MAR: ("grama", "quente"),
    Elemento.FOGO: ("cinzas", "vulcanica"),
    Elemento.GELO: ("neve", "fria"),
    Elemento.TERRA: ("areia", "arenito"),
    Elemento.TEMPESTADE: ("tormenta", "ametista"),
}

DRAGAO = {
    "corpo_claro": "#47dcb9",
    "corpo_escuro": "#16877a",
    "contorno": "#0d4a43",
    "barriga_clara": "#ffe0a6",
    "barriga_escura": "#ff9f5a",
    "asa_clara": "#ffb276",
    "asa_escura": "#ff5f6d",
    "asa_tras_clara": "#e0835a",
    "asa_tras_escura": "#b8465a",
    "osso": "#127065",
    "espinho_claro": "#ffcf6b",
    "espinho_escuro": "#ff7a3d",
    "chifre_claro": "#fff4dc",
    "chifre_escuro": "#d4b07c",
    "iris_clara": "#ffd84a",
    "iris_escura": "#e07000",
}
