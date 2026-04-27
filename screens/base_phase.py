import pygame
from settings import *
from screens.player import PhysicsPlayer

class BasePhase:
    LIVES = 3

    def __init__(self, game, region):
        self.game      = game
        self.region    = region
        self.q_index   = 0
        self.lives     = self.LIVES
        self.hits      = 0
        self.first_try = True
        self.attempts  = 0
        self.font      = pygame.font.SysFont("Arial", 18, bold=True)
        self.font_q    = pygame.font.SysFont("Arial", 19, bold=True)
        self.font_sm   = pygame.font.SysFont("Arial", 15)
        self.feedback_timer = 0
        self.feedback_text  = ""
        self.feedback_color = WHITE
        self.answered       = False
        self.tick           = 0
        self.scroll_y       = 0.0
        self.platforms      = []
        self.hazards        = []
        self.player         = None
        self._setup()

    def _setup(self): pass
    def _build_level(self): pass
    def _update_hazards(self): pass
    def _draw_background(self): pass
    def _draw_hazards(self): pass
    def _draw_platforms(self): pass
    def _extra_draw(self): pass
    def _update_phase(self): pass
    def _handle_phase_event(self, event): pass

    def _award_points(self, correct):
        if correct:
            pts = PONTOS_POR_ACERTO_PRIMEIRA if self.first_try else PONTOS_POR_ACERTO_SEGUNDA
            self.game.score += pts
            self.hits += 1
            return pts
        return 0

    def _next_question(self):
        from data.questions import QUESTIONS
        qs = QUESTIONS[self.region]
        self.q_index += 1

        if self.q_index >= len(qs):
            pct = self.hits / len(qs)

            if self.hits == len(qs):
                self.game.score += PONTOS_BONUS_FASE_PERFEITA

            if pct >= 0.7:
                self.game.mark_phase_completed(self.region)
                self.game.unlock_next(self.region)
                self.game.check_boss_unlock()

            self.game.go_to_results(self.hits, len(qs))
            return

        self.answered = False
        self.first_try = True
        self.attempts = 0
        self._build_level()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.game.go_to_map()
            self._handle_phase_event(event)

    def update(self):
        self.tick += 1
        self._update_phase()
        if self.feedback_timer > 0:
            self.feedback_timer -= 1
            if self.feedback_timer == 0 and self.answered:
                self._next_question()

    def draw(self):
        self.game.screen.fill(BG_COLOR)
        self._draw_background()
        self._draw_hazards()
        self._draw_platforms()
        if self.player:
            self.player.draw(self.game.screen)
        self._extra_draw()
        self._draw_hud()

    def _draw_hud(self):
        from data.questions import QUESTIONS
        s  = self.game.screen
        qs = QUESTIONS[self.region]
        q  = qs[self.q_index] if self.q_index < len(qs) else None

        pygame.draw.rect(s, (0, 0, 0), (0, 0, WIDTH, 72))
        pygame.draw.line(s, GRAY, (0, 72), (WIDTH, 72), 1)

        reg = self.font_sm.render(
            f"{self.region}  |  Q{self.q_index+1}/{len(qs)}  |  ⭐ {self.game.score}",
            True, YELLOW
        )
        s.blit(reg, (10, 5))

        for i in range(self.LIVES):
            col = RED if i < self.lives else DARK_GRAY
            pygame.draw.circle(s, col, (WIDTH - 30 - i * 28, 16), 10)
            pygame.draw.circle(s, WHITE, (WIDTH - 30 - i * 28, 16), 10, 2)

        if q:
            self._wrap(q["enunciado"], 10, 28, WIDTH - 20, self.font_q, WHITE)

        ctrl = self.font_sm.render(
            "← → / A D  mover  |  W / ↑ / ESPAÇO  pular  |  ESC  mapa",
            True,
            (80, 80, 100)
        )
        s.blit(ctrl, (WIDTH // 2 - ctrl.get_width() // 2, HEIGHT - 18))

        if self.feedback_timer > 0:
            fb_surf = pygame.Surface((WIDTH, 38), pygame.SRCALPHA)
            fb_surf.fill((0, 0, 0, 180))
            s.blit(fb_surf, (0, HEIGHT - 56))
            self._wrap(
                self.feedback_text,
                10,
                HEIGHT - 52,
                WIDTH - 20,
                self.font_sm,
                self.feedback_color
            )

    def _set_feedback(self, ok, text, duration=120):
        self.feedback_text  = text
        self.feedback_color = GREEN if ok else RED
        self.feedback_timer = duration
        self.answered       = ok

    def _wrap(self, text, x, y, max_w, font, color):
        words = text.split()
        line = ""
        for w in words:
            t = line + w + " "
            if font.size(t)[0] > max_w:
                self.game.screen.blit(font.render(line, True, color), (x, y))
                y += font.get_height() + 2
                line = w + " "
            else:
                line = t
        if line:
            self.game.screen.blit(font.render(line, True, color), (x, y))

    def _respawn(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = self.LIVES
            self.first_try = False
        self._build_level()