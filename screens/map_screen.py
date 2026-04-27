import pygame, math, random
from settings import *
from screens.player import draw_character

PORTAL_POSITIONS = [(110,460),(270,310),(450,190),(630,310),(790,460)]
BOSS_POS         = (WIDTH // 2, 480)
TREINO_POS       = (WIDTH // 2, 80)
class MapPlayer:
    def __init__(self):
        self.x, self.y = float(WIDTH//2), float(HEIGHT//2)
        self.speed = 4
        self.facing = 1
        self.tick = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x)-14, int(self.y)-23, 28, 46)

    def update(self, keys):
        m = False
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x -= self.speed; self.facing = -1; m = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x += self.speed; self.facing =  1; m = True
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y -= self.speed; m = True
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y += self.speed; m = True
        self.x = max(20, min(WIDTH-20,  self.x))
        self.y = max(20, min(HEIGHT-20, self.y))
        if m: self.tick += 1

    def draw(self, surface):
        draw_character(surface, self.x, self.y, scale=1.0,
                       tick=self.tick, facing=self.facing, on_ground=True)


class MapScreen:
    def __init__(self, game):
        self.game   = game
        self.player = MapPlayer()
        self.portal_cooldown = 0
        self.font     = pygame.font.SysFont("Arial", 13, bold=True)
        self.font_hud = pygame.font.SysFont("Arial", 20, bold=True)
        self.portals  = [pygame.Rect(px-36, py-36, 72, 72) for px,py in PORTAL_POSITIONS]
        self.boss_portal   = pygame.Rect(BOSS_POS[0]-42,   BOSS_POS[1]-42,   84, 84)
        self.treino_portal = pygame.Rect(TREINO_POS[0]-36, TREINO_POS[1]-36, 72, 72)
        self.stars    = [(random.randint(0,WIDTH), random.randint(0,HEIGHT),
                          random.uniform(0.5, 2.2)) for _ in range(100)]
        self.tick      = 0
        self.particles = []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.go_to_menu()

    def update(self):
        self.tick += 1
        keys = pygame.key.get_pressed()
        self.player.update(keys)

        for i, pos in enumerate(PORTAL_POSITIONS):
            if self.game.unlocked[i] and random.random() < 0.3:
                angle = random.uniform(0, math.pi*2)
                speed = random.uniform(0.5, 2)
                self.particles.append({
                    "x": float(pos[0]), "y": float(pos[1]),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed - 1,
                    "life": random.randint(20,50),
                    "color": REGION_COLORS[i],
                })

        if self.game.boss_unlocked and random.random() < 0.4:
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(0.5, 2.5)
            self.particles.append({
                "x": float(BOSS_POS[0]), "y": float(BOSS_POS[1]),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 1,
                "life": random.randint(20,50),
                "color": (220,50,50),
            })

        if random.random() < 0.25:
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(0.3, 1.5)
            self.particles.append({
                "x": float(TREINO_POS[0]), "y": float(TREINO_POS[1]),
                "vx": math.cos(angle) * speed,
                "vy": math.sin(angle) * speed - 0.5,
                "life": random.randint(20,45),
                "color": (200,180,80),
            })

        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1

        if self.portal_cooldown > 0:
            self.portal_cooldown -= 1
            return

        for i, portal in enumerate(self.portals):
            if self.player.rect.colliderect(portal) and self.game.unlocked[i]:
                self.portal_cooldown = 30
                self.game.go_to_challenge(REGIONS[i])
                return

        if self.game.boss_unlocked:
            if self.player.rect.colliderect(self.boss_portal):
                self.portal_cooldown = 30
                self.game.go_to_boss()
                return

        if self.player.rect.colliderect(self.treino_portal):
            self.portal_cooldown = 30
            self.game.go_to_treino()
            return

    def draw(self):
        s = self.game.screen
        s.fill(BG_COLOR)

        for row in range(0, HEIGHT, 3):
            t = row / HEIGHT
            pygame.draw.line(s,
                (int(8+t*10), int(10+t*12), int(25+t*18)),
                (0, row), (WIDTH, row))

        for sx, sy, sr in self.stars:
            tw = int(120 + 80*math.sin(self.tick*0.04+sx))
            pygame.draw.circle(s, (tw,tw,tw), (sx,sy), int(sr))

        for p in self.particles:
            col = tuple(min(255,c) for c in p["color"])
            pygame.draw.circle(s, col, (int(p["x"]),int(p["y"])), 2)

        for i in range(len(PORTAL_POSITIONS)-1):
            col = REGION_COLORS[i] if self.game.unlocked[i+1] else (40,40,60)
            pygame.draw.line(s, col, PORTAL_POSITIONS[i], PORTAL_POSITIONS[i+1], 3)

        for i, (pos, portal) in enumerate(zip(PORTAL_POSITIONS, self.portals)):
            unlocked = self.game.unlocked[i]
            col = REGION_COLORS[i] if unlocked else (45,45,65)
            if unlocked:
                glow_r = int(42 + 8*math.sin(self.tick*0.05+i))
                gs = pygame.Surface((glow_r*2+24, glow_r*2+24), pygame.SRCALPHA)
                pygame.draw.circle(gs, (*col,45), (glow_r+12,glow_r+12), glow_r+12)
                s.blit(gs, (pos[0]-glow_r-12, pos[1]-glow_r-12))
            pygame.draw.circle(s, col, pos, 36)
            pygame.draw.circle(s, WHITE, pos, 36, 2)
            icon = pygame.font.SysFont("Arial",28,bold=True).render(
                REGION_ICONS[i], True, WHITE if unlocked else GRAY)
            s.blit(icon, (pos[0]-icon.get_width()//2, pos[1]-icon.get_height()//2))
            if not unlocked:
                lk = pygame.font.SysFont("Arial",13).render("🔒", True, GRAY)
                s.blit(lk, (pos[0]+22, pos[1]-38))
            lbl = self.font.render(REGIONS[i], True, WHITE if unlocked else GRAY)
            s.blit(lbl, (pos[0]-lbl.get_width()//2, pos[1]+42))

        glow_r = int(36 + 6*math.sin(self.tick*0.06))
        gs = pygame.Surface((glow_r*2+20, glow_r*2+20), pygame.SRCALPHA)
        pygame.draw.circle(gs, (200,180,80,40), (glow_r+10,glow_r+10), glow_r+10)
        s.blit(gs, (TREINO_POS[0]-glow_r-10, TREINO_POS[1]-glow_r-10))
        pygame.draw.circle(s, (160,140,40), TREINO_POS, 32)
        pygame.draw.circle(s, YELLOW, TREINO_POS, 32, 2)
        icon_t = pygame.font.SysFont("Arial",22,bold=True).render("📖", True, WHITE)
        s.blit(icon_t, (TREINO_POS[0]-icon_t.get_width()//2, TREINO_POS[1]-icon_t.get_height()//2))
        lbl_t = self.font.render("TREINO", True, YELLOW)
        s.blit(lbl_t, (TREINO_POS[0]-lbl_t.get_width()//2, TREINO_POS[1]+38))
        sub_t = pygame.font.SysFont("Arial",11).render("Manuscrito do Cálculo", True, (160,140,80))
        s.blit(sub_t, (TREINO_POS[0]-sub_t.get_width()//2, TREINO_POS[1]+54))

        if self.game.boss_unlocked:
            glow_r = int(50 + 12*math.sin(self.tick*0.07))
            gs = pygame.Surface((glow_r*2+30, glow_r*2+30), pygame.SRCALPHA)
            pygame.draw.circle(gs, (220,50,50,50), (glow_r+15,glow_r+15), glow_r+15)
            s.blit(gs, (BOSS_POS[0]-glow_r-15, BOSS_POS[1]-glow_r-15))
            pygame.draw.circle(s, RED,    BOSS_POS, 42)
            pygame.draw.circle(s, YELLOW, BOSS_POS, 42, 3)
            icon_b = pygame.font.SysFont("Arial",30,bold=True).render("☠", True, YELLOW)
            s.blit(icon_b, (BOSS_POS[0]-icon_b.get_width()//2, BOSS_POS[1]-icon_b.get_height()//2))
            lbl_b = self.font.render("CHEFÃO", True, RED)
            s.blit(lbl_b, (BOSS_POS[0]-lbl_b.get_width()//2, BOSS_POS[1]+48))
            sub_b = pygame.font.SysFont("Arial",12).render("Monstro do Cálculo", True, ORANGE)
            s.blit(sub_b, (BOSS_POS[0]-sub_b.get_width()//2, BOSS_POS[1]+64))
        else:
            pygame.draw.circle(s, (40,20,20), BOSS_POS, 42)
            pygame.draw.circle(s, (80,40,40), BOSS_POS, 42, 2)
            icon_b = pygame.font.SysFont("Arial",24,bold=True).render("🔒", True, (80,40,40))
            s.blit(icon_b, (BOSS_POS[0]-icon_b.get_width()//2, BOSS_POS[1]-icon_b.get_height()//2))
            lbl_b = self.font.render("CHEFÃO", True, (80,40,40))
            s.blit(lbl_b, (BOSS_POS[0]-lbl_b.get_width()//2, BOSS_POS[1]+48))
            req = pygame.font.SysFont("Arial",11).render(
                f"Complete todas as fases + {PONTOS_MINIMOS_CHEFAO}pts", True, (80,60,60))
            s.blit(req, (BOSS_POS[0]-req.get_width()//2, BOSS_POS[1]+64))

        self.player.draw(s)

        _rsz = (80, 80)
        _reflect_surf = pygame.Surface(_rsz, pygame.SRCALPHA)
        draw_character(_reflect_surf, _rsz[0] // 2, 18,
                       scale=0.9, tick=self.player.tick,
                       facing=self.player.facing, on_ground=True)
        _reflect_surf = pygame.transform.flip(_reflect_surf, False, True)
        _reflect_surf.set_alpha(35)
        s.blit(_reflect_surf,
               (int(self.player.x) - _rsz[0] // 2,
                int(self.player.y) + 22))

        pygame.draw.rect(s, (0,0,0), (0,0,WIDTH,32))
        sc = self.font_hud.render(f"{self.game.score} pts", True, YELLOW)
        s.blit(sc, (10,5))
        if not self.game.boss_unlocked:
            prog = pygame.font.SysFont("Arial",13).render(
                f"Chefão: {self.game.score}/{PONTOS_MINIMOS_CHEFAO}pts", True, ORANGE)
            s.blit(prog, (WIDTH//2-prog.get_width()//2, 8))
        hint = pygame.font.SysFont("Arial",14).render(
            "WASD/Setas: mover  |  Toque no portal  |  ESC: menu", True, GRAY)
        s.blit(hint, (WIDTH-hint.get_width()-10, 8))
        if self.portal_cooldown > 0:
            msg = pygame.font.SysFont("Arial",16).render("Entrando...", True, YELLOW)
            s.blit(msg, (WIDTH//2-msg.get_width()//2, 35))