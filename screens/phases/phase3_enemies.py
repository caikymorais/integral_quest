import pygame, math, random
from settings import *
from screens.base_phase import BasePhase
from screens.player import PhysicsPlayer
from data.questions import QUESTIONS

class Enemy:
    def __init__(self, x, label, correct, direction):
        self.rect     = pygame.Rect(x, HEIGHT-110, 110, 40)
        self.label    = label
        self.correct  = correct
        self.vx       = direction * random.uniform(1.5, 2.8)
        self.alive    = True
        self.squash   = 0
        self.color    = (200,60,60) if not correct else (60,60,200)

    def update(self):
        self.rect.x += int(self.vx)
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.vx *= -1
        if self.squash > 0: self.squash -= 1

    def draw(self, surface, font):
        if not self.alive: return
        h = self.rect.h - self.squash*2
        r = pygame.Rect(self.rect.x, self.rect.y+self.squash, self.rect.w, h)
        pygame.draw.rect(surface, self.color, r, border_radius=10)
        pygame.draw.rect(surface, WHITE, r, 2, border_radius=10)
        # Olhinhos
        pygame.draw.circle(surface, WHITE,(r.x+20, r.y+14),6)
        pygame.draw.circle(surface, WHITE,(r.x+r.w-20, r.y+14),6)
        pygame.draw.circle(surface, BLACK,(r.x+21, r.y+14),3)
        pygame.draw.circle(surface, BLACK,(r.x+r.w-19, r.y+14),3)
        txt = font.render(self.label, True, WHITE)
        surface.blit(txt,(r.centerx-txt.get_width()//2, r.y+22))


class Phase3Enemies(BasePhase):
    """Inimigos andam pelo chão. Player pula em cima do correto para destruí-lo.
       Pular no errado tira uma vida."""

    def _setup(self):
        self._build_level()

    def _build_level(self):
        q = QUESTIONS[self.region][self.q_index]
        self.player = PhysicsPlayer(WIDTH//2-14, HEIGHT-200)
        # Plataforma chão
        self.platforms = [{"rect": pygame.Rect(0, HEIGHT-70, WIDTH, 20),
                           "label":"","correct":False,"state":"idle",
                           "color":DARK_GRAY,"is_floor":True}]
        # Plataformas flutuantes laterais
        for i in range(3):
            self.platforms.append({"rect": pygame.Rect(i*280+40, HEIGHT-230-i*40, 160, 18),
                                   "label":"","correct":False,"state":"idle",
                                   "color":(30,40,60),"is_floor":True})

        n = len(q["opts"])
        self.enemies = []
        xs = [80 + i*(WIDTH-160)//(n-1 if n>1 else 1) for i in range(n)]
        for i,(opt,x) in enumerate(zip(q["opts"],xs)):
            self.enemies.append(Enemy(x, opt, (i==q["correta"]), 1 if i%2==0 else -1))

        self.pit_rects = [pygame.Rect(-60, HEIGHT-70,60,100),
                          pygame.Rect(WIDTH, HEIGHT-70,60,100)]
        self.correct_killed = False

    def _update_phase(self):
        if self.player.dead:
            if self.player.dead_timer > 45:
                self.player.dead = False
                self._respawn()
            return

        keys = pygame.key.get_pressed()
        flat = [{"rect":p["rect"]} for p in self.platforms]
        self.player.update(keys, flat)

        for e in self.enemies:
            if e.alive: e.update()

        # Player cai no buraco
        if self.player.y > HEIGHT + 20:
            self.player.die(); return

        if not self.answered:
            for e in self.enemies:
                if not e.alive: continue
                # Pular em cima
                if (self.player.vy > 0 and
                        self.player.rect.colliderect(e.rect) and
                        self.player.y + self.player.h - self.player.vy <= e.rect.y + 6):
                    self.player.vy = -10
                    self.attempts += 1
                    e.squash = 8
                    pts = self._award_points(e.correct)
                    if e.correct:
                        e.alive = False
                        self.correct_killed = True
                        self._set_feedback(True,
                            f"✓ +{pts}pts — {QUESTIONS[self.region][self.q_index]['feedback_ok']}")
                    else:
                        e.alive = False
                        self.first_try = False
                        self._set_feedback(False,
                            QUESTIONS[self.region][self.q_index]["feedback_erro"],
                            duration=80)
                        self.player.die()
                    break

                # Colidir de lado
                if (self.player.rect.colliderect(e.rect) and
                        not (self.player.y + self.player.h - self.player.vy <= e.rect.y + 6)):
                    self.player.die(); return

    def _draw_background(self):
        s = self.game.screen
        for row in range(0,HEIGHT,3):
            t=row/HEIGHT
            pygame.draw.line(s,(int(15+t*15),int(10+t*10),int(30+t*20)),(0,row),(WIDTH,row))
        # Tijolos de fundo
        for bx in range(0,WIDTH,60):
            for by in range(72,HEIGHT-70,30):
                pygame.draw.rect(s,(25,20,35),(bx,by,58,28),1)

    def _draw_hazards(self):
        s = self.game.screen
        pygame.draw.rect(s,RED_DARK,(0,HEIGHT-70,WIDTH,70))
        for i in range(0,WIDTH,20):
            pygame.draw.line(s,ORANGE,(i,HEIGHT-70),(i+10,HEIGHT),2)

    def _draw_platforms(self):
        s = self.game.screen
        for p in self.platforms:
            pygame.draw.rect(s, p["color"], p["rect"], border_radius=4)
            pygame.draw.rect(s, (60,60,80), p["rect"], 1, border_radius=4)
        for e in self.enemies:
            e.draw(s, self.font)

    def _extra_draw(self):
        s = self.game.screen
        hint = self.font_sm.render("Pule em cima do inimigo CORRETO!", True, YELLOW)
        s.blit(hint,(WIDTH//2-hint.get_width()//2, 75))