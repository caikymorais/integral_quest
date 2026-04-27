import pygame
import random
from settings import *

MANUSCRITO = {
    "Noção de Integral": [
        ("O que é a Integral?",
         "A integral mede a área acumulada sob uma curva f(x) entre dois pontos.\n"
         "Imagine dividir essa área em retângulos finos — quanto mais finos, mais precisa."),
        ("Soma de Riemann",
         "Σ f(xᵢ)·Δx  — somamos as áreas de n retângulos de largura Δx.\n"
         "Quando n→∞ e Δx→0, a soma converge para a integral definida."),
        ("Notação",
         "∫[a,b] f(x) dx  lê-se: integral de a até b de f de x dx.\n"
         "• a e b = limites de integração\n"
         "• f(x) = integrando\n"
         "• dx = variável de integração"),
    ],
    "Integral Indefinida": [
        ("Definição",
         "∫ f(x) dx = F(x) + C,  onde F'(x) = f(x).\n"
         "A integral indefinida encontra a família de primitivas de f."),
        ("Regra da Potência",
         "∫ xn dx = xn+1/(n+1) + C    (n != -1)\n\n"
         "Exemplos:\n"
         "• ∫ x2 dx = x3/3 + C\n"
         "• ∫ x5 dx = x6/6 + C\n"
         "• ∫ 1 dx  = x + C"),
        ("Regras Básicas",
         "• ∫ k·f(x) dx = k·∫ f(x) dx\n"
         "• ∫ [f+g] dx = ∫f dx + ∫g dx\n"
         "• ∫ ex dx = ex + C\n"
         "• ∫ sin(x) dx = -cos(x) + C\n"
         "• ∫ cos(x) dx = sin(x) + C"),
    ],
    "Substituição": [
        ("Ideia Central",
         "Quando o integrando tem a forma f(g(x))·g'(x), fazemos:\n"
         "u = g(x)  →  du = g'(x)dx\n"
         "Assim a integral fica mais simples em termos de u."),
        ("Passo a Passo",
         "1. Identifique u = parte interna\n"
         "2. Calcule du = u' dx\n"
         "3. Substitua no integrando\n"
         "4. Integre em u\n"
         "5. Substitua u de volta por g(x)"),
        ("Exemplo",
         "∫ 2x·cos(x2) dx\n\n"
         "u = x2  →  du = 2x dx\n"
         "= ∫ cos(u) du\n"
         "= sin(u) + C\n"
         "= sin(x2) + C"),
    ],
    "Integração por Partes": [
        ("Fórmula",
         "∫ u dv = uv − ∫ v du\n\n"
         "Derivada do produto ao contrário:\n"
         "d(uv) = u dv + v du  →  ∫u dv = uv − ∫v du"),
        ("Como escolher u? — LIATE",
         "L — Logaritmo (ln x)\n"
         "I — Inversa trigonométrica\n"
         "A — Algébrica (xn)\n"
         "T — Trigonométrica\n"
         "E — Exponencial (ex)"),
        ("Exemplo",
         "∫ x·ex dx\n\n"
         "u = x     →  du = dx\n"
         "dv = ex dx  →  v = ex\n\n"
         "= x·ex − ∫ex dx\n"
         "= x·ex − ex + C\n"
         "= ex(x−1) + C"),
    ],
    "Integral Definida": [
        ("Teorema Fundamental",
         "∫[a,b] f(x) dx = F(b) − F(a)\n\n"
         "Onde F é qualquer primitiva de f.\n"
         "Conecta derivação e integração."),
        ("Propriedades",
         "• ∫[a,a] f dx = 0\n"
         "• ∫[a,b] f dx = −∫[b,a] f dx\n"
         "• ∫[a,b] k·f dx = k·∫[a,b] f dx\n"
         "• ∫[a,b] f dx + ∫[b,c] f dx = ∫[a,c] f dx"),
        ("Exemplo",
         "∫[0,3] x2 dx\n\n"
         "F(x) = x3/3\n"
         "F(3) − F(0) = 27/3 − 0 = 9\n\n"
         "A área sob x2 de 0 a 3 é 9."),
    ],
}


class TreinoScreen:

    def __init__(self, game):
        self.game       = game
        self.tick       = 0
        self.region_idx = 0
        self.card_idx   = 0
        self.regions    = list(MANUSCRITO.keys())
        self.particles  = []

        self.f_header = pygame.font.SysFont("Arial", 24, bold=True)
        self.f_tab    = pygame.font.SysFont("Arial", 12, bold=True)
        self.f_title  = pygame.font.SysFont("Arial", 22, bold=True)
        self.f_sub    = pygame.font.SysFont("Arial", 17, bold=True)
        self.f_body   = pygame.font.SysFont("Arial", 15)
        self.f_hint   = pygame.font.SysFont("Arial", 13)
        self.f_nav    = pygame.font.SysFont("Arial", 20, bold=True)

        self.btn_prev_r = pygame.Rect(10,          HEIGHT//2-20, 36, 40)
        self.btn_next_r = pygame.Rect(WIDTH-46,    HEIGHT//2-20, 36, 40)
        self.btn_prev_c = pygame.Rect(WIDTH//2-120, HEIGHT-52,  100, 34)
        self.btn_next_c = pygame.Rect(WIDTH//2+20,  HEIGHT-52,  100, 34)
        self.btn_voltar = pygame.Rect(WIDTH-160,    HEIGHT-52,  150, 34)

        self._cached_region = None
        self._cached_card   = None
        self._card_surfs    = []
        self._tab_surfs     = []

        self._rebuild_cache()

    def _rebuild_cache(self):
        """Reconstrói as surfaces de texto apenas quando o card muda."""
        reg_key  = self.region_idx
        card_key = self.card_idx
        if reg_key == self._cached_region and card_key == self._cached_card:
            return

        self._cached_region = reg_key
        self._cached_card   = card_key
        self._card_surfs    = []

        card_x, card_y = 60, 100
        card_w         = WIDTH - 120

        s = self.f_hint.render(
            f"Card {self.card_idx+1} / {len(self.current_cards)}",
            True, (140,120,60))
        self._card_surfs.append((s, card_x+12, card_y+10))

        s = self.f_title.render(self.current_card[0], True, YELLOW)
        self._card_surfs.append((s, card_x+12, card_y+30))

        lines = self.current_card[1].split("\n")
        by    = card_y + 66
        for line in lines:
            if line == "":
                by += 8
                continue
            col  = (200,200,255) if line.startswith("•") else (220,210,180)
            surf = self.f_body.render(line, True, col)
            self._card_surfs.append((surf, card_x+20, by))
            by  += 22

        self._tab_surfs = []
        tab_w = (WIDTH-20) // len(self.regions)
        for i, reg in enumerate(self.regions):
            col = WHITE if i == self.region_idx else GRAY
            s   = self.f_tab.render(REGION_ICONS[i]+" "+reg[:12], True, col)
            self._tab_surfs.append((s, 10+i*tab_w+4, 67, i))

    @property
    def current_region(self):  return self.regions[self.region_idx]
    @property
    def current_cards(self):   return MANUSCRITO[self.current_region]
    @property
    def current_card(self):    return self.current_cards[self.card_idx]

    def _next_card(self):
        if self.card_idx < len(self.current_cards)-1: self.card_idx += 1
        else: self._next_region()
        self._rebuild_cache()

    def _prev_card(self):
        if self.card_idx > 0: self.card_idx -= 1
        else: self._prev_region()
        self._rebuild_cache()

    def _next_region(self):
        self.region_idx = (self.region_idx+1) % len(self.regions)
        self.card_idx   = 0
        self._rebuild_cache()

    def _prev_region(self):
        self.region_idx = (self.region_idx-1) % len(self.regions)
        self.card_idx   = 0
        self._rebuild_cache()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:              self.game.go_to_map()
                if event.key in (pygame.K_RIGHT, pygame.K_d): self._next_card()
                if event.key in (pygame.K_LEFT,  pygame.K_a): self._prev_card()
                if event.key in (pygame.K_UP,    pygame.K_w): self._prev_region()
                if event.key in (pygame.K_DOWN,  pygame.K_s): self._next_region()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self.btn_next_c.collidepoint(mx,my):  self._next_card()
                if self.btn_prev_c.collidepoint(mx,my):  self._prev_card()
                if self.btn_next_r.collidepoint(mx,my):  self._next_region()
                if self.btn_prev_r.collidepoint(mx,my):  self._prev_region()
                if self.btn_voltar.collidepoint(mx,my):  self.game.go_to_map()

    def update(self):
        self.tick += 1
        if self.tick % 20 == 0:
            self.particles.append({
                "x":    random.uniform(0, WIDTH),
                "y":    float(HEIGHT + 10),
                "vy":   random.uniform(-0.6, -0.2),
                "life": random.randint(80, 160),
                "col":  random.choice([YELLOW, (200,180,80), WHITE]),
                "r":    1,
            })
        self.particles = [p for p in self.particles if p["life"] > 0]
        for p in self.particles:
            p["y"] += p["vy"]; p["life"] -= 1

    def draw(self):
        s = self.game.screen

        s.fill((22, 17, 8))
        for row in range(0, HEIGHT, 6):
            t = row / HEIGHT
            pygame.draw.line(s,
                (int(18+t*20), int(14+t*12), int(8+t*8)),
                (0, row), (WIDTH, row))

        for p in self.particles:
            pygame.draw.circle(s, p["col"], (int(p["x"]), int(p["y"])), p["r"])

        pygame.draw.rect(s, (30,22,10), (0,0,WIDTH,56))
        pygame.draw.line(s, YELLOW, (0,56),(WIDTH,56), 2)
        t = self.f_header.render("Manuscrito do Calculo", True, YELLOW)
        s.blit(t, (WIDTH//2-t.get_width()//2, 12))
        t = self.f_hint.render(
            "< > mudar card  |  cima/baixo mudar regiao  |  ESC voltar",
            True, (140,120,60))
        s.blit(t, (WIDTH//2-t.get_width()//2, 40))

        tab_w = (WIDTH-20) // len(self.regions)
        for surf, tx, ty, i in self._tab_surfs:
            active = (i == self.region_idx)
            col_bg = REGION_COLORS[i] if active else (30,30,40)
            pygame.draw.rect(s, col_bg, (10+i*tab_w, 60, tab_w-4, 28), border_radius=6)
            if active:
                pygame.draw.rect(s, WHITE, (10+i*tab_w, 60, tab_w-4, 28), 2, border_radius=6)
            s.blit(surf, (tx, ty))

        card_x, card_y, card_w, card_h = 60, 100, WIDTH-120, HEIGHT-200
        pygame.draw.rect(s, (10,8,4),  (card_x+5, card_y+5, card_w, card_h), border_radius=16)
        pygame.draw.rect(s, (38,30,14),(card_x,   card_y,   card_w, card_h), border_radius=16)
        pygame.draw.rect(s, REGION_COLORS[self.region_idx],
            (card_x, card_y, card_w, card_h), 3, border_radius=16)
        pygame.draw.line(s, REGION_COLORS[self.region_idx],
            (card_x+12, card_y+56), (card_x+card_w-12, card_y+56), 1)

        for surf, bx, by in self._card_surfs:
            s.blit(surf, (bx, by))

        total     = len(self.current_cards)
        dot_y     = card_y + card_h - 18
        dot_start = WIDTH//2 - (total*16)//2
        for i in range(total):
            col_d = YELLOW if i == self.card_idx else (60,50,30)
            pygame.draw.circle(s, col_d, (dot_start+i*16, dot_y), 5)

        mx, my = pygame.mouse.get_pos()
        for btn, lbl in [(self.btn_prev_r,"<"),(self.btn_next_r,">")]:
            bc = (70,55,20) if btn.collidepoint(mx,my) else (40,30,10)
            pygame.draw.rect(s, bc,    btn, border_radius=8)
            pygame.draw.rect(s, YELLOW,btn, 2, border_radius=8)
            t = self.f_nav.render(lbl, True, YELLOW)
            s.blit(t, (btn.centerx-t.get_width()//2, btn.centery-t.get_height()//2))

        btns = [
            (self.btn_prev_c, "< Anterior",      (50,40,10)),
            (self.btn_next_c, "Proximo >",        (50,40,10)),
            (self.btn_voltar, "Voltar ao Mapa",   (20,30,60)),
        ]
        for btn, lbl, col in btns:
            bc = tuple(min(255,v+30) for v in col) if btn.collidepoint(mx,my) else col
            pygame.draw.rect(s, bc,   btn, border_radius=8)
            pygame.draw.rect(s, GRAY, btn, 1, border_radius=8)
            t = self.f_hint.render(lbl, True, WHITE)
            s.blit(t, (btn.centerx-t.get_width()//2, btn.centery-t.get_height()//2))

        reg_lbl = self.f_hint.render(
            f"Regiao: {self.current_region}", True, REGION_COLORS[self.region_idx])
        s.blit(reg_lbl, (10, HEIGHT-18))