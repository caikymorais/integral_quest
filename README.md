# Integral Quest

**Integral Quest** é um serious game 2D desenvolvido em Python com Pygame para ajudar estudantes de Cálculo a revisar e praticar conceitos fundamentais de integrais de forma interativa.

## Visão geral

O jogo foi projetado para reforçar cinco tópicos centrais: noção de integral, integral indefinida, substituição, integração por partes e integral definida.
Cada região do mapa representa um desses tópicos e apresenta desafios com feedback imediato sobre acertos e erros, conectando a ação do jogador ao conceito matemático estudado.

## Objetivo educacional

O objetivo principal é apoiar estudantes que já tiveram um primeiro contato com integrais, oferecendo prática guiada e revisão de conteúdo em um ambiente lúdico.
O foco pedagógico inclui interpretar integral como área acumulada, aplicar regras básicas de integração, usar substituição, escolher corretamente elementos da integração por partes e calcular integrais definidas simples.

## Plataforma e tecnologias

O projeto foi pensado para execução em computadores desktop, em janela gráfica, com controle principal por teclado.
A implementação utiliza Python e a biblioteca Pygame, permitindo controlar diretamente fluxo de telas, mecânicas, feedback e progressão do jogador.

## Estrutura do jogo

O fluxo principal do jogo segue um mapa com portais temáticos, no qual o jogador escolhe uma região, resolve uma sequência de desafios e retorna ao mapa com sua pontuação atualizada.
A progressão acontece por desbloqueio de regiões conforme o desempenho do jogador, favorecendo revisão contínua em vez de derrota definitiva.

### Regiões de aprendizagem

| Região                | Conteúdo trabalhado                            | Papel no aprendizado                                                                 |
|-----------------------|-----------------------------------------------|--------------------------------------------------------------------------------------|
| Noção de Integral     | Área sob a curva e soma acumulada             | Introduz a interpretação geométrica da integral.                                      |
| Integral Indefinida   | Primitivas, regra da potência, soma, constante | Reforça técnicas algébricas básicas de integração.                                |
| Substituição          | Mudança de variável                           | Treina o reconhecimento de funções compostas e simplificação da integral.           |
| Integração por Partes | Escolha de \(u\) e \(dv\)                     | Trabalha transformação de integrais mais difíceis em formas mais simples.           |
| Integral Definida     | Aplicação da primitiva em intervalos          | Relaciona cálculo simbólico com valor acumulado em um intervalo.                   |

## Mecânicas principais

- Exploração do mapa com personagem em cenário 2D e entrada em portais temáticos.
- Fases com desafios relacionados ao conteúdo matemático de cada região, usando alternativas e interação direta com o cenário.
- Sistema de pontuação com recompensa por acerto e incentivo a acertar de primeira tentativa.
- Feedback pedagógico imediato explicando por que a resposta está correta ou incorreta.
- Repetição de fases para melhorar desempenho e consolidar aprendizagem, em vez de impor falha definitiva.

## Progressão e pontuação

A proposta original do projeto prevê avanço por regiões, desbloqueando novos conteúdos à medida que o jogador conclui desafios com desempenho mínimo satisfatório. 
Na versão atual do jogo, essa ideia foi expandida com sistema de pontuação global, fases desbloqueáveis, portal de treino e fase de chefão condicionada ao progresso total do jogador.

### Recursos adicionais implementados

- **Portal treino** com manuscrito de estudo para revisão de conteúdos antes ou durante a progressão no jogo.  
- **Portal chefão** liberado somente após concluir todas as fases e atingir a pontuação mínima global definida no projeto.  
- **Tela de vitória** ao concluir o chefão, seguida de retorno ao início para reiniciar a jornada.  
- **Sistema de resultados por fase** com acertos, porcentagem e retorno ao mapa.

## Fluxo de telas

A proposta do projeto define uma tela inicial, tela de mapa, telas de desafio e tela de resultados de fase.
Na implementação atual, esse fluxo foi ampliado com tela de treino, portal de chefão e tela final de vitória, mantendo a lógica central descrita no documento de projeto.

## Público-alvo

O jogo é voltado para estudantes que estejam cursando Cálculo e que já tiveram contato inicial com integrais, podendo ser usado individualmente ou como apoio em contexto de sala de aula.
Isso faz do projeto uma ferramenta de revisão e prática, com ênfase em aprendizagem ativa por tentativa, erro e correção imediata.

## Como executar

1. Instale o Python 3.  
2. Instale o Pygame:

```bash
pip install pygame
```

3. Execute o jogo a partir do arquivo principal:

```bash
python main.py
```

## Controles

- **Setas** ou **WASD**: mover o personagem.  
- **W**, **Seta para cima** ou **Espaço**: pular, nas fases de plataforma.  
- **ESC**: voltar ao mapa ou menu, dependendo da tela atual.  
- **Mouse**: interagir com botões em telas como resultados.

## Organização sugerida do projeto

```text
integral_quest/
├── main.py
├── game.py
├── settings.py
├── data/
│   └── questions.py
├── screens/
│   ├── menu.py
│   ├── map_screen.py
│   ├── results.py
│   ├── treino.py
│   ├── victory.py
│   ├── player.py
│   └── phases/
│       ├── phase1_lava.py
│       ├── phase2_spikes.py
│       ├── phase3_enemies.py
│       ├── phase4_water.py
│       ├── phase5_lightning.py
│       └── phase_boss.py
└── README.md
```

## Diferenciais do projeto

O projeto combina conteúdo de Cálculo com estrutura de progressão inspirada em jogos de aventura e plataforma, o que ajuda a transformar revisão teórica em experiência prática.
Ao associar cada tipo de integral a uma mecânica específica e a feedback conceitual imediato, o jogo se alinha ao mapa de aprendizagem proposto no documento acadêmico.

## Próximas melhorias sugeridas

- Adicionar sons e música ambiente para reforçar feedback e identidade do jogo.  
- Incluir sistema de salvamento de progresso.  
- Expandir o manuscrito de treino com exemplos resolvidos passo a passo.  
- Adicionar indicadores visuais de desempenho por região no mapa.  
- Criar mais questões por fase para aumentar a rejogabilidade.

## Créditos

Projeto acadêmico de serious game voltado ao ensino de integrais, desenvolvido como apoio ao estudo de Cálculo em ambiente desktop com Pygame.

Aluno: Caiky de Morais Alves
