"""Controlador: liga o modelo (arquipélago), os serviços e as views."""
import random
import tkinter as tk
from tkinter import messagebox
from typing import List, Optional, Set, Tuple

from ..algoritmos import ALGORITMO_PADRAO, ALGORITMOS
from ..dominio.arquipelago import Arquipelago
from ..dominio.geometria import Ponto
from ..dominio.grafos import GRAFOS
from ..dominio.rota import Rota
from ..servicos import ErroDePlanejamento, PlanejadorDeRota, ilhas_do_grafo
from .animacao import AnimadorDeVoo
from .mapa import MapaView
from .painel import PainelDeControle
from .tema import COR

class AplicacaoRotaDosDragoes:
    def __init__(self, raiz: tk.Tk) -> None:
        self.raiz = raiz
        raiz.title("Rota dos Dragões — Caixeiro Viajante")
        raiz.configure(bg=COR["painel"])
        raiz.resizable(False, False)

        # modelo e serviços
        self.arquipelago = Arquipelago()
        self.planejador = PlanejadorDeRota()

        # estado da sessão
        self.rota: Optional[Rota] = None
        self.rastro: List[Tuple[float, float, float, float]] = []
        self.visitadas: Set[int] = set()

        # views
        self.mapa = MapaView(raiz)
        self.mapa.grid(row=0, column=0, padx=12, pady=12)
        self.painel = PainelDeControle(
            raiz, list(ALGORITMOS), ALGORITMO_PADRAO, list(GRAFOS),
            ao_gerar=self.carregar_grafo, ao_sortear=self.sortear_quantidade,
            ao_calcular=self.calcular_rota, ao_voar=self.voar, ao_parar=self.parar_voo)
        self.painel.grid(row=0, column=1, sticky="ns", padx=(0, 14), pady=12)

        self.animador = AnimadorDeVoo(raiz, lambda: self.painel.velocidade,
                                      ao_quadro=self.mapa.desenhar_voo,
                                      ao_chegar=self._ao_chegar_na_ilha,
                                      ao_terminar=self._ao_terminar_voo)

        self.arquipelago.inscrever(self._ao_mudar_arquipelago)
        self.carregar_grafo()

    # --------------------------------------------------- reação ao modelo
    def _ao_mudar_arquipelago(self) -> None:
        self._descartar_rota()
        self._redesenhar()

    def _descartar_rota(self) -> None:
        self.animador.parar()
        self.rota = None
        self.rastro = []
        self.visitadas = set()
        self.painel.limpar_resultado()

    def _redesenhar(self) -> None:
        self.mapa.renderizar(self.arquipelago, self.grafo, self.rota, self.rastro, self.visitadas)

    def carregar_grafo(self) -> None:
        self.grafo = GRAFOS[self.painel.grafo]
        self.arquipelago.substituir(
            ilhas_do_grafo(self.grafo, self.mapa.largura, self.mapa.altura)
        )
        self.painel.mostrar_status(f"{len(self.grafo)} ilhas no arquipélago.")

    # ---------------------------------------------------------- ações: rota
    def sortear_quantidade(self) -> None:
        self.painel.grafo = random.choice(tuple(GRAFOS))
        self.carregar_grafo()

    def calcular_rota(self) -> bool:
        algoritmo = ALGORITMOS[self.painel.algoritmo]
        self._descartar_rota()
        self.painel.mostrar_status("Calculando rota…")
        self.raiz.update_idletasks()
        try:
            rota = self.planejador.planejar(self.grafo, algoritmo)
        except ErroDePlanejamento as erro:
            self._redesenhar()
            self.painel.mostrar_status("Rota indisponível.")
            messagebox.showwarning("Rota indisponível", str(erro))
            return False

        self.rota = rota
        self.painel.mostrar_resultado(rota)
        self.painel.registrar_historico(rota, algoritmo.nome_curto)
        self.painel.mostrar_status("Rota traçada. Aperte Voar!")
        self._redesenhar()
        return True

    # ----------------------------------------------------------- ações: voo
    def voar(self) -> None:
        if (self.rota is None or self.rota.algoritmo != self.painel.algoritmo) and not self.calcular_rota():
            return
        assert self.rota is not None
        self.animador.parar()
        self.rastro = []
        self.visitadas = {self.rota.ordem[0]}
        pontos: List[Ponto] = [self.arquipelago[i].posicao for i in self.rota.ordem]
        pontos.append(pontos[0])
        self._redesenhar()
        self.painel.mostrar_status("O dragão decolou do ninho!")
        self.animador.iniciar(pontos)

    def parar_voo(self) -> None:
        if self.animador.parar():
            self.painel.mostrar_status("Voo interrompido.")

    def _ao_chegar_na_ilha(self, segmento: int, trecho: Tuple[float, float, float, float]) -> None:
        assert self.rota is not None
        self.rastro.append(trecho)
        indice = self.rota.ordem[segmento % len(self.rota)]
        self.visitadas.add(indice)
        if segmento < len(self.rota):
            self.painel.mostrar_status(
                f"Passou por {self.arquipelago[indice].nome} ({len(self.visitadas)}/{len(self.grafo)})")
        self._redesenhar()

    def _ao_terminar_voo(self) -> None:
        self.painel.mostrar_status("Voo concluído! O dragão voltou ao ninho.")


def executar() -> None:
    raiz = tk.Tk()
    AplicacaoRotaDosDragoes(raiz)
    raiz.mainloop()
