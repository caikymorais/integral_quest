import pygame
import math
import random
from settings import *
from screens.base_phase import BasePhase
from screens.player import PhysicsPlayer
from data.questions import QUESTIONS


class Phase2Spikes(BasePhase):

    def _setup(self):
        self._build_level()

    def _build_level(self):
        q = QUESTIONS[self.region][self.q_index]
        self.player = PhysicsPlayer(WIDTH // 2 - 14, HEIGHT - 480)
        self.last_platform = None

        n  = len(q["opts"])
        xs = [int(WIDTH * (i + 1) / (n + 1)) - 95 for i in range(n)]

        self.platforms = [
            {"rect": pygame.Rect(0,   HEIGHT - 290, 130, 18),
             "label": "", "correct": False, "state": "solid",
             "color": (50, 50, 70), "is_answer": False, "visible": True, "fall_vy": 0.0},
            {"rect": pygame.Rect(770, HEIGHT - 290, 130, 18),
             "label": "", "correct": False, "state": "solid",
             "color": (50, 50, 70), "is_answer": False, "visible": True, "fall_vy": 0.0},
            {"rect": pygame.Rect(350, HEIGHT - 370, 200, 18),
             "label": "", "correct": False, "state": "solid",
             "color": (50, 50, 70), "is_answer": False, "visible": True, "fall_vy": 0.0},
        ]

        for i, (opt, x) in enumerate(zip(q["opts"], xs)):
            y = HEIGHT - 185 - i * 18
            self.platforms.append({
                "rect":      pygame.Rect(x, y, 200, 26),
                "label":     opt,
                "correct":   (i == q["correta"]),
                "state":     "idle",
                "color":     random.choice([BLUE, TEAL, PURPLE_DARK]),
                "is_answer": True,
                "visible":   True,
                "fall_vy":   0.0,
                "base_y":    float(y),
            })

        self.spikes = [pygame.Rect(sx, HEIGHT - 52, 30, 52) for sx in range(0, WIDTH, 40)]

    def _get_current_platform(self):
        if not self.player.on_ground:
            return None
        pr = self.player.rect
        for p in self.platforms:
            if not p["is_answer"]:
                continue
            if not p["visible"]:
                continue
            if p["state"] != "idle":
                continue
            if (pr.bottom >= p["rect"].top and
                    pr.bottom <= p["rect"].top + 20 and
                    pr.right  >  p["rect"].left + 10 and
                    pr.left   <  p["rect"].right - 10):
                return p
        return None

    def _update_phase(self):
        if self.player.dead:
            if self.player.dead_timer > 45:
                self.player.dead = False
                self.last_platform = None
                self._respawn()
            return

        keys = pygame.key.get_pressed()
        flat = [{"rect": p["rect"]} for p in self.platforms if p["visible"]]
        self.player.update(keys, flat)

        for p in self.platforms:
            if not p["is_answer"] or not p["visible"]:
                continue
            if p["state"] == "falling":
                p["fall_vy"] += 1.0
                p["rect"].y  += int(p["fall_vy"])
                if p["rect"].y > HEIGHT + 60:
                    p["visible"] = False

        for spike in self.spikes:
            if self.player.rect.colliderect(spike):
                self.player.die()
                return

        if self.player.y > HEIGHT + 20:
            self.player.die()
            return

        if self.answered:
            return

        current = self._get_current_platform()

        if current is not None and current != self.last_platform:
            self.last_platform = current
            self.attempts += 1
            pts = self._award_points(current["correct"])

            if current["correct"]:
                current["color"] = GREEN
                current["state"] = "active"
                self._set_feedback(
                    True,
                    f"✓ +{pts}pts — {QUESTIONS[self.region][self.q_index]['feedback_ok']}"
                )
            else:
                current["color"]   = RED
                current["state"]   = "falling"
                current["fall_vy"] = 3.0
                self.first_try     = False
                self._set_feedback(
                    False,
                    QUESTIONS[self.region][self.q_index]["feedback_erro"],
                    duration=90
                )

        if current is None:
            self.last_platform = None

    def _draw_background(self):
        s = self.game.screen
        for row in range(0, HEIGHT, 3):
            t = row / HEIGHT
            pygame.draw.line(s,
                (int(10 + t*20), int(20 + t*30), int(10 + t*15)),
                (0, row), (WIDTH, row))
        for i in range(12):
            nx  = (i * 157 + self.tick // 4) % WIDTH
            ny  = 80 + (i * 89) % (HEIGHT - 150)
            fog = pygame.Surface((80, 24), pygame.SRCALPHA)
            fog.fill((200, 200, 255, 10))
            s.blit(fog, (nx, ny))

    def _draw_hazards(self):
        s = self.game.screen
        pygame.draw.rect(s, RED_DARK, (0, HEIGHT - 52, WIDTH, 52))
        for spike in self.spikes:
            pts_tri = [
                (spike.x + 15, spike.y),
                (spike.x,      spike.y + spike.h),
                (spike.x + 30, spike.y + spike.h),
            ]
            pygame.draw.polygon(s, SPIKE, pts_tri)
            pygame.draw.polygon(s, WHITE, pts_tri, 1)

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
                    p["rect"].centery - txt.get_height() // 2
                ))

    def _extra_draw(self):
        s   = self.game.screen
        msg = self.font_sm.render(
            "Pule na resposta correta! Plataformas falsas caem nos espinhos.",
            True, YELLOW)
        s.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 76))