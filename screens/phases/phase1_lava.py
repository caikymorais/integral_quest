import pygame, math, random
from settings import *
from screens.base_phase import BasePhase
from screens.player import PhysicsPlayer
from data.questions import QUESTIONS

class Phase1Lava(BasePhase):

    def _setup(self):
        self._build_level()

    def _build_level(self):
        q = QUESTIONS[self.region][self.q_index]
        self.lava_y      = float(HEIGHT + 200)
        self.lava_speed  = 0.0
        self.lava_rising = False
        self.player      = PhysicsPlayer(WIDTH // 2 - 14, HEIGHT - 160)

        self.platforms = [{
            "rect": pygame.Rect(0, HEIGHT - 60, WIDTH, 20),
            "label": "", "correct": False, "state": "idle",
            "color": DARK_GRAY, "is_floor": True
        }]

        n = len(q["opts"])
        xs = [int(WIDTH * (i + 1) / (n + 1)) - 90 for i in range(n)]
        for i, (opt, x) in enumerate(zip(q["opts"], xs)):
            y = HEIGHT - 160 - random.randint(0, 20)
            self.platforms.append({
                "rect":    pygame.Rect(x, y, 190, 22),
                "label":   opt,
                "correct": (i == q["correta"]),
                "state":   "idle",
                "color":   random.choice([BLUE, BLUE_DARK, PURPLE_DARK, TEAL]),
                "is_floor": False,
                "base_y":  float(y),
                "bob":     random.uniform(0, math.pi * 2),
            })

        self.rects_riemann = []
        for i in range(12):
            rx = 40 + i * 68
            rh = random.randint(30, 120)
            self.rects_riemann.append((rx, HEIGHT - 80, 60, rh))

    def _update_phase(self):
        if self.player.dead:
            if self.player.dead_timer > 45:
                self.player.dead = False
                self._respawn()
            return

        keys = pygame.key.get_pressed()
        flat = [{"rect": p["rect"]} for p in self.platforms]
        self.player.update(keys, flat)

        for p in self.platforms:
            if not p.get("is_floor"):
                p["rect"].y = int(p["base_y"] + math.sin(self.tick * 0.03 + p["bob"]) * 5)

        if self.lava_rising:
            self.lava_y -= self.lava_speed
            if self.answered:
                self.lava_speed = max(0, self.lava_speed - 0.05)

        if self.player.y + self.player.h >= self.lava_y:
            self.player.die()
            return

        if not self.answered:
            for p in self.platforms:
                if p.get("is_floor"): continue
                if (self.player.on_ground and
                        self.player.rect.colliderect(p["rect"]) and
                        p["state"] == "idle"):
                    p["state"] = "active"
                    self.attempts += 1
                    pts = self._award_points(p["correct"])
                    if p["correct"]:
                        p["color"]      = GREEN
                        self.lava_rising = False
                        self.lava_speed  = 0
                        self._set_feedback(True,
                            f"✓ +{pts}pts — {QUESTIONS[self.region][self.q_index]['feedback_ok']}")
                    else:
                        p["color"]       = RED
                        self.first_try   = False
                        self.lava_rising = True
                        self.lava_speed  = min(self.lava_speed + 0.5, 2.5)
                        self._set_feedback(False,
                            f"✗ {QUESTIONS[self.region][self.q_index]['feedback_erro']}",
                            duration=90)
                    break

    def _draw_background(self):
        s = self.game.screen
        for row in range(0, HEIGHT, 3):
            t = row / HEIGHT
            pygame.draw.line(s, (int(20+t*30), int(8+t*10), int(15+t*10)), (0,row),(WIDTH,row))

        for i, (rx, ry, rw, rh) in enumerate(self.rects_riemann):
            pygame.draw.rect(s, (40+i*6, 30, 80), (rx, ry-rh, rw, rh))
            pygame.draw.rect(s, (60,40,100), (rx, ry-rh, rw, rh), 1)

        if not self.lava_rising and not self.answered:
            warn = self.font_sm.render("Erre uma questão e a lava começa a subir!", True, ORANGE)
            s.blit(warn, (WIDTH//2 - warn.get_width()//2, 76))

    def _draw_hazards(self):
        s = self.game.screen
        lava_top = int(self.lava_y)
        if lava_top >= HEIGHT: return

        pts = [(0, HEIGHT), (0, lava_top)]
        for px in range(0, WIDTH + 10, 8):
            wave = math.sin(px * 0.04 + self.tick * 0.12) * 7
            pts.append((px, lava_top + int(wave)))
        pts.append((WIDTH, HEIGHT))
        pygame.draw.polygon(s, LAVA1, pts)

        for px in range(0, WIDTH, 6):
            wave = math.sin(px * 0.04 + self.tick * 0.12) * 7
            bright = int(140 + 80 * math.sin(px * 0.02 + self.tick * 0.06))
            pygame.draw.circle(s, (255, bright, 0), (px, lava_top + int(wave)), 2)

        lbl = self.font_sm.render("LAVA", True, YELLOW)
        s.blit(lbl, (8, min(lava_top + 4, HEIGHT - 20)))

    def _draw_platforms(self):
        s = self.game.screen
        for p in self.platforms:
            pygame.draw.rect(s, p["color"], p["rect"], border_radius=8)
            if not p.get("is_floor"):
                pygame.draw.rect(s, WHITE, p["rect"], 2, border_radius=8)
                txt = self.font.render(p["label"], True, WHITE)
                s.blit(txt, (p["rect"].centerx - txt.get_width()//2,
                             p["rect"].centery - txt.get_height()//2))