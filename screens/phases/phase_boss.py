import pygame
import math
import random
from settings import *
from screens.base_phase import BasePhase
from screens.player import PhysicsPlayer


BOSS_QUESTIONS = [
    {
        "enunciado": "∫ (3x² + 2x) dx = ?",
        "opts": ["x³ + x² + C", "6x + 2 + C", "x³ + x + C", "3x³ + x² + C"],
        "correta": 0,
        "feedback_ok": "Correto! Integre termo a termo: ∫3x²dx + ∫2xdx = x³ + x² + C.",
        "feedback_erro": "Errado. Integre termo a termo: x³ + x² + C.",
    },
    {
        "enunciado": "∫[0,1] (x² + 1) dx = ?",
        "opts": ["4/3", "1/3", "2", "1"],
        "correta": 0,
        "feedback_ok": "Correto! F(x)=x³/3+x → F(1)-F(0) = 1/3+1 = 4/3.",
        "feedback_erro": "Errado. F(x)=x³/3+x → F(1)-F(0) = 4/3.",
    },
    {
        "enunciado": "Para ∫ sin(x)·cos(x) dx, use u = sin(x). Resultado:",
        "opts": ["sin²(x)/2 + C", "cos²(x)/2 + C", "-cos(2x)/2 + C", "sin(x)cos(x) + C"],
        "correta": 0,
        "feedback_ok": "Correto! u=sin(x), du=cos(x)dx → ∫u du = u²/2 = sin²(x)/2 + C.",
        "feedback_erro": "Errado. Com u=sin(x): sin²(x)/2 + C.",
    },
    {
        "enunciado": "∫ ln(x) dx = ? (use integração por partes)",
        "opts": ["x·ln(x) − x + C", "x/ln(x) + C", "ln²(x)/2 + C", "1/x + C"],
        "correta": 0,
        "feedback_ok": "Correto! u=ln(x), dv=dx → x·ln(x) − ∫x·(1/x)dx = x·ln(x) − x + C.",
        "feedback_erro": "Errado. Por partes: x·ln(x) − x + C.",
    },
    {
        "enunciado": "∫[1,e] ln(x) dx = ?",
        "opts": ["1", "e−1", "e", "2"],
        "correta": 0,
        "feedback_ok": "Correto! F(x)=x·ln(x)−x → F(e)−F(1) = (e−e)−(0−1) = 1.",
        "feedback_erro": "Errado. F(e)−F(1) = 1.",
    },
]


class BossMonster:

    def __init__(self):
        self.x           = float(WIDTH // 2)
        self.y           = float(130)
        self.hp          = 5
        self.max_hp      = 5
        self.phase       = 0
        self.tick        = 0
        self.anger       = 0.0
        self.projectiles = []
        self.stun_timer  = 0
        self.shake       = 0

    @property
    def cx(self): return int(self.x)
    @property
    def cy(self): return int(self.y)

    def take_hit(self):
        self.hp         = max(0, self.hp - 1)
        self.stun_timer = 40
        self.phase      = 2
        self.shake      = 20

    def get_angry(self):
        self.anger = min(1.0, self.anger + 0.2)

    def update(self, tick, player_x):
        self.tick = tick
        if self.shake > 0:
            self.shake -= 1

        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0:
                self.phase = 0
            return

        self.x = WIDTH // 2 + math.sin(tick * 0.02) * 120

        interval = max(40, 90 - int(self.anger * 50))
        if tick % interval == 0 and self.hp > 0:
            speed = 4 + self.anger * 3
            angle = math.atan2(player_x - self.cx, 0) + random.uniform(-0.3, 0.3)
            self.projectiles.append({
                "x": float(self.cx),
                "y": float(self.cy + 60),
                "vx": math.sin(angle) * speed,
                "vy": 5 + self.anger * 2,
            })
            if self.anger > 0.5:
                for da in [-0.5, 0.5]:
                    self.projectiles.append({
                        "x": float(self.cx),
                        "y": float(self.cy + 60),
                        "vx": math.sin(angle + da) * speed,
                        "vy": 5 + self.anger * 2,
                    })

        for p in self.projectiles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
        self.projectiles = [p for p in self.projectiles
                            if 0 < p["x"] < WIDTH and p["y"] < HEIGHT + 20]

    def draw(self, surface, tick):
        sx      = int(self.shake * math.sin(tick * 1.2)) if self.shake > 0 else 0
        cx      = self.cx + sx
        cy      = self.cy
        stunned = self.stun_timer > 0
        anger_c = int(self.anger * 200)

        pygame.draw.ellipse(surface, (20, 10, 10), (cx-65, cy+90, 130, 24))

        body_col = (min(255, 80 + anger_c), 20, 20) if not stunned else (100, 100, 180)
        pygame.draw.ellipse(surface, body_col, (cx-60, cy-40, 120, 140))
        pygame.draw.ellipse(surface,
            (200, 50, 50) if not stunned else (150, 150, 255),
            (cx-60, cy-40, 120, 140), 3)

        for i in range(6):
            angle = (i / 6) * math.pi * 2 + tick * 0.04
            tx1 = cx + int(50 * math.cos(angle))
            ty1 = cy + int(40 * math.sin(angle) * 0.5) + 30
            tx2 = cx + int(90 * math.cos(angle + 0.3))
            ty2 = cy + int(70 * math.sin(angle * 1.3)) + 60
            col_t = (min(255, 180 + anger_c), 30, 30) if not stunned else (80, 80, 200)
            pygame.draw.line(surface, col_t, (tx1, ty1), (tx2, ty2), 4)
            pygame.draw.circle(surface, col_t, (tx2, ty2), 6)

        eye_blink = (tick % 90 > 85)
        for ex, ey_off in [(-20, -15), (20, -15)]:
            pygame.draw.circle(surface, (255, 220, 0), (cx+ex, cy+ey_off), 14)
            if not eye_blink:
                pygame.draw.circle(surface, (10, 10, 10),    (cx+ex+3, cy+ey_off), 7)
                pygame.draw.circle(surface, (255, 255, 255), (cx+ex+5, cy+ey_off-4), 3)
            else:
                pygame.draw.line(surface, (10, 10, 10),
                    (cx+ex-10, cy+ey_off), (cx+ex+10, cy+ey_off), 3)

        if stunned:
            pygame.draw.arc(surface, (150, 150, 255),
                (cx-20, cy+25, 40, 20), 0, math.pi, 3)
        else:
            pygame.draw.arc(surface, (255, 100, 0),
                (cx-25, cy+20, 50, 25), math.pi, 2*math.pi, 3)
            for d in range(-15, 16, 10):
                pygame.draw.polygon(surface, WHITE, [
                    (cx+d,   cy+28),
                    (cx+d+5, cy+28),
                    (cx+d+2, cy+38),
                ])

        font_big = pygame.font.SysFont("Arial", 36, bold=True)
        sym = font_big.render("∫", True, (255, 200, 0) if not stunned else WHITE)
        surface.blit(sym, (cx - sym.get_width()//2, cy+5))

        bar_w = 140
        bar_x = cx - bar_w // 2
        bar_y = cy - 70
        pygame.draw.rect(surface, (60, 20, 20), (bar_x, bar_y, bar_w, 14), border_radius=4)
        hp_pct = self.hp / self.max_hp
        hp_col = GREEN if hp_pct > 0.5 else (YELLOW if hp_pct > 0.25 else RED)
        pygame.draw.rect(surface, hp_col,
            (bar_x, bar_y, int(bar_w * hp_pct), 14), border_radius=4)
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, 14), 2, border_radius=4)
        hp_txt = pygame.font.SysFont("Arial", 11, bold=True).render(
            f"HP: {self.hp}/{self.max_hp}", True, WHITE)
        surface.blit(hp_txt, (cx - hp_txt.get_width()//2, bar_y+1))

        for proj in self.projectiles:
            px, py = int(proj["x"]), int(proj["y"])
            pygame.draw.circle(surface, (255, 80, 0), (px, py), 10)
            pygame.draw.circle(surface, YELLOW, (px, py), 10, 2)
            pt = pygame.font.SysFont("Arial", 9, bold=True).render("dx", True, WHITE)
            surface.blit(pt, (px - pt.get_width()//2, py - pt.get_height()//2))

        if self.anger > 0.3:
            aura    = pygame.Surface((160, 200), pygame.SRCALPHA)
            a_alpha = int(self.anger * 60)
            pygame.draw.ellipse(aura, (255, 50, 0, a_alpha), (0, 0, 160, 200))
            surface.blit(aura, (cx-80, cy-60))


class PhaseBoss(BasePhase):

    LIVES = 5

    def __init__(self, game):
        self.game           = game
        self.region         = "Chefão"
        self.q_index        = 0
        self.lives          = self.LIVES
        self.hits           = 0
        self.first_try      = True
        self.attempts       = 0
        self.font           = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_q         = pygame.font.SysFont("Arial", 19, bold=True)
        self.font_sm        = pygame.font.SysFont("Arial", 15)
        self.feedback_timer = 0
        self.feedback_text  = ""
        self.feedback_color = WHITE
        self.answered       = False
        self.tick           = 0
        self.scroll_y       = 0.0
        self.platforms      = []
        self.hazards        = []
        self.player         = None
        self._setup()

    def _setup(self):
        self.questions    = BOSS_QUESTIONS[:]
        self.q_index      = 0
        self.hits         = 0
        self.boss         = BossMonster()
        self.boss_beaten  = False
        self.intro_timer  = 90
        self.flash_timer  = 0
        self.flash_col    = WHITE
        self.last_platform = None
        self._build_level()

    def _build_level(self):
        self.player        = PhysicsPlayer(80, HEIGHT - 180)
        self.answered      = False
        self.first_try     = True
        self.attempts      = 0
        self.last_platform = None

        q = self.questions[self.q_index]
        n = len(q["opts"])

        self.platforms = [
            {"rect": pygame.Rect(0,   HEIGHT-90,  200, 18),
             "label": "", "correct": False, "state": "solid",
             "color": (40,40,60), "is_answer": False, "visible": True},
            {"rect": pygame.Rect(700, HEIGHT-90,  200, 18),
             "label": "", "correct": False, "state": "solid",
             "color": (40,40,60), "is_answer": False, "visible": True},
            {"rect": pygame.Rect(300, HEIGHT-200, 300, 18),
             "label": "", "correct": False, "state": "solid",
             "color": (40,40,60), "is_answer": False, "visible": True},
        ]

        xs = [int(WIDTH * (i+1) / (n+1)) - 95 for i in range(n)]
        ys = [HEIGHT-300, HEIGHT-340, HEIGHT-310, HEIGHT-350]
        for i, (opt, x) in enumerate(zip(q["opts"], xs)):
            y = ys[i % len(ys)]
            self.platforms.append({
                "rect":      pygame.Rect(x, y, 195, 26),
                "label":     opt,
                "correct":   (i == q["correta"]),
                "state":     "idle",
                "color":     random.choice([BLUE, TEAL, PURPLE_DARK, BLUE_DARK]),
                "is_answer": True,
                "visible":   True,
                "base_y":    float(y),
                "bob":       random.uniform(0, math.pi*2),
            })

    def _get_current_platform(self):
        if not self.player.on_ground:
            return None
        pr = self.player.rect
        for p in self.platforms:
            if not p["is_answer"] or not p["visible"] or p["state"] != "idle":
                continue
            plat = p["rect"]
            if (pr.bottom >= plat.top and
                    pr.bottom <= plat.top + 20 and
                    pr.right  >  plat.left + 10 and
                    pr.left   <  plat.right - 10):
                return p
        return None

    def _update_phase(self):
        if self.intro_timer > 0:
            self.intro_timer -= 1
            return

        if self.boss_beaten:
            return

        if self.player.dead:
            if self.player.dead_timer > 45:
                self.player.dead   = False
                self.last_platform = None
                self._respawn()
            return

        keys = pygame.key.get_pressed()
        flat = [{"rect": p["rect"]} for p in self.platforms if p["visible"]]
        self.player.update(keys, flat)

        for p in self.platforms:
            if p["is_answer"] and p["visible"]:
                p["rect"].y = int(p["base_y"] + math.sin(self.tick*0.025 + p["bob"]) * 5)

        self.boss.update(self.tick, self.player.x)

        for proj in list(self.boss.projectiles):
            pr = pygame.Rect(int(proj["x"])-10, int(proj["y"])-10, 20, 20)
            if self.player.rect.colliderect(pr) and not self.player.dead:
                self.player.die()
                self.boss.get_angry()
                self.boss.projectiles.remove(proj)
                break

        if self.player.y > HEIGHT + 20:
            self.player.die()
            return

        if self.flash_timer > 0:
            self.flash_timer -= 1

        if self.answered:
            return

        current = self._get_current_platform()
        if current is not None and current != self.last_platform:
            self.last_platform = current
            self.attempts     += 1

            if current["correct"]:
                current["color"]  = GREEN
                current["state"]  = "active"
                self.hits        += 1
                pts = PONTOS_POR_ACERTO_PRIMEIRA if self.first_try else PONTOS_POR_ACERTO_SEGUNDA
                pts += 10
                self.game.score  += pts
                self.boss.take_hit()
                self.flash_timer  = 15
                self.flash_col    = GREEN

                if self.boss.hp <= 0:
                    self.boss_beaten    = True
                    self.feedback_timer = 180
                    self.feedback_text  = "CHEFÃO DERROTADO! Você dominou o Cálculo!"
                    self.feedback_color = YELLOW
                    self.game.score    += 50
                    return

                self._set_feedback(True,
                    f"✓ +{pts}pts — Dano! HP: {self.boss.hp}/{self.boss.max_hp} — "
                    f"{self.questions[self.q_index]['feedback_ok']}")
                self.answered       = True
                self.feedback_timer = 100
            else:
                current["color"] = RED
                current["state"] = "wrong"
                self.first_try   = False
                self.boss.get_angry()
                self.flash_timer = 15
                self.flash_col   = RED
                self._set_feedback(False,
                    self.questions[self.q_index]["feedback_erro"],
                    duration=90)

        if current is None:
            self.last_platform = None

    def _next_question(self):
        self.q_index += 1
        if self.q_index >= len(self.questions) or self.boss_beaten:
            if self.boss.hp <= 0:
                self.game.score += PONTOS_BONUS_FASE_PERFEITA
            self.game.go_to_victory()
            return
        self.answered      = False
        self.first_try     = True
        self.attempts      = 0
        self.last_platform = None
        self._build_level()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game.go_to_map()
                if self.boss_beaten:
                    self.game.go_to_victory()

    def update(self):
        self.tick += 1
        self._update_phase()
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0:
                if self.boss_beaten:
                    self.game.go_to_victory()
                elif self.answered:
                    self._next_question()

    def draw(self):
        self.game.screen.fill(BG_COLOR)
        self._draw_background()
        self._draw_platforms()
        if self.player and not self.boss_beaten:
            self.player.draw(self.game.screen)
        self._extra_draw()
        self._draw_hud()

    def _draw_background(self):
        s = self.game.screen
        for row in range(0, HEIGHT, 3):
            t = row / HEIGHT
            pygame.draw.line(s,
                (int(15+t*10), int(5+t*5), int(30+t*20)),
                (0, row), (WIDTH, row))

        for i in range(4):
            lx = (i * 230 + self.tick * 2) % WIDTH
            if (self.tick // 20 + i) % 3 == 0:
                pygame.draw.line(s, (80, 50, 120), (lx, 0), (lx+30, HEIGHT), 1)

        pygame.draw.rect(s, (30, 20, 40), (0, HEIGHT-70, WIDTH, 70))
        for bx in range(0, WIDTH, 80):
            pygame.draw.rect(s, (40, 30, 55), (bx, HEIGHT-70, 78, 68), 1)

        if self.flash_timer > 0:
            fl    = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            alpha = int(self.flash_timer * 8)
            fl.fill((*self.flash_col, alpha))
            s.blit(fl, (0, 0))

    def _draw_hazards(self):
        pass

    def _draw_platforms(self):
        s = self.game.screen
        for p in self.platforms:
            if not p["visible"]:
                continue
            pygame.draw.rect(s, p["color"], p["rect"], border_radius=8)
            pygame.draw.rect(s, WHITE, p["rect"], 2, border_radius=8)
            if p["is_answer"] and p["label"]:
                txt = self.font.render(p["label"], True, WHITE)
                s.blit(txt, (
                    p["rect"].centerx - txt.get_width()  // 2,
                    p["rect"].centery - txt.get_height() // 2,
                ))

    def _extra_draw(self):
        s = self.game.screen

        if self.intro_timer > 0:
            alpha = min(255, self.intro_timer * 4)
            ov    = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, alpha))
            s.blit(ov, (0, 0))
            txt = pygame.font.SysFont("Arial", 42, bold=True).render(
                "⚔ MONSTRO DO CÁLCULO", True, RED)
            s.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 30))
            sub = pygame.font.SysFont("Arial", 20).render(
                "Pule nas respostas certas para dar dano!", True, YELLOW)
            s.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 30))
            return

        self.boss.draw(s, self.tick)

        if self.boss_beaten:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 160))
            s.blit(ov, (0, 0))
            f1 = pygame.font.SysFont("Arial", 52, bold=True)
            f2 = pygame.font.SysFont("Arial", 22)
            t1 = f1.render("VITÓRIA FINAL!", True, YELLOW)
            t2 = f2.render(f"Pontuação total: {self.game.score}", True, WHITE)
            t3 = f2.render("Pressione qualquer tecla para continuar...", True, GRAY)
            s.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 80))
            s.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
            s.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 50))

    def _draw_hud(self):
        s = self.game.screen
        q = self.questions[self.q_index] if self.q_index < len(self.questions) else None

        pygame.draw.rect(s, (20, 5, 20), (0, 0, WIDTH, 72))
        pygame.draw.line(s, RED, (0, 72), (WIDTH, 72), 1)

        reg = self.font_sm.render(
            f"☠ CHEFÃO  |  Q{self.q_index+1}/{len(self.questions)}  |  ⭐ {self.game.score}",
            True, RED)
        s.blit(reg, (10, 5))

        for i in range(self.LIVES):
            col = RED if i < self.lives else DARK_GRAY
            pygame.draw.circle(s, col, (WIDTH - 30 - i*28, 16), 10)
            pygame.draw.circle(s, WHITE, (WIDTH - 30 - i*28, 16), 10, 2)

        if q:
            self._wrap(q["enunciado"], 10, 28, WIDTH-20, self.font_q, YELLOW)

        ctrl = self.font_sm.render(
            "← → / A D  mover  |  W / ↑ / ESPAÇO  pular  |  ESC  mapa",
            True, (80, 60, 80))
        s.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, HEIGHT-18))

        if self.feedback_timer > 0:
            fb_surf = pygame.Surface((WIDTH, 38), pygame.SRCALPHA)
            fb_surf.fill((0, 0, 0, 180))
            s.blit(fb_surf, (0, HEIGHT-56))
            self._wrap(self.feedback_text, 10, HEIGHT-52, WIDTH-20,
                       self.font_sm, self.feedback_color)