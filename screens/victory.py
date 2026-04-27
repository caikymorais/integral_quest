import pygame
import math
import random
from settings import *
from screens.player import draw_character


class VictoryScreen:

    def __init__(self, game):
        self.game        = game
        self.tick        = 0
        self.font_big    = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_med    = pygame.font.SysFont("Arial", 26, bold=True)
        self.font_sm     = pygame.font.SysFont("Arial", 18)
        self.font_btn    = pygame.font.SysFont("Arial", 22, bold=True)
        self.btn_restart = pygame.Rect(WIDTH//2 - 200, HEIGHT - 130, 180, 52)
        self.btn_menu    = pygame.Rect(WIDTH//2 + 20,  HEIGHT - 130, 180, 52)
        self.confetti = [
            [random.randint(0, WIDTH),
             random.randint(-HEIGHT, 0),
             random.uniform(-1.5, 1.5),
             random.uniform(2, 5),
             random.choice([RED, YELLOW, GREEN, CYAN, ORANGE, PURPLE])]
            for _ in range(120)
        ]
        self.stars = [(random.randint(0, WIDTH),
                       random.randint(0, HEIGHT),
                       random.uniform(0.5, 2.0)) for _ in range(80)]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if self.btn_restart.collidepoint(mx, my):
                    self.game.reset_game()
                elif self.btn_menu.collidepoint(mx, my):
                    self.game.go_to_menu()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.game.reset_game()
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_m:
                    self.game.go_to_menu()

    def update(self):
        self.tick += 1
        for c in self.confetti:
            c[0] += c[2] + math.sin(self.tick * 0.05 + c[0]) * 0.5
            c[1] += c[3]
            if c[1] > HEIGHT + 10:
                c[1] = random.randint(-60, 0)
                c[0] = random.randint(0, WIDTH)

    def draw(self):
        s = self.game.screen
        s.fill(BG_COLOR)

        for row in range(0, HEIGHT, 3):
            t = row / HEIGHT
            pygame.draw.line(s,
                (int(10 + t*15), int(5 + t*8), int(30 + t*25)),
                (0, row), (WIDTH, row))

        for sx, sy, sr in self.stars:
            tw = int(100 + 80 * math.sin(self.tick * 0.04 + sx))
            pygame.draw.circle(s, (tw, tw, tw), (sx, sy), int(sr))

        for c in self.confetti:
            pygame.draw.rect(s, c[4], (int(c[0]), int(c[1]), 8, 8))

        glow = int(70 + 50 * math.sin(self.tick * 0.06))
        gs   = pygame.Surface((700, 120), pygame.SRCALPHA)
        pygame.draw.ellipse(gs, (255, 200, 0, glow), (0, 0, 700, 120))
        s.blit(gs, (WIDTH//2 - 350, 50))

        for dx, dy, col in [(4, 4, BLACK), (0, 0, YELLOW)]:
            t1 = self.font_big.render("VOCÊ VENCEU!", True, col)
            s.blit(t1, (WIDTH//2 - t1.get_width()//2 + dx, 60 + dy))

        sub = self.font_med.render("O Monstro do Cálculo foi derrotado!", True, ORANGE)
        s.blit(sub, (WIDTH//2 - sub.get_width()//2, 130))

        draw_character(s, WIDTH//2, 260,
                       scale=2.2, tick=self.tick, on_ground=True)

        score_txt = self.font_med.render(
            f"Pontuação Final: {self.game.score}", True, YELLOW)
        s.blit(score_txt, (WIDTH//2 - score_txt.get_width()//2, 330))

        rank, rank_col = self._get_rank()
        rank_txt = self.font_med.render(f"Classificação: {rank}", True, rank_col)
        s.blit(rank_txt, (WIDTH//2 - rank_txt.get_width()//2, 368))

        stats = [
            f"Fases completadas: {sum(1 for u in self.game.unlocked[1:] if u)} / {len(REGIONS)}",
            f"Chefão derrotado: {'✓ SIM!' if self.game.boss_unlocked else '✗ NÃO'}",
        ]
        for i, st in enumerate(stats):
            t = self.font_sm.render(st, True, GRAY)
            s.blit(t, (WIDTH//2 - t.get_width()//2, 408 + i * 26))

        mx, my = pygame.mouse.get_pos()
        for btn, lbl, col in [
            (self.btn_restart, "[R]  Jogar Novamente", GREEN_DARK),
            (self.btn_menu,    "[M]  Menu Principal",  BLUE_DARK),
        ]:
            bc = tuple(min(255, v + 30) for v in col) if btn.collidepoint(mx, my) else col
            shadow = pygame.Rect(btn.x+3, btn.y+3, btn.w, btn.h)
            pygame.draw.rect(s, BLACK,  shadow, border_radius=12)
            pygame.draw.rect(s, bc,     btn,    border_radius=12)
            pygame.draw.rect(s, WHITE,  btn, 2, border_radius=12)
            t = self.font_btn.render(lbl, True, WHITE)
            s.blit(t, (btn.centerx - t.get_width()//2, btn.centery - t.get_height()//2))

    def _get_rank(self):
        score = self.game.score
        if score >= 250:
            return "MESTRE DO CÁLCULO", YELLOW
        elif score >= 180:
            return "EXPERT",           ORANGE
        elif score >= 120:
            return "AVANÇADO",         CYAN
        else:
            return "INICIANTE",        GRAY