import pygame
from scripts.utils import json_into_dictionary

BASE_IMG_PATH = 'data/images/'
BLACK = (0, 0, 0)

class Animation:
    def __init__(self, game, action_type, spritesheet_path, json_frame_data_path = None, loopable = True):
        self.game = game
        self.action_type = action_type
        self.spritesheet_path = spritesheet_path
        self.json_frame_data_path = json_frame_data_path
        self.spritesheet = pygame.image.load(BASE_IMG_PATH + spritesheet_path).convert_alpha()
        self.json_frame_data = json_into_dictionary(json_frame_data_path)
        self.loopable = loopable

        self.done = False
        self.current_frame = 0
        
        self.first_frame_data = self.json_frame_data['frames'][self.action_type + ' 0.aseprite']
        self.frame_width = self.first_frame_data['sourceSize']['w']
        self.frame_height = self.first_frame_data['sourceSize']['h']
        self.frames_total = len(self.json_frame_data['frames'])
        self.frame_duration = self.game.GAME_MAX_FPS / (1000 / self.first_frame_data['duration'])
        
    def copy(self):
        return Animation(self.game, self.action_type, self.spritesheet_path, self.json_frame_data_path, self.loopable)
        
    def extract_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey(BLACK)
        x = w * int(self.current_frame)
        sprite.blit(self.spritesheet, (0, 0), (x, y, w, h))
        return sprite
    
    def update(self):
        if self.loopable == True:
            self.current_frame = (self.current_frame + 1 / self.frame_duration) % self.frames_total
            
        if self.loopable == False:
            pass