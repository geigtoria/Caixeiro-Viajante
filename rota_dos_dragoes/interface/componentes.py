"""Fábricas de widgets com o visual do tema."""
import tkinter as tk
from typing import Callable, Optional

from .tema import COR, FONTE_BOTAO, FONTE_SECAO, FONTE_TEXTO


def criar_secao(pai: tk.Misc, texto: str) -> None:
    tk.Label(pai, text=texto, font=FONTE_SECAO, fg=COR["texto"],
             bg=COR["painel"]).pack(anchor="w", pady=(10, 2))
    tk.Frame(pai, bg=COR["botao"], height=2).pack(fill="x", pady=(0, 4))


def criar_botao(pai: tk.Misc, texto: str, comando: Callable[[], None],
                destaque: bool = False) -> tk.Button:
    base = COR["ouro"] if destaque else COR["botao"]
    hover = COR["ouro_claro"] if destaque else COR["botao_hover"]
    frente = COR["painel"] if destaque else "white"
    botao = tk.Button(pai, text=texto, command=comando, bg=base, fg=frente,
                      activebackground=hover, activeforeground=frente, relief="flat",
                      font=FONTE_BOTAO, cursor="hand2", pady=4)
    botao.pack(fill="x", pady=3)
    botao.bind("<Enter>", lambda _e: botao.config(bg=hover))
    botao.bind("<Leave>", lambda _e: botao.config(bg=base))
    return botao


def criar_info(pai: tk.Misc, texto: str, cor: Optional[str] = None) -> tk.Label:
    rotulo = tk.Label(pai, text=texto, fg=cor or COR["texto"], bg=COR["painel"],
                      font=FONTE_TEXTO, anchor="w", justify="left", wraplength=250)
    rotulo.pack(fill="x")
    return rotulo
