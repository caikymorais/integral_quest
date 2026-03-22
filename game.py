import pygame
from settings import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock=pygame.time.Clock()
        self.running=True
        self.score=0
        self.unlocked=[True]+[False]*4
        self.state="menu"
        self.current_region=None
        self.screens={}

    def run(self):
        from screens.menu       import MenuScreen
        from screens.map_screen import MapScreen
        self.screens["menu"]=MenuScreen(self)
        self.screens["map"]=MapScreen(self)
        while self.running:
            self.clock.tick(FPS)
            cur=self.screens.get(self.state)
            if cur:
                cur.handle_events()
                cur.update()
                cur.draw()
            pygame.display.flip()
        pygame.quit()

    def go_to_challenge(self,region_name):
        from screens.phases.phase1_lava      import Phase1Lava
        from screens.phases.phase2_spikes    import Phase2Spikes
        from screens.phases.phase3_enemies   import Phase3Enemies
        from screens.phases.phase4_water     import Phase4Water
        from screens.phases.phase5_lightning import Phase5Lightning
        PHASE_MAP={
            "Noção de Integral":     Phase1Lava,
            "Integral Indefinida":   Phase2Spikes,
            "Substituição":          Phase3Enemies,
            "Integração por Partes": Phase4Water,
            "Integral Definida":     Phase5Lightning,
        }
        self.current_region=region_name
        self.screens["challenge"]=PHASE_MAP[region_name](self,region_name)
        self.state="challenge"

    def go_to_map(self):
        self.screens["map"].portal_cooldown=90
        self.state="map"

    def go_to_results(self,hits,total):
        from screens.results import ResultsScreen
        self.screens["results"]=ResultsScreen(self,self.current_region,hits,total)
        self.state="results"

    def unlock_next(self,region_name):
        idx=REGIONS.index(region_name)
        if idx+1<len(REGIONS):
            self.unlocked[idx+1]=True