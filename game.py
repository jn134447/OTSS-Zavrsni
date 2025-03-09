import pygame
import os
from scripts.entities import Player, Coin
from scripts.utils import load_images, load_image
from scripts.tilemap import Tilemap
from scripts.animation import Animation

# https://www.youtube.com/watch?v=2gABYM5M0ww

class Game():
    def __init__(self):
        pygame.init()

        self.BACKGROUND_COLOR = (100, 100, 100)
        self.BACKGROUND_PARRALAX = 0.1
        
        SCREEN_WIDTH = 1000
        SCREEN_HEIGHT = 1000
        DISPLAY_SCALE_FACTOR = 3
        
        self.GAME_MAX_FPS = 60

        
        pygame.display.set_caption('Zavrsni Rad')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((SCREEN_WIDTH / DISPLAY_SCALE_FACTOR,
                                        SCREEN_HEIGHT / DISPLAY_SCALE_FACTOR))
        
        self.clock = pygame.time.Clock()
        self.clock.tick(self.GAME_MAX_FPS)
        
        self.camera_scroll = [0, 0]
        self.camera_speed_x = 30 # Lower number = Faster snapping
        self.camera_speed_y = 70 # Higher number = Slower snapping
        
        self.assets = {
            'background/purple_space': load_image('background/purple_space.png'),
            'castle_ground': load_images('tiles/castle_ground'),
            'space_ship_ground': load_images('tiles/space_ship_ground'),
            'player/idle': Animation(self, 'idle', 'entities/player/idle/idle.png', 'entities/player/idle/idle.json'),
            'player/run': Animation(self, 'running', 'entities/player/running/running.png', 'entities/player/running/running.json'),
            'player/jump': Animation(self, 'jump', 'entities/player/jump/jump.png', 'entities/player/jump/jump.json'),
            'player/duck': Animation(self, 'duck', 'entities/player/duck/duck.png', 'entities/player/duck/duck.json'),
            'player/duck_run': Animation(self, 'duck_run', 'entities/player/duck_run/duck_run.png', 'entities/player/duck_run/duck_run.json'),
            'coin/idle': Animation(self, 'idle', 'entities/coin/idle/idle.png', 'entities/coin/idle/idle.json'),
        }
        
        # self.assets['background/stars'] = pygame.transform.scale(self.assets['background/stars'], self.display.get_size())

        self.current_world_and_level = [0, 0] # [word, level]
        
        self.player = Player(self, (150, 150), [9, 18])
        self.tilemap = Tilemap(self, tile_size=16)
        self.tilemap.load_level(self.current_world_and_level)
        self.coin = Coin(self, (500, 200), [16, 16])
       
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
        
            if self.coin.collected == True:
                if self.current_world_and_level[1] >= 3: 
                    self.current_world_and_level[0] += 1
                    self.current_world_and_level[1] = 0
                self.tilemap.load_level(self.current_world_and_level)
                self.player = Player(self, (150, 150), [9, 18])
                self.coin = Coin(self, (500, 200), [16, 16]) 
            
            # Game State Updates
            self.player.register_input_events()
            self.player.update(self.tilemap, [self.player.movement[0], self.player.movement[1]], self.player.speed)
            self.coin.update(self.tilemap)
            
            

            # Camera Updates
            self.camera_scroll[0] += (self.player.center_pos[0] - self.display.get_width() / 2 - self.camera_scroll[0]) / self.camera_speed_x
            self.camera_scroll[1] += (self.player.center_pos[1] - self.display.get_height() / 2 - self.camera_scroll[1]) / self.camera_speed_y
            self.camera_render_scroll = (int(self.camera_scroll[0]), int(self.camera_scroll[1]))
            
            # Debug prints
            # os.system('clr')
            # print('##### Player State ####')            
            # print('Movement', self.player.movement)
            # print('Velocity:', self.player.velocity)
            # print('Player Size:', self.player.size, self.player.base_size)
            # print('Player Pos:', int(self.player.pos[1]), int(self.player.center_pos[1]))
            # print('Player rect:', self.player.rect(), self.player.rect().top)
            # print('Player Center Pos:', self.player.center_pos)
            # print('Current Action:', self.player.action)
            # print('Player collision:', self.player.collisions)
            # print('Tiles around player center pos:', self.tilemap.tiles_around(self.player.center_pos))
            # print('Used Jump:', self.player.used_jump)
            # print('Canceled Jump:', self.player.canceled_jump)
            # print('Air Time:', self.player.air_time)
            # print('\n#### Current Scene Info ####')
            # print('Current Scene:', self.current_scene)
            # print('Current current_world_and_level', self.current_world_and_level)
            # print(self.assets['space_ship_ground'])

            
            # Rendering           
            self.display.fill(self.BACKGROUND_COLOR)
            # self.display.blit(self.assets['background/stars'], (0, 0))
            
            self.tilemap.render(self.display, camera_offset = self.camera_render_scroll)
            self.player.render(self.display, camera_offset = self.camera_render_scroll, debug_hitbox_show=False)
            self.coin.render(self.display, camera_offset = self.camera_render_scroll, debug_hitbox_show=False)

            # Flip Buffer
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            pygame.display.update()  
            
            # Clock          
            self.clock.tick(self.GAME_MAX_FPS)

Game().run()
pygame.quit()
print('Game Terminated.')
