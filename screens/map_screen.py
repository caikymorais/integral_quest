import pygame, math, random
from settings import *
from screens.player import draw_character

PORTAL_POSITIONS=[(110,460),(270,310),(450,190),(630,310),(790,460)]

class MapPlayer:
    def __init__(self):
        self.x,self.y=float(WIDTH//2),float(HEIGHT//2)
        self.speed=4; self.facing=1; self.tick=0
    @property
    def rect(self): return pygame.Rect(int(self.x)-14,int(self.y)-23,28,46)
    def update(self,keys):
        m=False
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.x-=self.speed;self.facing=-1;m=True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.x+=self.speed;self.facing=1;m=True
        if keys[pygame.K_UP]    or keys[pygame.K_w]: self.y-=self.speed;m=True
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: self.y+=self.speed;m=True
        self.x=max(20,min(WIDTH-20,self.x))
        self.y=max(60,min(HEIGHT-20,self.y))
        if m: self.tick+=1
    def draw(self,surface):
        draw_character(surface,self.x,self.y,scale=1.0,tick=self.tick,
                       facing=self.facing,on_ground=True)


class MapScreen:
    def __init__(self,game):
        self.game=game; self.player=MapPlayer()
        self.portal_cooldown=0
        self.font=pygame.font.SysFont("Arial",13,bold=True)
        self.font_hud=pygame.font.SysFont("Arial",20,bold=True)
        self.portals=[pygame.Rect(px-36,py-36,72,72) for px,py in PORTAL_POSITIONS]
        self.stars=[(random.randint(0,WIDTH),random.randint(0,HEIGHT),random.uniform(0.5,2.2))
                    for _ in range(100)]
        self.tick=0
        self.particles=[]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.game.running=False
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                self.game.state="menu"

    def update(self):
        self.tick+=1
        keys=pygame.key.get_pressed()
        self.player.update(keys)
        # Partículas nos portais desbloqueados
        for i,pos in enumerate(PORTAL_POSITIONS):
            if self.game.unlocked[i] and random.random()<0.3:
                angle=random.uniform(0,math.pi*2)
                self.particles.append({
                    "x":float(pos[0]),"y":float(pos[1]),
                    "vx":math.cos(angle)*random.uniform(0.5,2),
                    "vy":math.sin(angle)*random.uniform(0.5,2)-1,
                    "life":random.randint(20,50),
                    "color":REGION_COLORS[i],
                })
        self.particles=[p for p in self.particles if p["life"]>0]
        for p in self.particles:
            p["x"]+=p["vx"]; p["y"]+=p["vy"]; p["life"]-=1

        if self.portal_cooldown>0:
            self.portal_cooldown-=1; return
        for i,portal in enumerate(self.portals):
            if self.player.rect.colliderect(portal) and self.game.unlocked[i]:
                self.game.go_to_challenge(REGIONS[i]); return

    def draw(self):
        s=self.game.screen
        s.fill(BG_COLOR)
        # Gradiente fundo
        for row in range(0,HEIGHT,3):
            t=row/HEIGHT
            pygame.draw.line(s,(int(8+t*10),int(10+t*12),int(25+t*18)),(0,row),(WIDTH,row))

        # Estrelas twinkle
        for sx,sy,sr in self.stars:
            tw=int(120+80*math.sin(self.tick*0.04+sx))
            pygame.draw.circle(s,(tw,tw,tw),(sx,sy),int(sr))

        # Partículas dos portais
        for p in self.particles:
            alpha=int(255*(p["life"]/50))
            col=tuple(min(255,c) for c in p["color"])
            pygame.draw.circle(s,col,(int(p["x"]),int(p["y"])),2)

        # Trilha
        for i in range(len(PORTAL_POSITIONS)-1):
            col=REGION_COLORS[i] if self.game.unlocked[i+1] else (40,40,60)
            pygame.draw.line(s,col,PORTAL_POSITIONS[i],PORTAL_POSITIONS[i+1],3)

        # Portais
        for i,(pos,portal) in enumerate(zip(PORTAL_POSITIONS,self.portals)):
            unlocked=self.game.unlocked[i]
            col=REGION_COLORS[i] if unlocked else (45,45,65)
            if unlocked:
                glow_r=int(42+8*math.sin(self.tick*0.05+i))
                gs=pygame.Surface((glow_r*2+24,glow_r*2+24),pygame.SRCALPHA)
                pygame.draw.circle(gs,(*col,45),(glow_r+12,glow_r+12),glow_r+12)
                s.blit(gs,(pos[0]-glow_r-12,pos[1]-glow_r-12))
            pygame.draw.circle(s,col,pos,36)
            pygame.draw.circle(s,(30,30,50),pos,36,0)
            pygame.draw.circle(s,col,pos,36)
            pygame.draw.circle(s,WHITE,pos,36,2)
            icon=pygame.font.SysFont("Arial",28,bold=True).render(REGION_ICONS[i],True,WHITE if unlocked else GRAY)
            s.blit(icon,(pos[0]-icon.get_width()//2,pos[1]-icon.get_height()//2))
            if not unlocked:
                lk=pygame.font.SysFont("Arial",13).render("🔒",True,GRAY)
                s.blit(lk,(pos[0]+22,pos[1]-38))
            lbl=self.font.render(REGIONS[i],True,WHITE if unlocked else GRAY)
            s.blit(lbl,(pos[0]-lbl.get_width()//2,pos[1]+42))

        self.player.draw(s)

        # HUD
        pygame.draw.rect(s,(0,0,0),(0,0,WIDTH,32))
        sc=self.font_hud.render(f"⭐ {self.game.score} pts",True,YELLOW)
        s.blit(sc,(10,5))
        hint=pygame.font.SysFont("Arial",14).render(
            "WASD/Setas: mover  |  Toque no portal  |  ESC: menu",True,GRAY)
        s.blit(hint,(WIDTH-hint.get_width()-10,8))
        if self.portal_cooldown>0:
            msg=pygame.font.SysFont("Arial",16).render("Retornando...",True,YELLOW)
            s.blit(msg,(WIDTH//2-msg.get_width()//2,35))