import pygame, math, random
from settings import *
from screens.player import draw_character

class Star:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.randint(0,WIDTH)
        self.y = random.randint(0,HEIGHT)
        self.r = random.uniform(0.5,2.5)
        self.speed = random.uniform(0.05,0.3)
        self.alpha = random.randint(80,255)
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT: self.reset(); self.y=0

class Particle:
    def __init__(self):
        self.reset()
    def reset(self):
        self.x = random.uniform(0,WIDTH)
        self.y = random.uniform(HEIGHT//2, HEIGHT)
        self.vy = -random.uniform(0.5,1.5)
        self.vx = random.uniform(-0.3,0.3)
        self.life = random.randint(60,180)
        self.max_life = self.life
        self.r = random.uniform(1,3)
        self.color = random.choice([CYAN,BLUE_LIGHT,YELLOW,PURPLE])
    def update(self):
        self.x += self.vx; self.y += self.vy; self.life -= 1
        if self.life <= 0: self.reset()
    def draw(self,surface):
        alpha = int(255*(self.life/self.max_life))
        col = tuple(min(255,c) for c in self.color)
        pygame.draw.circle(surface,col,(int(self.x),int(self.y)),int(self.r))


class Button:
    def __init__(self,x,y,w,h,text,color,hover):
        self.rect=pygame.Rect(x,y,w,h)
        self.text=text; self.color=color; self.hover=hover
        self.font=pygame.font.SysFont("Arial",27,bold=True)
        self.scale=1.0
    def draw(self,surface):
        mx,my=pygame.mouse.get_pos()
        hovered=self.rect.collidepoint(mx,my)
        target=1.06 if hovered else 1.0
        self.scale += (target-self.scale)*0.15
        w=int(self.rect.w*self.scale); h=int(self.rect.h*self.scale)
        r=pygame.Rect(self.rect.centerx-w//2,self.rect.centery-h//2,w,h)
        col=self.hover if hovered else self.color
        # Sombra
        shadow=pygame.Rect(r.x+4,r.y+4,r.w,r.h)
        pygame.draw.rect(surface,(0,0,0),shadow,border_radius=14)
        pygame.draw.rect(surface,col,r,border_radius=14)
        pygame.draw.rect(surface,WHITE,r,2,border_radius=14)
        txt=self.font.render(self.text,True,WHITE)
        surface.blit(txt,(r.centerx-txt.get_width()//2,r.centery-txt.get_height()//2))
    def is_clicked(self,event):
        return event.type==pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)


class MenuScreen:
    def __init__(self,game):
        self.game=game; self.tick=0
        self.stars=[Star() for _ in range(140)]
        self.particles=[Particle() for _ in range(60)]
        self.font_title=pygame.font.SysFont("Arial",70,bold=True)
        self.font_sub=pygame.font.SysFont("Arial",22)
        self.font_sm=pygame.font.SysFont("Arial",15)
        self.buttons=[
            Button(WIDTH//2-130,360,260,58,"▶   Jogar",BLUE,BLUE_DARK),
            Button(WIDTH//2-130,438,260,58,"✕   Sair",(150,30,30),(100,15,15)),
        ]
        # Portais decorativos no menu
        self.portal_angles=[0]*5

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.game.running=False
            if self.buttons[0].is_clicked(event): self.game.state="map"
            if self.buttons[1].is_clicked(event): self.game.running=False

    def update(self):
        self.tick+=1
        for s in self.stars: s.update()
        for p in self.particles: p.update()
        for i in range(5): self.portal_angles[i]+=0.02*(i+1)

    def draw(self):
        s=self.game.screen
        s.fill(BG_COLOR)

        # Estrelas
        for star in self.stars:
            tw=int(150+80*math.sin(self.tick*0.03+star.x))
            pygame.draw.circle(s,(tw,tw,tw),(int(star.x),int(star.y)),int(star.r))

        # Partículas flutuantes
        for p in self.particles: p.draw(s)

        # Portais decorativos pequenos
        portal_xs=[100,200,700,780,440]
        portal_ys=[500,350,500,350,520]
        for i,(px,py) in enumerate(zip(portal_xs,portal_ys)):
            col=REGION_COLORS[i]
            angle=self.portal_angles[i]
            for j in range(8):
                a=angle+j*math.pi/4
                ox2=int(px+30*math.cos(a)); oy2=int(py+30*math.sin(a))
                pygame.draw.circle(s,col,(ox2,oy2),3)
            pygame.draw.circle(s,col,(px,py),22)
            pygame.draw.circle(s,WHITE,(px,py),22,2)
            icon=pygame.font.SysFont("Arial",16,bold=True).render(REGION_ICONS[i],True,WHITE)
            s.blit(icon,(px-icon.get_width()//2,py-icon.get_height()//2))

        # Glow do título
        glow=int(80+50*math.sin(self.tick*0.05))
        gs=pygame.Surface((560,100),pygame.SRCALPHA)
        pygame.draw.ellipse(gs,(*YELLOW,glow),(0,0,560,100))
        s.blit(gs,(WIDTH//2-280,100))

        # Título com sombra
        for dx,dy,col in [(4,4,(0,0,0)),(0,0,YELLOW)]:
            t=self.font_title.render("Integral Quest",True,col)
            s.blit(t,(WIDTH//2-t.get_width()//2+dx,105+dy))

        sub=self.font_sub.render("Explorando o Mundo das Integrais",True,GRAY)
        s.blit(sub,(WIDTH//2-sub.get_width()//2,182))

        # Personagem grande animado
        draw_character(s,WIDTH//2,275,scale=1.9,tick=self.tick,on_ground=True)

        for btn in self.buttons: btn.draw(s)

        footer=self.font_sm.render(
            "Disciplina: Resolução de Problemas Multivariáveis  |  Prof. Pedro Girotto",
            True,(60,60,80))
        s.blit(footer,(WIDTH//2-footer.get_width()//2,HEIGHT-22))