import pygame
import os
import json
from scripts.utils import load_images
from scripts.tilemap import Tilemap
from scripts.animation import Animation

# Keybinds:
#  I - import
#  O - Overwrite
#  W, S - Scroll Tilesets
#  A, D - Scroll Tile Variant
#  Q, E - Rotate 90DEG
#  Arrow Keys - Camera Movement
#  Home - Return Camera
#  Delete - Wipe Level Data

# https://www.youtube.com/watch?v=2gABYM5M0ww

BACKGROUND_COLOR = (50, 50, 50)
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
GAME_MAX_FPS = 60
DISPLAY_SCALE_FACTOR = 2
CAMERA_SPEED = 3

BASE_LEVEL_DATA_PATH = 'data/level_data/'


class Editor():
    def __init__(self):
        pygame.init()
        
        pygame.display.set_caption('Level_Editor: Shitty Castlevania')
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.display = pygame.Surface((SCREEN_WIDTH / DISPLAY_SCALE_FACTOR, SCREEN_HEIGHT / DISPLAY_SCALE_FACTOR))
        
        self.clock = pygame.time.Clock()
        
        self.camera_scroll = [0, 0]
        
        self.assets = {
            'castle_ground': load_images('tiles/castle_ground'),
            'space_ship_ground': load_images('tiles/space_ship_ground'),
        }
        
        self.movement = [False, False, False, False]
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0
        self.tile_rotation = 0
        
        self.wipe_tilemap = 0
        
        self.clicking = False
        self.right_clicking = False
        
        self.file_import, self.file_export = False, False
        self.world_folders = os.listdir(BASE_LEVEL_DATA_PATH)
        self.selected_world_folder = 0
        self.level_files = []
        self.selected_level_file = 0
        
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False 
                
                # Mouse Click Register
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.clicking = True    
                    if event.button == 3:
                        self.right_clicking = True
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.right_clicking = False

                if event.type == pygame.KEYDOWN:
                    # Tile Selection
                    if event.key == pygame.K_w:
                        self.tile_variant = 0
                        self.tile_rotation = 0
                        self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                    if event.key == pygame.K_s:
                        self.tile_variant = 0
                        self.tile_rotation = 0
                        self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                    if event.key == pygame.K_a:
                        self.tile_rotation = 0
                        self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                    if event.key == pygame.K_d:
                        self.tile_rotation = 0
                        self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                    if event.key == pygame.K_q:
                        self.tile_rotation = (self.tile_rotation - 1) % 4
                    if event.key == pygame.K_e:
                        self.tile_rotation = (self.tile_rotation + 1) % 4 
                        
                    # File Import/Export
                    if event.key == pygame.K_i:
                        self.file_import = True
                    if event.key == pygame.K_o:
                        self.file_export = True
                        
                    # Level Selection
                    if event.key == pygame.K_j:
                        self.selected_level_file = 0
                        self.selected_world_folder = (self.selected_world_folder - 1) % len(self.world_folders)
                    if event.key == pygame.K_k:   
                        self.selected_level_file = 0
                        self.selected_world_folder = (self.selected_world_folder + 1) % len(self.world_folders)
                    if event.key == pygame.K_n:
                        self.selected_level_file = (self.selected_level_file - 1) % len(self.level_files)
                    if event.key == pygame.K_m:
                        self.selected_level_file = (self.selected_level_file + 1) % len(self.level_files)
                    
                    # Tilemap Editing
                    if event.key == pygame.K_DELETE:
                        self.wipe_tilemap = True
                    
                    # Camera Movement
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True 
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = True   
                    if event.key == pygame.K_HOME:
                        self.camera_scroll = [0, 0]
                        
                if event.type == pygame.KEYUP:
                    # Camera Movement
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = False 
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
                    if event.key == pygame.K_UP:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN:
                        self.movement[3] = False  

            # Display Selected Tile
            current_tile_image = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_image.set_alpha(100)
            current_tile_image = pygame.transform.rotate(current_tile_image, self.tile_rotation * -90)
            
            # Mouse Position BS
            mouse_position = pygame.mouse.get_pos() # Mouse pos depending on position in the game window, top-left being (0, 0)
            mouse_position = (mouse_position[0] / DISPLAY_SCALE_FACTOR, mouse_position[1] / DISPLAY_SCALE_FACTOR)
            tile_position = ((mouse_position[0] + self.camera_scroll[0]) // self.tilemap.tile_size, 
                             (mouse_position[1] + self.camera_scroll[1]) // self.tilemap.tile_size)
            tile_position = (int(tile_position[0]), 
                             int(tile_position[1]))
            
            # Camera Offset scroll
            render_scroll = (int(self.camera_scroll[0]), int(self.camera_scroll[1]))
            
            # Tilemap Editing
            tile_location = str(tile_position[0]) + ';' + str(tile_position[1])
            if self.clicking:
                self.tilemap.tilemap[str(tile_position[0]) + ';' + str(tile_position[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': tile_position, 'rotation': self.tile_rotation}
            if self.right_clicking:
                if tile_location in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_location]
            if self.wipe_tilemap:
                self.tilemap.tilemap.clear()
                self.wipe_tilemap = False
                
            # Import/Export Tilemap
            self.level_files = os.listdir(BASE_LEVEL_DATA_PATH + self.world_folders[self.selected_world_folder])
            selected_json_file = BASE_LEVEL_DATA_PATH + self.world_folders[self.selected_world_folder] + '/' + str(self.selected_level_file) +'.json'
            
            if self.file_import:
                with open(selected_json_file, 'r') as json_file:
                    json_file_loaded = json.load(json_file)
                self.tilemap.tilemap = json_file_loaded
                self.file_import = False
                    
            if self.file_export:
                json_tilemap_export = json.dumps(self.tilemap.tilemap)
                with open(selected_json_file, 'w') as json_file:
                    json_file.write(json_tilemap_export)
                    self.file_export = False

            # Camera System
            if self.movement[0]:
                self.camera_scroll[0] += -CAMERA_SPEED
            if self.movement[1]:
                self.camera_scroll[0] += CAMERA_SPEED
            if self.movement[2]:
                self.camera_scroll[1] += -CAMERA_SPEED
            if self.movement[3]:
                self.camera_scroll[1] += CAMERA_SPEED

            # Rendering           
            self.display.fill(BACKGROUND_COLOR)
            self.display.blit(current_tile_image, (5, 5)) # (5, 5) = Pixel offset for selected tiles
            self.display.blit(current_tile_image, (tile_position[0] * self.tilemap.tile_size - self.camera_scroll[0], 
                                                   tile_position[1] * self.tilemap.tile_size - self.camera_scroll[1]))
            self.tilemap.render(self.display, camera_offset=render_scroll)

            # Debug prints
            os.system('clear')
            print('#### Selected Tiles Infomation ####')
            # print('Tile List:', self.tile_list)
            # print('Selected Tile Group:', self.tile_list[self.tile_group])
            # print('Current Tile Variant:', self.tile_variant)
            # print('Current Tile Rotation:', self.tile_rotation)
            print('Hovered Tile Position:', tile_position)
            
            print('\n#### Camera Movement ####')
            print('Movement:', self.movement)
            print('Camera Scroll:', self.camera_scroll)
            
            print('\n#### File System ####')
            # print('File Import|Export:', self.file_import, '|', self.file_export)
            print('Current World Folder:', self.selected_world_folder, '||' ,self.world_folders[self.selected_world_folder])
            print('Current Level:', self.selected_level_file, '||' ,self.level_files[self.selected_level_file])
            print('World Folders', self.world_folders)
            print('Level Jsons:', self.level_files)
            
            print('\n#### Mouse Position/State ####')
            print('Mouse Position:', mouse_position)
            # print('Left|Right Click State:', self.clicking, '|', self.right_clicking)
            
            # print('\n#### Tilemap Information ####')
            # print('Tile Location:', tile_location)
            # print('Tilemap:', self.tilemap.tilemap)
            # print('Off-grid Tiles:', self.tilemap.offgrid_tiles)
            # print('Current Level Data:', open(selected_json_file, 'r').read())
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            self.clock.tick(GAME_MAX_FPS)
            pygame.display.update()            
            

Editor().run()
pygame.quit()
