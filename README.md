# Rota dos Dragões

O dragão sai do ninho (vértice 1), visita as ilhas e retorna. O mapa mostra
as arestas disponíveis e seus pesos. A posição das ilhas serve para desenhar
o grafo. O custo usa os pesos dos exemplos da aula.

## Como executar

Com Python 3.8+ e Tkinter instalado:

```bash
python -m pip install -r requirements.txt
python main.py
```

Escolha no menu qualquer tamanho de **5 a 18 pontos** ou use
**Sortear quantidade de ilhas** para carregar um tamanho ao acaso.
Os dois tamanhos das extremidades usam os grafos da aula. Os tamanhos
intermediários são cenários fixos derivados do grafo de 18 pontos.

Clique em **Calcular rota** para ver o custo e em **Voar!** para acompanhar
o percurso. Compare os algoritmos no mesmo arquipélago.

- **Força Bruta** busca o circuito ótimo sem revisitar ilhas. Até 10 vértices.
- **Dijkstra** usa caminhos mínimos para escolher a próxima ilha ainda não
  visitada. Pode passar por uma ilha mais de uma vez e não garante o ótimo.
- **Dijkstra com controle de visitas** registra os vértices visitados em uma máscara.
  Busca o circuito ótimo sem revisitas. Até 18 vértices.

## Comparação dos grafos

| Grafo | Força Bruta | Dijkstra | Dijkstra com controle de visitas |
| --- | ---: | ---: | ---: |
| 5 pontos | 15 | 17 | 15 |
| 18 pontos | Indisponível pelo limite de 10 pontos | 411 | 390 |

## Testes

```bash
python -m unittest discover -s tests -v
```
