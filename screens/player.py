import pygame
import math
from settings import *

_CHAR_W, _CHAR_H = 80, 120
_CHAR_CX, _CHAR_CY = _CHAR_W // 2, 45


def draw_character(surface, cx, cy, scale=1.0, tick=0, facing=1,
                   on_ground=True, dead=False):
    run       = math.sin(tick * 0.2) * 7 if (on_ground and not dead) else 0
    air       = math.sin(tick * 0.1) * 2 if not on_ground else 0
    arm_swing = math.sin(tick * 0.2) * 10 if on_ground else 0
    rot_angle = 90 * min(1.0, tick / 10) if dead else 0

    cs = pygame.Surface((_CHAR_W, _CHAR_H), pygame.SRCALPHA)
    lx, ly = _CHAR_CX, _CHAR_CY

    a = int(air)
    r = int(run)
    sw = int(arm_swing)

    pygame.draw.rect(cs, PANTS, (lx-12, ly+18+a, 10, 22+r), border_radius=4)
    pygame.draw.rect(cs, PANTS, (lx+2, ly+18+a, 10, 22-r), border_radius=4)

    pygame.draw.ellipse(cs, SHOE, (lx-14, ly+38+abs(r)+a, 14, 8))
    pygame.draw.ellipse(cs, SHOE, (lx+2, ly+38+abs(r)+a, 14, 8))

    pygame.draw.rect(cs, SHIRT, (lx-13, ly+a, 26, 22), border_radius=6)
    pygame.draw.rect(cs, BLUE_LIGHT, (lx-13, ly+8+a, 26, 5))

    pygame.draw.rect(cs, SKIN, (lx-22, ly+2+sw+a, 9, 18), border_radius=5)
    pygame.draw.rect(cs, SKIN, (lx+13, ly+2-sw+a, 9, 18), border_radius=5)
    pygame.draw.circle(cs, (220, 80, 80), (lx-17, ly+18+sw+a), 5)
    pygame.draw.circle(cs, (220, 80, 80), (lx+17, ly+18-sw+a), 5)

    pygame.draw.rect(cs, SKIN, (lx-4, ly-5+a, 8, 7))

    pygame.draw.ellipse(cs, SKIN, (lx-16, ly-30+a, 32, 28))
    pygame.draw.ellipse(cs, HAIR, (lx-16, ly-32+a, 32, 16))
    pygame.draw.rect(cs, HAIR, (lx-16, ly-20+a, 10, 6), border_radius=3)

    pygame.draw.circle(cs, WHITE, (lx+5, ly-17+a), 5)
    pygame.draw.circle(cs, (30, 30, 80), (lx+7, ly-17+a), 3)
    pygame.draw.circle(cs, WHITE, (lx+6, ly-18+a), 1)

    if dead:
        pygame.draw.line(cs, RED, (lx+2, ly-20+a), (lx+8, ly-14+a), 2)
        pygame.draw.line(cs, RED, (lx+8, ly-20+a), (lx+2, ly-14+a), 2)
    else:
        pygame.draw.arc(cs, (200, 100, 100),
                        (lx-7, ly-13+a, 14, 8),
                        math.pi + 0.3, 2 * math.pi - 0.3, 2)

    pygame.draw.rect(cs, BLUE_DARK, (lx-16, ly-33+a, 32, 8), border_radius=5)

    if scale != 1.0:
        new_w = max(1, int(_CHAR_W * scale))
        new_h = max(1, int(_CHAR_H * scale))
        cs = pygame.transform.smoothscale(cs, (new_w, new_h))

    if facing == -1:
        cs = pygame.transform.flip(cs, True, False)

    if rot_angle > 0:
        cs = pygame.transform.rotate(cs, -rot_angle)

    rect = cs.get_rect(center=(int(cx), int(cy)))
    surface.blit(cs, rect)


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

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing = 1
        else:
            self.vx *= 0.75

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]
                or keys[pygame.K_w]) and self.on_ground:
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
        anim_tick = self.dead_timer if self.dead else self.tick
        draw_character(surface,
                       self.x + self.w // 2,
                       self.y + self.h // 2 - 4,
                       scale=scale,
                       tick=anim_tick,
                       facing=self.facing,
                       on_ground=self.on_ground,
                       dead=self.dead)