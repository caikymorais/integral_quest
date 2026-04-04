import pygame
import math
import random
from settings import *
from screens.base_phase import BasePhase
from screens.player import PhysicsPlayer
from data.questions import QUESTIONS


class Phase4Water(BasePhase):

    def _setup(self):
        self._build_level()

    def _build_level(self):
        q = QUESTIONS[self.region][self.q_index]
        self.player      = PhysicsPlayer(WIDTH // 2 - 14, HEIGHT - 368)
        self.water_y     = float(HEIGHT + 80)
        self.water_speed = 0.15
        self.stage       = "u"
        self.chosen_u    = None
        self.last_platform = None

        self.correct_u  = q["opts"][q["correta"]]
        self.correct_dv = q["opts"][(q["correta"] + 1) % len(q["opts"])]

        self.platforms = [
            # Plataformas sólidas de travessia — mais separadas das respostas
            {"rect": pygame.Rect(0,   HEIGHT - 120, 160, 18),
             "label": "", "opt": "", "correct": False, "state": "solid",
             "color": (50, 50, 70), "is_floor": True, "is_answer": False,
             "visible": True, "base_y": float(HEIGHT - 120), "bob": 0.0, "side": 0},
            {"rect": pygame.Rect(740, HEIGHT - 120, 160, 18),
             "label": "", "opt": "", "correct": False, "state": "solid",
             "color": (50, 50, 70), "is_floor": True, "is_answer": False,
             "visible": True, "base_y": float(HEIGHT - 120), "bob": 0.0, "side": 1},
            # Plataforma segura central — player nasce aqui
            {"rect": pygame.Rect(330, HEIGHT - 320, 240, 18),
             "label": "", "opt": "", "correct": False, "state": "solid",
             "color": (50, 50, 70), "is_floor": True, "is_answer": False,
             "visible": True, "base_y": float(HEIGHT - 320), "bob": 0.0, "side": 0},
        ]

        opts     = q["opts"][:]
        shuffled = opts[:]
        random.shuffle(shuffled)

        for i, opt in enumerate(shuffled):
            side       = i % 2
            x          = (50 + (i // 2) * 200) if side == 0 else (WIDTH // 2 + 50 + (i // 2) * 200)
            y          = HEIGHT - 200 - (i // 2) * 55
            is_correct = (opt == self.correct_u or opt == self.correct_dv)
            self.platforms.append({
                "rect":      pygame.Rect(x, y, 175, 26),
                "label":     opt,
                "opt":       opt,
                "correct":   is_correct,
                "state":     "idle",
                # Verde = gabarito (remova após testes)
                "color":     GREEN if is_correct else (BLUE if side == 0 else PURPLE_DARK),
                "is_floor":  False,
                "is_answer": True,
                "visible":   True,
                "base_y":    float(y),
                "bob":       random.uniform(0, math.pi * 2),
                "side":      side,
            })

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
            plat = p["rect"]
            if (pr.bottom >= plat.top and
                    pr.bottom <= plat.top + 20 and
                    pr.right  >  plat.left + 10 and
                    pr.left   <  plat.right - 10):
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

        # Bob das plataformas de resposta
        for p in self.platforms:
            if p["is_answer"] and p["visible"]:
                p["rect"].y = int(p["base_y"] + math.sin(self.tick * 0.025 + p["bob"]) * 5)

        # Água sobe
        self.water_y -= self.water_speed

        # Água mata
        if self.player.y + self.player.h >= self.water_y:
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
            opt = current["opt"]

            if self.stage == "u":
                if opt == self.correct_u:
                    current["state"] = "active"
                    current["color"] = CYAN
                    self.chosen_u    = opt
                    self.stage       = "dv"
                    self.water_speed = max(0.05, self.water_speed - 0.05)
                else:
                    current["state"] = "wrong"
                    current["color"] = RED
                    self.first_try   = False
                    self.water_speed += 0.15
                    self._set_feedback(False,
                        f"u={opt} não é a melhor escolha. Tente outro.",
                        duration=80)

            elif self.stage == "dv":
                self.attempts += 1
                pts = self._award_points(opt == self.correct_dv)
                if opt == self.correct_dv:
                    current["color"] = GREEN
                    current["state"] = "active"
                    self.water_speed = 0
                    self._set_feedback(True,
                        f"✓ +{pts}pts — {QUESTIONS[self.region][self.q_index]['feedback_ok']}")
                else:
                    current["color"] = RED
                    current["state"] = "wrong"
                    self.first_try   = False
                    self.water_speed += 0.15
                    self._set_feedback(False,
                        QUESTIONS[self.region][self.q_index]["feedback_erro"],
                        duration=80)

        if current is None:
            self.last_platform = None

    def _draw_background(self):
        s = self.game.screen
        for row in range(0, HEIGHT, 3):
            t = row / HEIGHT
            pygame.draw.line(s,
                (int(8 + t*12), int(15 + t*20), int(30 + t*40)),
                (0, row), (WIDTH, row))

        # Divisória u / dv
        pygame.draw.line(s, (50, 50, 80), (WIDTH//2, 72), (WIDTH//2, HEIGHT - 60), 1)
        u_lbl = self.font.render("← escolha  u", True, CYAN)
        d_lbl = self.font.render("escolha dv  →", True, PURPLE)
        s.blit(u_lbl, (WIDTH//4  - u_lbl.get_width()//2, 76))
        s.blit(d_lbl, (3*WIDTH//4 - d_lbl.get_width()//2, 76))

    def _draw_hazards(self):
        s  = self.game.screen
        wy = int(self.water_y)
        if wy >= HEIGHT:
            return

        pts = [(0, HEIGHT), (0, wy)]
        for px in range(0, WIDTH + 10, 10):
            wave = math.sin(px * 0.03 + self.tick * 0.08) * 8
            pts.append((px, wy + int(wave)))
        pts.append((WIDTH, HEIGHT))
        pygame.draw.polygon(s, WATER, pts)

        for px in range(0, WIDTH, 8):
            wave = math.sin(px * 0.03 + self.tick * 0.08) * 8
            pygame.draw.circle(s, WATER_LIGHT, (px, wy + int(wave)), 2)

        lbl = self.font_sm.render("💧 ÁGUA", True, CYAN)
        s.blit(lbl, (8, min(wy + 4, HEIGHT - 20)))

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
        s = self.game.screen

        # Etapa atual
        stage_txt = f"Etapa: escolha  {'u' if self.stage == 'u' else 'dv'}"
        if self.chosen_u:
            stage_txt += f"   (u = {self.chosen_u} ✓)"
        lbl = self.font.render(stage_txt, True, YELLOW)
        s.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 95))

        # Fórmula
        formula = self.font.render("∫u dv  =  uv  −  ∫v du", True, GRAY)
        s.blit(formula, (WIDTH//2 - formula.get_width()//2, 115))

        # Legenda das plataformas seguras
        hint = self.font_sm.render(
            "Plataformas cinzas = zona segura  |  Coloridas = respostas",
            True, (120, 120, 140))
        s.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 38))