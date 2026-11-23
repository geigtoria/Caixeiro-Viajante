"""Renderização dos sprites com Pillow (sem depender do Tkinter).

Tudo aqui gera imagens PIL; a conversão para o Tkinter fica em ``sprites.py``.
"""
from .ceu import renderizar_ceu
from .dragao import RenderizadorDeDragao
from .ilha_flutuante import RenderizadorDeIlhaFlutuante, SpriteIlha

__all__ = ["renderizar_ceu", "RenderizadorDeDragao", "RenderizadorDeIlhaFlutuante", "SpriteIlha"]
