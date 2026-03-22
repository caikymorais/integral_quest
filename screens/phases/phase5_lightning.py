import pygame, math, random
from settings import *
from screens.base_phase import BasePhase
from screens.player import PhysicsPlayer
from data.questions import QUESTIONS

class Lightning:
    def __init__(self, x):
        self.x     = x
        self.timer = random.randint(30, 90)
        self.active= False
        self.flash = 0

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = True
            self.flash  = 12
            self.timer  = random.randint(50,120)
        if self.flash > 0: self.flash -= 1
        if self.flash == 0: self.active = False

    def draw(self, surface, font, label):
        col = YELLOW if self.flash > 6 else (150,150,0)
        pygame.draw.rect(surface, col, (self.x-5, 72, 10, HEIGHT-120))
        txt = font.render(label, True, col)
        surface.blit(txt,(self.x-txt.get_width()//2, HEIGHT-110))


class Phase5Lightning(BasePhase):
    """Raios caem nas posições ERRADAS. Player pula na plataforma com o valor correto
       de F(b)-F(a). Gráfico da função é desenhado no fundo."""

    def _setup(self):
        self._build_level()

    def _build_level(self):
        q = QUESTIONS[self.region][self.q_index]
        self.player = PhysicsPlayer(60, HEIGHT-180)

        self.platforms = [{"rect":pygame.Rect(0,HEIGHT-60,WIDTH,20),
                           "label":"","correct":False,"state":"idle",
                           "color":DARK_GRAY,"is_floor":True}]
        n = len(q["opts"])
        xs = [int(WIDTH*(i+1)/(n+1))-95 for i in range(n)]
        ys = [HEIGHT-220, HEIGHT-260, HEIGHT-200, HEIGHT-240]
        for i,(opt,x) in enumerate(zip(q["opts"],xs)):
            self.platforms.append({
                "rect":    pygame.Rect(x, ys[i%len(ys)], 190, 22),
                "label":   opt,
                "correct": (i==q["correta"]),
                "state":   "idle",
                "color":   random.choice([BLUE,TEAL,PURPLE_DARK,BLUE_DARK]),
                "is_floor": False,
                "base_y":  float(ys[i%len(ys)]),
                "bob":     random.uniform(0,math.pi*2),
            })

        # Raios nas posições erradas
        wrong_xs = [p["rect"].centerx for p in self.platforms
                    if not p.get("is_floor") and not p["correct"]]
        self.lightnings = [Lightning(x) for x in wrong_xs]

    def _update_phase(self):
        if self.player.dead:
            if self.player.dead_timer > 45:
                self.player.dead = False
                self._respawn()
            return

        keys = pygame.key.get_pressed()
        flat = [{"rect":p["rect"]} for p in self.platforms]
        self.player.update(keys, flat)

        for p in self.platforms:
            if not p.get("is_floor"):
                p["rect"].y = int(p["base_y"]+math.sin(self.tick*0.025+p["bob"])*5)

        for lt in self.lightnings:
            lt.update()
            if lt.active and lt.flash > 8:
                lr = pygame.Rect(lt.x-20, 72, 40, HEIGHT-130)
                if self.player.rect.colliderect(lr):
                    self.player.die(); return

        if self.player.y > HEIGHT+20:
            self.player.die(); return

        if not self.answered:
            for p in self.platforms:
                if p.get("is_floor"): continue
                if (self.player.on_ground and
                        self.player.rect.colliderect(p["rect"]) and
                        p["state"]=="idle"):
                    self.attempts += 1
                    pts = self._award_points(p["correct"])
                    p["state"]="active"
                    if p["correct"]:
                        p["color"]=GREEN
                        for lt in self.lightnings: lt.timer=9999
                        self._set_feedback(True,
                            f"✓ +{pts}pts — {QUESTIONS[self.region][self.q_index]['feedback_ok']}")
                    else:
                        p["color"]=RED
                        self.first_try=False
                        self._set_feedback(False,
                            QUESTIONS[self.region][self.q_index]["feedback_erro"],
                            duration=80)
                    break

    def _draw_background(self):
        s = self.game.screen
        for row in range(0,HEIGHT,3):
            t=row/HEIGHT
            pygame.draw.line(s,(int(5+t*15),int(5+t*10),int(25+t*35)),(0,row),(WIDTH,row))

        # Gráfico decorativo (curva e área)
        ox,oy = 80, HEIGHT-62
        scale_x, scale_y = 60, 40
        pygame.draw.line(s,GRAY,(ox,oy),(ox+660,oy),1)
        pygame.draw.line(s,GRAY,(ox,oy),(ox,oy-220),1)

        pts_fill = [(ox,oy)]
        pts_line = []
        for px in range(0,600):
            xv = px/scale_x
            yv = xv*0.8 + math.sin(xv)*10
            yv = min(yv, 200)
            pts_fill.append((ox+px, oy-int(yv)))
            pts_line.append((ox+px, oy-int(yv)))
        pts_fill.append((ox+600,oy))
        if len(pts_fill)>2:
            fill_surf = pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
            pygame.draw.polygon(fill_surf,(80,180,255,25),pts_fill)
            s.blit(fill_surf,(0,0))
        if len(pts_line)>1:
            pygame.draw.lines(s,CYAN,False,pts_line,2)

        # Labels eixos
        s.blit(self.font_sm.render("x",(True),GRAY),(ox+610,oy-5))
        s.blit(self.font_sm.render("f(x)",True,GRAY),(ox+5,oy-220))

    def _draw_hazards(self):
        s = self.game.screen
        q = QUESTIONS[self.region][self.q_index]
        wrong_plats = [p for p in self.platforms
                       if not p.get("is_floor") and not p["correct"]]
        for lt,p in zip(self.lightnings, wrong_plats):
            lt.draw(s, self.font_sm, "")

    def _draw_platforms(self):
        s = self.game.screen
        for p in self.platforms:
            col = p["color"]
            pygame.draw.rect(s,col,p["rect"],border_radius=8)
            if not p.get("is_floor"):
                pygame.draw.rect(s,WHITE,p["rect"],2,border_radius=8)
                txt=self.font.render(p["label"],True,WHITE)
                s.blit(txt,(p["rect"].centerx-txt.get_width()//2,
                            p["rect"].centery-txt.get_height()//2))

    def _extra_draw(self):
        s = self.game.screen
        hint = self.font_sm.render("⚡ Evite os raios! Pule no valor correto de F(b)−F(a)", True, YELLOW)
        s.blit(hint,(WIDTH//2-hint.get_width()//2,76))