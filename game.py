import pygame
from settings import *

class Game:
    def __init__(self):
        self.boss_unlocked = False
        pygame.init()
        self.screen  = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()
        self.running = True
        self.score   = 0
        self.unlocked       = [True] + [False] * 4
        self.state          = "menu"
        self.current_region = None
        self.screens        = {}
        self.completed = [False] * len(REGIONS)
        self.boss_just_unlocked = False

    def run(self):
        from screens.menu       import MenuScreen
        from screens.map_screen import MapScreen
        self.screens["menu"] = MenuScreen(self)
        self.screens["map"]  = MapScreen(self)
        while self.running:
            self.clock.tick(FPS)
            cur = self._current_screen()
            if cur:
                cur.handle_events()
                cur.update()
                cur.draw()
            pygame.display.flip()
        pygame.quit()

    def _current_screen(self):
        """Retorna o objeto de tela atual — suporta string OU objeto direto."""
        if isinstance(self.state, str):
            return self.screens.get(self.state)
        return self.state   # objeto direto (boss, treino, victory…)

    # ── Navegação ──────────────────────────────────────────────────────────

    def go_to_menu(self):
        self.state = "menu"

    def go_to_map(self):
        self.screens["map"].portal_cooldown = 90
        self.state = "map"

    def go_to_challenge(self, region_name):
        from screens.phases.phase1_lava      import Phase1Lava
        from screens.phases.phase2_spikes    import Phase2Spikes
        from screens.phases.phase3_enemies   import Phase3Enemies
        from screens.phases.phase4_water     import Phase4Water
        from screens.phases.phase5_lightning import Phase5Lightning
        PHASE_MAP = {
            "Noção de Integral":     Phase1Lava,
            "Integral Indefinida":   Phase2Spikes,
            "Substituição":          Phase3Enemies,
            "Integração por Partes": Phase4Water,
            "Integral Definida":     Phase5Lightning,
        }
        self.current_region      = region_name
        self.screens["challenge"] = PHASE_MAP[region_name](self, region_name)
        self.state               = "challenge"

    def go_to_results(self, hits, total):
        from screens.results import ResultsScreen
        self.screens["results"] = ResultsScreen(self, self.current_region, hits, total)
        self.state = "results"

    def go_to_treino(self):
        from screens.treino import TreinoScreen
        self.state = TreinoScreen(self)   # objeto direto — ok com _current_screen

    def go_to_boss(self):
        from screens.phases.phase_boss import PhaseBoss
        self.state = PhaseBoss(self)      # objeto direto — ok com _current_screen

    def go_to_victory(self):
        from screens.victory import VictoryScreen
        self.state = VictoryScreen(self)  # objeto direto — ok com _current_screen

    # ── Lógica de jogo ─────────────────────────────────────────────────────

    def unlock_next(self, region_name):
        idx = REGIONS.index(region_name)
        if idx + 1 < len(REGIONS):
            self.unlocked[idx + 1] = True

    def check_boss_unlock(self):
        """Libera o chefão somente se TODAS as fases foram concluídas e pontos suficientes."""
        self.boss_just_unlocked = False
        all_done = all(self.completed)
        if all_done and self.score >= PONTOS_MINIMOS_CHEFAO and not self.boss_unlocked:
            self.boss_unlocked = True
            self.boss_just_unlocked = True

    def mark_phase_completed(self, region_name):
        idx = REGIONS.index(region_name)
        self.completed[idx] = True

    def reset_game(self):
        self.score         = 0
        self.unlocked      = [True] + [False] * len(REGIONS)
        self.boss_unlocked = False
        self.go_to_menu()
        self.completed = [False] * len(REGIONS)
        self.boss_just_unlocked = False