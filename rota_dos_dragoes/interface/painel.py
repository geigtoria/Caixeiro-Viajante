import tkinter as tk
from typing import Callable, Sequence

from ..dominio.rota import Rota
from ..util.formatacao import formatar_numero
from .componentes import criar_botao, criar_info, criar_secao
from .tema import COR, FONTE_DICA, FONTE_MONO, FONTE_TEXTO, FONTE_TITULO

Acao = Callable[[], None]


class PainelDeControle(tk.Frame):
    """Barra lateral. Não contém regra de negócio: só lê entradas e
    repassa os cliques para as ações recebidas do controlador."""

    def __init__(self, pai: tk.Misc, nomes_algoritmos: Sequence[str], algoritmo_padrao: str,
                 nomes_grafos: Sequence[str],
                 *, ao_gerar: Acao, ao_sortear: Acao, ao_calcular: Acao,
                 ao_voar: Acao, ao_parar: Acao) -> None:
        super().__init__(pai, bg=COR["painel"], width=270)
        self._montar_cabecalho()
        self._montar_arquipelago(nomes_grafos, ao_gerar, ao_sortear)
        self._montar_algoritmo(nomes_algoritmos, algoritmo_padrao, ao_calcular)
        self._montar_voo(ao_voar, ao_parar)
        self._montar_resultado()

    # ------------------------------------------------------------ montagem
    def _montar_cabecalho(self) -> None:
        tk.Label(self, text="Rota dos Dragões", font=FONTE_TITULO,
                 fg=COR["ouro"], bg=COR["painel"]).pack(anchor="w")
        tk.Label(self, text="Leve o dragão por todas as ilhas\ne de volta ao ninho no menor voo.",
                 font=FONTE_DICA, fg=COR["suave"], bg=COR["painel"],
                 justify="left").pack(anchor="w", pady=(0, 10))

    def _montar_arquipelago(self, nomes: Sequence[str],
                             ao_gerar: Acao, ao_sortear: Acao) -> None:
        criar_secao(self, "Arquipélago")
        self._grafo = tk.StringVar(value=nomes[0])
        self._montar_menu(self._grafo, nomes, command=lambda _: ao_gerar())
        criar_botao(self, "Sortear quantidade de ilhas", ao_sortear)

    def _montar_algoritmo(self, nomes: Sequence[str], padrao: str, ao_calcular: Acao) -> None:
        criar_secao(self, "Algoritmo")
        self._algoritmo = tk.StringVar(value=padrao)
        self._montar_menu(self._algoritmo, nomes)
        criar_botao(self, "Calcular rota", ao_calcular)

    def _montar_menu(self, variavel, nomes, **opcoes) -> None:
        menu = tk.OptionMenu(self, variavel, *nomes, **opcoes)
        menu.config(bg=COR["painel2"], fg=COR["texto"], activebackground=COR["botao"],
                    activeforeground="white", highlightthickness=0, relief="flat",
                    font=FONTE_TEXTO, anchor="w")
        menu["menu"].config(bg=COR["painel2"], fg=COR["texto"],
                            activebackground=COR["botao"], font=FONTE_TEXTO)
        menu.pack(fill="x", pady=2)

    def _montar_voo(self, ao_voar: Acao, ao_parar: Acao) -> None:
        criar_secao(self, "Voo")
        tk.Label(self, text="Velocidade do dragão", fg=COR["texto"], bg=COR["painel"],
                 font=FONTE_DICA).pack(anchor="w")
        self._velocidade = tk.Scale(self, from_=1, to=10, orient="horizontal",
                                    showvalue=False, bg=COR["painel"], fg=COR["texto"],
                                    troughcolor=COR["painel2"], highlightthickness=0,
                                    activebackground=COR["ouro"])
        self._velocidade.set(5)
        self._velocidade.pack(fill="x")
        criar_botao(self, "Voar!", ao_voar, destaque=True)
        criar_botao(self, "Parar voo", ao_parar)

    def _montar_resultado(self) -> None:
        criar_secao(self, "Resultado")
        self._lbl_distancia = criar_info(self, "")
        self._lbl_tempo = criar_info(self, "")
        self._lbl_status = criar_info(self, "Pronto para voar.", cor=COR["ouro"])
        self.limpar_resultado()

        criar_secao(self, "Histórico")
        self._historico = tk.Listbox(self, height=6, bg=COR["painel2"], fg=COR["texto"],
                                     font=FONTE_MONO, relief="flat", highlightthickness=0,
                                     selectbackground=COR["botao"])
        self._historico.pack(fill="x", pady=2)

    # ------------------------------------------------------------- leitura
    @property
    def grafo(self) -> str:
        return self._grafo.get()

    @grafo.setter
    def grafo(self, nome: str) -> None:
        self._grafo.set(nome)

    @property
    def algoritmo(self) -> str:
        return self._algoritmo.get()

    @property
    def velocidade(self) -> int:
        return int(self._velocidade.get())

    # ------------------------------------------------------------- escrita
    def mostrar_status(self, texto: str) -> None:
        self._lbl_status.config(text=texto)

    def mostrar_resultado(self, rota: Rota) -> None:
        self._lbl_distancia.config(
            text=f"Custo: {formatar_numero(rota.comprimento)}")
        self._lbl_tempo.config(text=f"Cálculo: {formatar_numero(rota.tempo_ms, 3)} ms")

    def limpar_resultado(self) -> None:
        self._lbl_distancia.config(text="Custo: —")
        self._lbl_tempo.config(text="Cálculo: —")

    def registrar_historico(self, rota: Rota, rotulo: str) -> None:
        self._historico.insert(
            0, f"{rotulo:<9}{len(set(rota.ordem)):>3} ilhas {formatar_numero(rota.comprimento):>8}")
