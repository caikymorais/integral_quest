import pygame, math
from settings import *
from screens.player import draw_character

class ResultsScreen:
    def __init__(self,game,region,hits,total):
        self.game=game; self.region=region
        self.hits=hits; self.total=total; self.tick=0
        self.font=pygame.font.SysFont("Arial",34,bold=True)
        self.font_sm=pygame.font.SysFont("Arial",21)
        self.font_btn=pygame.font.SysFont("Arial",24,bold=True)
        self.btn_map=pygame.Rect(WIDTH//2-230,460,210,56)
        self.btn_rep=pygame.Rect(WIDTH//2+20,460,210,56)
        # Confetes
        import random
        self.confetti=[(random.randint(0,WIDTH),random.uniform(-HEIGHT,0),
                        random.uniform(-1,1),random.uniform(2,5),
                        random.choice([YELLOW,GREEN,CYAN,ORANGE,PURPLE]))
                       for _ in range(80)]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT: self.game.running=False
            if event.type==pygame.MOUSEBUTTONDOWN:
                if self.btn_map.collidepoint(event.pos): self.game.go_to_map()
                if self.btn_rep.collidepoint(event.pos): self.game.go_to_challenge(self.region)
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_m: self.game.go_to_map()
                if event.key==pygame.K_r: self.game.go_to_challenge(self.region)

    def update(self):
        self.tick+=1
        pct=self.hits/self.total if self.total else 0
        if pct>=0.7:
            self.confetti=[(x+vx,y+vy,vx,vy,c)
                           for x,y,vx,vy,c in self.confetti]
            self.confetti=[(x,y if y<HEIGHT else -20,vx,vy,c)
                           for x,y,vx,vy,c in self.confetti]

    def draw(self):
        s=self.game.screen
        s.fill(BG_COLOR)
        pct=self.hits/self.total if self.total else 0
        ok=pct>=0.7
        col=GREEN if ok else RED
        msg="Região Completa! 🎉" if ok else f"Precisa de 70% — você fez {pct*100:.0f}%"

        # Confetes
        if ok:
            for x,y,vx,vy,c in self.confetti:
                pygame.draw.rect(s,c,(int(x),int(y),6,6))

        # Personagem
        draw_character(s,WIDTH//2,HEIGHT//2-40,scale=2.0,tick=self.tick,on_ground=True)

        # Glow resultado
        if ok:
            gs=pygame.Surface((400,60),pygame.SRCALPHA)
            glow=int(60+40*math.sin(self.tick*0.08))
            pygame.draw.ellipse(gs,(*GREEN,glow),(0,0,400,60))
            s.blit(gs,(WIDTH//2-200,78))

        def center(text,y,font,color):
            t=font.render(text,True,color)
            s.blit(t,(WIDTH//2-t.get_width()//2,y))

        center(self.region,40,self.font,YELLOW)
        center(msg,85,self.font,col)
        center(f"Acertos: {self.hits}/{self.total}  ({pct*100:.0f}%)",130,self.font_sm,WHITE)
        center(f"Pontuação total: ⭐ {self.game.score}",162,self.font_sm,YELLOW)
        center("10pts = acerto de primeira  |  5pts = acerto após erro",200,
               pygame.font.SysFont("Arial",15),(100,100,120))

        for btn,lbl,c in [
            (self.btn_map,"[M]  Voltar ao Mapa",BLUE),
            (self.btn_rep,"[R]  Repetir Fase",PURPLE),
        ]:
            mx,my=pygame.mouse.get_pos()
            bc=tuple(min(255,v+30) for v in c) if btn.collidepoint(mx,my) else c
            shadow=pygame.Rect(btn.x+3,btn.y+3,btn.w,btn.h)
            pygame.draw.rect(s,(0,0,0),shadow,border_radius=12)
            pygame.draw.rect(s,bc,btn,border_radius=12)
            pygame.draw.rect(s,WHITE,btn,2,border_radius=12)
            t=self.font_btn.render(lbl,True,WHITE)
            s.blit(t,(btn.centerx-t.get_width()//2,btn.centery-t.get_height()//2))