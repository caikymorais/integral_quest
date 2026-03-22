import pygame
import math
from settings import *


def draw_character(surface, cx, cy, scale=1.0, tick=0, facing=1, on_ground=True, dead=False):
    s = scale
    run = math.sin(tick * 0.2) * 7 * s if (on_ground and not dead) else 0
    air = math.sin(tick * 0.1) * 2 * s if not on_ground else 0
    rot = math.radians(90 * min(1.0, tick / 10)) if dead else 0

    def pt(x, y):
        # Rotaciona em torno de (cx, cy) se morto
        if dead:
            dx, dy = x - cx, y - cy
            nx = dx * math.cos(rot) - dy * math.sin(rot)
            ny = dx * math.sin(rot) + dy * math.cos(rot)
            return (int(cx + nx), int(cy + ny))
        return (int(x), int(y))

    # --- Pernas ---
    leg_l = pygame.Rect(int(cx-12*s), int(cy+18*s+air), int(10*s), int(22*s+run))
    leg_r = pygame.Rect(int(cx+2*s),  int(cy+18*s+air), int(10*s), int(22*s-run))
    pygame.draw.rect(surface, PANTS, leg_l, border_radius=4)
    pygame.draw.rect(surface, PANTS, leg_r, border_radius=4)
    # Sapatos
    pygame.draw.ellipse(surface, SHOE, (int(cx-14*s), int(cy+38*s+abs(run)+air), int(14*s), int(8*s)))
    pygame.draw.ellipse(surface, SHOE, (int(cx+2*s),  int(cy+38*s+abs(run)+air), int(14*s), int(8*s)))

    # --- Corpo ---
    body = pygame.Rect(int(cx-13*s), int(cy+air), int(26*s), int(22*s))
    pygame.draw.rect(surface, SHIRT, body, border_radius=6)
    # Detalhe camisa — listra
    pygame.draw.rect(surface, BLUE_LIGHT,
        (int(cx-13*s), int(cy+8*s+air), int(26*s), int(5*s)))

    # --- Braços ---
    arm_swing = math.sin(tick * 0.2) * 10 * s if on_ground else 0
    pygame.draw.rect(surface, SKIN,
        (int(cx-22*s), int(cy+2*s+arm_swing+air), int(9*s), int(18*s)), border_radius=5)
    pygame.draw.rect(surface, SKIN,
        (int(cx+13*s), int(cy+2*s-arm_swing+air), int(9*s), int(18*s)), border_radius=5)
    # Luvas
    pygame.draw.circle(surface, (220,80,80),
        (int(cx-17*s), int(cy+18*s+arm_swing+air)), int(5*s))
    pygame.draw.circle(surface, (220,80,80),
        (int(cx+17*s), int(cy+18*s-arm_swing+air)), int(5*s))

    # --- Pescoço ---
    pygame.draw.rect(surface, SKIN,
        (int(cx-4*s), int(cy-5*s+air), int(8*s), int(7*s)))

    # --- Cabeça ---
    head_rect = (int(cx-16*s), int(cy-30*s+air), int(32*s), int(28*s))
    pygame.draw.ellipse(surface, SKIN, head_rect)
    # Cabelo
    pygame.draw.ellipse(surface, HAIR,
        (int(cx-16*s), int(cy-32*s+air), int(32*s), int(16*s)))
    # Franja
    pygame.draw.rect(surface, HAIR,
        (int(cx-16*s), int(cy-20*s+air), int(10*s), int(6*s)), border_radius=3)

    # Olhos
    eye_x = cx + facing * 5 * s
    pygame.draw.circle(surface, WHITE, (int(eye_x), int(cy-17*s+air)), int(5*s))
    pygame.draw.circle(surface, (30,30,80), (int(eye_x+facing*1.5*s), int(cy-17*s+air)), int(3*s))
    pygame.draw.circle(surface, WHITE, (int(eye_x+facing*1*s), int(cy-18*s+air)), int(1*s))  # reflexo

    if dead:
        # X nos olhos
        pygame.draw.line(surface, RED,
            (int(eye_x-3*s), int(cy-20*s+air)),
            (int(eye_x+3*s), int(cy-14*s+air)), max(1,int(2*s)))
        pygame.draw.line(surface, RED,
            (int(eye_x+3*s), int(cy-20*s+air)),
            (int(eye_x-3*s), int(cy-14*s+air)), max(1,int(2*s)))
    else:
        # Sorriso
        pygame.draw.arc(surface, (200, 100, 100),
            (int(cx-7*s), int(cy-13*s+air), int(14*s), int(8*s)),
            math.pi+0.3, 2*math.pi-0.3, max(1,int(2*s)))

    # Capacete/boné
    pygame.draw.rect(surface, BLUE_DARK,
        (int(cx-16*s), int(cy-33*s+air), int(32*s), int(8*s)), border_radius=5)


class PhysicsPlayer:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.w = 28
        self.h = 48
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.tick = 0
        self.speed = 5.2
        self.jump_force = -15.5
        self.gravity = 0.72
        self.dead = False
        self.dead_timer = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, keys, platforms, scroll_y=0):
        if self.dead:
            self.dead_timer += 1
            self.vy += self.gravity
            self.y += self.vy
            return

        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:
            self.vx = -self.speed; self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed;  self.facing = 1
        else:
            self.vx *= 0.75

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = self.jump_force

        self.vy = min(self.vy + self.gravity, 20)
        self.x = max(0, min(WIDTH - self.w, self.x + self.vx))

        self.y += self.vy
        self.on_ground = False
        for p in platforms:
            pr = p["rect"]
            if (self.rect.colliderect(pr) and self.vy >= 0
                    and self.y + self.h - self.vy <= pr.y + 8):
                self.y = pr.y - self.h
                self.vy = 0
                self.on_ground = True

        if self.on_ground or abs(self.vx) > 0.5:
            self.tick += 1

    def die(self):
        if not self.dead:
            self.dead = True
            self.dead_timer = 0
            self.vy = -8

    def draw(self, surface, scale=1.0):
        draw_character(surface,
                       self.x + self.w // 2,
                       self.y + self.h // 2 - 4,
                       scale=scale,
                       tick=self.tick,
                       facing=self.facing,
                       on_ground=self.on_ground,
                       dead=self.dead)