# Integral Quest

**Integral Quest** é um serious game 2D desenvolvido em Python com Pygame, utilizado como projeto prático para a disciplina de **Computação Gráfica**, demonstrando a aplicação das quatro transformações geométricas fundamentais: **Translação**, **Rotação**, **Escala** e **Reflexão**.

## Disciplina

- **Disciplina:** Computação Gráfica
- **Professora:** Suzana Sousa
- **Aluno:** Caiky de Morais Alves, Stênio Gabriel Botelho do Carmo, Maria Eduarda Ribeiro Ramos

## Visão Geral

O jogo foi projetado para reforçar cinco tópicos centrais de Cálculo: noção de integral, integral indefinida, substituição, integração por partes e integral definida. Cada região do mapa representa um desses tópicos e apresenta desafios com feedback imediato, conectando a ação do jogador ao conceito matemático estudado.

O foco do projeto na disciplina de Computação Gráfica é a **implementação explícita das transformações geométricas** em todas as mecânicas visuais do jogo, utilizando matrizes de transformação homogênea 2D (3×3).

## Mecânicas Principais

- Exploração do mapa com personagem em cenário 2D e entrada em portais temáticos
- Fases com desafios relacionados ao conteúdo matemático de cada região
- Sistema de pontuação com recompensa por acerto
- Feedback pedagógico imediato
- Progressão por desbloqueio de regiões

## Controles

- **Setas** ou **WASD**: mover o personagem
- **W**, **Seta para cima** ou **Espaço**: pular
- **ESC**: voltar ao mapa ou menu
- **Mouse**: interagir com botões

## Como Executar

1. Instale o Python 3.
2. Instale o Pygame:

```bash
pip install pygame
```

3. Execute o jogo:

```bash
python main.py
```

## Estrutura do Projeto

```text
integral_quest/
├── main.py              # Ponto de entrada
├── game.py              # Controle de estados e navegação
├── settings.py          # Constantes e configurações
├── data/
│   └── questions.py     # Banco de questões por região
├── screens/
│   ├── menu.py          # Tela inicial (ROTAÇÃO nos portais)
│   ├── map_screen.py    # Mapa com portais (REFLEXÃO no chão)
│   ├── player.py        # ★ Personagem (TODAS as 4 transformações)
│   ├── base_phase.py    # Motor base das fases
│   ├── results.py       # Resultados por fase
│   ├── treino.py        # Manuscrito de estudo
│   ├── victory.py       # Tela de vitória
│   └── phases/
│       ├── phase1_lava.py       # TRANSLAÇÃO da lava
│       ├── phase2_spikes.py     # TRANSLAÇÃO de plataformas caindo
│       ├── phase3_enemies.py    # REFLEXÃO + ESCALA dos inimigos
│       ├── phase4_water.py      # TRANSLAÇÃO da água
│       ├── phase5_lightning.py  # TRANSLAÇÃO das plataformas
│       └── phase_boss.py       # ROTAÇÃO dos tentáculos e projéteis
└── README.md
```

## Tecnologias

- **Linguagem:** Python 3
- **Biblioteca gráfica:** Pygame
- **Representação:** Coordenadas homogêneas 2D com matrizes 3×3

## Créditos

Projeto acadêmico desenvolvido para a disciplina de Computação Gráfica, demonstrando a aplicação prática de transformações geométricas em um jogo educacional interativo.
