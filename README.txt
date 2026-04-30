Forest RPG Map Generator V3
===========================

Este projeto gera um mapa procedural inspirado na composição geral de RPGs 2D cozy: rio à esquerda, floresta densa, clareiras de terra, vila, campamento e montanhas/rochas.

Não é cópia de Heartwood Online. A ideia é capturar a estrutura visual geral: floresta + vila + rio + montanhas + objetos em camadas.

Como rodar:
1. Extraia o ZIP.
2. Instale pygame:
   pip install pygame
3. Rode:
   python main.py

Controles:
- WASD / setas: mover
- R: gerar outro mapa
- G: mostrar/esconder grade
- H: mostrar/esconder hitboxes
- F5: exportar mapa completo como generated_map.png
- ESC: sair

Observação:
Os assets originais continuam na pasta assets/. O código também gera algumas imagens em tempo real, como pinheiros, nuvens e a casa de telhado vermelho, para aproximar a composição do mapa de referência.
